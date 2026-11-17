"""Paper figures from the results/ tables (and the audio for the spectrograms)."""
import csv, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.signal import spectrogram
from analysis.common import TAKES, load

R = Path("results"); F = Path("paper/figures"); F.mkdir(parents=True, exist_ok=True)
COL = {"DJI Flip": "#2a78d6", "DJI Neo 2": "#eb6834", "DJI Mini 4 Pro": "#1baf7a", "DJI Matrice 350": "#c98500"}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3de"
plt.rcParams.update({"font.size": 8, "font.family": "serif", "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False,
                     "lines.linewidth": 1.2, "legend.frameon": False})
W1 = 3.5  # IEEE single column, inches

def read(name): return list(csv.DictReader(open(R/name)))

# 1. spectrogram excerpts
ex = [("flip_2m", "DJI Flip, 2 m"), ("neo2_2m", "DJI Neo 2, 2 m"), ("mini4pro_2m", "DJI Mini 4 Pro, 2 m"), ("matrice350", "DJI Matrice 350")]
fig, axs = plt.subplots(4, 1, figsize=(W1, 4.6), sharex=True)
for ax, (t, lab) in zip(axs, ex):
    fs, x = load(t, "synchronized_reference"); seg = x[60*fs:120*fs]
    f, tt, S = spectrogram(seg, fs, nperseg=4096, noverlap=3072)
    m = f <= 3000; Sd = 10*np.log10(S[m]+1e-20); top = np.percentile(Sd, 99.5)
    ax.pcolormesh(tt, f[m]/1e3, Sd, shading="auto", cmap="Greys", vmin=top-50, vmax=top, rasterized=True)
    ax.grid(False); ax.set_ylabel("kHz"); ax.text(0.01, 0.92, lab, transform=ax.transAxes, va="top",
            fontsize=7, color=INK, bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
axs[-1].set_xlabel("time from 60 s into the synchronized reference (s)")
fig.tight_layout(h_pad=0.3); fig.savefig(F/"fig_spectrograms.pdf", dpi=300); plt.close(fig)

# 2. long-term spectra
L = np.load(R/"ltas.npz"); f = L["f"]; m = (f >= 50) & (f <= 4000)
fig, ax = plt.subplots(figsize=(W1, 2.2))
for t, lab in (("flip_2m", "DJI Flip"), ("neo2_2m", "DJI Neo 2"), ("mini4pro_2m", "DJI Mini 4 Pro"), ("matrice350", "DJI Matrice 350")):
    ax.plot(f[m], 10*np.log10(L[t][m]), color=COL[lab], label=lab, lw=1.0)
ax.set_xscale("log"); ax.set_xlim(50, 4000); ax.set_xticks([50, 100, 200, 500, 1000, 2000, 4000])
ax.set_xticklabels(["50", "100", "200", "500", "1k", "2k", "4k"])
ax.set_xlabel("frequency (Hz)"); ax.set_ylabel("PSD (dB re FS$^2$/Hz)")
ax.legend(fontsize=6.5, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0), handlelength=1.2, columnspacing=0.8)
fig.tight_layout(); fig.savefig(F/"fig_ltas.pdf"); plt.close(fig)

# 3. level vs distance
lev = read("levels.csv"); d = {"2m": 2, "5m": 5, "10m": 10}
fig, axs = plt.subplots(1, 2, figsize=(W1, 1.9), sharey=False)
for ax, key, title in ((axs[0], "ref_median_dbfs", "reference"), (axs[1], "array_median_dbfs", "array")):
    for ac in ("DJI Flip", "DJI Neo 2", "DJI Mini 4 Pro"):
        rr = [r for r in lev if r["aircraft"] == ac and r["distance"] in d]
        xs = [d[r["distance"]] for r in rr]; ys = [float(r[key]) for r in rr]
        ax.plot(xs, ys, "o-", color=COL[ac], ms=3.5, label=ac.replace("DJI ", ""))
    y0 = np.mean([float(r[key]) for r in lev if r["distance"] == "2m"])
    xx = np.array([2, 10]); ax.plot(xx, y0-20*np.log10(xx/2), ls=":", color=MUTED, lw=1)
    ax.set_xscale("log"); ax.minorticks_off(); ax.set_xticks([2, 5, 10]); ax.set_xticklabels(["2", "5", "10"])
    ax.set_xlabel("sidecar distance (m)"); ax.set_title(title, fontsize=8, color=INK)
axs[0].set_ylabel("median 1-s level (dBFS)"); axs[0].legend(fontsize=6.5, loc="lower left")
axs[1].text(4.2, -59.5, "free-field\n$-20\\log_{10}r$", fontsize=6, color=MUTED)
fig.tight_layout(); fig.savefig(F/"fig_level_distance.pdf"); plt.close(fig)

# 4. array channel layout
lay = read("array_layout.csv")
code = {"A": 2, "C": 1, "D": 0}
M = np.array([[code[c] for c in r["pattern"]] for r in lay])
fig, ax = plt.subplots(figsize=(W1, 2.6))
ax.imshow(M, cmap=ListedColormap(["#f1f0ec", "#9a998f", "#1c5cab"]), aspect="auto", vmin=0, vmax=2)
ax.set_xticks(range(8)); ax.set_xticklabels(range(1, 9)); ax.set_xlabel("channel index in the WAV file")
ax.set_yticks(range(len(lay))); ax.set_yticklabels([r["session_id"].replace("multi_flip_neo2_mini4pro_matrice_free", "multi_4_aircraft_free") for r in lay], fontsize=6)
ax.grid(False); ax.set_xticks(np.arange(-.5, 8, 1), minor=True); ax.set_yticks(np.arange(-.5, len(lay), 1), minor=True)
ax.grid(which="minor", color="white", lw=1.5); ax.tick_params(which="minor", length=0)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(fc="#1c5cab", label="acoustic"), Patch(fc="#9a998f", label="constant"), Patch(fc="#f1f0ec", ec=MUTED, lw=.4, label="dead")],
          loc="upper center", bbox_to_anchor=(0.35, 1.14), ncol=3, fontsize=6, handlelength=1)
fig.tight_layout(); fig.savefig(F/"fig_array_layout.pdf"); plt.close(fig)

# 5. sync residual vs time
win = read("sync_windows.csv"); summ = {r["session_id"]: r for r in read("sync_summary.csv")}
fig, ax = plt.subplots(figsize=(W1, 2.1))
for t in TAKES:
    rr = [r for r in win if r["session_id"] == t and r["valid"] == "True"]
    tt = np.array([float(r["t_ref_s"]) for r in rr]); lg = np.array([float(r["lag_s"]) for r in rr])
    med = float(summ[t]["median_lag_ms"])/1e3; k = np.abs(lg-med) < 0.5
    off = abs(med) > 0.2
    ax.plot(tt[k], 1e3*(lg[k]), ".", ms=2.5, color=("#eb6834" if off else "#2a78d6"), alpha=.7)
ax.set_yscale("symlog", linthresh=100); ax.set_yticks([-3000, -1000, -100, 0, 100, 1000, 3000])
ax.set_yticklabels(["-3 s", "-1 s", "-100", "0", "100", "1 s", "3 s"])
ax.set_xlabel("time in synchronized reference (s)"); ax.set_ylabel("measured array lag (ms)")
ax.text(300, 300, "offset takes", color="#eb6834", fontsize=7); ax.text(230, -60, "aligned takes", color="#2a78d6", fontsize=7)
fig.tight_layout(); fig.savefig(F/"fig_sync.pdf"); plt.close(fig)
print("figures written")
