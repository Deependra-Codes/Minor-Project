"""Synthetic UNSW-NB15-shaped data: same column roles, a few hundred rows, one informative feature."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ids.data import TEST_FILE, TRAIN_FILE

CLASSES = ["Normal", "Exploits", "Worms"]


def fake_frame(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cat = rng.choice(CLASSES, size=n, p=[0.6, 0.3, 0.1])
    code = np.array([CLASSES.index(c) for c in cat])
    return pd.DataFrame(
        {
            "id": np.arange(n),
            "dur": rng.random(n),
            "sbytes": rng.integers(0, 5000, n),
            "sttl": code * 60 + rng.integers(0, 5, n),  # informative on purpose
            "proto": rng.choice(["tcp", "udp"], n),
            "service": rng.choice(["-", "http", "dns"], n),
            "state": rng.choice(["FIN", "INT"], n),
            "attack_cat": cat,
            "label": (cat != "Normal").astype(int),
        }
    )


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    fake_frame(300, seed=0).to_csv(tmp_path / TRAIN_FILE, index=False)
    test = fake_frame(150, seed=1)
    test.loc[0, "proto"] = "sctp"  # category never seen in training
    test.to_csv(tmp_path / TEST_FILE, index=False)
    return tmp_path
