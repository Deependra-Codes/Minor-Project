"""One header byte, the source TTL, carries most of the detector's verdicts. This module measures that.

Every rule here (which TTL values count as normal, the fill value for a forged feature) comes from the
training file; test labels are used only to score. The rewrite edits recorded flows in feature space: it
simulates an attacker who sets the initial TTL of their packets, it does not regenerate traffic.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier

from ids.data import CATEGORICAL, NORMAL, Split, make_split, target
from ids.metrics import per_class_recall, score
from ids.models import SEED, fit
from ids.plots import ttl_sweep_chart

TTL = ["sttl", "dttl", "ct_state_ttl"]
DERIVED_FROM = ["state", "sttl", "dttl"]  # UNSW-NB15 computes ct_state_ttl from these three
BINARY_MODELS = ("XGBoost", "HistGB-balanced")


def feature_sets(columns) -> dict[str, list[str]]:
    return {"all": list(columns), "no_ttl": [c for c in columns if c not in TTL]}


def _ttl_stats(train: pd.DataFrame) -> pd.DataFrame:
    return train.groupby("sttl")["label"].agg(rows="size", attack_share="mean")


def normal_ttls(train: pd.DataFrame, min_normals: int = 100, max_attack_share: float = 0.05) -> list[int]:
    """Source TTLs that the training file says belong to normal hosts."""
    stats = _ttl_stats(train)
    normals = stats["rows"] * (1 - stats["attack_share"])
    keep = (normals >= min_normals) & (stats["attack_share"] < max_attack_share)
    return [int(v) for v in stats.index[keep]]


def attack_ttls(train: pd.DataFrame, min_share: float = 0.01) -> list[int]:
    """Source TTLs that cover 1%+ of training flows and are mostly attacks: the testbed's attack hosts."""
    stats = _ttl_stats(train)
    keep = (stats["rows"] >= min_share * len(train)) & (stats["attack_share"] > 0.5)
    return [int(v) for v in stats.index[keep]]


def rewrite_values(train: pd.DataFrame) -> list[int]:
    """The normal TTLs, plus the TTL that training normals carry most often."""
    mode = int(train.loc[train["label"] == 0, "sttl"].mode().iloc[0])
    return sorted(set(normal_ttls(train)) | {mode})


def ct_rule(X_train: pd.DataFrame) -> DecisionTreeClassifier | None:
    """ct_state_ttl as the feature extractor derives it from state, sttl and dttl, learned from training rows.

    An edited TTL with the old ct_state_ttl is a flow no extractor can produce, so every edit re-derives it.
    """
    if not {"ct_state_ttl", *DERIVED_FROM} <= set(X_train):
        return None
    return DecisionTreeClassifier(random_state=SEED).fit(X_train[DERIVED_FROM], X_train["ct_state_ttl"])


def _rederive(X: pd.DataFrame, rows: np.ndarray, rule: DecisionTreeClassifier | None) -> pd.DataFrame:
    if rule is not None and rows.any():
        X.loc[rows, "ct_state_ttl"] = rule.predict(X.loc[rows, DERIVED_FROM])
    return X


def rewrite(X: pd.DataFrame, is_attack: np.ndarray, value: int, rule=None) -> pd.DataFrame:
    """A copy of X with the source TTL of attack rows set to value and their ct_state_ttl re-derived."""
    out = X.copy()
    out.loc[is_attack, "sttl"] = value
    return _rederive(out, is_attack, rule)


def forge(X: pd.DataFrame, fills: dict, forged: list[str], rule=None) -> pd.DataFrame:
    """A copy of X with the forged features set to their fills; ct_state_ttl re-derived if an input moved."""
    out = X.copy()
    for feature in forged:
        out[feature] = fills[feature]
    moved = "ct_state_ttl" not in forged and bool(set(forged) & set(DERIVED_FROM))
    return _rederive(out, np.full(len(out), moved), rule)


def forgery_fills(X_train: pd.DataFrame, y_train: pd.Series) -> dict[str, float]:
    """A typical normal value per feature: the mode for categorical features, the median otherwise."""
    normal = X_train[y_train.to_numpy() == NORMAL]
    return {c: float(normal[c].mode().iloc[0] if c in CATEGORICAL else normal[c].median()) for c in X_train}


def top_pro_attack(contribs: np.ndarray, features: list[str], attack_index: int) -> np.ndarray:
    """Most pro-attack feature per row from XGBoost pred_contribs (the last column is the bias).

    A binary XGBoost margin is the log-odds of class 1. With classes ['Attack', 'Normal'] Attack is class 0,
    so the most pro-attack feature is the one with the most negative contribution.
    """
    per_feature = contribs[:, :-1]
    return np.asarray(features)[per_feature.argmin(1) if attack_index == 0 else per_feature.argmax(1)]


def _flagged(fitted: tuple, X: pd.DataFrame) -> np.ndarray:
    model, classes, cols = fitted
    return classes[model.predict_proba(X[cols]).argmax(1)] != NORMAL


def _rate(flags: np.ndarray) -> float:
    return float(flags.mean()) if len(flags) else float("nan")


def _clean(binary: Split, multi: Split, sets: dict, hosts: list[int], out: Path) -> tuple[dict, list[dict]]:
    """Fit both binary models on both feature sets and score them; also the 10-class cost of dropping TTL."""
    X_train, X_test = binary.X_train.astype(float), binary.X_test.astype(float)
    normal = binary.y_test.to_numpy() == NORMAL
    host = binary.X_test["sttl"].isin(hosts).to_numpy()
    fitted, rows, recalls = {}, [], {}
    for name in BINARY_MODELS:
        for fs, cols in sets.items():
            fitted[(name, fs)] = (*fit(name, X_train[cols], binary.y_train), cols)
            flagged = _flagged(fitted[(name, fs)], X_test)
            rows.append(
                {"task": "binary", "model": name, "features": fs, "n_features": len(cols)}
                | {"eval_rows": len(flagged)}
                | score(binary.y_test, np.where(flagged, "Attack", NORMAL))
                | {
                    "far_attack_ttl_normals": _rate(flagged[normal & host]),
                    "far_other_normals": _rate(flagged[normal & ~host]),
                }
            )
    for fs, cols in sets.items():
        model, classes = fit("XGBoost", multi.X_train[cols], multi.y_train)
        pred = classes[model.predict_proba(multi.X_test[cols]).argmax(1)]
        rows.append(
            {"task": "multiclass", "model": "XGBoost", "features": fs, "n_features": len(cols)}
            | {"eval_rows": len(pred)}
            | score(multi.y_test, pred)
        )
        recalls[fs] = per_class_recall(multi.y_test, pred)
    pd.DataFrame(recalls).rename_axis("class").to_csv(out / "recall_ttl_free.csv", float_format="%.4f")
    return fitted, rows


def _rewrites(fitted: dict, binary: Split, train: pd.DataFrame, rule, types: np.ndarray) -> list[dict]:
    """Detection after rewriting the source TTL of every attack flow to each normal TTL from the rule."""
    X_test, rows = binary.X_test.astype(float), []
    attack, normals = types != NORMAL, train.loc[train["label"] == 0, "sttl"]
    for (name, fs), model in fitted.items():
        clean = _flagged(model, X_test)
        for value in rewrite_values(train):
            flagged = _flagged(model, rewrite(X_test, attack, value, rule))
            assert np.array_equal(flagged[~attack], clean[~attack])  # normal flows are untouched
            rows.append(
                {"model": name, "features": fs, "ttl": value, "attack_rows": int(attack.sum())}
                | {
                    "train_normal_share": float((normals == value).mean()),
                    "clean_detection": _rate(clean[attack]),
                }
                | {"detection": _rate(flagged[attack])}
                | {f"det_{t}": _rate(flagged[types == t]) for t in sorted(set(types[attack]))}
            )
    return rows


def _sweep(fitted: dict, binary: Split, attack: np.ndarray, rule) -> list[dict]:
    """Detection of the all-feature binary models for every possible source TTL, 0-255, on attack flows."""
    X, rows = binary.X_test.astype(float)[attack], []
    every = np.ones(len(X), bool)
    for name in BINARY_MODELS:
        for value in range(256):
            flagged = _flagged(fitted[(name, "all")], rewrite(X, every, value, rule))
            rows.append({"model": name, "ttl": value, "detection": _rate(flagged)})
    return rows


def _forgery(fitted: dict, binary: Split, attack: np.ndarray, rule) -> list[dict]:
    """Set one feature of every attack flow to a typical normal value; for XGBoost, also worst + one more."""
    fills = forgery_fills(binary.X_train.astype(float), binary.y_train)
    X_attack, rows = binary.X_test.astype(float)[attack], []

    def detection(model: tuple, forged: list[str]) -> float:
        return _rate(_flagged(model, forge(X_attack, fills, forged, rule)))

    for (name, fs), model in fitted.items():
        single = {f: detection(model, [f]) for f in model[2]}
        rows += [
            {"model": name, "features": fs, "forged": f, "n_forged": 1, "detection": d}
            for f, d in single.items()
        ]
        if name == "XGBoost":
            worst = min(single, key=single.get)
            rows += [
                {"model": name, "features": fs, "forged": f"{worst}+{f}", "n_forged": 2}
                | {"detection": detection(model, [worst, f])}
                for f in model[2]
                if f != worst
            ]
    return rows


def _attribution(fitted: dict, binary: Split, train: pd.DataFrame, sets: dict, rule) -> dict:
    """Why the all-feature XGBoost raises false alarms, and whether 39 features still see the TTL group."""
    model, classes, cols = fitted[("XGBoost", "all")]
    X_test, hosts = binary.X_test.astype(float), attack_ttls(train)
    false_alarm = (binary.y_test.to_numpy() == NORMAL) & _flagged(fitted[("XGBoost", "all")], X_test)
    out = {"false_alarms": int(false_alarm.sum()), "attack_ttls": " ".join(map(str, hosts))}
    keys = ("fa_top_feature_sttl_share", "fa_attack_ttl_share", "no_ttl_recovers_attack_ttl_auc")
    out |= dict.fromkeys(keys, float("nan"))  # same columns on every run, NaN where undefined
    if rule is not None:  # how often the learned rule gives the test file's own ct_state_ttl
        derived = rule.predict(X_test[DERIVED_FROM])
        out["ct_rule_test_match"] = float(np.mean(derived == X_test["ct_state_ttl"]))
    if false_alarm.any():
        contribs = model.get_booster().predict(xgb.DMatrix(X_test.loc[false_alarm, cols]), pred_contribs=True)
        top = top_pro_attack(contribs, cols, int(np.searchsorted(classes, "Attack")))
        out |= {"fa_top_feature_sttl_share": float(np.mean(top == "sttl"))}
        out |= {"fa_attack_ttl_share": float(X_test.loc[false_alarm, "sttl"].isin(hosts).mean())}
    host_train, host_test = binary.X_train["sttl"].isin(hosts), binary.X_test["sttl"].isin(hosts)
    if host_train.nunique() == 2 and host_test.nunique() == 2:
        proxy = HistGradientBoostingClassifier(random_state=SEED).fit(
            binary.X_train[sets["no_ttl"]], host_train
        )
        guess = proxy.predict_proba(binary.X_test[sets["no_ttl"]])[:, 1]
        out["no_ttl_recovers_attack_ttl_auc"] = float(roc_auc_score(host_test, guess))
    return out


def evasion(train: pd.DataFrame, test: pd.DataFrame, out: Path) -> dict[str, list[dict]]:
    """TTL rewrite, the 0-255 sweep, the forgery test, attribution and the TTL-free detector."""
    binary, multi = make_split(train, test, "binary"), make_split(train, test, "multiclass")
    sets, rule = feature_sets(binary.X_train.columns), ct_rule(binary.X_train.astype(float))
    attack = binary.y_test.to_numpy() != NORMAL
    fitted, ttl_free = _clean(binary, multi, sets, attack_ttls(train), out)
    sweep = _sweep(fitted, binary, attack, rule)
    marks = {v: "normal TTL" for v in rewrite_values(train)} | {v: "attack TTL" for v in attack_ttls(train)}
    ttl_sweep_chart(pd.DataFrame(sweep), marks, out / "ttl_sweep.png")
    return {
        "ttl_free": ttl_free,
        "evasion": _rewrites(fitted, binary, train, rule, target(test, "multiclass").to_numpy()),
        "ttl_sweep": sweep,
        "substitution": _forgery(fitted, binary, attack, rule),
        "ttl_attribution": [_attribution(fitted, binary, train, sets, rule)],
    }
