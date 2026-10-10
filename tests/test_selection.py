import pytest

from ids.data import make_split, read_partition
from ids.selection import METHODS, rank_features


@pytest.mark.parametrize("method", METHODS)
def test_informative_feature_ranks_first(data_dir, method):
    split = make_split(*read_partition(data_dir), "multiclass")
    ranking = rank_features(split.X_train, split.y_train, method)
    assert ranking[0] == "sttl"
    assert sorted(ranking) == sorted(split.X_train.columns)


def test_unknown_method_is_rejected(data_dir):
    split = make_split(*read_partition(data_dir), "binary")
    with pytest.raises(ValueError, match="unknown method"):
        rank_features(split.X_train, split.y_train, "chi2")
