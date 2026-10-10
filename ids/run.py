"""Run every experiment on the official UNSW-NB15 split and write the results folder.

python -m ids.run --data data --out results
"""

import argparse
from pathlib import Path

import pandas as pd

from ids.data import make_split, read_partition, target
from ids.experiments import baselines, ceiling, improve, selection, zero_day
from ids.plots import feedback_chart


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--data", type=Path, default=Path("data"), help="folder with the two official CSVs")
    parser.add_argument("--out", type=Path, default=Path("results"))
    parser.add_argument(
        "--feedback-per-round", type=int, default=200, help="flows an analyst labels per round"
    )
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
    print(counts.to_string(), "\n", flush=True)

    rows, ladder, curve, ceilings = [], [], [], []
    for task in ("binary", "multiclass"):
        split = make_split(train, test, task)
        for name, step in (("baselines", baselines), ("selection", selection)):
            print(f"[{task}] {name} ...", flush=True)
            rows += step(split, task, args.out)
        print(f"[{task}] improve ...", flush=True)
        task_ladder, task_curve = improve(split, task, args.out, args.feedback_per_round)
        ladder, curve = ladder + task_ladder, curve + task_curve
        ceilings.append(ceiling(split, task, args.out))
    print("[binary] zero-day ...", flush=True)
    zero = zero_day(train, test, args.out)
    feedback_chart(pd.DataFrame(curve), args.out / "feedback.png")

    for name, table in (
        ("results", rows),
        ("improvement", ladder),
        ("feedback_curve", curve),
        ("ceiling", ceilings),
        ("zero_day", zero),
    ):
        pd.DataFrame(table).to_csv(args.out / f"{name}.csv", index=False, float_format="%.4f")
    print(
        pd.DataFrame(ladder)[["task", "variant", "accuracy", "macro_f1", "false_alarm_rate"]].to_string(
            index=False
        )
    )
    print(f"\nwrote {args.out}/")


if __name__ == "__main__":
    main()
