"""Slide visuals that do not depend on experiment results. Colors and font follow docs/ppt-content.md.

python scripts/slide_figures.py [out_dir]   (default: docs/assets)
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

NAVY, BLUE, ORANGE = "#0B1F3A", "#2A78D6", "#EB6834"
INK, MUTED, LINE, SURFACE = "#1F1F1E", "#6B6A64", "#E4E3DF", "#F5F7FA"
plt.rcParams.update({"font.family": "Inter", "font.size": 11, "text.color": INK})

# Official partition, training file. Same table as docs/research.md; ids.run re-checks it on the real data.
TRAIN_COUNTS = {
    "Normal": 56_000,
    "Generic": 40_000,
    "Exploits": 33_393,
    "Fuzzers": 18_184,
    "DoS": 12_264,
    "Reconnaissance": 10_491,
    "Analysis": 2_000,
    "Backdoor": 1_746,
    "Shellcode": 1_133,
    "Worms": 130,
}


def _box(ax, x, y, w, h, fill="white", edge=BLUE, ls="-", lw=1.8):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08", fc=fill, ec=edge, lw=lw, ls=ls
        )
    )


def _arrow(ax, start, end, color=NAVY, ls="-", rad=0.0):
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={
            "arrowstyle": "-|>",
            "color": color,
            "lw": 1.6,
            "ls": ls,
            "connectionstyle": f"arc3,rad={rad}",
        },
    )


def _save(fig, path):
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def class_distribution(path: Path) -> None:
    names, counts = list(TRAIN_COUNTS)[::-1], list(TRAIN_COUNTS.values())[::-1]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    colors = [ORANGE if n == "Worms" else BLUE for n in names]
    ax.barh(names, counts, height=0.62, color=colors)
    ax.set_xscale("log")
    ax.set_xlim(60, 400_000)
    for i, c in enumerate(counts):
        ax.text(c * 1.15, i, f"{c:,}", va="center", fontsize=10, color=INK)
    ax.text(130 * 3.2, 0, "Normal : Worms = 431 : 1", va="center", fontsize=10, fontweight="semibold")
    ax.set_xticks([100, 1_000, 10_000, 100_000], ["100", "1k", "10k", "100k"])
    ax.tick_params(axis="x", which="both", colors=MUTED, labelsize=9, length=0)
    ax.tick_params(axis="y", length=0, labelsize=10.5)
    ax.grid(axis="x", color=LINE, lw=0.8)
    ax.set_axisbelow(True)
    ax.spines[:].set_visible(False)
    ax.set_xlabel("training records (log scale)", color=MUTED, fontsize=9)
    _save(fig, path)


def pipeline(path: Path) -> None:
    steps = [  # (title, caption, optional)
        ("Official CSVs", "175,341 train\n82,332 test", False),
        ("Preprocess", "drop row id; encode\nprotocol, service, state", False),
        ("Train XGBoost", "all 42 features;\n5-fold out-of-fold copy", False),
        ("Rare-class bias", "one offset per class,\ntuned for macro-F1", False),
        ("Prior shift", "EM estimates the live\nattack share, no labels", False),
        ("Analyst feedback", "optional: 5 rounds of\n200 labelled flows", True),
        ("Evaluate once", "on the flows\nnobody labelled", False),
    ]
    fig, ax = plt.subplots(figsize=(16, 3.0))
    w, gap = 2.2, 0.35
    for i, (title, caption, optional) in enumerate(steps):
        x = i * (w + gap)
        _box(ax, x, 0.55, w, 1.25, ls="--" if optional else "-")
        ax.text(
            x + w / 2, 1.45, title, ha="center", va="center", fontsize=11.5, fontweight="semibold", color=NAVY
        )
        ax.text(x + w / 2, 0.95, caption, ha="center", va="center", fontsize=9, color=MUTED, linespacing=1.4)
        if i < len(steps) - 1:
            _arrow(ax, (x + w + 0.04, 1.17), (x + w + gap - 0.04, 1.17))
    left, right = 1 * (w + gap), 4 * (w + gap) + w
    ax.plot([left, left, right, right], [0.42, 0.3, 0.3, 0.42], color=NAVY, lw=1.4)
    ax.text((left + right) / 2, 0.12, "never sees a test label", ha="center", fontsize=11, color=NAVY)
    ax.set_xlim(-0.1, len(steps) * w + (len(steps) - 1) * gap + 0.1)
    ax.set_ylim(0, 1.9)
    ax.axis("off")
    _save(fig, path)


def zero_day(path: Path) -> None:
    attacks = [n for n in TRAIN_COUNTS if n != "Normal"]
    fig, ax = plt.subplots(figsize=(12, 3.9))
    for i, name in enumerate(attacks):
        x, y = (i % 3) * 1.75, 2.0 - (i // 3) * 0.8
        held = name == "Worms"
        _box(
            ax,
            x,
            y,
            1.55,
            0.55,
            fill="white" if held else SURFACE,
            edge=ORANGE if held else SURFACE,
            ls="--" if held else "-",
            lw=1.6,
        )
        ax.text(
            x + 0.775, y + 0.275, name, ha="center", va="center", fontsize=10.5, color=MUTED if held else NAVY
        )
    ax.text(3.5 + 0.775, 0.12, "held out of training", ha="center", fontsize=9.5)
    _box(ax, 6.6, 1.0, 1.9, 0.9)
    ax.text(7.55, 1.45, "Detector", ha="center", va="center", fontsize=13, fontweight="semibold", color=NAVY)
    _arrow(ax, (5.25, 1.75), (6.55, 1.62))
    ax.text(6.15, 2.15, "train: 8 known types\n+ Normal", ha="center", fontsize=9.5, color=MUTED)
    _arrow(ax, (5.1, 0.55), (6.55, 1.2), color=ORANGE, ls="--", rad=0.15)
    ax.text(5.95, 0.5, "test only", ha="center", fontsize=9.5, color=MUTED)
    _box(ax, 9.15, 0.9, 3.0, 1.1, fill=SURFACE, edge=SURFACE)
    ax.text(
        10.65,
        1.45,
        "Unseen-attack detection rate\n= share of Worms flows\nflagged as attack",
        ha="center",
        va="center",
        fontsize=10,
        color=INK,
        linespacing=1.4,
    )
    _arrow(ax, (8.55, 1.45), (9.15, 1.45))
    ax.text(0, -0.45, "Repeated for each of the 9 attack types", fontsize=9.5, color=MUTED)
    ax.set_xlim(-0.1, 12.25)
    ax.set_ylim(-0.6, 2.7)
    ax.axis("off")
    _save(fig, path)


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for make in (class_distribution, pipeline, zero_day):
        make(out / f"{make.__name__}.png")
        print(f"wrote {out / make.__name__}.png")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/assets"))
