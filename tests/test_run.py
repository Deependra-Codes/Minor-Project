import pandas as pd

from ids.models import MODELS
from ids.run import main
from ids.selection import METHODS


def test_end_to_end_writes_every_output(data_dir, tmp_path):
    out = tmp_path / "results"
    main(["--data", str(data_dir), "--out", str(out)])
    rows = pd.read_csv(out / "results.csv")
    per_task = len(MODELS) + len(METHODS) * 2  # 6 features -> k in (5, 6)
    assert len(rows) == 2 * per_task
    for name in [
        "class_counts.csv",
        "ranking_binary.csv",
        "per_class_recall_multiclass.csv",
        "confusion_multiclass.png",
        "selection_binary.png",
    ]:
        assert (out / name).exists(), name
