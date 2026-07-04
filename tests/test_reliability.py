"""Tests for the reliability benchmarks (rev-8 C2).

The second referee's central technical point: the independent-replicate agreement
of an estimator that returns a *fresh* Monte-Carlo draw is ``2*ICC - 1``, not the
ICC ceiling. These tests pin that relationship on synthetic replicates with a
known ICC, so the manuscript's corrected benchmark cannot silently regress.
"""

from __future__ import annotations

import numpy as np
import pytest

from caspectra.eval.dynamics import DYNAMICS_FEATURE_NAMES
from caspectra.eval.reliability import (
    _icc_from_matrix,
    _mean_pairwise_agreement,
    reliability_benchmarks,
)


def _synthetic(target_icc: float, *, K: int = 20, N: int = 600, seed: int = 0) -> np.ndarray:
    """``(K, N)`` replicates with signal var 1 and noise var set for ``target_icc``."""
    rng = np.random.default_rng(seed)
    sigma_e = np.sqrt((1.0 - target_icc) / target_icc)  # sigma_a = 1
    theta = rng.normal(0.0, 1.0, size=(1, N))
    return theta + rng.normal(0.0, sigma_e, size=(K, N))


@pytest.mark.parametrize("target_icc", [0.994, 0.90, 0.80, 0.60])
def test_agreement_is_two_icc_minus_one(target_icc: float) -> None:
    x = _synthetic(target_icc)
    icc = _icc_from_matrix(x)
    agreement = _mean_pairwise_agreement(x)
    # ICC recovered to a few percent...
    assert abs(icc - target_icc) < 0.03
    # ...and the independent-replicate agreement tracks 2*ICC-1, NOT ICC.
    assert abs(agreement - (2.0 * icc - 1.0)) < 0.02
    if target_icc < 0.99:  # the two benchmarks are meaningfully different here
        assert agreement < icc - 0.05


def test_agreement_below_icc_for_noisy_target() -> None:
    """A noisy target (survival-like) has agreement well below its ICC ceiling."""
    x = _synthetic(0.80)
    bench = reliability_benchmarks(np.stack([x] * len(DYNAMICS_FEATURE_NAMES), axis=-1), n_boot=200)
    v = bench[DYNAMICS_FEATURE_NAMES[0]]
    assert v["agreement_r2"] < v["icc"]
    assert v["icc_ci"][0] <= v["icc"] <= v["icc_ci"][1]
    assert v["agreement_ci"][0] <= v["agreement_r2"] <= v["agreement_ci"][1]


def test_perfect_reliability_gives_agreement_one() -> None:
    """Noise-free replicates: ICC = 1 and agreement = 1 (they coincide only here)."""
    rng = np.random.default_rng(1)
    theta = rng.normal(size=(1, 300))
    x = np.repeat(theta, 12, axis=0)
    assert _icc_from_matrix(x) == pytest.approx(1.0, abs=1e-6)
    assert _mean_pairwise_agreement(x) == pytest.approx(1.0, abs=1e-6)
