import numpy as np
import pandas as pd
import pytest

from ids.metrics import per_class_f1, per_class_recall, score


def test_detection_and_false_alarm_rates():
    y_true = pd.Series(["Normal", "Normal", "Normal", "Normal", "DoS", "Worms"])
    y_pred = np.array(["Normal", "Normal", "Normal", "DoS", "Worms", "Normal"])
    s = score(y_true, y_pred)
    assert s["detection_rate"] == pytest.approx(0.5)  # DoS flagged (wrong class still counts), Worms missed
    assert s["false_alarm_rate"] == pytest.approx(0.25)
    assert s["accuracy"] == pytest.approx(0.5)


def test_per_class_recall_exposes_minority_class():
    y_true = pd.Series(["Normal"] * 9 + ["Worms"])
    y_pred = np.array(["Normal"] * 10)
    assert per_class_recall(y_true, y_pred) == {"Normal": 1.0, "Worms": 0.0}
    assert score(y_true, y_pred)["accuracy"] == pytest.approx(0.9)  # high accuracy, missed every worm


def test_per_class_f1_scores_every_true_class():
    y_true = pd.Series(["Normal"] * 3 + ["Worms"])
    y_pred = np.array(["Normal", "Normal", "Worms", "Worms"])
    out = per_class_f1(y_true, y_pred)
    assert out == pytest.approx({"Normal": 0.8, "Worms": 2 / 3})
    never_predicted = per_class_f1(y_true, np.array(["Normal"] * 4))
    assert never_predicted == pytest.approx({"Normal": 6 / 7, "Worms": 0.0})
