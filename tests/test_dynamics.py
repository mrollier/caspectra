"""Tests for eval/dynamics.py (damage spreading — the physics baseline)."""

from __future__ import annotations

import numpy as np

from caspectra.eval.dynamics import (
    DYNAMICS_FEATURE_NAMES,
    damage_spreading_features,
    dynamics_feature_matrix,
)

SURVIVAL = DYNAMICS_FEATURE_NAMES.index("damage_survival")
FRACTION = DYNAMICS_FEATURE_NAMES.index("damage_fraction")
RATE = DYNAMICS_FEATURE_NAMES.index("spreading_rate")


def test_damage_dies_for_null_rule() -> None:
    """Rule 0 wipes everything after one step, so the damage cannot survive."""
    f = damage_spreading_features(0, width=63, n_pairs=8)
    assert f[SURVIVAL] == 0.0
    assert f[FRACTION] == 0.0


def test_damage_frozen_for_identity_rule() -> None:
    """Rule 204 repeats the IC forever: the single flipped cell persists, inert."""
    f = damage_spreading_features(204, width=63, n_pairs=8)
    assert f[SURVIVAL] == 1.0
    assert np.isclose(f[FRACTION], 1 / 63)
    assert f[RATE] < 0.05  # extent stays 1 cell: no spreading at all


def test_damage_spreads_ballistically_for_chaotic_rule() -> None:
    """Rule 30 is the canonical chaotic rule: damage should race outward."""
    f = damage_spreading_features(30, width=63, n_pairs=8)
    assert f[SURVIVAL] > 0.9
    assert f[RATE] > 0.5  # a substantial fraction of light speed
    assert f[FRACTION] > 0.1


def test_ic_density_is_part_of_the_protocol() -> None:
    """The features are conditioned on the IC measure (FOUNDATIONS.md §1).

    Rule 184 (traffic) is the canonical density-dependent rule: at low density
    cars free-flow (damage advects, small fraction), near 0.5 jams interact.
    The exact values don't matter here — only that changing the Bernoulli
    parameter measurably changes the feature vector.
    """
    sparse = damage_spreading_features(184, width=63, n_pairs=16, ic_density=0.1)
    dense = damage_spreading_features(184, width=63, n_pairs=16, ic_density=0.5)
    assert not np.allclose(sparse, dense)


def test_feature_matrix_shape_and_order_independence() -> None:
    rules = [0, 30, 204]
    m = dynamics_feature_matrix(rules, width=63, n_pairs=4, seed=0)
    assert m.shape == (3, len(DYNAMICS_FEATURE_NAMES))
    # Each rule gets its own spawned RNG stream, so a row does not depend on
    # which other rules are in the list.
    m2 = dynamics_feature_matrix([0], width=63, n_pairs=4, seed=0)
    assert np.allclose(m[0], m2[0])
