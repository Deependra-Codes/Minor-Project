"""The experiments. Each takes the official split, returns rows, and saves its own figures."""

from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import QuantileTransformer

from ids.adapt import em_attack_share, prior_shift, query_uncertain, tune_class_bias
from ids.ceiling import identifiability
from ids.data import NORMAL, Split, Task, make_split, target
from ids.metrics import per_class_f1, per_class_recall, score
from ids.models import MODELS, SEED, fit
from ids.plots import conflict_chart, confusion, recall_gain, selection_curve, zero_day_chart
from ids.selection import METHODS, rank_features

KS = (5, 10, 15, 20, 30)
SELECTION_MODEL = "HistGB"  # fast enough for 36 refits; the ranking, not the model, is under test
FINAL_MODEL = "XGBoost"
ROUNDS, WEIGHT = 5, 20  # analyst feedback: 5 rounds; a labelled flow counts as 20 training flows
EPS = 1e-12


def fit_proba(name: str, X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, weight=None):
    """Returns classes, test probabilities, fit seconds, predict µs per row."""
    start = perf_counter()
    model, classes = fit(name, X_train, y_train, weight)
    fit_s = perf_counter() - start
    start = perf_counter()
    proba = model.predict_proba(X_test)
    return classes, proba, fit_s, (perf_counter() - start) / len(X_test) * 1e6


def evaluate(name: str, split: Split, columns: list[str]) -> tuple[dict, np.ndarray]:
    classes, proba, fit_s, predict_us = fit_proba(
        name, split.X_train[columns], split.y_train, split.X_test[columns]
    )
    pred = classes[proba.argmax(1)]
    row = {"model": name, "n_features": len(columns), **score(split.y_test, pred)}
    return row | {"fit_s": fit_s, "predict_us_per_row": predict_us}, pred


def baselines(split: Split, task: Task, out: Path) -> list[dict]:
    """Every model on all features, plus per-class recall and F1 (F1 is what the ceilings bound)."""
    rows, recalls, f1s = [], {}, {}
    for name in MODELS:
        row, pred = evaluate(name, split, list(split.X_train.columns))
        rows.append({"task": task, "selection": "none"} | row)
        recalls[name], f1s[name] = per_class_recall(split.y_test, pred), per_class_f1(split.y_test, pred)
    for kind, table in (("recall", recalls), ("f1", f1s)):
        pd.DataFrame(table).rename_axis("class").to_csv(
            out / f"per_class_{kind}_{task}.csv", float_format="%.4f"
        )
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
    pd.DataFrame(rankings).rename_axis("rank").to_csv(out / f"ranking_{task}.csv")
    selection_curve(
        pd.DataFrame(rows), out / f"selection_{task}.png", f"{task}: {SELECTION_MODEL} on top-k features"
    )
    return rows


def feedback_loop(split: Split, per_round: int) -> tuple[np.ndarray, np.ndarray, float, list[dict]]:
    """An analyst labels the least certain test flows, the model is refit, ROUNDS times.

    Returns the labelled indices, the final test probabilities, the weighted attack share the final model
    was trained on, and one curve row per round, scored on the flows not labelled so far.
    """
    classes = np.unique(split.y_train)
    labelled = np.array([], dtype=int)
    _, proba, _, _ = fit_proba(FINAL_MODEL, split.X_train, split.y_train, split.X_test)
    curve = [{"labels": 0} | score(split.y_test, classes[proba.argmax(1)])]
    for _ in range(ROUNDS):
        labelled = np.r_[labelled, query_uncertain(proba, per_round, labelled)]
        y = pd.concat([split.y_train, split.y_test.iloc[labelled]])
        weight = np.r_[np.ones(len(split.y_train)), np.full(len(labelled), WEIGHT)]
        X = pd.concat([split.X_train, split.X_test.iloc[labelled]])
        _, proba, _, _ = fit_proba(FINAL_MODEL, X, y, split.X_test, weight)
        rest = np.setdiff1d(np.arange(len(split.y_test)), labelled)
        curve.append(
            {"labels": len(labelled)} | score(split.y_test.iloc[rest], classes[proba[rest].argmax(1)])
        )
    return labelled, proba, float(np.average(y != NORMAL, weights=weight)), curve


def improve(split: Split, task: Task, out: Path, per_round: int) -> tuple[list[dict], list[dict]]:
    """FINAL_MODEL; label-free prior shift and class bias; then analyst feedback. All scored on the same
    test flows: the ones no analyst labelled."""
    classes = np.unique(split.y_train)
    y = np.searchsorted(classes, split.y_train)
    normal = int(np.searchsorted(classes, NORMAL))
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    oof = cross_val_predict(MODELS[FINAL_MODEL](SEED), split.X_train, y, cv=cv, method="predict_proba")
    bias = tune_class_bias(np.log(oof + EPS), y, fixed=normal)
    _, proba, _, _ = fit_proba(FINAL_MODEL, split.X_train, split.y_train, split.X_test)
    labelled, fb_proba, fb_share, curve = feedback_loop(split, per_round)
    rest = np.setdiff1d(np.arange(len(split.y_test)), labelled)

    def shifted(p: np.ndarray, trained_share: float) -> np.ndarray:
        live_share = em_attack_share(1 - p[rest, normal], trained_share)  # unlabelled flows only
        return prior_shift(np.log(p + EPS), normal, trained_share, live_share)

    base, train_share = np.log(proba + EPS), float(np.mean(y != normal))
    variants = {
        "base": base,
        "+prior shift": shifted(proba, train_share),
        "+class bias": base + bias,
        "+prior shift +class bias": shifted(proba, train_share) + bias,
        "+feedback": np.log(fb_proba + EPS),
        "+feedback +prior shift": shifted(fb_proba, fb_share),
        "+feedback +prior shift +class bias": shifted(fb_proba, fb_share) + bias,
    }
    y_rest = split.y_test.iloc[rest]
    preds = {k: classes[v[rest].argmax(1)] for k, v in variants.items()}
    meta = {"task": task, "model": FINAL_MODEL, "labels_used": len(labelled), "eval_rows": len(rest)}
    rows = [meta | {"variant": k} | score(y_rest, pred) for k, pred in preds.items()]
    final = preds["+feedback +prior shift +class bias"]
    recalls = {"base": per_class_recall(y_rest, preds["base"]), "final": per_class_recall(y_rest, final)}
    pd.DataFrame(recalls).rename_axis("class").to_csv(out / f"recall_gain_{task}.csv", float_format="%.4f")
    recall_gain(
        *recalls.values(), out / f"recall_gain_{task}.png", f"{task}: per-class recall, base vs final"
    )
    confusion(y_rest, final, out / f"confusion_{task}.png", f"{task}: final model")
    return rows, [{"task": task} | row for row in curve]


def ceiling(split: Split, task: Task, out: Path) -> dict:
    """Best possible test scores with these features; the multiclass run also plots per-class conflicts."""
    result = identifiability(split.X_test, split.y_test)
    if task == "multiclass":
        conflict_chart(result["conflict_share"], out / "conflict.png")
    flat = {k: v for k, v in result.items() if not isinstance(v, dict)}
    for key, prefix in (("f1_ceiling", "f1_ceiling"), ("conflict_share", "conflict")):
        flat |= {f"{prefix}_{c}": v for c, v in result[key].items()}
    return {"task": task} | flat


def zero_day(train: pd.DataFrame, test: pd.DataFrame, out: Path) -> list[dict]:
    """Leave one attack type out of training; does the binary detector still flag it?"""
    test_cat = target(test, "multiclass").to_numpy()
    full = make_split(train, test, "binary")
    classes, proba, _, _ = fit_proba(SELECTION_MODEL, full.X_train, full.y_train, full.X_test)
    seen = classes[proba.argmax(1)]
    rows = []
    for attack in sorted(set(test_cat) - {NORMAL}):
        held = make_split(train[target(train, "multiclass") != attack], test, "binary")
        classes, proba, _, _ = fit_proba(SELECTION_MODEL, held.X_train, held.y_train, held.X_test)
        unseen, mask = classes[proba.argmax(1)], test_cat == attack
        rows.append(
            {
                "held_out": attack,
                "test_rows": int(mask.sum()),
                "detection_seen": float(np.mean(seen[mask] != NORMAL)),
                "detection_unseen": float(np.mean(unseen[mask] != NORMAL)),
            }
        )
    zero_day_chart(pd.DataFrame(rows), out / "zero_day.png")
    return rows


def diagnose(train: pd.DataFrame, test: pd.DataFrame, out: Path) -> list[dict]:
    """Where binary false alarms come from: the TTL shortcut, and what the training data says about them."""
    ttl = pd.concat(
        [
            df.groupby("sttl")["label"].agg(rows="size", attack_share="mean").assign(split=name)
            for name, df in (("train", train), ("test", test))
        ]
    ).reset_index()
    per_value = ttl.groupby("sttl")["rows"].sum()
    common = per_value[per_value >= 0.01 * per_value.sum()].index  # TTL values covering 1%+ of all flows
    ttl[ttl["sttl"].isin(common)].to_csv(out / "ttl_shift.csv", index=False, float_format="%.4f")

    binary, multi = make_split(train, test, "binary"), make_split(train, test, "multiclass")
    classes, proba, _, _ = fit_proba(FINAL_MODEL, binary.X_train, binary.y_train, binary.X_test)
    normal = binary.y_test.to_numpy() == NORMAL
    flagged = classes[proba.argmax(1)] != NORMAL
    false_alarm, kept = normal & flagged, normal & ~flagged
    classes, proba, _, _ = fit_proba(FINAL_MODEL, multi.X_train, multi.y_train, multi.X_test)
    read_as = pd.Series(classes[proba.argmax(1)][false_alarm]).value_counts(normalize=True)

    scale = QuantileTransformer(n_quantiles=200, random_state=SEED).fit(binary.X_train)
    neighbours = NearestNeighbors(n_neighbors=10).fit(scale.transform(binary.X_train))
    attack = binary.y_train.to_numpy() != NORMAL

    def neighbour_attack_share(mask: np.ndarray) -> float:
        if not mask.any():
            return float("nan")
        idx = neighbours.kneighbors(scale.transform(binary.X_test[mask]), return_distance=False)
        return float(attack[idx].mean())

    return [
        {
            "normal_flows": int(normal.sum()),
            "false_alarms": int(false_alarm.sum()),
            "fa_read_as": read_as.index[0] if len(read_as) else "",
            "fa_read_as_share": float(read_as.iloc[0]) if len(read_as) else float("nan"),
            "fa_train_neighbour_attack_share": neighbour_attack_share(false_alarm),
            "ok_train_neighbour_attack_share": neighbour_attack_share(kept),
        }
    ]
