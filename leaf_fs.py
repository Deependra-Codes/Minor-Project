"""Medicinal leaf classification: EfficientNetB0 features -> feature selection -> classic ML.

Usage: python leaf_fs.py <dataset_dir> [out_dir]
dataset_dir: any folder tree where each species is a folder of images.
Writes features.npz (cache), results.csv and fs_plot.png to out_dir (default: results/).
"""
import csv
import sys
import time
from pathlib import Path

import keras
import matplotlib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import f_classif, mutual_info_classif
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}
KS = [32, 64, 128, 256, 512, 1280]
SEED = 42


def find_images(root):
    paths, labels = [], []
    for d in sorted(p for p in Path(root).rglob("*") if p.is_dir()):
        imgs = sorted(f for f in d.iterdir() if f.suffix.lower() in IMG_EXT)
        paths += imgs
        labels += [d.name] * len(imgs)
    return paths, np.array(labels)


def extract(paths, batch=64):
    model = keras.applications.EfficientNetB0(include_top=False, pooling="avg", weights="imagenet")
    feats = []
    for i in range(0, len(paths), batch):
        x = np.stack([keras.utils.img_to_array(keras.utils.load_img(p, target_size=(224, 224)))
                      for p in paths[i:i + batch]])
        feats.append(model.predict(x, verbose=0))  # model rescales 0-255 input itself
        print(f"features {min(i + batch, len(paths))}/{len(paths)}", end="\r")
    print()
    return np.concatenate(feats)


def evaluate(clf, Xtr, Xte, ytr, yte):
    t = time.perf_counter()
    clf.fit(Xtr, ytr)
    fit_s = time.perf_counter() - t
    t = time.perf_counter()
    pred = clf.predict(Xte)
    pred_ms = (time.perf_counter() - t) / len(yte) * 1000
    return accuracy_score(yte, pred), f1_score(yte, pred, average="macro"), fit_s, pred_ms


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "results")
    out.mkdir(exist_ok=True)
    cache = out / "features.npz"
    if cache.exists():
        d = np.load(cache)
        X, y = d["X"], d["y"]
    else:
        paths, y = find_images(root)
        classes, counts = np.unique(y, return_counts=True)
        print(f"{len(paths)} images, {len(classes)} classes")
        for c, n in zip(classes, counts):
            print(f"  {n:4d}  {c}")
        X = extract(paths)
        np.savez_compressed(cache, X=X, y=y)

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    rows = []

    # 1) Classifiers on all 1280 features
    clfs = {
        "SVM-RBF": SVC(C=10),
        "KNN-5": KNeighborsClassifier(5),
        "RF-300": RandomForestClassifier(300, random_state=SEED, n_jobs=-1),
        "LogReg": LogisticRegression(max_iter=2000),
    }
    for name, clf in clfs.items():
        rows.append(["none", X.shape[1], name, *evaluate(make_pipeline(StandardScaler(), clf), Xtr, Xte, ytr, yte)])
        print(rows[-1])

    # 2) Feature selection (fit on train only) + SVM. Rank once, then slice top-k.
    scaler = StandardScaler().fit(Xtr)
    Str, Ste = scaler.transform(Xtr), scaler.transform(Xte)
    ks = [k for k in KS if k <= min(X.shape[1], len(ytr))]
    rank = {
        "ANOVA-F": np.argsort(-np.nan_to_num(f_classif(Str, ytr)[0])),
        "MutualInfo": np.argsort(-mutual_info_classif(Str, ytr, random_state=SEED)),
    }
    pca = PCA(max(ks), random_state=SEED).fit(Str)
    Ptr, Pte = pca.transform(Str), pca.transform(Ste)
    for k in ks:
        for method, idx in rank.items():
            rows.append([method, k, "SVM-RBF", *evaluate(SVC(C=10), Str[:, idx[:k]], Ste[:, idx[:k]], ytr, yte)])
            print(rows[-1])
        rows.append(["PCA", k, "SVM-RBF", *evaluate(SVC(C=10), Ptr[:, :k], Pte[:, :k], ytr, yte)])
        print(rows[-1])

    with open(out / "results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["selection", "n_features", "classifier", "accuracy", "macro_f1", "fit_s", "predict_ms_per_img"])
        w.writerows([r[:3] + [f"{v:.4f}" for v in r[3:]] for r in rows])

    for method in ["ANOVA-F", "MutualInfo", "PCA"]:
        pts = [(r[1], r[3]) for r in rows if r[0] == method]
        plt.plot(*zip(*pts), marker="o", label=method)
    plt.xscale("log", base=2)
    plt.xlabel("number of features")
    plt.ylabel("test accuracy (SVM-RBF)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(out / "fs_plot.png", dpi=150, bbox_inches="tight")
    print(f"saved {out}/results.csv and {out}/fs_plot.png")


if __name__ == "__main__":
    main()
