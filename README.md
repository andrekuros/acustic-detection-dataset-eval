This is an independent acoustic-detection data record and is not part of a software platform.

# Indoor multirotor acoustic collection (CONCEPTIO / ITA)

`DataSet_Arena_Indoor_v0.2_Extended_Time` is an indoor acoustic collection of thirteen multirotor takes. This repository documents that collection. It does not contain the audio, and it does not contain a manuscript or a detection result.

Author line, used here as a placeholder: CONCEPTIO Laboratory, Instituto Tecnológico de Aeronáutica, São José dos Campos.

## Before the Zenodo upload

Do these three things before creating the Zenodo record.

1. Confirm the license. The text below marks CC BY 4.0 as the intended license, and it is pending confirmation. This repository does not include a `LICENSE` file, because that file would assert a license the authors have not confirmed.
2. Replace the author placeholder with the author list the laboratory wants. Do not invent personal names to fill it.
3. Decide the unresolved Matrice label. The folder, the file stem, and the sidecar disagree. The identifier `matrice350_trajectory_UNRESOLVED` records the conflict. It does not choose a side.

The set is 4,923,379,537 bytes (4.92 GB), under the Zenodo 50 GB limit.

## What to upload

Upload the dataset, not a paper.

From the share, upload the thirteen session trees plus the eight files that sit beside them: `METODOLOGIA_PROCESSAMENTO.pdf` and seven `especificacoes_oficiais_fabricante.json` sheets.

From this repository, put these files at the root of the same upload, next to the aircraft folders:

- `README.md`
- `catalog.csv`
- `channel_audit.csv`

`catalog.csv` is one measured row per session. `channel_audit.csv` is a file-level check of the raw array channels (312 windows). Both describe the recordings. They are not a detector evaluation.

Leave out any manuscript, bibliography, and score table.

## Where the audio is now

Public share, read-only:

https://cloud.conceptio.ita.br/index.php/s/3pmRmz7CokJpZr5

Folder name: `DataSet_Arena_Indoor_v0.2_Extended_Time`.

WebDAV endpoint: `https://cloud.conceptio.ita.br/public.php/webdav/` with username `3pmRmz7CokJpZr5` and an empty password. The share contains 14,904 files and 4,923,379,537 bytes. Do not commit that tree to git.

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

Measured totals: raw reference 2623.95 s; raw array 2609.66 s; synchronized reference 2445.73 s; synchronized array 2436.99 s; 2440 reference slices; 2430 array slices; 9740 fragment PNGs; 117 overview PNGs. Session trees hold 14,896 files and 4,923,219,458 bytes.

## Labels that stay as written

Sidecars on the Flip takes say `DJI FPV Flip`. The specification JSON names DJI Flip. The canonical aircraft name is DJI Flip. The sidecar string is kept in `catalog.csv`.

Sidecars say `DJI Neo 2`. The specification JSON in `DJI_NEO_2/` describes DJI Neo (about 135 g), not Neo 2. Do not publish those figures as Neo 2 specifications. Specification sheets are copied manufacturer data, not campaign measurements. The same Neo block is copied into the multi-aircraft sheets.

Distances are sidecar strings only (`2m`, `5m`, `10m`, `LIVRE`). There is no range log. `LIVRE` means free flight.

`mini4pro_noguard_free` is a free flight without a propeller guard. There is no matched free flight with the guard, so the guard is confounded with the flight pattern.

The two multi-aircraft takes have no time marks that assign a segment to one airframe.

`matrice350_trajectory_UNRESOLVED`: folder `DJI_MATRICE_350/10m, 5m e 2m` and file stem `DJI_MATRICE_10M_5M_2M`, but the sidecar says `"drone": "DJI Flip"`, `"distancia": "2m"`, timestamp `2026-04-30 15:34:23`. Do not choose between those labels. This take is shorter (80.63 s raw reference) and louder at mid-file (−21.87 dBFS). The manufacturer sheet next to that folder names a DJI Matrice 350 RTK and does not resolve the sidecar.

Canonical ids: `flip_{2,5,10}m`, `neo2_{2,5,10}m`, `mini4pro_{2,5,10}m`, `mini4pro_noguard_free`, `multi_neo2_mini4pro_free`, `multi_flip_neo2_mini4pro_matrice_free`, `matrice350_trajectory_UNRESOLVED`.

## Synchronization and slices

Four synchronized pairs differ by at least 1 s: `flip_5m` +1.79 s, `neo2_5m` −4.46 s, `mini4pro_5m` +10.56 s, `mini4pro_noguard_free` +1.31 s. The other nine are within 0.12 s. Slice indexes are not a shared time base on the four mismatched takes. `neo2_2m` differs by 0.03 s, but the floors still differ (179 reference slices and 180 array slices) because the containers fall on opposite sides of an integer second.

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
- unresolved Matrice folder: 1–5

On that unresolved take, channels 7 and 8 are `mixed`. The window at 1.0 s is idle on both. Their loudest windows are −74.00 dBFS (channel 7) and −75.84 dBFS (channel 8).

On the twelve May takes, middle windows of varying channels lie between −55.67 and −47.01 dBFS. Start windows of those channels lie between −67.83 and −60.39 dBFS. End windows span −62.38 to −34.16 dBFS, so level is not monotonic. On the unresolved take, middle windows of channels 1–5 lie between −38.54 and −37.58 dBFS. Do not interpret level changes as a flight profile. There is no trajectory log.

## Processing note

`METODOLOGIA_PROCESSAMENTO.pdf` is part of the collection. It is two pages. It says a 3 kHz high-pass was used only to find a metallic calibration strike, raw files were kept, six channels were extracted, absolute silence was used to flag dead channels, audio was cut into 1 s windows, and a Welch PSD plus RMS board compares the Behringer channel with the six exported channels. It does not say the stored WAV samples were filtered. It does not give room size, microphone coordinates, the Behringer model, the ReSpeaker model, filter order, FFT length, hop, or flight profile. The dead-channel check was not applied as a deletion: zero channels remain in the release.

There is one take per cell, no noise-only recording, and no repeated trial. Do not add a detector score to the Zenodo record.

## Paste-ready Zenodo fields

Upload type: `dataset`

Title:

```text
Indoor acoustic recordings of multirotor aircraft with a reference microphone and an eight-channel array (DataSet_Arena_Indoor_v0.2_Extended_Time)
```

Creators (placeholder; replace before submission):

```text
CONCEPTIO Laboratory, Instituto Tecnológico de Aeronáutica, São José dos Campos
```

Publication date: the date of the Zenodo upload. Do not backdate it.

Version: `0.2`

Language: `en` (several folder names are Portuguese)

License: leave unset until the authors confirm it. The intended license, pending that confirmation, is Creative Commons Attribution 4.0 International (CC BY 4.0).

Keywords:

```text
acoustic recording; multirotor; microphone array; indoor; unmanned aircraft; Behringer; ReSpeaker
```

Description:

```text
This is an independent acoustic-detection data record and is not part of a software platform. Thirteen indoor multirotor takes were recorded at the CONCEPTIO laboratory of the Instituto Tecnológico de Aeronáutica, São José dos Campos. Each take has a mono Behringer reference channel at 44.1 kHz, IEEE float32, and an eight-channel ReSpeaker array at 16 kHz, 16-bit PCM. Neither microphone model is named in the release. A two-page processing note describes a 3 kHz high-pass used only to find a metallic calibration strike, a six-channel mono export, one-second slices, and a Welch power-spectral-density and RMS board. Raw files were kept, and digitally zero channels were not deleted. Container lengths total 2623.95 s of raw reference audio, 2609.66 s of raw array audio, 2445.73 s of synchronized reference audio, and 2436.99 s of synchronized array audio, with 2440 reference slices and 2430 array slices. Four synchronized pairs differ by at least one second. The take matrice350_trajectory_UNRESOLVED still has conflicting folder, file-stem, and sidecar labels. The collection has one take per cell, no noise-only recording, and no repeated trial. This upload is the recordings and the file notes, not a detection evaluation. The intended license is CC BY 4.0, pending confirmation, and the author line is a placeholder.
```
