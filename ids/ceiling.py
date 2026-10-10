"""The best any classifier can do on these features.

Rows with identical feature vectors but different labels cannot all be classified correctly, because a
deterministic classifier gives every identical row the same answer. So any classifier is one way of
answering each group of identical rows, and its scores are bounded by the best such answers:

- accuracy: answer every group with its majority label (exact ceiling);
- macro-F1: the majority answer is NOT the best; the ceiling lies between a concrete labelling found by
  search (`macro_f1_lower`) and the mean of the per-class F1 ceilings (`macro_f1_upper`);
- per-class F1 ceilings are each reached on their own, not all at once.

Like any oracle these read the labels they bound; nothing is fitted from them.
"""

import numpy as np
import pandas as pd

GRID = np.unique(np.r_[np.linspace(-8, 8, 65), np.linspace(-1, 1, 41)])  # log-weight steps for _reweight


def group_counts(X: pd.DataFrame, y: pd.Series) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Count matrix G[group, class] over groups of identical vectors, the class names, each row's group."""
    group, _ = pd.factorize(pd.util.hash_pandas_object(X, index=False).to_numpy())
    classes, label = np.unique(y.to_numpy(), return_inverse=True)
    G = np.zeros((group.max() + 1, len(classes)), np.int64)
    np.add.at(G, (group, label), 1)
    return G, classes, group


def group_f1(G: np.ndarray, assign: np.ndarray) -> np.ndarray:
    """Per-class F1 when every row of group g is answered with class assign[g]."""
    k = G.shape[1]
    tp = np.bincount(assign, weights=G[np.arange(len(G)), assign], minlength=k)
    predicted = np.bincount(assign, weights=G.sum(1), minlength=k)
    return 2 * tp / (predicted + G.sum(0))


def class_f1_ceilings(G: np.ndarray) -> np.ndarray:
    """Exact best F1 of each class alone: the best prefix of groups sorted by that class's purity."""
    n, P = G.sum(1), G.sum(0)
    out = np.zeros(G.shape[1])
    for c in range(G.shape[1]):
        has = G[:, c] > 0
        order = np.argsort(-(G[has, c] / n[has]), kind="stable")
        tp, predicted = np.cumsum(G[has, c][order]), np.cumsum(n[has][order])
        out[c] = (2 * tp / (predicted + P[c])).max()
    return out


def _reweight(log_counts: np.ndarray, score, sweeps: int = 8) -> np.ndarray:
    """Coordinate ascent on per-class log-weights w for the rule: answer argmax_c(log n_gc + w_c)."""
    log_w = np.zeros(log_counts.shape[1])
    best = score((log_counts + log_w).argmax(1))
    for _ in range(sweeps):
        improved = False
        for c in range(len(log_w)):
            trials = [score((log_counts + log_w + np.eye(len(log_w))[c] * step).argmax(1)) for step in GRID]
            j = int(np.argmax(trials))
            if trials[j] > best + 1e-12:
                best, improved, log_w[c] = trials[j], True, log_w[c] + GRID[j]
        if not improved:
            break
    return (log_counts + log_w).argmax(1)


def _local_search(Gm: np.ndarray, tp: np.ndarray, predicted: np.ndarray, P: np.ndarray, answer: np.ndarray):
    """Move one mixed group at a time to the class that raises macro-F1 most, until no move helps."""
    n = Gm.sum(1)
    for _ in range(50):
        moved = False
        for i in range(len(Gm)):
            a = answer[i]
            f1 = 2 * tp / (predicted + P)
            leave = 2 * (tp[a] - Gm[i, a]) / (predicted[a] - n[i] + P[a]) - f1[a]
            gain = 2 * (tp + Gm[i]) / (predicted + n[i] + P) - f1 + leave
            gain[a] = 0.0
            b = int(gain.argmax())
            if gain[b] > 1e-12:
                tp[a], predicted[a], tp[b], predicted[b] = (
                    tp[a] - Gm[i, a],
                    predicted[a] - n[i],
                    tp[b] + Gm[i, b],
                    predicted[b] + n[i],
                )
                answer[i], moved = b, True
        if not moved:
            break
    return answer


def macro_f1_lower(G: np.ndarray) -> tuple[float, np.ndarray]:
    """A concrete answer per group with high macro-F1, so a lower bound on the macro-F1 ceiling.

    Pure groups keep their own class (moving one can only lower macro-F1). Mixed groups are answered by
    a reweighted majority, then improved one group at a time.
    """
    k, P = G.shape[1], G.sum(0).astype(float)
    assign = G.argmax(1)
    mixed = (G > 0).sum(1) > 1
    if mixed.any():
        Gm = G[mixed].astype(float)
        pure = ~mixed
        tp0 = np.bincount(assign[pure], weights=G[pure].sum(1), minlength=k).astype(float)

        def totals(answer):
            tp = tp0 + np.bincount(answer, weights=Gm[np.arange(len(Gm)), answer], minlength=k)
            return tp, tp0 + np.bincount(answer, weights=Gm.sum(1), minlength=k)

        def score(answer):
            tp, predicted = totals(answer)
            return float((2 * tp / (predicted + P)).mean())

        answer = _reweight(np.where(Gm > 0, np.log(np.maximum(Gm, 1)), -np.inf), score)
        assign[mixed] = _local_search(Gm, *totals(answer), P, answer)
    return float(group_f1(G, assign).mean()), assign


def identifiability(X: pd.DataFrame, y: pd.Series) -> dict:
    G, classes, _ = group_counts(X, y)
    lower, _ = macro_f1_lower(G)
    ceilings = class_f1_ceilings(G)
    mixed = (G > 0).sum(1) > 1
    return {
        "accuracy_ceiling": float(G.max(1).sum() / G.sum()),
        "majority_macro_f1": float(group_f1(G, G.argmax(1)).mean()),  # what the accuracy oracle gets
        "macro_f1_lower": lower,
        "macro_f1_upper": float(ceilings.mean()),
        "f1_ceiling": {str(c): float(v) for c, v in zip(classes, ceilings, strict=True)},
        "conflict_share": {
            str(c): float(v) for c, v in zip(classes, G[mixed].sum(0) / G.sum(0), strict=True)
        },
    }
