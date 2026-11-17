"""Re-measure the alignment of synchronized_reference vs synchronized_array.

For each take, the reference is resampled to 16 kHz, both signals are
band-passed 200-4000 Hz, and the normalized cross-correlation is computed between a 4-s reference
window and a 34-s array window centred on the same nominal time, every 10 s.
Lag > 0 means the array lags the reference (the event appears later in the
array file). A window counts as valid when the |rho| peak exceeds 8 times the
median |rho| over the search range. Writes results/sync_windows.csv and
results/sync_summary.csv.
"""
import csv, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")
import numpy as np
from scipy.signal import resample_poly, butter, sosfiltfilt, correlate
from scipy.stats import theilslopes
from analysis.common import TAKES, load

OUT = Path("results"); OUT.mkdir(exist_ok=True)
FS = 16000; WIN = 4.0; SEARCH = 15.0; STEP = 10.0
sos = butter(4, [200, 4000], btype="band", fs=FS, output="sos")
layout = {r["session_id"]: [int(c) for c in r["acoustic_channels"].split()]
          for r in csv.DictReader(open(OUT/"array_layout.csv"))}

def xcorr_lag(x, y):
    """Normalized cross-correlation of x against every same-length slice of y.
    Returns (index of the |rho| peak, |rho| at peak, peak / median |rho|)."""
    c = correlate(y, x, mode="valid", method="fft")
    e = np.sqrt(correlate(y**2, np.ones(len(x)), mode="valid", method="fft"))*np.linalg.norm(x)
    c = np.abs(c/(e+1e-20))
    k = int(np.argmax(c))
    return k, c[k], c[k]/(np.median(c)+1e-12)

win_rows, summ = [], []
for t in TAKES:
    fr, r = load(t, "synchronized_reference"); fa, a = load(t, "synchronized_array")
    r16 = sosfiltfilt(sos, resample_poly(r, 160, 441))
    ch = layout[t][0]-1
    y = sosfiltfilt(sos, a[:, ch])
    w, s = int(WIN*FS), int(SEARCH*FS)
    lags, times = [], []
    for t0 in np.arange(SEARCH+1, len(r16)/FS - WIN - SEARCH - 1, STEP):
        i = int(t0*FS)
        x = r16[i:i+w]; yy = y[i-s:i+w+s]
        if len(yy) < w+2*s or np.max(np.abs(x)) <= 2/32768: continue
        k, rho, pk = xcorr_lag(x, yy)
        lag = (k - s)/FS
        valid = pk > 8
        win_rows.append(dict(session_id=t, t_ref_s=round(t0, 1), lag_s=round(lag, 4), rho=round(rho, 3), peak_ratio=round(pk, 1), valid=valid))
        if valid: lags.append(lag); times.append(t0)
    lags = np.array(lags); times = np.array(times)
    # robust fit: drop windows more than 0.5 s from the median (harmonic or
    # dropout-induced false peaks), then Theil-Sen slope = relative clock drift
    med0 = np.median(lags); keep = np.abs(lags - med0) < 0.5
    L, T = lags[keep], times[keep]
    slope, icpt, _, _ = theilslopes(L, T)
    resid = L - (icpt + slope*T)
    n_all = sum(1 for q in win_rows if q["session_id"] == t)
    summ.append(dict(session_id=t, array_channel=ch+1, windows=n_all, used=int(keep.sum()),
                     median_lag_ms=round(1e3*np.median(L), 1),
                     lag_at_start_ms=round(1e3*(icpt+slope*T[0]), 1),
                     lag_at_end_ms=round(1e3*(icpt+slope*T[-1]), 1),
                     drift_ppm=round(1e6*slope, 0),
                     residual_mad_ms=round(1e3*np.median(np.abs(resid)), 1)))
    print(summ[-1])
for name, rows in (("sync_windows.csv", win_rows), ("sync_summary.csv", summ)):
    with open(OUT/name, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
