"""Reference-channel dropouts, clipping, and the array channel layout.

Writes results/integrity.csv and results/array_layout.csv.
"""
import csv, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")
import numpy as np
from analysis.common import TAKES, load

OUT = Path("results"); OUT.mkdir(exist_ok=True)
LSB = 1/32768        # the float32 reference holds 16-bit values (multiples of 2^-15)
FRAME_S = 0.1        # a dropout frame is 100 ms with |x| <= 2 LSB

def dropouts(x, fs):
    h = int(FRAME_S*fs); n = len(x)//h
    quiet = np.max(np.abs(x[:n*h].reshape(n, h)), axis=1) <= 2*LSB
    z = np.concatenate([[0], quiet.astype(np.int8), [0]])
    d = np.diff(z); s = np.where(d == 1)[0]; e = np.where(d == -1)[0]
    return s*FRAME_S, (e - s)*FRAME_S

rows = []
for t in TAKES:
    for kind in ("raw_reference", "synchronized_reference"):
        fs, x = load(t, kind)
        st, L = dropouts(x, fs)
        on_grid = bool(np.all(np.mod(x[::97]*32768, 1) == 0))
        rows.append(dict(session_id=t, file=kind, duration_s=round(len(x)/fs, 3),
                         int16_grid=on_grid, dropouts=len(L), dropout_total_s=round(L.sum(), 1),
                         longest_dropout_s=round(L.max(), 1) if len(L) else 0,
                         dropout_starts_s=" ".join(f"{v:.1f}" for v in st),
                         clipped_samples=int(np.sum(np.abs(x) >= 0.999)),
                         peak_dbfs=round(20*np.log10(np.max(np.abs(x))), 2)))
    fs, a = load(t, "raw_array")
    rows.append(dict(session_id=t, file="raw_array", duration_s=round(len(a)/fs, 3),
                     int16_grid=True, dropouts="", dropout_total_s="", longest_dropout_s="",
                     dropout_starts_s="", clipped_samples=int(np.sum(np.abs(a) >= 32767/32768)),
                     peak_dbfs=round(20*np.log10(np.max(np.abs(a))), 2)))
with open(OUT/"integrity.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# Array layout. The ReSpeaker 6-mic kit delivers 8 slots: 6 microphones and
# 2 playback-echo channels, and the driver is known to rotate slot order
# between recordings. Each channel is classified on 1-s RMS levels of the
# synchronized file: "dead" if the median level is <= -70 dBFS, "constant" if
# the 1-s levels vary by less than 0.8 dB (std), otherwise "acoustic".
# For acoustic channels we also report the correlation of the 1-s level
# series with the reference, using only seconds with no reference dropout.
lay = []
for t in TAKES:
    fs, a = load(t, "synchronized_array"); fr, r = load(t, "synchronized_reference")
    n = min(len(a)//fs, len(r)//fr) - 2
    ks = range(1, n)
    ref = np.array([10*np.log10(np.mean(r[k*fr:(k+1)*fr]**2)+1e-20) for k in ks])
    ok = np.array([np.sum(r[k*fr:(k+1)*fr] == 0) < 0.005*fr for k in ks])
    cls, rs = [], []
    for c in range(8):
        lv = np.array([10*np.log10(np.mean(a[k*fs:(k+1)*fs, c]**2)+1e-20) for k in ks])
        med = np.median(lv)
        if med <= -70: k_ = "dead"
        elif np.std(lv) < 0.8: k_ = "constant"
        else:
            k_ = "acoustic"; rs.append(np.corrcoef(lv[ok], ref[ok])[0, 1])
        cls.append(k_)
    acoustic = [c+1 for c in range(8) if cls[c] == "acoustic"]
    sig = "".join({"acoustic": "A", "constant": "C", "dead": "D"}[k] for k in cls)
    rot = next((s for s in range(8) if (sig[s:]+sig[:s]) == "AAAAACDD"), "")
    lay.append(dict(session_id=t, pattern=sig, acoustic_channels=" ".join(map(str, acoustic)),
                    n_acoustic=len(acoustic), rotation_to_canonical=rot,
                    median_r_with_reference=round(float(np.median(rs)), 3) if rs else ""))
    print(lay[-1])
with open(OUT/"array_layout.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(lay[0])); w.writeheader(); w.writerows(lay)
