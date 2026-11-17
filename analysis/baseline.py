"""Reference baseline for 3-class aircraft identification (Flip / Neo 2 / Mini 4 Pro).

Uses only the nine fixed-distance takes. Three protocols:
  random  - 5-fold split over 1-s segments, ignoring take identity (leaky:
            neighbouring seconds of one take land in train and test);
  LODO    - leave-one-distance-out: train on two sidecar distances, test on
            the third; every test take is unseen;
  cross   - LODO, but train on one sensor and test on the other.
Metric: balanced accuracy and macro-F1 over test segments.
Writes results/baseline.csv and results/baseline_confusion.csv.
"""
import csv, sys
from pathlib import Path
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score, f1_score, confusion_matrix

OUT = Path("results")
D = np.load(OUT/"features.npz")
CLASSES = ["DJI Flip", "DJI Neo 2", "DJI Mini 4 Pro"]
keep = np.isin(D["y"], CLASSES) & np.isin(D["dist"], ["2m", "5m", "10m"])
X, y, dist, sensor = D["X"][keep], D["y"][keep], D["dist"][keep], D["sensor"][keep]

MODELS = {
    "logreg": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)),
    "rf": lambda: RandomForestClassifier(n_estimators=300, min_samples_leaf=2, n_jobs=-1, random_state=0),
}
rows, conf = [], []

def score(tag, model, tr_sensor, te_sensor, yt, yp, folds):
    rows.append(dict(protocol=tag, model=model, train_sensor=tr_sensor, test_sensor=te_sensor,
                     folds=folds, n_test=len(yt),
                     balanced_accuracy=round(balanced_accuracy_score(yt, yp), 3),
                     macro_f1=round(f1_score(yt, yp, average="macro"), 3)))
    print(rows[-1])

for m, mk in MODELS.items():
    for s in ("reference", "array"):
        idx = np.where(sensor == s)[0]
        # random segment split
        yt, yp = [], []
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(X[idx], y[idx]):
            clf = mk().fit(X[idx][tr], y[idx][tr]); yt += list(y[idx][te]); yp += list(clf.predict(X[idx][te]))
        score("random", m, s, s, yt, yp, 5)
    for s_tr in ("reference", "array"):
        for s_te in ("reference", "array"):
            yt, yp = [], []
            for d in ("2m", "5m", "10m"):
                tr = (sensor == s_tr) & (dist != d); te = (sensor == s_te) & (dist == d)
                clf = mk().fit(X[tr], y[tr]); p = clf.predict(X[te]); yt += list(y[te]); yp += list(p)
            tag = "LODO" if s_tr == s_te else "LODO-cross-sensor"
            score(tag, m, s_tr, s_te, yt, yp, 3)
            if m == "logreg":
                C = confusion_matrix(yt, yp, labels=CLASSES)
                for i, a in enumerate(CLASSES):
                    for j, b in enumerate(CLASSES):
                        conf.append(dict(protocol=tag, train_sensor=s_tr, test_sensor=s_te, true=a, pred=b, count=int(C[i, j])))
for name, R in (("baseline.csv", rows), ("baseline_confusion.csv", conf)):
    with open(OUT/name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(R[0])); w.writeheader(); w.writerows(R)

# Out-of-condition check: models trained on all nine fixed-distance takes,
# applied to the free-flight takes. No time labels exist for the multi-aircraft
# takes, so only the share of predicted classes is reported.
ood = []
for s in ("reference", "array"):
    tr = (sensor == s)
    clf = MODELS["logreg"]().fit(X[tr], y[tr])
    for t in ("mini4pro_noguard_free", "multi_neo2_mini4pro_free", "multi_flip_neo2_mini4pro_matrice_free"):
        te = (D["take"] == t) & (D["sensor"] == s)
        p = clf.predict(D["X"][te])
        row = dict(sensor=s, session_id=t, n=int(te.sum()))
        for c in CLASSES: row[c] = round(float(np.mean(p == c)), 3)
        ood.append(row); print(row)
with open(OUT/"baseline_free_flights.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(ood[0])); w.writeheader(); w.writerows(ood)
