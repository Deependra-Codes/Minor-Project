import pandas as pd
import pytest

from ids.data import TEST_FILE, TRAIN_FILE, make_split, read_partition


def test_split_drops_id_and_targets(data_dir):
    split = make_split(*read_partition(data_dir), "multiclass")
    assert list(split.X_train.columns) == [
        "dur",
        "sbytes",
        "sttl",
        "proto",
        "service",
        "state",
        "dttl",
        "ct_state_ttl",
    ]
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


def test_byte_order_mark_does_not_hide_the_id_column(data_dir):
    # some mirrors of the official files start with a UTF-8 BOM, which renames "id" to "﻿id"
    for name in (TRAIN_FILE, TEST_FILE):
        text = (data_dir / name).read_text()
        (data_dir / name).write_text("﻿" + text, encoding="utf-8")
    split = make_split(*read_partition(data_dir), "binary")
    assert not any("id" in c for c in split.X_train.columns)
