import pandas as pd
import pytest

from ids.ceiling import identifiability


def test_identical_vectors_with_different_labels_cap_accuracy():
    X = pd.DataFrame({"a": [1, 1, 1, 2], "b": [0, 0, 0, 5]})
    y = pd.Series(["DoS", "DoS", "Exploits", "Normal"])
    out = identifiability(X, y)
    assert out["accuracy_ceiling"] == pytest.approx(0.75)  # best constant answer for the 3 twins is DoS
    assert out["conflict_share"] == {"DoS": 1.0, "Exploits": 1.0, "Normal": 0.0}
