import numpy as np
import pandas as pd

from ids.data import Split
from ids.evasion import (
    BINARY_MODELS,
    _forgery,
    _rewrites,
    _sweep,
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
    # the unedited row's recorded ct_state_ttl (3) is not what the rule would give, and must survive
    X = pd.DataFrame(
        {"state": [1, 1, 1], "sttl": [254, 254, 62], "dttl": [0, 0, 0], "ct_state_ttl": [2, 3, 1]}
    ).assign(sbytes=[10, 20, 30])
    is_attack = np.array([True, False, True])
    out = rewrite(X, is_attack, 31)
    assert list(out["sttl"]) == [31, 254, 31] and list(out["ct_state_ttl"]) == [2, 3, 1]
    out = rewrite(X, is_attack, 31, _ct_rule())
    assert list(out["ct_state_ttl"]) == [0, 3, 0]  # re-derived on edited rows only
    assert list(out["sbytes"]) == [10, 20, 30]
    assert list(X["sttl"]) == [254, 254, 62] and list(X["ct_state_ttl"]) == [2, 3, 1]


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


class _FlagsCt:
    """Stands in for a fitted model: calls a flow an attack exactly when its ct_state_ttl is non-zero."""

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        attack = (X["ct_state_ttl"].to_numpy() > 0).astype(float)
        return np.c_[attack, 1 - attack]


def _stub_run():
    """Three attack flows on state 1 and one normal flow, and a model that only reads ct_state_ttl."""
    X = pd.DataFrame(
        {"state": [1, 1, 1, 0], "sttl": [254, 254, 62, 31], "dttl": [0] * 4, "ct_state_ttl": [2, 2, 1, 0]}
    ).astype(float)
    y = pd.Series(["Attack", "Attack", "Attack", "Normal"])
    model = (_FlagsCt(), np.array(["Attack", "Normal"]), list(X.columns))
    return {(name, "all"): model for name in BINARY_MODELS}, Split(X, X, y, y), y.to_numpy() != "Normal"


def test_every_ttl_edit_is_scored_with_ct_state_ttl_rederived():
    fitted, split, attack = _stub_run()
    sweep = pd.DataFrame(_sweep(fitted, split, attack, _ct_rule()))
    by_ttl = sweep[sweep["model"] == "XGBoost"].set_index("ttl")["detection"]
    assert len(sweep) == 512 and by_ttl[31] == 0.0 and by_ttl[254] == 1.0  # over the three attacks only
    types = np.array(["Exploits", "Exploits", "DoS", "Normal"])
    rewrites = pd.DataFrame(_rewrites(fitted, split, _train_frame(), _ct_rule(), types))
    assert (rewrites["clean_detection"] == 1.0).all() and (rewrites["detection"] == 0.0).all()
    forged = pd.DataFrame(_forgery(fitted, split, attack, _ct_rule()))
    single = forged[forged["n_forged"] == 1].drop_duplicates("forged").set_index("forged")["detection"]
    assert single["sttl"] == 0.0 and single["ct_state_ttl"] == 0.0
