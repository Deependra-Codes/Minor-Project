"""Scores for one prediction. Attack-vs-normal rates are computed for both tasks."""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, recall_score

from ids.data import NORMAL


def score(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    is_attack, flagged = np.asarray(y_true) != NORMAL, np.asarray(y_pred) != NORMAL
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "detection_rate": flagged[is_attack].mean() if is_attack.any() else float("nan"),
        "false_alarm_rate": flagged[~is_attack].mean() if (~is_attack).any() else float("nan"),
    }


def per_class_recall(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    labels = sorted(set(y_true))
    return dict(
        zip(labels, recall_score(y_true, y_pred, labels=labels, average=None, zero_division=0), strict=True)
    )
