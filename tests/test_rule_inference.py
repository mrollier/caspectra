"""Tests for the mechanistic rule-inference estimator (R4)."""

from __future__ import annotations

import numpy as np
import pytest

from caspectra.ca.eca import ECASimulator, independent_rules
from caspectra.ca.range_ca import RangeCA, embed_eca, sample_rules
from caspectra.eval.dynamics import damage_spreading_features
from caspectra.eval.rule_inference import (
    infer_rule,
    mechanistic_estimate,
    neighbourhood_indices,
)


def test_neighbourhood_indices_match_rangeca():
    """The inference index scheme must match the forward simulator's exactly."""
    rng = np.random.default_rng(0)
    for radius in (1, 2, 3):
        row = rng.integers(0, 2, size=64, dtype=np.uint8)
        sim = RangeCA(0, radius)  # rule irrelevant; only the index method is used
        expected = sim._neighbourhood_index(row)
        got = neighbourhood_indices(row, radius)
        assert np.array_equal(got, expected)


def test_infer_rule_roundtrips_all_eca_reps():
    """Every one of the 88 ECA representatives is recovered from one diagram."""
    rng = np.random.default_rng(1)
    for rule in independent_rules():
        ic = rng.integers(0, 2, size=127, dtype=np.uint8)
        diagram = ECASimulator(rule).evolve(ic, 63)
        inferred, coverage, consistent = infer_rule(diagram, radius=1)
        assert inferred == rule, f"rule {rule} inferred as {inferred}"
        assert consistent
        assert 0.0 <= coverage <= 1.0


def test_infer_rule_roundtrips_range2_embedded():
    """Embedded ECAs (famous complex rules included) at radius 2.

    Whole-table recovery is only guaranteed when the diagram exercises all 32
    neighbourhoods (coverage 1); the always-true correctness property is that the
    *inferred* rule reproduces the observed diagram exactly, and that it equals
    the generating rule whenever coverage is complete.
    """
    rng = np.random.default_rng(2)
    for eca in (54, 110, 106, 30, 90, 204):
        rule = embed_eca(eca, 2)
        ic = rng.integers(0, 2, size=127, dtype=np.uint8)
        diagram = RangeCA(rule, 2).evolve(ic, 30)
        inferred, coverage, _ = infer_rule(diagram, radius=2)
        # The inferred rule is consistent with every observed transition.
        assert np.array_equal(RangeCA(inferred, 2).evolve(ic, 30), diagram)
        if coverage == 1.0:
            assert inferred == rule


def test_infer_rule_sampled_range2_high_accuracy():
    """On uniformly sampled range-2 rules a single wide diagram is near-perfect."""
    rng = np.random.default_rng(3)
    rules = sample_rules(30, 2, np.random.default_rng(7))
    exact = []
    for rule in rules:
        ic = rng.integers(0, 2, size=127, dtype=np.uint8)
        diagram = RangeCA(rule, 2).evolve(ic, 30)
        inferred, _, _ = infer_rule(diagram, radius=2)
        exact.append(inferred == rule)
    assert np.mean(exact) >= 0.9


def test_infer_rule_all_zero_defaults_to_rule_zero():
    """A diagram that dies to zeros infers rule 0 (unobserved entries default 0)."""
    diagram = np.zeros((30, 63), dtype=np.uint8)
    diagram[0, 3] = 1  # a lone seed that rule-0 immediately kills
    inferred, coverage, _ = infer_rule(diagram, radius=1)
    assert inferred == 0
    assert coverage < 1.0  # not every neighbourhood is exercised


def test_mechanistic_estimate_equals_direct_when_inference_exact():
    """With an identical RNG the estimate equals the direct target bit-for-bit —
    proving the estimator differs from the truth only by MC noise, never by
    inference error, when the rule is fully recovered."""
    rule = 30
    ic = np.random.default_rng(4).integers(0, 2, size=127, dtype=np.uint8)
    diagram = ECASimulator(rule).evolve(ic, 63)

    feats_mech, inferred, coverage = mechanistic_estimate(
        diagram,
        radius=1,
        width=127,
        n_pairs=64,
        rng=np.random.default_rng(123),
    )
    feats_direct = damage_spreading_features(
        rule,
        width=127,
        n_pairs=64,
        rng=np.random.default_rng(123),
    )
    assert inferred == rule
    assert coverage == pytest.approx(1.0)
    assert np.allclose(feats_mech, feats_direct)
