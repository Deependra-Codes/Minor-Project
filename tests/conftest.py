"""Synthetic UNSW-NB15-shaped data: same column roles, a few hundred rows, one informative feature."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ids.data import TEST_FILE, TRAIN_FILE
from ids.run import main

CLASSES = ["Normal", "Exploits", "Worms"]


def fake_frame(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cat = rng.choice(CLASSES, size=n, p=[0.6, 0.3, 0.1])
    code = np.array([CLASSES.index(c) for c in cat])
    frame = pd.DataFrame(
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
    frame["dttl"] = rng.choice([0, 29, 252], n)
    frame["ct_state_ttl"] = derive_ct(frame)
    return frame


def derive_ct(frame: pd.DataFrame) -> np.ndarray:
    """ct_state_ttl from state and the TTLs, the way UNSW-NB15 derives it."""
    return np.where((frame["sttl"] >= 60) & (frame["state"] == "INT"), 2, 0)


def write_split(path: Path) -> Path:
    fake_frame(300, seed=0).to_csv(path / TRAIN_FILE, index=False)
    test = fake_frame(150, seed=1)
    test.loc[0, "proto"] = "sctp"  # category never seen in training
    normals = test.index[test["attack_cat"] == "Normal"][:8]
    test.loc[normals, "sttl"] = 62  # normal hosts on an attack TTL: the run must see false alarms
    test["ct_state_ttl"] = derive_ct(test)
    test.to_csv(path / TEST_FILE, index=False)
    return path


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    return write_split(tmp_path)


@pytest.fixture(scope="session")
def results_dir(tmp_path_factory) -> Path:
    """One end-to-end run on the fake split, shared by every test that reads its outputs."""
    data = write_split(tmp_path_factory.mktemp("data"))
    main(["--data", str(data), "--out", str(data / "results"), "--feedback-per-round", "5"])
    return data / "results"
