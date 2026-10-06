#!/usr/bin/env python3
"""Build the English Zenodo package and upload an unpublished draft.

Reads the token from the ZENODO_TOKEN environment variable, or from
/tmp/zenodo_token when that variable is unset. The token is never printed
and is never written into this repository.

The script does not call the Zenodo publish action.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import quote, unquote
from xml.etree import ElementTree as ET

import requests
from requests.adapters import HTTPAdapter

REPO = Path(__file__).resolve().parents[1]
WORK = Path("/tmp/zenodo-deposit")
TREE = WORK / "tree"
SESSION_ZIPS = WORK / "session-zips"
DRAFT_PATH = WORK / "draft.json"
OBSOLETE = [
    "flip_2m.zip",
    "flip_5m.zip",
    "flip_10m.zip",
    "neo2_2m.zip",
    "neo2_5m.zip",
    "neo2_10m.zip",
    "mini4pro_2m.zip",
    "mini4pro_5m.zip",
    "mini4pro_10m.zip",
    "matrice350_trajectory_UNRESOLVED.zip",
]
DAV = {"d": "DAV:"}

WEBDAV = "https://cloud.conceptio.ita.br/public.php/webdav/"
WEBDAV_USER = "3pmRmz7CokJpZr5"
ZENODO = "https://zenodo.org/api/deposit/depositions"

TITLE = (
    "Indoor acoustic recordings of multirotor aircraft with a reference "
    "microphone and an eight-channel array "
    "(DataSet_Arena_Indoor_v0.2_Extended_Time)"
)
DESCRIPTION = """<p>Indoor acoustic recordings of multirotor aircraft collected at the CONCEPTIO laboratory, Instituto Tecnológico de Aeronáutica, São José dos Campos (DataSet_Arena_Indoor_v0.2_Extended_Time).</p>
<p>Thirteen takes were recorded with a mono Behringer reference channel (44.1 kHz, IEEE float32) and an eight-channel ReSpeaker array (16 kHz, 16-bit PCM). Microphone models are not named. The array is described as a six-microphone circular array; channels 7 and 8 remain in the eight-channel files. Raw reference audio totals 3165.70 s. Each condition is a single take. Distances are sidecar labels. No range or trajectory log is included.</p>
<pre>
flip.zip
└── flip/
    ├── 2m/
    │   ├── raw_reference.wav            Behringer, mono, 44.1 kHz, float32
    │   ├── raw_array.wav                ReSpeaker, 8 channels, 16 kHz, 16-bit
    │   ├── synchronized_reference.wav
    │   ├── synchronized_array.wav
    │   └── sidecar.json                 aircraft, distance, timestamp, gains
    ├── 5m/                              same five files
    └── 10m/                             same five files
neo2.zip
└── neo2/{2m,5m,10m}/                    same five files
mini4pro.zip
└── mini4pro/{2m,5m,10m}/                same five files
mini4pro_noguard_free.zip
└── mini4pro_noguard_free/               same five files
multi_neo2_mini4pro_free.zip
└── multi_neo2_mini4pro_free/            same five files
multi_flip_neo2_mini4pro_matrice_free.zip
└── multi_flip_neo2_mini4pro_matrice_free/
matrice350.zip
└── matrice350/                          same five files; one trajectory labeled 10 m, 5 m, and 2 m
catalog.csv                              session table
channel_audit.csv                        array-channel levels
processing_methodology.pdf               processing note
dji_flip.json                            manufacturer sheet
dji_neo.json
dji_mini_4_pro.json
dji_matrice_350_rtk.json
dji_neo_and_mini_4_pro.json
dji_flip_neo_mini_4_pro_and_matrice_350.json
</pre>
<p>The matrice350 sidecar records the aircraft string DJI Flip. Neo sidecars say DJI Neo 2; the manufacturer sheet describes DJI Neo. Synchronized file lengths differ by at least 1 s for flip/5m, neo2/5m, mini4pro/5m, and mini4pro_noguard_free.</p>"""

SPECS = [
    (
        "DJI_FPV_FLIP/especificacoes_oficiais_fabricante.json",
        "specifications/dji_flip.json",
    ),
    (
        "DJI_NEO_2/especificacoes_oficiais_fabricante.json",
        "specifications/dji_neo.json",
    ),
    (
        "DJI_MINI_4_PRO/especificacoes_oficiais_fabricante.json",
        "specifications/dji_mini_4_pro.json",
    ),
    (
        "DJI_MATRICE_350/especificacoes_oficiais_fabricante.json",
        "specifications/dji_matrice_350_rtk.json",
    ),
    (
        "DJI_NEO_2_E_DJI_MINI_4_PRO/especificacoes_oficiais_fabricante.json",
        "specifications/dji_neo_and_mini_4_pro.json",
    ),
    (
        "DJI_FLIP_NEO_MINI_MATRICE/especificacoes_oficiais_fabricante.json",
        "specifications/dji_flip_neo_mini_4_pro_and_matrice_350.json",
    ),
]


def token() -> str:
    value = os.environ.get("ZENODO_TOKEN", "").strip()
    if not value:
        path = Path("/tmp/zenodo_token")
        if path.is_file():
            value = path.read_text().strip()
    if not value:
        sys.exit("Zenodo token is missing. Set ZENODO_TOKEN.")
    return value


def webdav_url(relative: str) -> str:
    return WEBDAV + "/".join(quote(part, safe="") for part in relative.split("/"))


def download(session: requests.Session, relative: str, dest: Path, expected: int | None) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and expected is not None and dest.stat().st_size == expected:
        print(f"keep {dest.name} ({expected} bytes)", flush=True)
        return
    part = dest.with_name(dest.name + ".part")
    url = webdav_url(relative)
    last_error: Exception | None = None
    for attempt in range(6):
        try:
            existing = part.stat().st_size if part.is_file() else 0
            headers = {"Range": f"bytes={existing}-"} if existing else {}
            response = session.get(url, headers=headers, stream=True, timeout=(30, 180))
            if response.status_code == 416:
                part.unlink(missing_ok=True)
                continue
            if response.status_code == 200 and existing:
                existing = 0
            response.raise_for_status()
            mode = "ab" if existing and response.status_code == 206 else "wb"
            written = existing if mode == "ab" else 0
            with part.open(mode) as handle:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        handle.write(chunk)
                        written += len(chunk)
            if expected is not None and written != expected:
                part.unlink(missing_ok=True)
                raise RuntimeError(f"{relative}: got {written}, expected {expected}")
            part.replace(dest)
            print(f"got {relative} ({dest.stat().st_size} bytes)", flush=True)
            return
        except Exception as exc:  # noqa: BLE001 - retry network failures
            last_error = exc
            wait = 2 ** attempt
            print(f"retry {attempt + 1} {relative}: {exc}", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"download failed: {relative}: {last_error}")


def list_files(session: requests.Session, relative: str) -> list[tuple[str, int, str]]:
    body = (
        '<?xml version="1.0"?>'
        '<d:propfind xmlns:d="DAV:"><d:prop>'
        "<d:getcontentlength/><d:resourcetype/>"
        "</d:prop></d:propfind>"
    )
    response = session.request(
        "PROPFIND",
        webdav_url(relative),
        data=body,
        headers={"Depth": "1", "Content-Type": "application/xml"},
        timeout=120,
    )
    response.raise_for_status()
    root = ET.fromstring(response.content)
    found: list[tuple[str, int, str]] = []
    for item in root.findall("d:response", DAV):
        href = unquote(item.find("d:href", DAV).text or "")
        path = href.split("/public.php/webdav/", 1)[-1].strip("/")
        if path == relative.strip("/"):
            continue
        props = item.find("d:propstat/d:prop", DAV)
        kind = props.find("d:resourcetype", DAV)
        if kind is not None and kind.find("d:collection", DAV) is not None:
            continue
        length = props.find("d:getcontentlength", DAV)
        name = path.split("/")[-1]
        found.append((name, int(length.text), path))
    return found


def pick(entries: list[tuple[str, int, str]], name: str) -> tuple[str, int, str]:
    hits = [entry for entry in entries if entry[0].lower() == name.lower()]
    if len(hits) != 1:
        sys.exit(f"{name}: found {[entry[0] for entry in hits]}")
    return hits[0]


def package_files(session: requests.Session, rows: list[dict[str, str]]) -> list[tuple[str, str, int]]:
    files: list[tuple[str, str, int]] = []
    for row in rows:
        rel = row["relative_path"]
        stem = row["file_stem"]
        archive = f"sessions/{row['session_id']}"
        raw = list_files(session, f"{rel}/Brutos")
        synced = list_files(session, f"{rel}/Sincronizados")
        chosen = [
            (pick(raw, f"{stem}.wav"), f"{archive}/raw_reference.wav"),
            (pick(raw, f"respe_{stem}.wav"), f"{archive}/raw_array.wav"),
            (pick(synced, f"{stem}.wav"), f"{archive}/synchronized_reference.wav"),
            (pick(synced, f"respe_{stem}.wav"), f"{archive}/synchronized_array.wav"),
            (pick(raw, f"respe_{stem}.json"), f"{archive}/sidecar.json"),
        ]
        for (name, size, source), target in chosen:
            print(f"map {name} -> {target} ({size} bytes)", flush=True)
            files.append((source, target, size))
    for source, target in [("METODOLOGIA_PROCESSAMENTO.pdf", "processing_methodology.pdf"), *SPECS]:
        info = session.head(webdav_url(source), timeout=60)
        info.raise_for_status()
        files.append((source, target, int(info.headers["Content-Length"])))
    return files


def fetch_tree() -> None:
    rows = list(csv.DictReader((REPO / "catalog.csv").open(newline="")))
    if len(rows) != 13:
        sys.exit(f"catalog.csv has {len(rows)} rows; expected 13")
    session = requests.Session()
    session.auth = (WEBDAV_USER, "")
    for source, archive, size in package_files(session, rows):
        download(session, source, TREE / archive, size)
    for name in ("README.md", "catalog.csv", "channel_audit.csv"):
        target = TREE / name
        target.write_bytes((REPO / name).read_bytes())
        print(f"copied {name}", flush=True)


def session_archives() -> list[Path]:
    SESSION_ZIPS.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader((REPO / "catalog.csv").open(newline="")))
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        zip_name = f"{row['archive_dir'].split('/')[0]}.zip"
        groups.setdefault(zip_name, []).append(row)
    archives: list[Path] = []
    for zip_name, members in groups.items():
        packed: list[tuple[str, list[Path]]] = []
        for row in members:
            source = TREE / "sessions" / row["session_id"]
            files = sorted(path for path in source.iterdir() if path.is_file())
            if len(files) != 5:
                sys.exit(f"{row['session_id']}: expected 5 files, found {[path.name for path in files]}")
            packed.append((row["archive_dir"], files))
        dest = SESSION_ZIPS / zip_name
        newest = max(path.stat().st_mtime for _, files in packed for path in files)
        if not dest.is_file() or dest.stat().st_mtime < newest:
            with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
                for archive_dir, files in packed:
                    for path in files:
                        archive.write(path, f"{archive_dir}/{path.name}")
        print(f"zip {dest.name} {dest.stat().st_size}", flush=True)
        archives.append(dest)
    return archives


def record_files() -> list[Path]:
    specs = sorted((TREE / "specifications").glob("*.json"))
    if len(specs) != 6:
        sys.exit(f"expected 6 specification files, found {len(specs)}")
    methodology = TREE / "processing_methodology.pdf"
    if not methodology.is_file():
        sys.exit(f"missing {methodology}")
    return [
        *session_archives(),
        methodology,
        *specs,
        REPO / "README.md",
        REPO / "catalog.csv",
        REPO / "channel_audit.csv",
    ]


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zenodo_request(session: requests.Session, method: str, url: str, **kwargs):
    timeout = kwargs.pop("timeout", 120)
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            response = session.request(method, url, timeout=timeout, **kwargs)
            if response.status_code in (429, 500, 502, 503, 504):
                raise RuntimeError(f"HTTP {response.status_code}")
            return response
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"{method} {url} failed: {last_error}")


def upload_draft() -> None:
    headers = {
        "Authorization": f"Bearer {token()}",
        "Content-Type": "application/json",
    }
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=0))
    listed = zenodo_request(session, "GET", ZENODO, headers=headers)
    if listed.status_code != 200:
        sys.exit(f"list depositions failed: HTTP {listed.status_code}")
    matches = [
        item
        for item in listed.json()
        if not item.get("submitted") and (item.get("metadata") or {}).get("title") == TITLE
    ]
    if matches:
        chosen = max(matches, key=lambda item: item["id"])
        loaded = zenodo_request(session, "GET", f"{ZENODO}/{chosen['id']}", headers=headers)
        if loaded.status_code != 200:
            sys.exit(f"load deposition failed: HTTP {loaded.status_code}")
        deposition = loaded.json()
        print(f"reuse draft id {deposition['id']}", flush=True)
    else:
        created = zenodo_request(session, "POST", ZENODO, headers=headers, json={})
        if created.status_code not in (200, 201):
            sys.exit(f"create deposition failed: HTTP {created.status_code}")
        deposition = created.json()
        print(f"draft id {deposition['id']}", flush=True)
    dep_id = deposition["id"]
    bucket = deposition["links"]["bucket"]

    metadata = {
        "metadata": {
            "title": TITLE,
            "upload_type": "dataset",
            "publication_date": "2026-10-05",
            "description": DESCRIPTION,
            "creators": [
                {
                    "name": "CONCEPTIO Laboratory",
                    "affiliation": "Instituto Tecnológico de Aeronáutica, São José dos Campos",
                }
            ],
            "keywords": [
                "acoustic recording",
                "multirotor",
                "microphone array",
                "indoor",
                "unmanned aircraft",
                "Behringer",
                "ReSpeaker",
            ],
            "version": "0.2",
            "language": "eng",
            "notes": (
                "Distance series are grouped by aircraft in flip.zip, neo2.zip, and mini4pro.zip. "
                "matrice350.zip is the Matrice 350 trajectory."
            ),
        }
    }
    updated = zenodo_request(
        session,
        "PUT",
        f"{ZENODO}/{dep_id}",
        headers=headers,
        json=metadata,
    )
    if updated.status_code != 200:
        sys.exit(f"metadata update failed: HTTP {updated.status_code} {updated.text[:400]}")

    uploads = record_files()
    file_records = []
    for path in uploads:
        local = md5(path)
        put_headers = {"Authorization": headers["Authorization"]}
        response = None
        for attempt in range(5):
            print(f"upload {path.name} attempt {attempt + 1}", flush=True)
            try:
                with path.open("rb") as handle:
                    response = session.put(
                        f"{bucket}/{quote(path.name)}",
                        data=handle,
                        headers=put_headers,
                        timeout=(30, 3600),
                    )
            except requests.RequestException as exc:
                response = None
                print(f"upload retry {path.name}: {exc.__class__.__name__}", flush=True)
                time.sleep(15 * (attempt + 1))
                continue
            if response.status_code in (200, 201):
                break
            print(f"upload retry {path.name}: HTTP {response.status_code}", flush=True)
            time.sleep(15 * (attempt + 1))
        if response is None or response.status_code not in (200, 201):
            detail = "" if response is None else response.text[:400]
            code = "none" if response is None else response.status_code
            sys.exit(f"upload {path.name} failed: HTTP {code} {detail}")
        body = response.json()
        remote = str(body.get("checksum", ""))
        if remote != f"md5:{local}":
            sys.exit(f"checksum mismatch for {path.name}: remote {remote}")
        print(f"uploaded {path.name} md5 {local} size {path.stat().st_size}", flush=True)
        file_records.append(
            {"name": path.name, "size": path.stat().st_size, "checksum": remote}
        )

    for name in OBSOLETE:
        removed = session.delete(
            f"{bucket}/{quote(name)}",
            headers={"Authorization": headers["Authorization"]},
            timeout=120,
        )
        if removed.status_code not in (204, 404):
            sys.exit(f"delete {name} failed: HTTP {removed.status_code}")
        print(f"removed {name} HTTP {removed.status_code}", flush=True)

    final = zenodo_request(session, "GET", f"{ZENODO}/{dep_id}", headers=headers)
    final.raise_for_status()
    record = final.json()
    if record.get("submitted") or record.get("state") == "done":
        sys.exit("deposition was published; that was not requested")
    summary = {
        "id": dep_id,
        "state": record.get("state"),
        "submitted": record.get("submitted"),
        "html": record["links"].get("html"),
        "title": record.get("metadata", {}).get("title"),
        "license": record.get("metadata", {}).get("license"),
        "files": file_records,
    }
    DRAFT_PATH.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action in ("all", "fetch"):
        fetch_tree()
    if action in ("all", "zip"):
        session_archives()
    if action in ("all", "upload"):
        upload_draft()


if __name__ == "__main__":
    main()
