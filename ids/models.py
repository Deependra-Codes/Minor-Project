"""Classifier factory. The one place to change a model or its hyperparameters.

Every model is fitted on integer class indices (see experiments.fit_proba), which XGBoost requires.
"""

from collections.abc import Callable

from sklearn.base import ClassifierMixin
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

MODELS: dict[str, Callable[[int], ClassifierMixin]] = {
    "LogReg": lambda seed: make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "DecisionTree": lambda seed: DecisionTreeClassifier(random_state=seed),
    "RandomForest": lambda seed: RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=seed),
    "HistGB": lambda seed: HistGradientBoostingClassifier(random_state=seed),
    "HistGB-balanced": lambda seed: HistGradientBoostingClassifier(
        class_weight="balanced", random_state=seed
    ),
    "XGBoost": lambda seed: XGBClassifier(
        n_estimators=300, max_depth=8, learning_rate=0.1, tree_method="hist", n_jobs=-1, random_state=seed
    ),
}
