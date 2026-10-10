"""Report figures. Series colors are a validated categorical palette; each method also gets its own marker."""

from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from sklearn.metrics import confusion_matrix  # noqa: E402

SERIES = {"anova_f": ("#2a78d6", "o"), "mutual_info": ("#eb6834", "s"), "rf_importance": ("#1baf7a", "^")}
METHOD_NAMES = {
    "anova_f": "ANOVA F-test",
    "mutual_info": "mutual information",
    "rf_importance": "RF importance",
}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3df"
BLUES = LinearSegmentedColormap.from_list("blues", ["#fcfcfb", "#86b6ef", "#2a78d6", "#0d366b"])
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Inter", "DejaVu Sans"]})


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
        ax.plot(
            r["n_features"], r["macro_f1"], color=color, marker=marker, lw=2, ms=6, label=METHOD_NAMES[method]
        )
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


def _hbar_axes(ax: plt.Axes, labels: list[str], title: str, xlabel: str) -> None:
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlim(0, 1.08)
    ax.set_xlabel(xlabel, color=MUTED)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    _style(ax, title)
    ax.spines["left"].set_visible(False)


def _gain_labels(base: float, final: float, pad: float = 0.02):
    """(x, ha) of the baseline and final labels, each on the outer side of its own dot."""
    if final >= base:
        return (base - pad, "right"), (final + pad, "left")
    return (base + pad, "left"), (final - pad, "right")


def recall_gain(base: dict[str, float], final: dict[str, float], path: Path, title: str) -> None:
    """Dumbbell per class: grey dot = baseline recall, blue dot = improved recall."""
    labels = sorted(base, key=base.get)
    fig, ax = plt.subplots(figsize=(7.2, 0.9 + 0.42 * len(labels)))
    for i, c in enumerate(labels):
        ax.plot([base[c], final[c]], [i, i], color=GRID, lw=3, solid_capstyle="round", zorder=1)
        (base_x, base_ha), (final_x, final_ha) = _gain_labels(base[c], final[c])
        ax.text(base_x, i, f"{base[c]:.2f}", ha=base_ha, va="center", fontsize=8, color=MUTED)
        ax.text(final_x, i, f"{final[c]:.2f}", ha=final_ha, va="center", fontsize=8, color=INK)
    ax.scatter([base[c] for c in labels], range(len(labels)), s=55, color=MUTED, zorder=2, label="baseline")
    ax.scatter(
        [final[c] for c in labels],
        range(len(labels)),
        s=55,
        color=SERIES["anova_f"][0],
        zorder=3,
        label="improved",
    )
    _hbar_axes(ax, labels, title, "recall on the official test set")
    ax.legend(frameon=False, loc="lower right", labelcolor=INK)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def zero_day_chart(rows: pd.DataFrame, path: Path) -> None:
    """Detection of each attack type when it was in training (blue) vs held out of training (orange)."""
    rows = rows.sort_values("detection_unseen")
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(7.2, 0.9 + 0.5 * len(rows)))
    for offset, col, color, label in (
        (0.19, "detection_seen", SERIES["anova_f"][0], "seen in training"),
        (-0.19, "detection_unseen", SERIES["mutual_info"][0], "never seen (zero-day)"),
    ):
        ax.barh(y + offset, rows[col], height=0.36, color=color, label=label)
        for yi, v in zip(y + offset, rows[col], strict=True):
            ax.text(v + 0.01, yi, f"{v:.2f}", va="center", fontsize=8, color=INK)
    _hbar_axes(
        ax,
        list(rows["held_out"]),
        "Detection rate: seen vs never-seen attack type",
        "share flagged as attack",
    )
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, labelcolor=INK)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def conflict_chart(share: dict[str, float], path: Path) -> None:
    """Share of each class's test rows whose exact feature vector also carries another label."""
    labels = sorted(share, key=share.get)
    fig, ax = plt.subplots(figsize=(7.2, 0.9 + 0.42 * len(labels)))
    ax.barh(range(len(labels)), [share[c] for c in labels], height=0.62, color=SERIES["anova_f"][0])
    for i, c in enumerate(labels):
        ax.text(share[c] + 0.01, i, f"{share[c]:.0%}", va="center", fontsize=8.5, color=INK)
    _hbar_axes(ax, labels, "Test rows identical to a row of another class", "share of the class's test rows")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def feedback_chart(curve: pd.DataFrame, path: Path) -> None:
    """False-alarm rate after each round of analyst labels, one line per task."""
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for (task, rows), (color, marker) in zip(curve.groupby("task"), list(SERIES.values()), strict=False):
        ax.plot(rows["labels"], rows["false_alarm_rate"], color=color, marker=marker, lw=2, ms=6, label=task)
        last = rows.iloc[-1]
        ax.text(
            last["labels"] + 15,
            last["false_alarm_rate"],
            f"{last['false_alarm_rate']:.1%}",
            va="center",
            fontsize=9,
            color=INK,
        )
    ax.set_xticks(sorted(curve["labels"].unique()))
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_xlabel("test-day flows labelled by an analyst", color=MUTED)
    ax.set_ylabel("false-alarm rate on unlabelled flows", color=MUTED)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.legend(frameon=False, labelcolor=INK)
    _style(ax, "False alarms fall as an analyst labels the least certain flows")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def mark_groups(marks: dict[int, str]) -> dict[str, list[int]]:
    """TTL values per kind of vertical mark, sorted."""
    kinds = ("normal TTL", "attack TTL")
    return {kind: sorted(v for v, label in marks.items() if label == kind) for kind in kinds}


def ttl_sweep_chart(rows: pd.DataFrame, marks: dict[int, str], path: Path) -> None:
    """Detection when every attack flow's source TTL is set to one value, 0-255, one line per model."""
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    colors = (SERIES["anova_f"][0], SERIES["mutual_info"][0])
    for (model, r), color in zip(rows.groupby("model", sort=False), colors, strict=False):
        ax.plot(r["ttl"], r["detection"], color=color, lw=2, label=model)
    styles = {"normal TTL": "--", "attack TTL": ":"}
    for kind, values in mark_groups(marks).items():
        ls = styles[kind]
        for value in values:
            ax.axvline(value, color=MUTED, lw=1, ls=ls, zorder=0)
        if values:
            ax.plot([], [], color=MUTED, lw=1, ls=ls, label=f"{kind}: {', '.join(map(str, values))}")
    ax.set_xlim(0, 255)
    ax.set_xticks([0, 32, 64, 96, 128, 160, 192, 224, 255])
    ax.set_ylim(-0.02, 1.02)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_xlabel("source TTL written into every attack flow", color=MUTED)
    ax.set_ylabel("attacks still detected", color=MUTED)
    ax.legend(frameon=False, labelcolor=INK, fontsize=8.5, loc="lower right")
    _style(ax, "Detection after rewriting one header byte")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
