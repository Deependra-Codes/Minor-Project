import pandas as pd

from ids.models import MODELS
from ids.run import main
from ids.selection import METHODS


def test_end_to_end_writes_every_output(data_dir, tmp_path):
    out = tmp_path / "results"
    main(["--data", str(data_dir), "--out", str(out), "--feedback-per-round", "5"])
    rows = pd.read_csv(out / "results.csv")
    per_task = len(MODELS) + len(METHODS) * 2  # 6 features -> k in (5, 6)
    assert len(rows) == 2 * per_task
    ladder = pd.read_csv(out / "improvement.csv")
    assert list(ladder["variant"].unique()) == [
        "base",
        "+prior shift",
        "+class bias",
        "+prior shift +class bias",
        "+feedback",
        "+feedback +prior shift +class bias",
    ]
    assert (ladder["eval_rows"] == 150 - 5 * 5).all()  # every variant scored on the same unlabelled flows
    zero_day = pd.read_csv(out / "zero_day.csv")
    assert set(zero_day["held_out"]) == {"Exploits", "Worms"}
    for name in [
        "class_counts.csv",
        "ceiling.csv",
        "ranking_binary.csv",
        "per_class_recall_multiclass.csv",
        "confusion_multiclass.png",
        "selection_binary.png",
        "recall_gain_multiclass.png",
        "zero_day.png",
        "conflict.png",
        "feedback_curve.csv",
        "feedback.png",
    ]:
        assert (out / name).exists(), name
