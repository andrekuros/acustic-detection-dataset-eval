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
from urllib.parse import quote

import requests

REPO = Path(__file__).resolve().parents[1]
WORK = Path("/tmp/zenodo-deposit")
TREE = WORK / "tree"
ZIP_NAME = "indoor_multirotor_acoustic_collection_v0.2.zip"
ZIP_PATH = WORK / ZIP_NAME
DRAFT_PATH = WORK / "draft.json"
MANIFEST_PATH = Path("/tmp/ads-measure/manifest.json")

WEBDAV = "https://cloud.conceptio.ita.br/public.php/webdav/"
WEBDAV_USER = "3pmRmz7CokJpZr5"
ZENODO = "https://zenodo.org/api/deposit/depositions"

TITLE = (
    "Indoor acoustic recordings of multirotor aircraft with a reference "
    "microphone and an eight-channel array "
    "(DataSet_Arena_Indoor_v0.2_Extended_Time)"
)
DESCRIPTION = (
    "This is an independent acoustic-detection data record and is not part "
    "of a software platform. Thirteen indoor multirotor takes were recorded "
    "at the CONCEPTIO laboratory of the Instituto Tecnológico de Aeronáutica, "
    "São José dos Campos. Each take has a mono Behringer reference channel "
    "at 44.1 kHz, IEEE float32, and an eight-channel ReSpeaker array at "
    "16 kHz, 16-bit PCM. Neither microphone model is named in the release. "
    "The zip uses English paths under sessions/SESSION_ID/: "
    "raw_reference.wav, raw_array.wav, synchronized_reference.wav, "
    "synchronized_array.wav, and sidecar.json, plus "
    "processing_methodology.pdf and manufacturer sheets under "
    "specifications/. One-second slices, the six-channel mono export, and "
    "spectrogram pictures are omitted. They are cuts or pictures of the "
    "synchronized audio, and catalog.csv still records their counts on the "
    "source share. A two-page processing note describes a 3 kHz high-pass "
    "used only to find a metallic calibration strike, and a Welch "
    "power-spectral-density and RMS board. Raw files were kept, and "
    "digitally zero channels were not deleted. Container lengths total "
    "2623.95 s of raw reference audio, 2609.66 s of raw array audio, "
    "2445.73 s of synchronized reference audio, and 2436.99 s of "
    "synchronized array audio. Four synchronized pairs differ by at least "
    "one second. The take matrice350_trajectory_UNRESOLVED still has "
    "conflicting folder, file-stem, and sidecar labels. Sidecars say DJI "
    "Neo 2; the copied manufacturer sheet describes DJI Neo (about 135 g), "
    "not Neo 2. The collection has one take per cell, no noise-only "
    "recording, and no repeated trial. This upload is the recordings and "
    "the file notes, not a detection evaluation. The intended license is "
    "CC BY 4.0, pending confirmation, and the author line is a placeholder."
)

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


def load_sizes() -> dict[str, int]:
    if not MANIFEST_PATH.is_file():
        return {}
    sizes: dict[str, int] = {}
    prefix = "/public.php/webdav/"
    for entry in json.loads(MANIFEST_PATH.read_text()):
        if entry.get("is_dir"):
            continue
        href = entry["href"]
        if href.startswith(prefix):
            sizes[href[len(prefix) :]] = int(entry["size"])
    return sizes


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


def package_files(rows: list[dict[str, str]]) -> list[tuple[str, str]]:
    files: list[tuple[str, str]] = []
    for row in rows:
        rel = row["relative_path"]
        stem = row["file_stem"]
        archive = row["archive_dir"]
        files.extend(
            [
                (f"{rel}/Brutos/{stem}.wav", f"{archive}/raw_reference.wav"),
                (f"{rel}/Brutos/respe_{stem}.wav", f"{archive}/raw_array.wav"),
                (f"{rel}/Sincronizados/{stem}.wav", f"{archive}/synchronized_reference.wav"),
                (
                    f"{rel}/Sincronizados/respe_{stem}.wav",
                    f"{archive}/synchronized_array.wav",
                ),
                (f"{rel}/Brutos/respe_{stem}.json", f"{archive}/sidecar.json"),
            ]
        )
    files.append(("METODOLOGIA_PROCESSAMENTO.pdf", "processing_methodology.pdf"))
    files.extend(SPECS)
    return files


def fetch_tree() -> None:
    rows = list(csv.DictReader((REPO / "catalog.csv").open(newline="")))
    if len(rows) != 13:
        sys.exit(f"catalog.csv has {len(rows)} rows; expected 13")
    sizes = load_sizes()
    session = requests.Session()
    session.auth = (WEBDAV_USER, "")
    for source, archive in package_files(rows):
        download(session, source, TREE / archive, sizes.get(source))
    for name in ("README.md", "catalog.csv", "channel_audit.csv"):
        target = TREE / name
        target.write_bytes((REPO / name).read_bytes())
        print(f"copied {name}", flush=True)


def build_zip() -> None:
    if ZIP_PATH.is_file():
        ZIP_PATH.unlink()
    count = 0
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for path in sorted(TREE.rglob("*")):
            if path.is_file() and not path.name.endswith(".part"):
                archive.write(path, path.relative_to(TREE).as_posix())
                count += 1
    print(f"zip {ZIP_PATH} files={count} bytes={ZIP_PATH.stat().st_size}", flush=True)


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
    created = zenodo_request(session, "POST", ZENODO, headers=headers, json={})
    if created.status_code not in (200, 201):
        sys.exit(f"create deposition failed: HTTP {created.status_code}")
    deposition = created.json()
    dep_id = deposition["id"]
    bucket = deposition["links"]["bucket"]
    print(f"draft id {dep_id}", flush=True)

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
                "Draft. License is unset until the authors confirm it. "
                "The intended license is CC BY 4.0. The creator line is a "
                "placeholder. matrice350_trajectory_UNRESOLVED is unresolved."
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

    uploads = [
        ZIP_PATH,
        REPO / "README.md",
        REPO / "catalog.csv",
        REPO / "channel_audit.csv",
    ]
    file_records = []
    for path in uploads:
        local = md5(path)
        put_headers = {"Authorization": headers["Authorization"]}
        response = None
        for attempt in range(4):
            with path.open("rb") as handle:
                response = session.put(
                    f"{bucket}/{quote(path.name)}",
                    data=handle,
                    headers=put_headers,
                    timeout=7200,
                )
            if response.status_code in (200, 201):
                break
            print(f"upload retry {attempt + 1} {path.name}: HTTP {response.status_code}", flush=True)
            time.sleep(2 ** attempt)
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
        build_zip()
    if action in ("all", "upload"):
        if not ZIP_PATH.is_file():
            sys.exit(f"missing {ZIP_PATH}")
        upload_draft()


if __name__ == "__main__":
    main()
