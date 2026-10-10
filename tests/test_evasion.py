import numpy as np
import pandas as pd

from ids.evasion import (
    attack_ttls,
    ct_rule,
    feature_sets,
    forge,
    forgery_fills,
    normal_ttls,
    rewrite,
    rewrite_values,
    top_pro_attack,
)


def _train_frame():
    # (sttl, normals, attacks): 31 and 64 are normal hosts; 0 is mixed; 254 is the attack testbed; 1 is rare;
    # 32 has 101 rows but only 99 normals; 255 is all attacks but under 1% of rows
    spec = [(31, 200, 0), (64, 150, 0), (0, 120, 20), (254, 10, 500), (1, 50, 0), (32, 99, 2), (255, 0, 5)]
    rows = [(ttl, 0, 7 if ttl == 31 else 3) for ttl, n, _ in spec for _ in range(n)]
    rows += [(ttl, 1, 1) for ttl, _, a in spec for _ in range(a)]
    return pd.DataFrame(rows, columns=["sttl", "label", "ct_state_ttl"])


def test_ttl_rules_come_from_training_rows_only():
    train = _train_frame()
    assert normal_ttls(train) == [31, 64]
    assert attack_ttls(train) == [254]
    assert rewrite_values(train) == [31, 64]  # adds the mode of training normals (31) to the normal TTLs


def _ct_rule():
    # ct_state_ttl is 2 only for state 1 with source TTL 254, as UNSW-NB15 derives it from state and TTLs
    X = pd.DataFrame({"state": [0, 0, 1, 1] * 5, "sttl": [254, 31, 254, 31] * 5, "dttl": [0] * 20})
    X["ct_state_ttl"] = np.where((X["sttl"] == 254) & (X["state"] == 1), 2, 0)
    return ct_rule(X)


def test_ct_rule_rederives_ct_state_ttl_from_state_and_ttls():
    probe = pd.DataFrame({"state": [1, 1, 0], "sttl": [254, 31, 254], "dttl": [0, 0, 0]})
    assert list(_ct_rule().predict(probe)) == [2, 0, 0]
    assert ct_rule(pd.DataFrame({"sttl": [1], "ct_state_ttl": [0]})) is None  # no state or dttl column


def test_rewrite_edits_only_attack_rows_and_leaves_the_input_alone():
    X = pd.DataFrame(
        {"state": [1, 1, 1], "sttl": [254, 254, 62], "dttl": [0, 0, 0], "ct_state_ttl": [2, 2, 1]}
    ).assign(sbytes=[10, 20, 30])
    is_attack = np.array([True, False, True])
    out = rewrite(X, is_attack, 31)
    assert list(out["sttl"]) == [31, 254, 31] and list(out["ct_state_ttl"]) == [2, 2, 1]
    out = rewrite(X, is_attack, 31, _ct_rule())
    assert list(out["ct_state_ttl"]) == [0, 2, 0]  # re-derived on edited rows only
    assert list(out["sbytes"]) == [10, 20, 30]
    assert list(X["sttl"]) == [254, 254, 62] and list(X["ct_state_ttl"]) == [2, 2, 1]


def test_forge_rederives_ct_state_ttl_only_when_its_inputs_change():
    X = pd.DataFrame({"state": [1], "sttl": [254], "dttl": [0], "ct_state_ttl": [2], "sbytes": [10]})
    fills, rule = {"sttl": 31, "ct_state_ttl": 5, "sbytes": 20}, _ct_rule()
    assert list(forge(X, fills, ["sttl"], rule)["ct_state_ttl"]) == [0]
    assert list(forge(X, fills, ["sbytes"], rule)["ct_state_ttl"]) == [2]
    assert list(forge(X, fills, ["sttl", "ct_state_ttl"], rule)["ct_state_ttl"]) == [5]  # forged directly
    assert list(X["sttl"]) == [254]


def test_no_ttl_drops_exactly_the_three_ttl_fields():
    sets = feature_sets(["sttl", "sbytes", "dttl", "ct_state_ttl"])
    assert sets == {"all": ["sttl", "sbytes", "dttl", "ct_state_ttl"], "no_ttl": ["sbytes"]}


def test_forgery_fills_use_training_normals_only():
    # proto is categorical: its fill is the normals' mode (1), not their median (5)
    X = pd.DataFrame(
        {"sbytes": [10.0, 30.0, 50.0, 60.0, 70.0, 5000.0], "proto": [1.0, 1.0, 5.0, 6.0, 7.0, 9.0]}
    )
    y = pd.Series(["Normal"] * 5 + ["Attack"])
    assert forgery_fills(X, y) == {"sbytes": 50.0, "proto": 1.0}


def test_top_pro_attack_follows_the_margin_orientation():
    contribs = np.array([[0.5, -2.0, 0.1, 9.9], [-0.3, 0.2, 1.5, 9.9]])  # last column is the bias
    features = ["a", "b", "c"]
    # Attack is class 0, so XGBoost's margin is the log-odds of Normal: pro-attack = most negative
    assert list(top_pro_attack(contribs, features, attack_index=0)) == ["b", "a"]
    assert list(top_pro_attack(contribs, features, attack_index=1)) == ["a", "c"]
