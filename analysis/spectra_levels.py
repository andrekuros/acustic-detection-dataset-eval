"""Long-term spectra, dominant tonal frequency, and level versus sidecar distance.

Writes results/levels.csv, results/ltas.npz.
"""
import csv, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")
import numpy as np
from scipy.signal import welch
from analysis.common import TAKES, load, sidecar

OUT = Path("results"); EDGE = 5
layout = {r["session_id"]: [int(c) for c in r["acoustic_channels"].split()]
          for r in csv.DictReader(open(OUT/"array_layout.csv"))}
rows, ltas = [], {}
for t in TAKES:
    fr, r = load(t, "synchronized_reference"); fa, a = load(t, "synchronized_array")
    n = len(r)//fr
    sec = [r[k*fr:(k+1)*fr] for k in range(EDGE, n-EDGE)]
    sec = [s for s in sec if np.max(np.abs(s)) > 2/32768]
    lr = np.array([10*np.log10(np.mean(s**2)) for s in sec])
    chs = [c-1 for c in layout[t]]
    na = len(a)//fa
    la = np.array([10*np.log10(np.mean(a[k*fa:(k+1)*fa, chs]**2)) for k in range(EDGE, na-EDGE)])
    # dominant tonal component 150-1500 Hz per 1-s reference second
    dom = []
    for s in sec:
        f, P = welch(s, fr, nperseg=8192)
        m = (f >= 150) & (f <= 1500); dom.append(f[m][np.argmax(P[m])])
    dom = np.array(dom)
    f, P = welch(np.concatenate(sec), fr, nperseg=8192); ltas[t] = P
    rows.append(dict(session_id=t, aircraft=sidecar(t)["aircraft"], distance=sidecar(t)["distance"],
                     ref_median_dbfs=round(np.median(lr), 2), ref_p10_dbfs=round(np.percentile(lr, 10), 2),
                     ref_p90_dbfs=round(np.percentile(lr, 90), 2),
                     array_median_dbfs=round(np.median(la), 2),
                     dominant_hz_median=round(np.median(dom), 0),
                     dominant_hz_p25=round(np.percentile(dom, 25), 0), dominant_hz_p75=round(np.percentile(dom, 75), 0)))
    print(rows[-1])
np.savez_compressed(OUT/"ltas.npz", f=f, **ltas)
with open(OUT/"levels.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
