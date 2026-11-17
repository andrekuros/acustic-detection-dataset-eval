"""1-s log-mel segment features for the baseline (shared by both sensors).

Both sensors are brought to 16 kHz (the reference is resampled 44.1->16 kHz),
so a model can be trained on one sensor and tested on the other.
Writes results/features.npz.
"""
import csv, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")
import numpy as np
from scipy.signal import resample_poly, stft
from analysis.common import TAKES, SINGLE, load, sidecar

FS = 16000; NFFT = 1024; HOP = 512; NMEL = 64; FMIN, FMAX = 50.0, 8000.0
EDGE_S = 5            # drop the first and last 5 s (handling, take-off, landing)
OUT = Path("results")

def mel_fb():
    hz2m = lambda f: 2595*np.log10(1+f/700); m2hz = lambda m: 700*(10**(m/2595)-1)
    pts = m2hz(np.linspace(hz2m(FMIN), hz2m(FMAX), NMEL+2))
    f = np.fft.rfftfreq(NFFT, 1/FS); W = np.zeros((NMEL, len(f)))
    for i in range(NMEL):
        lo, c, hi = pts[i:i+3]
        W[i] = np.clip(np.minimum((f-lo)/(c-lo), (hi-f)/(hi-c)), 0, None)
    return W
W = mel_fb()

def seg_features(x):
    _, _, Z = stft(x, FS, nperseg=NFFT, noverlap=NFFT-HOP, boundary=None, padded=False)
    M = np.log10(W @ (np.abs(Z)**2) + 1e-12)          # (NMEL, frames)
    level = M.mean()
    M = M - level                                     # per-segment level normalisation
    return np.concatenate([M.mean(1), M.std(1)]), level

layout = {r["session_id"]: [int(c) for c in r["acoustic_channels"].split()]
          for r in csv.DictReader(open(OUT/"array_layout.csv"))}
X, y, take, dist, sensor, tsec, lev = [], [], [], [], [], [], []
for t in TAKES:
    fr, r = load(t, "synchronized_reference"); r16 = resample_poly(r, 160, 441)
    fa, a = load(t, "synchronized_array"); arr = a[:, layout[t][0]-1]
    sc = sidecar(t)
    for name, sig in (("reference", r16), ("array", arr)):
        n = len(sig)//FS
        for k in range(EDGE_S, n-EDGE_S):
            s = sig[k*FS:(k+1)*FS]
            if np.max(np.abs(s)) <= 2/32768:   # reference dropout second
                continue
            f, L = seg_features(s)
            X.append(f); lev.append(L); y.append(sc["aircraft"]); take.append(t)
            dist.append(sc["distance"]); sensor.append(name); tsec.append(k)
np.savez_compressed(OUT/"features.npz", X=np.array(X), y=np.array(y), take=np.array(take),
                    dist=np.array(dist), sensor=np.array(sensor), t=np.array(tsec), level=np.array(lev))
print(len(X), "segments")
