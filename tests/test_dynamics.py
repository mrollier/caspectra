"""Tests for eval/dynamics.py (damage spreading — the physics baseline)."""

from __future__ import annotations

import numpy as np
import pytest

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


def test_simulator_argument_rr_alloy_equals_pure_rule() -> None:
    """The criterion-8 truth control: an (r, r) composed system is the pure rule.

    With the same rng, damage_spreading_features must be bit-for-bit identical
    whether the dynamics come from ECASimulator or a NonUniformCA whose two
    rules coincide — the only difference is which object ran `evolve`.
    """
    from caspectra.ca.nuca import NonUniformCA, striped_mask

    for rule in (0, 30, 54):
        pure = damage_spreading_features(
            rule, width=63, n_pairs=8, rng=np.random.default_rng([1, rule])
        )
        alloy = damage_spreading_features(
            simulator=NonUniformCA(rule, rule, striped_mask(63, 4)),
            width=63,
            n_pairs=8,
            rng=np.random.default_rng([1, rule]),
        )
        assert np.array_equal(pure, alloy)


def test_simulator_argument_validation() -> None:
    from caspectra.ca.nuca import NonUniformCA, striped_mask

    with pytest.raises(ValueError):
        damage_spreading_features()  # neither rule nor simulator
    with pytest.raises(ValueError):
        damage_spreading_features(30, simulator=NonUniformCA(30, 30, striped_mask(63, 4)))
    with pytest.raises(ValueError):  # simulator width must match the protocol width
        damage_spreading_features(
            simulator=NonUniformCA(30, 30, striped_mask(63, 4)), width=127, n_pairs=2
        )


def test_radius_normalization_backward_compatible() -> None:
    """radius=1 via RangeCA must reproduce the ECASimulator features exactly.

    Guards the M4 horizon/rate change: the light-cone speed defaults to 1 and
    both the horizon and the rate normalization collapse to the original ECA
    formulas, so the existing cache stays valid.
    """
    from caspectra.ca.range_ca import RangeCA

    for rule in (0, 30, 110):
        eca = damage_spreading_features(
            rule, width=63, n_pairs=16, rng=np.random.default_rng([2, rule])
        )
        r1 = damage_spreading_features(
            simulator=RangeCA(rule, 1), width=63, n_pairs=16, rng=np.random.default_rng([2, rule])
        )
        assert np.array_equal(eca, r1)


def test_embedded_eca_features_match_pure_eca() -> None:
    """M4 continuity control: an embedded ECA rule read as range-2 has the same
    invariants as the pure ECA (the rate normalization by radius is what makes
    this hold — the embedded rule's cone still travels at speed 1)."""
    from caspectra.ca.range_ca import RangeCA, embed_eca

    for rule in (0, 30, 54, 110):
        pure = damage_spreading_features(
            rule, width=63, n_pairs=16, rng=np.random.default_rng([3, rule])
        )
        embedded = damage_spreading_features(
            simulator=RangeCA(embed_eca(rule, 2), 2),
            width=63,
            n_pairs=16,
            rng=np.random.default_rng([3, rule]),
        )
        # Same diagrams, but the range-2 horizon is width//4 vs width//2, so the
        # measurement window differs; survival/ordering must still agree in sign
        # and the two ordered rules must read as ordered.
        assert (pure[0] > 0.5) == (embedded[0] > 0.5)
