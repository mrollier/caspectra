"""Tests for the mechanistic rule-inference estimator (R4)."""

from __future__ import annotations

import numpy as np
import pytest

from caspectra.ca.eca import ECASimulator, independent_rules
from caspectra.ca.range_ca import RangeCA, embed_eca, sample_rules
from caspectra.eval.dynamics import damage_spreading_features
from caspectra.eval.rule_inference import (
    complete_table,
    infer_rule,
    infer_rule_table,
    mechanistic_estimate,
    mechanistic_estimate_posterior,
    neighbourhood_indices,
    table_to_rule,
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


def test_completion_policies_agree_on_full_coverage_diverge_otherwise():
    """Completions are identical when the table is fully covered (rev-8 C3).

    On a fully-exercised diagram every policy fills nothing, so all give the exact
    generating rule; on an under-covered diagram the fills differ.
    """
    rng = np.random.default_rng(5)
    ic = rng.integers(0, 2, size=127, dtype=np.uint8)
    full = ECASimulator(30).evolve(ic, 63)  # rule 30 exercises all 8 entries
    table, observed, _ = infer_rule_table(full, radius=1)
    assert observed.all()
    assert {
        table_to_rule(complete_table(table, observed, p)) for p in ("zero", "one", "empirical")
    } == {30}

    # An under-covered diagram: a lone seed under rule 0 leaves most entries unseen.
    sparse = np.zeros((30, 63), dtype=np.uint8)
    sparse[0, 3] = 1
    t2, obs2, _ = infer_rule_table(sparse, radius=1)
    assert not obs2.all()
    r_zero = table_to_rule(complete_table(t2, obs2, "zero"))
    r_one = table_to_rule(complete_table(t2, obs2, "one"))
    assert r_zero != r_one  # the fill of unobserved entries changes the rule


def test_posterior_estimate_zero_spread_when_fully_covered():
    """A fully-covered table has no unobserved entries -> zero predictive spread."""
    ic = np.random.default_rng(6).integers(0, 2, size=127, dtype=np.uint8)
    diagram = ECASimulator(110).evolve(ic, 63)
    mean, std, _, coverage, k = mechanistic_estimate_posterior(
        diagram, radius=1, width=127, n_pairs=32, rng=np.random.default_rng(0)
    )
    assert k == 0
    assert coverage == pytest.approx(1.0)
    assert np.allclose(std, 0.0)
    assert mean.shape == (4,)


def test_posterior_estimate_has_spread_when_under_covered():
    """An under-covered table yields a non-trivial predictive interval."""
    sparse = np.zeros((40, 63), dtype=np.uint8)
    sparse[0, 3] = 1
    sparse[0, 30] = 1  # a couple of seeds so a few entries are observed, most not
    mean, std, _, coverage, k = mechanistic_estimate_posterior(
        sparse, radius=1, width=63, n_pairs=32, rng=np.random.default_rng(1)
    )
    assert k > 0
    assert coverage < 1.0
    assert std.shape == (4,) and np.all(std >= 0.0)
