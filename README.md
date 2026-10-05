This is an independent acoustic-detection data record and is not part of a software platform.

# Indoor multirotor acoustic collection (CONCEPTIO / ITA)

`DataSet_Arena_Indoor_v0.2_Extended_Time` is an indoor acoustic collection of thirteen multirotor takes. This repository documents that collection. It does not contain the audio, and it does not contain a manuscript or a detection result.

Author line, used here as a placeholder: CONCEPTIO Laboratory, Instituto Tecnológico de Aeronáutica, São José dos Campos.

## Before publishing the Zenodo record

`scripts/build_and_upload_zenodo.py` can create an unpublished draft. Do these three things before publishing it.

1. Confirm the license. The text below marks CC BY 4.0 as the intended license, and it is pending confirmation. This repository does not include a `LICENSE` file, because that file would assert a license the authors have not confirmed. Zenodo fills an empty license with CC0. That default is not a confirmed choice. Change the license field before publishing.
2. Replace the author placeholder with the author list the laboratory wants. Do not invent personal names to fill it.
3. Decide the unresolved Matrice label. The folder, the file stem, and the sidecar disagree. The identifier `matrice350_trajectory_UNRESOLVED` records the conflict. It does not choose a side.

The source share is 6,004,947,774 bytes (6.00 GB). The filtered package below is 2,654,584,283 bytes of audio, the processing note, and the manufacturer sheets, plus this README, `catalog.csv`, and `channel_audit.csv`. That is under the Zenodo 50 GB limit.

## What is in the Zenodo package

The source share uses Portuguese folder names and keeps several derived copies of the same audio. The deposit uses English names and keeps one copy of each recording.

Included, for every take:

| Archive file | Source |
| --- | --- |
| `sessions/<id>/raw_reference.wav` | `Brutos/<stem>.wav` |
| `sessions/<id>/raw_array.wav` | `Brutos/respe_<stem>.wav` |
| `sessions/<id>/synchronized_reference.wav` | `Sincronizados/<stem>.wav` |
| `sessions/<id>/synchronized_array.wav` | `Sincronizados/respe_<stem>.wav` |
| `sessions/<id>/sidecar.json` | the raw sidecar; the other two copies are identical |

`<id>` is the canonical session id. `catalog.csv` column `archive_dir` is `sessions/<id>`. `relative_path` remains the original share path. On the unresolved take, the raw array and its sidecar in `Brutos` are named `Respe_` with a capital R. The synchronized copies of those two files use `respe_`.

Also included: `processing_methodology.pdf` (the source file `METODOLOGIA_PROCESSAMENTO.pdf`) and the manufacturer JSON sheets, renamed under `specifications/`. The Mini 4 Pro sheet in the no-guard folder is byte-identical to `specifications/dji_mini_4_pro.json`, so it is not repeated. The JSON keys inside those sheets are still the Portuguese field names from the source. They are copied manufacturer data, not campaign measurements.

Left out:

- One-second slice WAVs. On the takes that were checked, each slice is an exact cut of the synchronized file, and the slice count is the floor of that duration.
- The six mono channel files. They are a split of channels 1–6 of `synchronized_array.wav`. Channels 7 and 8 remain in that eight-channel file.
- Spectrogram PNGs. They are pictures rendered from the synchronized audio. The processing note does not give the FFT length, hop, or colormap, so the archive keeps the audio rather than the pictures.

`catalog.csv` still records the slice and PNG counts of the source share. `channel_audit.csv` is a check of the raw array files. Neither file is a detector evaluation.

Zenodo does not store folders. Each session is therefore its own zip, `<id>.zip`, and that zip opens directly. Inside, the directory `<id>/` holds the five files above. `catalog.csv` column `archive_dir` is that directory. The processing note, the manufacturer JSON files, this README, the catalog, and the channel audit are separate files on the record.

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

`matrice350_trajectory_UNRESOLVED`: folder `DJI_MATRICE_350/10m, 5m e 2m` and file stem `DJI_MATRICE_10M_5M_2M`. The sidecar says `"drone": "DJI Flip"`, `"distancia": "10m, 5m e 2m"`, timestamp `2026-09-16 13:05:40`. The distance string matches the folder name and is not a single measured range. Do not choose the aircraft. The share copies of this take were replaced on 5 October 2026, and the durations below measure those copies. The raw reference is 622.38 s, and the mid-file level is −32.68 dBFS. The manufacturer sheet next to that folder names a DJI Matrice 350 RTK and does not resolve the sidecar.

Canonical ids: `flip_{2,5,10}m`, `neo2_{2,5,10}m`, `mini4pro_{2,5,10}m`, `mini4pro_noguard_free`, `multi_neo2_mini4pro_free`, `multi_flip_neo2_mini4pro_matrice_free`, `matrice350_trajectory_UNRESOLVED`.

## Synchronization and slices

Four synchronized pairs differ by at least 1 s: `flip_5m` +1.79 s, `neo2_5m` −4.46 s, `mini4pro_5m` +10.56 s, `mini4pro_noguard_free` +1.31 s. `matrice350_trajectory_UNRESOLVED` differs by −0.13 s. The other eight are within 0.12 s. Slice indexes are not a shared time base on the four mismatched takes. `neo2_2m` differs by 0.03 s, but the floors still differ (179 reference slices and 180 array slices) because the containers fall on opposite sides of an integer second. The unresolved take does the same (608 reference slices and 609 array slices).

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
- unresolved Matrice folder: 1, 5, 6, 7, 8

On that unresolved take, channel 2 is `mixed`: every window is signal, the span is 0.83 dB, and the loudest window is −60.89 dBFS. Channels 3 and 4 are `near_silent`. Their loudest windows are −83.08 dBFS and −86.88 dBFS. Channels 7 and 8 vary, and the six-channel export omits them. Channels 3 and 4 are still exported.

On the twelve May takes, middle windows of varying channels lie between −55.67 and −47.01 dBFS. Start windows of those channels lie between −67.83 and −60.39 dBFS. End windows span −62.38 to −34.16 dBFS, so level is not monotonic. On the unresolved take, middle windows of the varying channels lie between −39.18 and −38.11 dBFS. Do not interpret level changes as a flight profile. There is no trajectory log.

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

Language: `en` (archive paths are English; manufacturer JSON keys stay Portuguese)

License: leave unset until the authors confirm it. The intended license, pending that confirmation, is Creative Commons Attribution 4.0 International (CC BY 4.0). The deposit API fills an empty license with CC0. Replace that default before publishing.

Keywords:

```text
acoustic recording; multirotor; microphone array; indoor; unmanned aircraft; Behringer; ReSpeaker
```

Description:

```html
<p>Indoor acoustic recordings of multirotor aircraft collected at the CONCEPTIO laboratory, Instituto Tecnológico de Aeronáutica, São José dos Campos (DataSet_Arena_Indoor_v0.2_Extended_Time).</p>
<p>Thirteen takes were recorded with a mono Behringer reference channel (44.1 kHz, IEEE float32) and an eight-channel ReSpeaker array (16 kHz, 16-bit PCM). Microphone models are not named. The array is described as a six-microphone circular array; channels 7 and 8 remain in the eight-channel files. Raw reference audio totals 3165.70 s. Each condition is a single take.</p>
<p>The conditions are DJI Flip, DJI Neo 2, and DJI Mini 4 Pro at labeled distances of 2 m, 5 m, and 10 m; one Mini 4 Pro free flight without a propeller guard; one free flight of Neo 2 and Mini 4 Pro; and one free flight of Flip, Neo 2, Mini 4 Pro, and a Matrice. Distances are sidecar labels. No range or trajectory log is included.</p>
<p>Each session is a separate zip named with its session id, such as flip_2m.zip. The zip contains that directory with raw_reference.wav, raw_array.wav, synchronized_reference.wav, synchronized_array.wav, and sidecar.json. catalog.csv lists the sessions and durations. processing_methodology.pdf is the processing note, and the specification JSON files are copied manufacturer sheets.</p>
<p>In matrice350_trajectory_UNRESOLVED the directory names a Matrice trajectory and the sidecar names DJI Flip. Neo sidecars say DJI Neo 2; the manufacturer sheet describes DJI Neo. Four synchronized pairs differ by at least 1 s: flip_5m, neo2_5m, mini4pro_5m, and mini4pro_noguard_free.</p>
```
