This is an independent acoustic-detection data record and is not part of a software platform.

# Indoor Multirotor Acoustic Dataset for Drone Detection and Classification

`DataSet_Arena_Indoor_v0.2_Extended_Time` is an indoor acoustic collection of thirteen multirotor takes, prepared as a data record for acoustic drone detection and classification. This repository documents that collection. It does not contain the audio, and it does not contain a manuscript or a detection result.

Author line, used here as a placeholder: CONCEPTIO Laboratory, Instituto Tecnológico de Aeronáutica, São José dos Campos.

## Before publishing the Zenodo record

`scripts/build_and_upload_zenodo.py` can create an unpublished draft. Do these three things before publishing it.

1. Confirm the license. The text below marks CC BY 4.0 as the intended license, and it is pending confirmation. This repository does not include a `LICENSE` file, because that file would assert a license the authors have not confirmed. Zenodo fills an empty license with CC0. That default is not a confirmed choice. Change the license field before publishing.
2. Replace the author placeholder with the author list the laboratory wants. Do not invent personal names to fill it.
3. The archive name for that take is `matrice350`, following the directory and the file stem. The sidecar still says `DJI Flip`. That string stays in `catalog.csv`.

The source share is 6,004,947,774 bytes (6.00 GB). The filtered package below is 2,654,584,283 bytes of audio, the processing note, and the manufacturer sheets, plus this README, `catalog.csv`, and `channel_audit.csv`. That is under the Zenodo 50 GB limit.

## What is in the Zenodo package

The source share uses Portuguese folder names and keeps several derived copies of the same audio. The deposit uses English names and keeps one copy of each recording.

Included, for every take:

| File inside the take folder | Source |
| --- | --- |
| `raw_reference.wav` | `Brutos/<stem>.wav` |
| `raw_array.wav` | `Brutos/respe_<stem>.wav` |
| `synchronized_reference.wav` | `Sincronizados/<stem>.wav` |
| `synchronized_array.wav` | `Sincronizados/respe_<stem>.wav` |
| `sidecar.json` | the raw sidecar; the other two copies are identical |

`archive_dir` in `catalog.csv` is that folder. The zip name is the aircraft or flight: `flip.zip`, `neo2.zip`, and `mini4pro.zip` each hold the 2 m, 5 m, and 10 m folders. The four other flights are one folder each. `relative_path` remains the original share path. On the Matrice take, the raw array and its sidecar in `Brutos` are named `Respe_` with a capital R. The synchronized copies of those two files use `respe_`.

Also included: `processing_methodology.pdf` (the source file `METODOLOGIA_PROCESSAMENTO.pdf`) and the manufacturer JSON sheets, renamed under `specifications/`. The Mini 4 Pro sheet in the no-guard folder is byte-identical to `specifications/dji_mini_4_pro.json`, so it is not repeated. The JSON keys inside those sheets are still the Portuguese field names from the source. They are copied manufacturer data, not campaign measurements.

Left out:

- One-second slice WAVs. On the takes that were checked, each slice is an exact cut of the synchronized file, and the slice count is the floor of that duration.
- The six mono channel files. They are a split of channels 1–6 of `synchronized_array.wav`. Channels 7 and 8 remain in that eight-channel file.
- Spectrogram PNGs. They are pictures rendered from the synchronized audio. The processing note does not give the FFT length, hop, or colormap, so the archive keeps the audio rather than the pictures.

`catalog.csv` still records the slice and PNG counts of the source share. `channel_audit.csv` is a check of the raw array files. Neither file is a detector evaluation.

The record keeps one zip per aircraft or flight, so a reader can download a single aircraft. The processing note, the manufacturer JSON files, this README, the catalog, and the channel audit sit beside those zips. `catalog.csv` is the index.

`scripts/build_and_upload_zenodo.py` builds that package from the share and uploads the draft. The script does not publish the record.

## Where the audio is now

Public share, read-only:

https://cloud.conceptio.ita.br/index.php/s/3pmRmz7CokJpZr5

Folder name: `DataSet_Arena_Indoor_v0.2_Extended_Time`.

WebDAV endpoint: `https://cloud.conceptio.ita.br/public.php/webdav/` with username `3pmRmz7CokJpZr5` and an empty password. The share contains 18,123 files and 6,004,947,774 bytes. Do not commit that tree to git.

Two paths contain spaces and must be URL-quoted:

```text
DJI_MINI_4_PRO -  sem protetor
DJI_MATRICE_350/10m, 5m e 2m
```

The first has two spaces before `sem`. Quoted forms are `DJI_MINI_4_PRO%20-%20%20sem%20protetor` and `DJI_MATRICE_350/10m%2C%205m%20e%202m`.

## Collection

Thirteen takes. Each session folder contains `Brutos`, `Sincronizados`, `Sincronizados/Canais_Separados`, `Processados_Fatias`, `Espectrogramas_Audio_Fragmentado`, and `Espectrogramas_Audio_Geral`.

The Behringer reference is mono, 44.1 kHz, IEEE float32 (WAVE format 3). The model is not named. The ReSpeaker array is 8 channels, 16 kHz, 16-bit PCM. The model is not named. The methodology note calls it a six-microphone circular array. Only CH1–CH6 are exported as mono. Sidecar gains are eight ones. Channels 7 and 8 are never exported as mono files. They remain inside the 8-channel raw, synchronized, and slice WAVs.

Slices are exactly 1.000 s. Reference slices are mono float32 at 44.1 kHz. Array slices are 8-channel 16-bit PCM at 16 kHz. For every session and both sensors, the slice count equals the floor of that sensor’s synchronized duration. Two PNGs per slice (plain and `_TECNICO`) plus nine overview PNGs per session.

`sync_duration_delta_s` is synchronized reference duration minus synchronized array duration. It is a difference of container lengths, not a re-measured residual of the calibration impulse.

Reference mid-file RMS is a 2.0 s window of the raw reference file, starting at half that file’s duration minus 1 s. Full scale is amplitude 1. On the twelve takes timestamped 22 May 2026 the value is −40.90 to −35.43 dBFS.

Measured totals on the source share: raw reference 3165.70 s; raw array 3159.04 s; synchronized reference 2982.16 s; synchronized array 2973.53 s; 2976 reference slices; 2967 array slices; 11886 fragment PNGs; 117 overview PNGs. Session trees hold 18,115 files and 6,004,787,695 bytes. The Zenodo package keeps the raw and synchronized recordings and omits the slices, mono splits, and PNGs.

## Labels that stay as written

Sidecars on the Flip takes say `DJI FPV Flip`. The specification JSON names DJI Flip. The canonical aircraft name is DJI Flip. The sidecar string is kept in `catalog.csv`.

Sidecars say `DJI Neo 2`. The specification JSON in `DJI_NEO_2/` describes DJI Neo (about 135 g), not Neo 2. Do not publish those figures as Neo 2 specifications. Specification sheets are copied manufacturer data, not campaign measurements. The same Neo block is copied into the multi-aircraft sheets.

Distances are sidecar strings only (`2m`, `5m`, `10m`, `LIVRE`). There is no range log. `LIVRE` means free flight.

`mini4pro_noguard_free` is a free flight without a propeller guard. There is no matched free flight with the guard, so the guard is confounded with the flight pattern.

The two multi-aircraft takes have no time marks that assign a segment to one airframe.

`matrice350`: folder `DJI_MATRICE_350/10m, 5m e 2m` and file stem `DJI_MATRICE_10M_5M_2M`. The archive uses that Matrice name. The sidecar still says `"drone": "DJI Flip"`, `"distancia": "10m, 5m e 2m"`, timestamp `2026-09-16 13:05:40`. The distance string is the whole trajectory, not one measured range. The raw reference is 622.38 s, and the mid-file level is −32.68 dBFS. The manufacturer sheet names a DJI Matrice 350 RTK.

Canonical ids: `flip_{2,5,10}m`, `neo2_{2,5,10}m`, `mini4pro_{2,5,10}m`, `mini4pro_noguard_free`, `multi_neo2_mini4pro_free`, `multi_flip_neo2_mini4pro_matrice_free`, `matrice350`.

## Synchronization and slices

Four synchronized pairs differ by at least 1 s: `flip_5m` +1.79 s, `neo2_5m` −4.46 s, `mini4pro_5m` +10.56 s, `mini4pro_noguard_free` +1.31 s. `matrice350` differs by −0.13 s. The other eight are within 0.12 s. Slice indexes are not a shared time base on the four mismatched takes. `neo2_2m` differs by 0.03 s, but the floors still differ (179 reference slices and 180 array slices) because the containers fall on opposite sides of an integer second. `matrice350` does the same (608 reference slices and 609 array slices).

## Channel audit

`channel_audit.csv` has 312 rows: 13 takes, channels 1–8, three 2.0 s windows (32,000 frames) on the raw 8-channel file, starting at 1.0 s, at mid-file minus 1 s, and at 3 s before the end.

Per-window labels: `digital_zero` if the peak is 0; `idle` if the peak is at most 2; `stuck_constant` if every sample in the window is the same value; otherwise `signal`. Array levels are dBFS relative to full-scale integer 32768. A digital-zero window has an empty `rms_dbfs` cell.

A channel is varying only when every window is `signal`, its loudest window is above −80 dBFS, and the three windows span at least 3 dB. Flat means a span under 2 dB and a level below −58 dBFS. Near-silent means the loudest window is at or below −80 dBFS. A channel that is entirely zero, idle, or stuck keeps that class. `mixed` is the remaining case: not all windows are signal, and the loudest window is still above −80 dBFS.

Varying channels:

- `flip_2m`: 1, 5, 6, 7, 8
- `flip_5m`: 5, 6, 7, 8
- `flip_10m`: 1–5
- `neo2_2m`: 1, 2, 7, 8 (channels 5 and 6 are digital zeros and are still exported)
- `neo2_5m`: 3–6
- `neo2_10m`: 1, 2, 3, 7, 8
- `mini4pro_2m`: 1, 2, 3, 7, 8
- `mini4pro_5m`: 3–7
- `mini4pro_10m`: 1–5
- `mini4pro_noguard_free`: 7 only (the six-channel export omits it)
- both multi-aircraft takes: 1–5
- `matrice350`: 1, 5, 6, 7, 8

On `matrice350`, channel 2 is `mixed`: every window is signal, the span is 0.83 dB, and the loudest window is −60.89 dBFS. Channels 3 and 4 are `near_silent`. Their loudest windows are −83.08 dBFS and −86.88 dBFS. Channels 7 and 8 vary, and the six-channel export omits them. Channels 3 and 4 are still exported.

On the twelve May takes, middle windows of varying channels lie between −55.67 and −47.01 dBFS. Start windows of those channels lie between −67.83 and −60.39 dBFS. End windows span −62.38 to −34.16 dBFS, so level is not monotonic. On `matrice350`, middle windows of the varying channels lie between −39.18 and −38.11 dBFS. Do not interpret level changes as a flight profile. There is no trajectory log.

## Processing note

`METODOLOGIA_PROCESSAMENTO.pdf` is part of the collection. It is two pages. It says a 3 kHz high-pass was used only to find a metallic calibration strike, raw files were kept, six channels were extracted, absolute silence was used to flag dead channels, audio was cut into 1 s windows, and a Welch PSD plus RMS board compares the Behringer channel with the six exported channels. It does not say the stored WAV samples were filtered. It does not give room size, microphone coordinates, the Behringer model, the ReSpeaker model, filter order, FFT length, hop, or flight profile. The dead-channel check was not applied as a deletion: zero channels remain in the release.

There is one take per cell, no noise-only recording, and no repeated trial. Do not add a detector score to the Zenodo record.

## Paste-ready Zenodo fields

Upload type: `dataset`

Title:

```text
Indoor Multirotor Acoustic Dataset for Drone Detection and Classification (DataSet_Arena_Indoor_v0.2_Extended_Time)
```

Creators (placeholder; replace before submission):

```text
CONCEPTIO Laboratory, Instituto Tecnológico de Aeronáutica, São José dos Campos
```

Publication date: the date of the Zenodo upload. Do not backdate it.

Version: `0.2`

Language: `en` (archive paths are English; manufacturer JSON keys stay Portuguese)

License: leave unset until the authors confirm it. The intended license, pending that confirmation, is Creative Commons Attribution 4.0 International (CC BY 4.0). The deposit API fills an empty license with CC0. Replace that default before publishing.

Keywords:

```text
acoustic drone detection; drone classification; multirotor; microphone array; indoor; unmanned aircraft; Behringer; ReSpeaker
```

Description:

```html
<h2>Overview</h2>
<p>This dataset is for acoustic drone detection and classification. It provides indoor multirotor recordings so that a mono reference microphone and an eight-channel array can be compared on the same take. The collection is DataSet_Arena_Indoor_v0.2_Extended_Time, recorded at the CONCEPTIO Laboratory, Instituto Tecnológico de Aeronáutica, São José dos Campos. Thirteen takes cover DJI Flip, DJI Neo 2, DJI Mini 4 Pro, and DJI Matrice 350, including free flights and two multi-aircraft takes. Raw reference audio totals 3165.70 s. Each condition is one take. The record does not include a detector score or a trained model.</p>
<h2>Files</h2>
<p>Audio is one zip per aircraft or flight, a few hundred megabytes each. Download the zip for the aircraft you need. <code>catalog.csv</code> is the index of every take.</p>
<ul>
<li><strong>flip.zip</strong>, <strong>neo2.zip</strong>, <strong>mini4pro.zip</strong> — DJI Flip, DJI Neo 2, and DJI Mini 4 Pro at the sidecar distances 2 m, 5 m, and 10 m. Each distance is its own folder.</li>
<li><strong>mini4pro_noguard_free.zip</strong> — one Mini 4 Pro free flight with the propeller guard removed.</li>
<li><strong>multi_neo2_mini4pro_free.zip</strong> — one free flight with Neo 2 and Mini 4 Pro together.</li>
<li><strong>multi_flip_neo2_mini4pro_matrice_free.zip</strong> — one free flight with Flip, Neo 2, Mini 4 Pro, and Matrice together.</li>
<li><strong>matrice350.zip</strong> — one DJI Matrice 350 pass. The sidecar distance is the whole string "10m, 5m e 2m", one trajectory.</li>
<li><strong>catalog.csv</strong> — one row per take: folder inside the zip, durations, sidecar text, and the slice counts of the source share.</li>
<li><strong>channel_audit.csv</strong> — level of each array channel at the start, middle, and end of the raw array file.</li>
<li><strong>processing_methodology.pdf</strong> — the two-page processing note from the collection.</li>
<li><strong>dji_flip.json</strong>, <strong>dji_neo.json</strong>, <strong>dji_mini_4_pro.json</strong>, <strong>dji_matrice_350_rtk.json</strong>, <strong>dji_neo_and_mini_4_pro.json</strong>, <strong>dji_flip_neo_mini_4_pro_and_matrice_350.json</strong> — manufacturer sheets. The keys are the Portuguese field names from the source. These sheets are copied manufacturer data.</li>
</ul>
<h2>Recording</h2>
<p>Each take has a mono Behringer reference (44.1 kHz, IEEE float32) and an eight-channel ReSpeaker array (16 kHz, 16-bit PCM). Microphone model names are absent from the collection. The processing note calls the array a six-microphone circular array. Channels 7 and 8 stay in the eight-channel files. Distances are the strings in the sidecar: 2m, 5m, 10m, and LIVRE. LIVRE means free flight. The collection has no range log and no trajectory log.</p>
<h2>Inside a zip</h2>
<p>Every take folder holds the same five files. In flip.zip the 2 m take looks like this. The 5 m and 10 m folders, and the folders in the other zips, use the same five names.</p>
<pre>flip/2m/
├── raw_reference.wav           Behringer, mono, 44.1 kHz, float32
├── raw_array.wav               ReSpeaker, 8 channels, 16 kHz, 16-bit
├── synchronized_reference.wav
├── synchronized_array.wav
└── sidecar.json                aircraft, distance, timestamp, gains</pre>
<p>The WAV bytes are stored uncompressed. <code>archive_dir</code> in catalog.csv is that folder.</p>
<h2>Reading a take</h2>
<p><code>session_id</code> names the take. <code>raw_reference_s</code>, <code>raw_array_s</code>, <code>sync_reference_s</code>, and <code>sync_array_s</code> are container durations in seconds. <code>sync_duration_delta_s</code> is the synchronized reference duration minus the synchronized array duration. <code>reference_mid_rms_dbfs</code> is a 2.0 s window at the middle of the raw reference, in dBFS with full scale equal to 1.</p>
<p><code>channel_audit.csv</code> has one row per take, channel (1–8), and window (start, mid, end). <code>channel_class</code> is varying, flat, near_silent, digital_zero, idle, stuck_constant, or mixed. A channel is varying when all three windows are signal, the loudest window is above −80 dBFS, and the three windows span at least 3 dB.</p>
<h2>Limitations</h2>
<ul>
<li>The matrice350 sidecar still records the aircraft string DJI Flip. The archive name follows the folder and the file stem.</li>
<li>Neo sidecars say DJI Neo 2. The sheet dji_neo.json describes DJI Neo (about 135 g).</li>
<li>Flip sidecars say DJI FPV Flip. The sheet dji_flip.json names DJI Flip.</li>
<li>Four synchronized pairs differ by at least 1 s: flip/5m (+1.79 s), neo2/5m (−4.46 s), mini4pro/5m (+10.56 s), and mini4pro_noguard_free (+1.31 s). matrice350 differs by −0.13 s. The other eight are within 0.12 s.</li>
<li>mini4pro_noguard_free has no matched free flight with the guard on, so the missing guard is mixed with the flight pattern.</li>
<li>The two multi-aircraft takes have no time marks that assign a segment to one airframe.</li>
<li>There is one take per condition, no noise-only recording, and no repeated trial. Level changes along a file are not a flight profile.</li>
<li>The processing note used a 3 kHz high-pass only to find a metallic calibration strike. The note does not say the stored WAV samples were filtered, and it does not give room size, microphone coordinates, filter order, FFT length, or hop.</li>
</ul>
```
