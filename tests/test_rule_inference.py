"""Tests for the mechanistic rule-inference estimator (R4)."""

from __future__ import annotations

import numpy as np
import pytest

from caspectra.ca.eca import ECASimulator, independent_rules
from caspectra.ca.range_ca import RangeCA, embed_eca, sample_rules
from caspectra.eval.dynamics import damage_spreading_features
from caspectra.eval.rule_inference import (
    bayesian_mechanistic_estimate,
    complete_table,
    estimate_noise_rate,
    infer_rule,
    infer_rule_table,
    mechanistic_estimate,
    mechanistic_estimate_posterior,
    neighbourhood_indices,
    noisy_table_posterior,
    table_to_rule,
    transition_counts,
)


def _noisy(diagram: np.ndarray, flip_p: float, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return diagram ^ (rng.random(diagram.shape) < flip_p).astype(np.uint8)


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


def test_noisy_posterior_reduces_to_majority_at_zero_noise():
    """F1 at eps=0 must agree with the deterministic majority inference."""
    ic = np.random.default_rng(7).integers(0, 2, size=127, dtype=np.uint8)
    diagram = ECASimulator(30).evolve(ic, 63)
    ones, total = transition_counts(diagram, radius=1)
    p = noisy_table_posterior(ones, total, eps=0.0)
    assert table_to_rule((p >= 0.5).astype(np.uint8)) == 30
    seen = total > 0
    assert np.all((p[seen] > 0.999) | (p[seen] < 0.001))  # certain where observed


def test_noisy_posterior_recovers_rule_under_noise():
    """With enough observations the MAP table survives 5% bit-flip corruption,
    where the deterministic majority inference is already broken."""
    ic = np.random.default_rng(8).integers(0, 2, size=127, dtype=np.uint8)
    clean = ECASimulator(110).evolve(ic, 63)
    noisy = _noisy(clean, 0.05, seed=1)
    ones, total = transition_counts(noisy, radius=1)
    p = noisy_table_posterior(ones, total, eps=0.05)
    assert table_to_rule((p >= 0.5).astype(np.uint8)) == 110
    # And the posterior is *uncertain* rather than overconfident: no entry that
    # was materially contested should sit at machine-precision certainty.
    contested = (np.minimum(ones, total - ones) / np.maximum(total, 1)) > 0.3
    if contested.any():
        assert np.all((p[contested] > 1e-12) & (p[contested] < 1 - 1e-12))


def test_estimate_noise_rate_tracks_injected_noise():
    """Self-consistency estimation lands near the injected corruption level."""
    ic = np.random.default_rng(9).integers(0, 2, size=127, dtype=np.uint8)
    clean = ECASimulator(90).evolve(ic, 63)
    assert estimate_noise_rate(clean, radius=1) == 0.0
    est = estimate_noise_rate(_noisy(clean, 0.05, seed=2), radius=1)
    # Input-side flips corrupt neighbourhood indices too, so the *effective*
    # rate exceeds the per-cell rate; it must be positive and same-magnitude.
    assert 0.02 <= est <= 0.20


def test_bayesian_estimate_shapes_and_map_rule():
    ic = np.random.default_rng(10).integers(0, 2, size=127, dtype=np.uint8)
    noisy = _noisy(ECASimulator(30).evolve(ic, 63), 0.02, seed=3)
    mean, std, map_rule, p_bits, eps_used = bayesian_mechanistic_estimate(
        noisy,
        radius=1,
        width=63,
        n_pairs=16,
        n_samples=4,
        rng=np.random.default_rng(0),
    )
    assert mean.shape == (4,) and std.shape == (4,)
    assert p_bits.shape == (8,)
    assert 0.0 <= eps_used <= 0.5
    assert map_rule == 30  # 2% noise, 63 rows: posterior still nails rule 30
