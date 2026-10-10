"""Load the official UNSW-NB15 train/test partition. Encoders are fit on the training file only."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

TRAIN_FILE = "UNSW_NB15_training-set.csv"
TEST_FILE = "UNSW_NB15_testing-set.csv"
CATEGORICAL = ["proto", "service", "state"]
TARGETS = ["attack_cat", "label"]
DROPPED = ["id"]  # row number, not a traffic feature
NORMAL = "Normal"

Task = Literal["binary", "multiclass"]


@dataclass(frozen=True)
class Split:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series


def read_partition(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(data_dir / TRAIN_FILE)
    test = pd.read_csv(data_dir / TEST_FILE)
    missing = [c for c in CATEGORICAL + TARGETS if c not in train.columns]
    if missing:
        raise ValueError(f"{TRAIN_FILE} is missing columns {missing}")
    if list(train.columns) != list(test.columns):
        raise ValueError("training and testing files have different columns")
    for name, df in (("train", train), ("test", test)):
        if df.isna().any().any():
            raise ValueError(f"{name} has missing values in {list(df.columns[df.isna().any()])}")
    return train, test


def target(df: pd.DataFrame, task: Task) -> pd.Series:
    if task == "binary":
        return pd.Series(np.where(df["label"] == 1, "Attack", NORMAL), index=df.index, name="y")
    return df["attack_cat"].astype(str).str.strip().rename("y")


def make_split(train: pd.DataFrame, test: pd.DataFrame, task: Task) -> Split:
    features = [c for c in train.columns if c not in TARGETS + DROPPED]
    encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    X_train, X_test = train[features].copy(), test[features].copy()
    X_train[CATEGORICAL] = encoder.fit_transform(train[CATEGORICAL].astype(str))
    X_test[CATEGORICAL] = encoder.transform(test[CATEGORICAL].astype(str))
    return Split(X_train, X_test, target(train, task), target(test, task))
