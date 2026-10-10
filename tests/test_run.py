import numpy as np
import pandas as pd
import pytest

from ids.data import TEST_FILE, TRAIN_FILE
from ids.models import MODELS
from ids.selection import METHODS

ROUNDED = 1e-4  # results CSVs keep four decimals


def test_end_to_end_writes_every_output(results_dir):
    out = results_dir
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


def test_ceilings_bound_every_model_on_the_same_rows(results_dir):
    ceiling = pd.read_csv(results_dir / "ceiling.csv", index_col="task")
    m = ceiling.loc["multiclass"]
    assert m["majority_macro_f1"] <= m["macro_f1_lower"] + 1e-12 <= m["macro_f1_upper"] + 2e-12
    f1 = pd.read_csv(results_dir / "per_class_f1_multiclass.csv", index_col="class")
    for c, models in f1.iterrows():
        assert (models <= m[f"f1_ceiling_{c}"] + 1e-9).all(), c
    results = pd.read_csv(results_dir / "results.csv")
    for task, rows in results.groupby("task"):
        assert (rows["accuracy"] <= ceiling.loc[task, "accuracy_ceiling"] + 1e-9).all(), task


def test_evasion_tables_agree_with_each_other(results_dir):
    """Each TTL table is checked against another table that measures the same thing by another path."""
    train, test = (pd.read_csv(results_dir.parent / name) for name in (TRAIN_FILE, TEST_FILE))
    free = pd.read_csv(results_dir / "ttl_free.csv")
    binary = free[free["task"] == "binary"].set_index(["model", "features"])
    assert (free.groupby("task")["n_features"].agg(np.ptp) == 3).all()  # no_ttl drops exactly three
    evasion, sweep = pd.read_csv(results_dir / "evasion.csv"), pd.read_csv(results_dir / "ttl_sweep.csv")
    sweep = sweep.set_index(["model", "ttl"])["detection"]
    attacks = test.loc[test["label"] == 1, "attack_cat"].value_counts()
    normals = train.loc[train["label"] == 0, "sttl"]
    for _, r in evasion.iterrows():
        clean = binary.loc[(r["model"], r["features"]), "detection_rate"]
        assert r["clean_detection"] == pytest.approx(clean, abs=ROUNDED)
        assert r["train_normal_share"] == pytest.approx((normals == r["ttl"]).mean(), abs=ROUNDED)
        per_type = sum(r[f"det_{t}"] * n for t, n in attacks.items()) / attacks.sum()
        assert per_type == pytest.approx(r["detection"], abs=ROUNDED)
        if r["features"] == "all":  # same edit, two code paths
            assert r["detection"] == pytest.approx(sweep[(r["model"], r["ttl"])], abs=ROUNDED)


def test_false_alarm_tables_agree_with_each_other(results_dir):
    test = pd.read_csv(results_dir.parent / TEST_FILE)
    attr = pd.read_csv(results_dir / "ttl_attribution.csv").iloc[0]
    normal = test["label"] == 0
    host = normal & test["sttl"].isin([int(v) for v in str(attr["attack_ttls"]).split()])
    free = pd.read_csv(results_dir / "ttl_free.csv")
    for _, r in free[free["task"] == "binary"].iterrows():
        split = r["far_attack_ttl_normals"] * host.sum() + r["far_other_normals"] * (normal & ~host).sum()
        assert split / normal.sum() == pytest.approx(r["false_alarm_rate"], abs=2 * ROUNDED)
    xgb = free.set_index(["task", "model", "features"]).loc[("binary", "XGBoost", "all")]
    assert 0 < attr["false_alarms"] == pd.read_csv(results_dir / "diagnosis.csv")["false_alarms"].iloc[0]
    on_hosts = attr["fa_attack_ttl_share"] * attr["false_alarms"]
    expected = xgb["far_attack_ttl_normals"] * host.sum()
    assert on_hosts == pytest.approx(expected, abs=ROUNDED * (attr["false_alarms"] + host.sum()))
    assert attr["fa_top_feature_sttl_share"] == 1.0  # sttl is the fake data's only signal
    assert attr["ct_rule_test_match"] == 1.0  # the fake ct_state_ttl is an exact function of its inputs


def test_worst_forged_pair_is_built_on_the_worst_single_feature(results_dir):
    sub = pd.read_csv(results_dir / "substitution.csv")
    for fs, rows in sub[sub["model"] == "XGBoost"].groupby("features"):
        single, pair = rows[rows["n_forged"] == 1], rows[rows["n_forged"] == 2]
        worst = single.loc[single["detection"].idxmin(), "forged"]
        assert len(pair) == len(single) - 1 and pair["forged"].str.startswith(f"{worst}+").all(), fs
