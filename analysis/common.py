"""Shared helpers for the CiO-Drone-Acoustic technical-validation scripts.

DATA is the folder where the seven Zenodo zips were unpacked
(set CIO_DATA, default ./data/ex). Nothing here modifies the audio.
"""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np
from scipy.io import wavfile

DATA = Path(os.environ.get("CIO_DATA", "data/ex"))
TAKES = {
    "flip_2m": "flip/2m", "flip_5m": "flip/5m", "flip_10m": "flip/10m",
    "neo2_2m": "neo2/2m", "neo2_5m": "neo2/5m", "neo2_10m": "neo2/10m",
    "mini4pro_2m": "mini4pro/2m", "mini4pro_5m": "mini4pro/5m", "mini4pro_10m": "mini4pro/10m",
    "mini4pro_noguard_free": "mini4pro_noguard_free",
    "multi_neo2_mini4pro_free": "multi_neo2_mini4pro_free",
    "multi_flip_neo2_mini4pro_matrice_free": "multi_flip_neo2_mini4pro_matrice_free",
    "matrice350": "matrice350",
}
SINGLE = ["flip_2m","flip_5m","flip_10m","neo2_2m","neo2_5m","neo2_10m",
          "mini4pro_2m","mini4pro_5m","mini4pro_10m"]

def load(take: str, kind: str):
    """kind in raw_reference, raw_array, synchronized_reference, synchronized_array.
    Returns (fs, float64 array scaled to full scale 1, shape (n,) or (n,ch))."""
    fs, x = wavfile.read(DATA / TAKES[take] / f"{kind}.wav", mmap=True)
    if x.dtype == np.int16:
        x = x.astype(np.float64) / 32768.0
    else:
        x = np.asarray(x, dtype=np.float64)
    return fs, x

def sidecar(take: str) -> dict:
    return json.loads((DATA / TAKES[take] / "sidecar.json").read_text())

def db(x, floor=1e-12):
    return 10*np.log10(np.maximum(x, floor))
