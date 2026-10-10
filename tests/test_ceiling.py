import itertools

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import f1_score

from ids.ceiling import class_f1_ceilings, group_counts, identifiability, macro_f1_lower


def test_identical_vectors_with_different_labels_cap_accuracy():
    X = pd.DataFrame({"a": [1, 1, 1, 2], "b": [0, 0, 0, 5]})
    y = pd.Series(["DoS", "DoS", "Exploits", "Normal"])
    out = identifiability(X, y)
    assert out["accuracy_ceiling"] == pytest.approx(0.75)  # best constant answer for the 3 twins is DoS
    assert out["conflict_share"] == {"DoS": 1.0, "Exploits": 1.0, "Normal": 0.0}


def test_majority_oracle_is_not_the_macro_f1_ceiling():
    # vector A carries DoS x3 + Analysis x2, vector B carries DoS x5
    X = pd.DataFrame({"a": [0] * 5 + [1] * 5})
    y = pd.Series(["DoS"] * 3 + ["Analysis"] * 2 + ["DoS"] * 5)
    out = identifiability(X, y)
    assert out["accuracy_ceiling"] == pytest.approx(0.8)
    assert out["majority_macro_f1"] == pytest.approx(4 / 9)  # everything answered DoS
    assert out["macro_f1_lower"] == pytest.approx((4 / 7 + 10 / 13) / 2)  # A -> Analysis, B -> DoS
    assert out["macro_f1_upper"] == pytest.approx((4 / 7 + 8 / 9) / 2)
    assert out["f1_ceiling"] == pytest.approx({"Analysis": 4 / 7, "DoS": 8 / 9})
    G, classes, gid = group_counts(X, y)
    value, assign = macro_f1_lower(G)
    assert f1_score(y, classes[assign[gid]], average="macro") == pytest.approx(value)  # a real labelling


def _brute_force(G):
    g, k = G.shape
    assignments = np.array(list(itertools.product(range(k), repeat=g)))
    n, P = G.sum(1), G.sum(0)
    tp, pred = np.zeros((len(assignments), k)), np.zeros((len(assignments), k))
    rows = np.arange(len(assignments))
    for j in range(g):
        np.add.at(tp, (rows, assignments[:, j]), G[j, assignments[:, j]])
        np.add.at(pred, (rows, assignments[:, j]), n[j])
    f1 = 2 * tp / (pred + P)
    return f1.mean(1).max(), f1.max(0)


def test_bracket_contains_the_brute_force_optimum():
    rng = np.random.default_rng(42)
    gaps = []
    for _ in range(300):
        g = int(rng.integers(1, 8))
        G = rng.integers(0, 12, size=(g, 3)) * (rng.random((g, 3)) < 0.6) * rng.choice([1, 1, 5], size=(g, 1))
        for i in np.where(G.sum(1) == 0)[0]:
            G[i, rng.integers(3)] = 1
        for c in np.where(G.sum(0) == 0)[0]:
            G[rng.integers(g), c] += 1
        exact, per_class = _brute_force(G)
        lower, _ = macro_f1_lower(G)
        ceilings = class_f1_ceilings(G)
        assert lower <= exact + 1e-12 <= ceilings.mean() + 2e-12
        assert np.allclose(ceilings, per_class, atol=1e-12)
        gaps.append(exact - lower)
    # the search finds the optimum almost always; without either stage it misses 20 or more of these
    assert sum(g > 1e-9 for g in gaps) <= 10
