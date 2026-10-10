import numpy as np
import pandas as pd

from ids.evasion import (
    attack_ttls,
    forgery_fills,
    normal_ct,
    normal_ttls,
    rewrite,
    rewrite_values,
    top_pro_attack,
)


def _train_frame():
    # (sttl, normals, attacks): 31 and 64 are normal hosts; 0 is mixed; 254 is the attack testbed; 1 is rare
    spec = [(31, 200, 0), (64, 150, 0), (0, 120, 20), (254, 10, 500), (1, 50, 0)]
    rows = [(ttl, 0, 7 if ttl == 31 else 3) for ttl, n, _ in spec for _ in range(n)]
    rows += [(ttl, 1, 1) for ttl, _, a in spec for _ in range(a)]
    return pd.DataFrame(rows, columns=["sttl", "label", "ct_state_ttl"])


def test_ttl_rules_come_from_training_rows_only():
    train = _train_frame()
    assert normal_ttls(train) == [31, 64]
    assert attack_ttls(train) == [254]
    assert rewrite_values(train) == [31, 64]  # adds the mode of training normals (31) to the normal TTLs
    assert normal_ct(train, 31) == 7 and normal_ct(train, 64) == 3
    assert normal_ct(train.drop(columns="ct_state_ttl"), 31) is None


def test_rewrite_edits_only_attack_rows_and_leaves_the_input_alone():
    X = pd.DataFrame({"sttl": [254, 31, 62], "ct_state_ttl": [2, 0, 1], "sbytes": [10, 20, 30]})
    is_attack = np.array([True, False, True])
    out = rewrite(X, is_attack, 31)
    assert list(out["sttl"]) == [31, 31, 31] and list(out["ct_state_ttl"]) == [2, 0, 1]
    out = rewrite(X, is_attack, 31, ct_value=0)
    assert list(out["ct_state_ttl"]) == [0, 0, 0]
    assert list(out["sbytes"]) == [10, 20, 30]
    assert list(X["sttl"]) == [254, 31, 62] and list(X["ct_state_ttl"]) == [2, 0, 1]


def test_forgery_fills_use_training_normals_only():
    X = pd.DataFrame({"sbytes": [10.0, 30.0, 1000.0, 5000.0], "proto": [2.0, 2.0, 7.0, 7.0]})
    y = pd.Series(["Normal", "Normal", "Attack", "Attack"])
    assert forgery_fills(X, y) == {"sbytes": 20.0, "proto": 2.0}


def test_top_pro_attack_follows_the_margin_orientation():
    contribs = np.array([[0.5, -2.0, 0.1, 9.9], [-0.3, 0.2, 1.5, 9.9]])  # last column is the bias
    features = ["a", "b", "c"]
    # Attack is class 0, so XGBoost's margin is the log-odds of Normal: pro-attack = most negative
    assert list(top_pro_attack(contribs, features, attack_index=0)) == ["b", "a"]
    assert list(top_pro_attack(contribs, features, attack_index=1)) == ["a", "c"]
