"""Tests for the annealed / mean-field damage estimator (caspectra.eval.annealed).

Anchors are analytic: rules 0, 90, 128, 170, 204 and 30 have hand-computable
Boolean-derivative profiles, so most assertions are exact. Where the mean-field
approximation *deliberately* diverges from the Monte-Carlo target (rule 204's
frozen defect has MC cone_fill = 1 but mean-field 0), the divergence is
documented in `docs/research_directions_2026-07-07.md` §2 and NOT asserted away.
"""

from __future__ import annotations

import warnings

import numpy as np

from caspectra.ca.eca import ECASimulator
from caspectra.ca.range_ca import RangeCA, embed_eca
from caspectra.eval.annealed import (
    annealed_damage_map,
    annealed_damage_slope,
    annealed_estimate_from_diagram,
    annealed_features,
    annealed_horizon,
    cone_fill_fixed_point,
    damage_map,
    front_speeds,
    mean_boolean_derivative,
    single_bit_sensitivities,
    spreading_rate,
)
from caspectra.eval.dynamics import DYNAMICS_FEATURE_NAMES

SURVIVAL = DYNAMICS_FEATURE_NAMES.index("damage_survival")
FRACTION = DYNAMICS_FEATURE_NAMES.index("damage_fraction")
RATE = DYNAMICS_FEATURE_NAMES.index("spreading_rate")
FILL = DYNAMICS_FEATURE_NAMES.index("cone_fill")


def _table(rule: int, radius: int = 1) -> np.ndarray:
    return ECASimulator(rule).table if radius == 1 else RangeCA(rule, radius).table


def test_horizon_matches_dynamics_effective_steps():
    # dynamics.py evolves n_steps = width // (2*radius) - 1 ROWS (row 0 = IC),
    # so the damage row has had n_steps - 1 rule applications.
    assert annealed_horizon(127, 1) == 61
    assert annealed_horizon(127, 2) == 29
    assert annealed_horizon(63, 1) == 29


def test_null_rule_all_zero():
    d = damage_map(_table(0), 1)
    assert d.shape == (8,)
    assert np.all(d == 0.0)
    feats = annealed_features(_table(0), 1, width=127)
    assert feats.shape == (4,)
    assert np.all(np.isfinite(feats))
    assert np.allclose(feats, 0.0)


def test_single_bit_sensitivities_anchor_rules():
    # Offsets run -radius..+radius left to right.
    assert np.allclose(single_bit_sensitivities(_table(90), 1), [1.0, 0.0, 1.0])
    assert np.allclose(single_bit_sensitivities(_table(204), 1), [0.0, 1.0, 0.0])
    # Rule 170 = "copy right neighbour": only offset +1 is sensitive.
    assert np.allclose(single_bit_sensitivities(_table(170), 1), [0.0, 0.0, 1.0])


def test_slope_is_sum_of_sensitivities():
    for rule in (30, 90, 110, 128, 204):
        p = single_bit_sensitivities(_table(rule), 1)
        slope = annealed_damage_slope(p)
        assert np.isclose(slope, p.sum())
        assert np.isclose(slope, 3.0 * mean_boolean_derivative(p))
    assert np.isclose(annealed_damage_slope(single_bit_sensitivities(_table(204), 1)), 1.0)
    assert np.isclose(annealed_damage_slope(single_bit_sensitivities(_table(90), 1)), 2.0)


def test_rule90_closed_form_map_and_features():
    # Rule 90 = XOR of the outer neighbours: ĝ(y) = P[exactly one outer flip]
    # = 2y(1-y), independent of the centre bit.
    d = damage_map(_table(90), 1)
    for y in (0.0, 0.1, 0.25, 0.5, 0.9, 1.0):
        assert np.isclose(annealed_damage_map(d, 1, y), 2 * y * (1 - y), atol=1e-12)
    assert np.isclose(cone_fill_fixed_point(d, 1, width=127), 0.5, atol=1e-6)
    feats = annealed_features(_table(90), 1, width=127)
    assert feats[SURVIVAL] == 1.0
    # Light-speed cone: extent = 2*T + 1 = 123 cells after T = 61 effective
    # steps, normalised by 2*max_speed*n_steps = 124 (the dynamics.py convention).
    assert np.isclose(feats[RATE], 123.0 / 124.0, atol=0.02)
    assert np.isclose(feats[FILL], 0.5, atol=1e-6)
    assert np.isclose(feats[FRACTION], 0.5 * 123.0 / 127.0, atol=0.02)


def test_rule204_identity_survives_but_never_spreads():
    feats = annealed_features(_table(204), 1, width=127)
    assert feats[SURVIVAL] == 1.0  # deterministic single offspring
    # Frozen defect: extent stays 1, so the protocol-normalised rate is 1/124.
    assert feats[RATE] < 0.01
    # feats[FILL] is deliberately NOT asserted against the MC value (MC gives 1.0
    # for a single frozen cell; the marginal-guarded mean-field gives 0) — this
    # is the pre-declared marginal-rule failure mode.


def test_rule30_survives_and_spreads():
    feats = annealed_features(_table(30), 1, width=127)
    assert feats[SURVIVAL] == 1.0  # p(offset -1) = 1 forces survival
    assert 0.5 < feats[RATE] <= 1.0
    assert feats[FILL] > 0.2


def test_front_speeds_directionality():
    # Rule 170 copies the right neighbour: the defect drifts LEFT at speed 1,
    # so the leftward edge speed is +1 and the rightward edge speed is -1 —
    # net extent growth 0 (a translating single defect).
    v_r, v_l = front_speeds(single_bit_sensitivities(_table(170), 1), 1)
    assert np.isclose(v_l, 1.0, atol=0.01)
    assert np.isclose(v_r, -1.0, atol=0.01)
    # Rule 90 spreads symmetrically at light speed.
    v_r, v_l = front_speeds(single_bit_sensitivities(_table(90), 1), 1)
    assert np.isclose(v_r, 1.0, atol=0.01)
    assert np.isclose(v_l, 1.0, atol=0.01)


def test_ghat_matches_monte_carlo():
    rng = np.random.default_rng(7)
    for radius in (1, 2):
        n_bits = 2 * radius + 1
        size = 1 << n_bits
        for _ in range(3):
            table = rng.integers(0, 2, size=size).astype(np.uint8)
            d = damage_map(table, radius)
            for y in (0.1, 0.3, 0.6):
                n = 200_000
                x = rng.integers(0, size, size=n)
                flips = (rng.random((n, n_bits)) < y).astype(np.int64)
                mask = (flips << np.arange(n_bits)).sum(axis=1)
                mc = float(np.mean(table[x] != table[x ^ mask]))
                assert np.isclose(annealed_damage_map(d, radius, y), mc, atol=0.015)


def test_feature_order_follows_dynamics_names():
    # Rules 90 and 204 both survive, but only 90 spreads: the two features must
    # land in the positions DYNAMICS_FEATURE_NAMES declares.
    f90 = annealed_features(_table(90), 1, width=127)
    f204 = annealed_features(_table(204), 1, width=127)
    assert f90[SURVIVAL] == 1.0 and f204[SURVIVAL] == 1.0
    assert f90[RATE] > 0.9 and f204[RATE] < 0.01


def test_subcritical_rule128_finite_and_silent():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("error")
        feats = annealed_features(_table(128), 1, width=127)
    assert not caught
    assert np.all(np.isfinite(feats))
    # Σp = 3/4 < 1: extinction is near-certain at the 61-step horizon.
    assert feats[SURVIVAL] < 0.05
    assert feats[FILL] == 0.0
    assert feats[FRACTION] == 0.0


def test_from_diagram_matches_true_table_when_fully_observed():
    rng = np.random.default_rng(0)
    ic = rng.integers(0, 2, size=63, dtype=np.uint8)
    diagram = ECASimulator(30).evolve(ic, 64)
    feats, coverage = annealed_estimate_from_diagram(diagram, 1, width=127)
    assert coverage == 1.0
    assert np.allclose(feats, annealed_features(_table(30), 1, width=127))


def test_from_diagram_partial_coverage_is_finite():
    # A near-empty IC under the identity rule exercises only 4 of 8 entries.
    ic = np.zeros(63, dtype=np.uint8)
    ic[31] = 1
    diagram = ECASimulator(204).evolve(ic, 32)
    feats, coverage = annealed_estimate_from_diagram(diagram, 1, width=127)
    assert 0.0 < coverage < 1.0
    assert np.all(np.isfinite(feats))


def test_embedded_rule90_range2():
    table = RangeCA(embed_eca(90, 2), 2).table
    p = single_bit_sensitivities(table, 2)
    assert np.allclose(p, [0.0, 1.0, 0.0, 1.0, 0.0])  # offsets -2..+2
    feats = annealed_features(table, 2, width=127)
    assert feats[SURVIVAL] == 1.0
    # Speed-1 cone inside a radius-2 light cone: extent = 2*29 + 1 = 59 after
    # T = 29 effective steps, normalised by 2*2*30 = 120 — matches dynamics.py.
    assert np.isclose(feats[RATE], 59.0 / 120.0, atol=0.02)
    assert np.isclose(feats[FILL], 0.5, atol=1e-6)


def test_spreading_rate_marginal_guard():
    # Σp <= 1 (rules 204 and 0): edge speeds are guarded to 0 and the extent
    # stays 1 cell, so the protocol-normalised rate is 1/(2*r*n_steps) ≈ 0.008.
    # (spreading_rate is a *conditional-on-survival* estimate; the rule-0 zeroing
    # happens in annealed_features via the survival gate.)
    assert spreading_rate(single_bit_sensitivities(_table(204), 1), 1, width=127) < 0.01
    assert spreading_rate(single_bit_sensitivities(_table(0), 1), 1, width=127) < 0.01
