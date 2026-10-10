"""Report figures. Series colors are a validated categorical palette; each method also gets its own marker."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from sklearn.metrics import confusion_matrix  # noqa: E402

SERIES = {"anova_f": ("#2a78d6", "o"), "mutual_info": ("#eb6834", "s"), "rf_importance": ("#1baf7a", "^")}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3df"
BLUES = LinearSegmentedColormap.from_list("blues", ["#fcfcfb", "#86b6ef", "#2a78d6", "#0d366b"])


def _style(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, loc="left", color=INK, fontsize=11)
    ax.tick_params(colors=MUTED, labelsize=9)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)


def selection_curve(rows: pd.DataFrame, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for method, (color, marker) in SERIES.items():
        r = rows[rows["selection"] == method].sort_values("n_features")
        ax.plot(r["n_features"], r["macro_f1"], color=color, marker=marker, lw=2, ms=6, label=method)
    ax.set_xticks(sorted(rows["n_features"].unique()))
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_xlabel(f"features kept (of {rows['n_features'].max()})", color=MUTED)
    ax.set_ylabel("macro-F1, official test set", color=MUTED)
    ax.legend(frameon=False, labelcolor=INK)
    _style(ax, title)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def confusion(y_true: pd.Series, y_pred: np.ndarray, path: Path, title: str) -> None:
    labels = sorted(set(y_true))
    cm = confusion_matrix(y_true, y_pred, labels=labels, normalize="true")
    fig, ax = plt.subplots(figsize=(1.1 + 0.65 * len(labels), 0.9 + 0.6 * len(labels)))
    ax.imshow(cm, cmap=BLUES, vmin=0, vmax=1)
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    for i, j in zip(
        *np.nonzero(cm >= 0.01), strict=True
    ):  # skip near-zero cells so the real confusions stand out
        ax.text(
            j,
            i,
            f"{cm[i, j]:.2f}",
            ha="center",
            va="center",
            fontsize=8,
            color="white" if cm[i, j] > 0.6 else INK,
        )
    ax.set_xlabel("predicted", color=MUTED)
    ax.set_ylabel("true (each row sums to 1 = recall)", color=MUTED)
    _style(ax, title)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
