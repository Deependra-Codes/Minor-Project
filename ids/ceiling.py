"""The best any classifier can do on these features.

Rows with identical feature vectors but different labels cannot all be classified correctly. The
oracle answers each group of identical rows with its majority label; its score is a hard ceiling.
"""

import pandas as pd
from sklearn.metrics import f1_score


def identifiability(X: pd.DataFrame, y: pd.Series) -> dict:
    df = pd.DataFrame({"key": pd.util.hash_pandas_object(X, index=False).to_numpy(), "y": y.to_numpy()})
    counts = df.groupby(["key", "y"]).size().reset_index(name="n")
    majority = counts.sort_values("n", ascending=False, kind="stable").drop_duplicates("key")
    oracle = df["key"].map(majority.set_index("key")["y"])
    conflicted = df.groupby("key")["y"].transform("nunique") > 1
    return {
        "accuracy_ceiling": float((oracle == df["y"]).mean()),
        "macro_f1_ceiling": float(f1_score(df["y"], oracle, average="macro")),
        "conflict_share": {k: float(v) for k, v in conflicted.groupby(df["y"]).mean().items()},
    }
