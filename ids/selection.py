"""Rank features on the training split only. Each ranker returns column names, best first."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import f_classif, mutual_info_classif
from sklearn.model_selection import train_test_split

from ids.data import CATEGORICAL

METHODS = ("anova_f", "mutual_info", "rf_importance")


def rank_features(
    X: pd.DataFrame, y: pd.Series, method: str, seed: int = 42, sample: int = 20_000
) -> list[str]:
    if len(X) > sample:  # shortcut: ranks on a stratified sample, pass sample=len(X) for the final report
        X, _, y, _ = train_test_split(X, y, train_size=sample, stratify=y, random_state=seed)
    if method == "anova_f":
        scores = np.nan_to_num(f_classif(X, y)[0])
    elif method == "mutual_info":
        discrete = [c in CATEGORICAL for c in X.columns]
        scores = mutual_info_classif(X, y, discrete_features=discrete, random_state=seed)
    elif method == "rf_importance":
        forest = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=seed).fit(X, y)
        scores = forest.feature_importances_
    else:
        raise ValueError(f"unknown method {method!r}, expected one of {METHODS}")
    return list(X.columns[np.argsort(-scores, kind="stable")])
