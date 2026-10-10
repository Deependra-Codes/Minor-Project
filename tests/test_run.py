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
        "+feedback +prior shift",
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
        "ttl_shift.csv",
        "per_class_f1_multiclass.csv",
        "ttl_free.csv",
        "recall_ttl_free.csv",
        "substitution.csv",
        "ttl_attribution.csv",
        "ttl_sweep.png",
    ]:
        assert (out / name).exists(), name
    ceiling = pd.read_csv(out / "ceiling.csv")
    assert (ceiling["macro_f1_lower"] <= ceiling["macro_f1_upper"]).all()
    assert (ceiling["majority_macro_f1"] <= ceiling["macro_f1_upper"]).all()
    assert len(pd.read_csv(out / "ttl_sweep.csv")) == 256 * 2  # every TTL value, two binary models
    evasion = pd.read_csv(out / "evasion.csv")
    no_ttl = evasion[evasion["features"] == "no_ttl"]
    assert len(no_ttl) and (no_ttl["detection"] == no_ttl["clean_detection"]).all()  # immune by construction
    diagnosis = pd.read_csv(out / "diagnosis.csv").iloc[0]
    assert diagnosis["false_alarms"] <= diagnosis["normal_flows"]
    for share in ("fa_train_neighbour_attack_share", "ok_train_neighbour_attack_share"):
        assert 0 <= diagnosis[share] <= 1 or pd.isna(diagnosis[share])
    ttl = pd.read_csv(out / "ttl_shift.csv")
    assert set(ttl["split"]) == {"train", "test"} and ttl["attack_share"].between(0, 1).all()
