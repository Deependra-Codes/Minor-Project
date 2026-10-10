"""Run every experiment on the official UNSW-NB15 split and write the results folder.

python -m ids.run --data data --out results
"""

import argparse
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from ids.data import Split, Task, make_split, read_partition, target
from ids.metrics import per_class_recall, score
from ids.models import MODELS
from ids.plots import confusion, selection_curve
from ids.selection import METHODS, rank_features

KS = (5, 10, 15, 20, 30)
SELECTION_MODEL = "HistGB"
SEED = 42


def evaluate(model_name: str, split: Split, columns: list[str]) -> tuple[dict, np.ndarray]:
    model = MODELS[model_name](SEED)
    start = perf_counter()
    model.fit(split.X_train[columns], split.y_train)
    fit_s = perf_counter() - start
    start = perf_counter()
    pred = model.predict(split.X_test[columns])
    predict_us = (perf_counter() - start) / len(pred) * 1e6
    row = {"model": model_name, "n_features": len(columns), **score(split.y_test, pred)}
    return row | {"fit_s": fit_s, "predict_us_per_row": predict_us}, pred


def log(row: dict) -> None:
    print(
        f"{row['task']:10} {row['selection']:13} {row['model']:15} k={row['n_features']:<3}"
        f" acc={row['accuracy']:.4f} macroF1={row['macro_f1']:.4f}"
        f" DR={row['detection_rate']:.4f} FAR={row['false_alarm_rate']:.4f}",
        flush=True,
    )


def baselines(split: Split, task: Task, out: Path) -> list[dict]:
    """Every model on all features. Saves per-class recall and the best model's confusion matrix."""
    rows, recalls, best = [], {}, (-1.0, "", np.array([]))
    for name in MODELS:
        row, pred = evaluate(name, split, list(split.X_train.columns))
        rows.append({"task": task, "selection": "none"} | row)
        log(rows[-1])
        recalls[name] = per_class_recall(split.y_test, pred)
        if row["macro_f1"] > best[0]:
            best = (row["macro_f1"], name, pred)
    pd.DataFrame(recalls).rename_axis("class").to_csv(
        out / f"per_class_recall_{task}.csv", float_format="%.4f"
    )
    confusion(split.y_test, best[2], out / f"confusion_{task}.png", f"{task}: {best[1]}, all features")
    return rows


def selection(split: Split, task: Task, out: Path) -> list[dict]:
    """Rank features three ways on train, then refit SELECTION_MODEL on the top-k of each ranking."""
    n = split.X_train.shape[1]
    rows, rankings = [], {}
    for method in METHODS:
        rankings[method] = rank_features(split.X_train, split.y_train, method, SEED)
        for k in [k for k in KS if k < n] + [n]:
            row, _ = evaluate(SELECTION_MODEL, split, rankings[method][:k])
            rows.append({"task": task, "selection": method} | row)
            log(rows[-1])
    pd.DataFrame(rankings).rename_axis("rank").to_csv(out / f"ranking_{task}.csv")
    selection_curve(
        pd.DataFrame(rows), out / f"selection_{task}.png", f"{task}: {SELECTION_MODEL} on top-k features"
    )
    return rows


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--data", type=Path, default=Path("data"), help="folder with the two official CSVs")
    parser.add_argument("--out", type=Path, default=Path("results"))
    parser.add_argument("--task", choices=["binary", "multiclass", "both"], default="both")
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)

    train, test = read_partition(args.data)
    counts = (
        pd.DataFrame(
            {
                "train": target(train, "multiclass").value_counts(),
                "test": target(test, "multiclass").value_counts(),
            }
        )
        .fillna(0)
        .astype(int)
    )
    counts.rename_axis("class").to_csv(args.out / "class_counts.csv")
    print(counts.to_string(), "\n")

    rows = []
    for task in ("binary", "multiclass") if args.task == "both" else (args.task,):
        split = make_split(train, test, task)
        rows += baselines(split, task, args.out)
        rows += selection(split, task, args.out)
    pd.DataFrame(rows).to_csv(args.out / "results.csv", index=False, float_format="%.4f")
    print(f"\nwrote {args.out}/results.csv")


if __name__ == "__main__":
    main()
