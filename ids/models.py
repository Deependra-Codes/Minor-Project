"""Classifier factory. The one place to change a model or its hyperparameters.

Every model is fitted on integer class indices through `fit`, which XGBoost requires. XGBoost's thread
count is pinned: its result moves slightly with the number of threads, and a number that changes on
re-run is not a result.
"""

from collections.abc import Callable

import numpy as np
import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

SEED = 42

MODELS: dict[str, Callable[[int], ClassifierMixin]] = {
    "LogReg": lambda seed: make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "DecisionTree": lambda seed: DecisionTreeClassifier(random_state=seed),
    "RandomForest": lambda seed: RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=seed),
    "HistGB": lambda seed: HistGradientBoostingClassifier(random_state=seed),
    "HistGB-balanced": lambda seed: HistGradientBoostingClassifier(
        class_weight="balanced", random_state=seed
    ),
    "XGBoost": lambda seed: XGBClassifier(
        n_estimators=300, max_depth=8, learning_rate=0.1, tree_method="hist", n_jobs=4, random_state=seed
    ),
}


def fit(name: str, X: pd.DataFrame, y: pd.Series, weight: np.ndarray | None = None):
    """Fit MODELS[name] with SEED on integer class indices. Returns the model and the class names."""
    classes = np.unique(y)
    model = MODELS[name](SEED)
    extra = {} if weight is None else {"sample_weight": weight}  # a Pipeline rejects sample_weight=None
    model.fit(X, np.searchsorted(classes, y), **extra)
    return model, classes
