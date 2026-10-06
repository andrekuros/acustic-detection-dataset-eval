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
    "dji_flip.json",
    "dji_neo.json",
    "dji_mini_4_pro.json",
    "dji_matrice_350_rtk.json",
    "dji_neo_and_mini_4_pro.json",
    "dji_flip_neo_mini_4_pro_and_matrice_350.json",
]
DAV = {"d": "DAV:"}

WEBDAV = "https://cloud.conceptio.ita.br/public.php/webdav/"
WEBDAV_USER = "3pmRmz7CokJpZr5"
ZENODO = "https://zenodo.org/api/deposit/depositions"

# Prefer this draft when refreshing metadata or files. Do not publish it.
DRAFT_ID = 23170386
TITLE = (
    "Indoor Multirotor Acoustic Dataset for Drone Detection and Classification "
    "(DataSet_Arena_Indoor_v0.2_Extended_Time)"
)
DESCRIPTION = """<h2>Overview</h2>
<p>This dataset is for acoustic drone detection and classification. It provides indoor multirotor recordings so that a mono reference microphone and an eight-channel array can be compared on the same take. The collection is DataSet_Arena_Indoor_v0.2_Extended_Time, recorded at the CONCEPTIO Laboratory, Instituto Tecnológico de Aeronáutica, São José dos Campos. Thirteen takes cover DJI Flip, DJI Neo 2, DJI Mini 4 Pro, and DJI Matrice 350, including free flights and two multi-aircraft takes. Raw reference audio totals 3165.70 s. Each condition is one take. The record does not include a detector score or a trained model.</p>
<h2>Files</h2>
<p>Audio is one zip per aircraft or flight, a few hundred megabytes each. Download the zip for the aircraft you need. File names and JSON fields in the package are English. <code>catalog.csv</code> is the index of every take.</p>
<ul>
<li><strong>flip.zip</strong>, <strong>neo2.zip</strong>, <strong>mini4pro.zip</strong> — DJI Flip, DJI Neo 2, and DJI Mini 4 Pro at the sidecar distances 2 m, 5 m, and 10 m. Each distance is its own folder.</li>
<li><strong>mini4pro_noguard_free.zip</strong> — one Mini 4 Pro free flight with the propeller guard removed.</li>
<li><strong>multi_neo2_mini4pro_free.zip</strong> — one free flight with Neo 2 and Mini 4 Pro together.</li>
<li><strong>multi_flip_neo2_mini4pro_matrice_free.zip</strong> — one free flight with Flip, Neo 2, Mini 4 Pro, and Matrice together.</li>
<li><strong>matrice350.zip</strong> — one DJI Matrice 350 pass. The sidecar distance is the whole string "10m, 5m and 2m", one trajectory.</li>
<li><strong>catalog.csv</strong> — one row per take: folder inside the zip, durations, sidecar text, and the slice counts of the source share.</li>
<li><strong>channel_audit.csv</strong> — level of each array channel at the start, middle, and end of the raw array file.</li>
<li><strong>processing_methodology.pdf</strong> — the two-page processing note from the collection.</li>
<li><strong>aircraft_specifications.json</strong> — one English file with the manufacturer sheets for Flip, Neo, Mini 4 Pro, and Matrice 350 RTK. Copied manufacturer data, not campaign measurements.</li>
</ul>
<h2>Recording</h2>
<p>Each take has a mono Behringer reference (44.1 kHz, IEEE float32) and an eight-channel ReSpeaker array (16 kHz, 16-bit PCM). Microphone model names are absent from the collection. The processing note calls the array a six-microphone circular array. Channels 7 and 8 stay in the eight-channel files. Distances are the strings in the sidecar: 2m, 5m, 10m, and free. The collection has no range log and no trajectory log.</p>
<h2>Inside a zip</h2>
<p>Every take folder holds the same five files. In flip.zip the 2 m take looks like this. The 5 m and 10 m folders, and the folders in the other zips, use the same five names.</p>
<pre>flip/2m/
├── raw_reference.wav           Behringer, mono, 44.1 kHz, float32
├── raw_array.wav               ReSpeaker, 8 channels, 16 kHz, 16-bit
├── synchronized_reference.wav
├── synchronized_array.wav
└── sidecar.json                aircraft, distance, timestamp, gains</pre>
<p>The WAV bytes are stored uncompressed. <code>archive_dir</code> in catalog.csv is that folder. Each sidecar uses English keys: timestamp, aircraft, distance, gains.</p>
<h2>Reading a take</h2>
<p><code>session_id</code> names the take. <code>raw_reference_s</code>, <code>raw_array_s</code>, <code>sync_reference_s</code>, and <code>sync_array_s</code> are container durations in seconds. <code>sync_duration_delta_s</code> is the synchronized reference duration minus the synchronized array duration. <code>reference_mid_rms_dbfs</code> is a 2.0 s window at the middle of the raw reference, in dBFS with full scale equal to 1.</p>
<p><code>channel_audit.csv</code> has one row per take, channel (1–8), and window (start, mid, end). <code>channel_class</code> is varying, flat, near_silent, digital_zero, idle, stuck_constant, or mixed. A channel is varying when all three windows are signal, the loudest window is above −80 dBFS, and the three windows span at least 3 dB.</p>
<h2>Limitations</h2>
<ul>
<li>Package sidecars correct labels that were wrong or Portuguese on the source share. The Matrice take source sidecar said DJI Flip; the package sidecar says DJI Matrice 350. Flip source sidecars said DJI FPV Flip; the package says DJI Flip. Source distance LIVRE is free in the package. The Matrice source distance "10m, 5m e 2m" is "10m, 5m and 2m".</li>
<li>Neo session folders on the source share held a manufacturer sheet for DJI Neo (about 135 g), not Neo 2. That sheet is the dji_neo block in aircraft_specifications.json.</li>
<li>Four synchronized pairs differ by at least 1 s: flip/5m (+1.79 s), neo2/5m (−4.46 s), mini4pro/5m (+10.56 s), and mini4pro_noguard_free (+1.31 s). matrice350 differs by −0.13 s. The other eight are within 0.12 s.</li>
<li>mini4pro_noguard_free has no matched free flight with the guard on, so the missing guard is mixed with the flight pattern.</li>
<li>The two multi-aircraft takes have no time marks that assign a segment to one airframe.</li>
<li>There is one take per condition, no noise-only recording, and no repeated trial. Level changes along a file are not a flight profile.</li>
<li>The processing note used a 3 kHz high-pass only to find a metallic calibration strike. The note does not say the stored WAV samples were filtered, and it does not give room size, microphone coordinates, filter order, FFT length, or hop.</li>
</ul>"""

# Manufacturer sheets live in aircraft_specifications.json in the repository.

# Corrected English sidecar content written into each take folder.
ENGLISH_SIDECARS = {
    "flip_2m": ("2026-05-22 09:01:24.453156", "DJI Flip", "2m"),
    "flip_5m": ("2026-05-22 09:08:08.200775", "DJI Flip", "5m"),
    "flip_10m": ("2026-05-22 09:14:39.100076", "DJI Flip", "10m"),
    "neo2_2m": ("2026-05-22 09:47:58.841664", "DJI Neo 2", "2m"),
    "neo2_5m": ("2026-05-22 09:52:58.634050", "DJI Neo 2", "5m"),
    "neo2_10m": ("2026-05-22 09:58:33.579961", "DJI Neo 2", "10m"),
    "mini4pro_2m": ("2026-05-22 09:22:13.073119", "DJI Mini 4 Pro", "2m"),
    "mini4pro_5m": ("2026-05-22 09:26:14.535361", "DJI Mini 4 Pro", "5m"),
    "mini4pro_10m": ("2026-05-22 09:32:49.174844", "DJI Mini 4 Pro", "10m"),
    "mini4pro_noguard_free": ("2026-05-22 10:36:30.664300", "DJI Mini 4 Pro", "free"),
    "multi_neo2_mini4pro_free": (
        "2026-05-22 10:30:11.530212",
        "DJI Neo 2 + DJI Mini 4 Pro",
        "free",
    ),
    "multi_flip_neo2_mini4pro_matrice_free": (
        "2026-05-22 10:18:42.274861",
        "DJI Flip + DJI Neo 2 + DJI Mini 4 Pro + DJI Matrice 350",
        "free",
    ),
    "matrice350": ("2026-09-16 13:05:40.727258", "DJI Matrice 350", "10m, 5m and 2m"),
}


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
    for source, target in [("METODOLOGIA_PROCESSAMENTO.pdf", "processing_methodology.pdf")]:
        info = session.head(webdav_url(source), timeout=60)
        info.raise_for_status()
        files.append((source, target, int(info.headers["Content-Length"])))
    return files


def write_english_sidecars() -> None:
    gains = [1.0] * 8
    for session_id, (timestamp, aircraft, distance) in ENGLISH_SIDECARS.items():
        path = TREE / "sessions" / session_id / "sidecar.json"
        if not path.parent.is_dir():
            sys.exit(f"missing session folder for {session_id}")
        body = {
            "timestamp": timestamp,
            "aircraft": aircraft,
            "distance": distance,
            "gains": gains,
        }
        path.write_text(json.dumps(body, indent=2) + "\n")
        print(f"wrote English sidecar {session_id}", flush=True)


def fetch_tree() -> None:
    rows = list(csv.DictReader((REPO / "catalog.csv").open(newline="")))
    if len(rows) != 13:
        sys.exit(f"catalog.csv has {len(rows)} rows; expected 13")
    session = requests.Session()
    session.auth = (WEBDAV_USER, "")
    for source, archive, size in package_files(session, rows):
        download(session, source, TREE / archive, size)
    write_english_sidecars()
    for name in ("README.md", "catalog.csv", "channel_audit.csv", "aircraft_specifications.json"):
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
    write_english_sidecars()
    specs = REPO / "aircraft_specifications.json"
    if not specs.is_file():
        sys.exit(f"missing {specs}")
    methodology = TREE / "processing_methodology.pdf"
    if not methodology.is_file():
        sys.exit(f"missing {methodology}")
    return [
        *session_archives(),
        methodology,
        specs,
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
        if not item.get("submitted")
        and (
            item.get("id") == DRAFT_ID
            or (item.get("metadata") or {}).get("title") == TITLE
        )
    ]
    if matches:
        chosen = next((item for item in matches if item.get("id") == DRAFT_ID), None)
        if chosen is None:
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

    metadata = metadata_body()
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


def metadata_body() -> dict:
    return {
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
                "acoustic drone detection",
                "drone classification",
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
                "One zip per aircraft or flight. catalog.csv is the index. "
                "Package sidecars and aircraft_specifications.json are English. "
                "matrice350.zip is the Matrice 350 trajectory."
            ),
        }
    }


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action in ("all", "fetch"):
        fetch_tree()
    if action in ("all", "zip"):
        session_archives()
    if action in ("all", "upload"):
        upload_draft()
    if action == "describe":
        # A metadata PUT clears files already in the bucket, so this re-sends every file.
        upload_draft()


if __name__ == "__main__":
    main()
