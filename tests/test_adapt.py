import numpy as np
import pytest
from sklearn.metrics import f1_score

from ids.adapt import em_attack_share, prior_shift, query_uncertain, tune_class_bias


def test_em_recovers_a_shifted_attack_share():
    # posteriors are exact under a 0.6 training prior; the test stream really has 0.3 attacks
    rng = np.random.default_rng(0)
    y = rng.random(20_000) < 0.3
    s = np.where(y, rng.beta(5, 2, y.size), rng.beta(2, 5, y.size))
    ratio = (s / (1 - s)) ** 3  # exact likelihood ratio Beta(5,2) / Beta(2,5)
    p = ratio * 0.6 / (ratio * 0.6 + 0.4)
    assert em_attack_share(p, train_share=0.6) == pytest.approx(0.3, abs=0.03)


def test_prior_shift_is_identity_when_share_unchanged():
    logp = np.log(np.array([[0.7, 0.2, 0.1], [0.2, 0.5, 0.3]]))
    assert np.allclose(prior_shift(logp, normal=0, train_share=0.4, test_share=0.4), logp)


def test_prior_shift_toward_normal_flips_a_borderline_flow():
    logp = np.log(np.array([[0.45, 0.55]]))  # column 0 is Normal
    shifted = prior_shift(logp, normal=0, train_share=0.7, test_share=0.4)
    assert shifted.argmax(1)[0] == 0


def test_bias_tuning_recovers_an_underpredicted_rare_class():
    rng = np.random.default_rng(1)
    y = np.r_[np.zeros(900, int), np.ones(100, int)]
    score_rare = np.where(y == 1, rng.normal(0.8, 1, y.size), rng.normal(-0.8, 1, y.size))
    logp = np.c_[np.zeros(y.size), score_rare - 2.0]  # rare class scored too low on purpose
    before = f1_score(y, logp.argmax(1), average="macro")
    bias = tune_class_bias(logp, y, fixed=0)
    assert bias[0] == 0
    assert f1_score(y, (logp + bias).argmax(1), average="macro") > before + 0.1


def test_query_picks_the_least_certain_unlabelled_flows():
    proba = np.array([[0.9, 0.1], [0.55, 0.45], [0.5, 0.5], [0.3, 0.7], [0.52, 0.48]])
    # margins: 0.8, 0.1, 0.0, 0.4, 0.04 -> flow 2 is already labelled, so take 4 then 1
    assert list(query_uncertain(proba, budget=2, labelled=np.array([2]))) == [4, 1]
