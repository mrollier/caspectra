"""Tests for eval/salience.py (EVALUATION_CRITERIA.md diagnostics)."""

from __future__ import annotations

import numpy as np

from caspectra.eval.salience import (
    density_invariance_r2,
    excess_genotype_fraction,
    participation_ratio,
    per_class_cluster_recall,
    regress_out,
)


def test_regress_out_removes_linear_covariate() -> None:
    rng = np.random.default_rng(0)
    cov = rng.uniform(size=200)
    signal = rng.normal(size=(200, 8))
    emb = signal + 5.0 * cov[:, None]  # covariate injected into every dim
    residual = regress_out(emb, cov)
    # After removal the covariate is no longer linearly recoverable...
    corr = np.corrcoef(residual.T, cov)[-1, :-1]
    assert np.abs(corr).max() < 0.05
    # ...but the independent signal survives.
    corr_sig = np.corrcoef(residual[:, 0], signal[:, 0])[0, 1]
    assert corr_sig > 0.9


def test_participation_ratio_high_for_isotropic() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=(4000, 16))
    # Isotropic gaussian on the sphere spreads variance over all 16 dims.
    assert participation_ratio(x) > 12.0


def test_participation_ratio_one_for_rank_one_and_constant() -> None:
    rng = np.random.default_rng(0)
    direction = rng.normal(size=16)
    x = rng.normal(size=(500, 1)) * direction  # rank-1: all points on one line
    assert participation_ratio(x) < 1.5
    assert participation_ratio(np.ones((100, 16))) == 1.0


def test_per_class_cluster_recall_perfect_and_noise() -> None:
    classes = np.array([0] * 10 + [1] * 10)
    # Clusters exactly = classes -> recall 1 for both.
    recall = per_class_cluster_recall(classes.copy(), classes)
    assert recall == {0: 1.0, 1: 1.0}
    # All points HDBSCAN noise -> nothing is recalled.
    recall = per_class_cluster_recall(np.full(20, -1), classes)
    assert recall == {0: 0.0, 1: 0.0}


def test_per_class_cluster_recall_split_class() -> None:
    # Class 1 split across a cluster it owns (6 pts) and one owned by class 0.
    classes = np.array([0] * 10 + [1] * 10)
    clusters = np.array([0] * 10 + [0] * 4 + [1] * 6)
    recall = per_class_cluster_recall(clusters, classes)
    assert recall[0] == 1.0
    assert recall[1] == 0.6


def test_excess_genotype_fraction_extremes() -> None:
    # 4 orbits, 2 behaviour classes of 2 orbits each, 50 diagrams per orbit.
    orbits = np.repeat([0, 1, 2, 3], 50)
    classes = np.repeat([0, 0, 1, 1], 50)
    # Clusters = orbits: clustering resolves all within-class rule info -> ~1.
    fine = excess_genotype_fraction(orbits.copy(), orbits, classes)
    assert fine["excess_genotype_fraction"] > 0.99
    # Clusters = behaviour classes: no rule info beyond the class -> 0.
    coarse = excess_genotype_fraction(classes.copy(), orbits, classes)
    assert coarse["excess_genotype_fraction"] < 0.01


def test_density_invariance_r2_detects_raw_density_coordinate() -> None:
    rng = np.random.default_rng(0)
    n = 400
    density = rng.uniform(0.1, 0.9, size=n)
    images = (rng.uniform(size=(n, 16, 16)) < density[:, None, None]).astype(np.float32)
    noise = rng.normal(size=(n, 8))
    # Embedding that literally carries the raw density as one coordinate.
    emb = np.concatenate([density[:, None], noise], axis=1)
    out = density_invariance_r2(emb, images, seed=0)
    assert out["r2_density_raw"] > 0.9
    # Pure noise embedding decodes neither.
    out_noise = density_invariance_r2(noise, images, seed=0)
    assert out_noise["r2_density_raw"] < 0.2
