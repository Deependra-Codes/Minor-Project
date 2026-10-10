"""Label-free test-time adjustments. Nothing here reads test labels.

The normal/attack mix of live traffic drifts: 31.9% of the training file is normal, 44.9% of the test
file. `em_attack_share` estimates the new attack share from the model's own posteriors (Saerens et al.,
2002) and `prior_shift` re-weights the posteriors to it. `tune_class_bias` picks one additive log-bias
per class on out-of-fold training predictions to maximise macro-F1, so rare attack types are not
drowned by common ones. `query_uncertain` is the one step that needs a person: it picks the flows an
analyst should label, for the feedback loop in experiments.py.
"""

import numpy as np
from sklearn.metrics import f1_score


def em_attack_share(
    p_attack: np.ndarray, train_share: float, tol: float = 1e-9, max_iter: int = 1000
) -> float:
    share = train_share
    for _ in range(max_iter):
        attack = p_attack * share / train_share
        normal = (1 - p_attack) * (1 - share) / (1 - train_share)
        new = float(np.mean(attack / (attack + normal)))
        if abs(new - share) < tol:
            return new
        share = new
    return share


def prior_shift(log_proba: np.ndarray, normal: int, train_share: float, test_share: float) -> np.ndarray:
    """Move posterior mass between Normal and the attack classes; ratios among attacks are untouched."""
    shift = np.full(log_proba.shape[1], np.log(test_share / train_share))
    shift[normal] = np.log((1 - test_share) / (1 - train_share))
    return log_proba + shift


def tune_class_bias(
    log_proba: np.ndarray, y: np.ndarray, fixed: int | None = None, rounds: int = 3
) -> np.ndarray:
    """Coordinate ascent on macro-F1. The `fixed` class (Normal) keeps bias 0; FAR is left to prior_shift."""
    bias = np.zeros(log_proba.shape[1])
    best = f1_score(y, log_proba.argmax(1), average="macro")
    for _ in range(rounds):
        improved = False
        for c in (c for c in range(len(bias)) if c != fixed):
            for value in np.linspace(-3, 3, 25):
                trial = bias.copy()
                trial[c] = value
                f1 = f1_score(y, (log_proba + trial).argmax(1), average="macro")
                if f1 > best + 1e-9:
                    best, bias, improved = f1, trial, True
        if not improved:
            break
    return bias


def query_uncertain(proba: np.ndarray, budget: int, labelled: np.ndarray) -> np.ndarray:
    """The `budget` flows an analyst should label next: smallest gap between the top two probabilities."""
    top2 = np.sort(proba, axis=1)[:, -2:]
    margin = top2[:, 1] - top2[:, 0]
    margin[labelled] = np.inf
    return np.argsort(margin, kind="stable")[:budget]
