import pandas as pd
import pytest

from ids.data import TRAIN_FILE, make_split, read_partition


def test_split_drops_id_and_targets(data_dir):
    split = make_split(*read_partition(data_dir), "multiclass")
    assert list(split.X_train.columns) == ["dur", "sbytes", "sttl", "proto", "service", "state"]
    assert set(split.y_train) == {"Normal", "Exploits", "Worms"}


def test_binary_target_is_normal_vs_attack(data_dir):
    split = make_split(*read_partition(data_dir), "binary")
    assert set(split.y_test) == {"Normal", "Attack"}


def test_unseen_test_category_encodes_to_minus_one(data_dir):
    split = make_split(*read_partition(data_dir), "binary")
    assert split.X_test.loc[0, "proto"] == -1
    assert (split.X_train["proto"] >= 0).all()


def test_missing_column_is_rejected(data_dir):
    pd.read_csv(data_dir / TRAIN_FILE).drop(columns="attack_cat").to_csv(data_dir / TRAIN_FILE, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        read_partition(data_dir)
