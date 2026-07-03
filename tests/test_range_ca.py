"""Tests for ca/range_ca.py — the M4 range-r binary CA and its symmetry group."""

from __future__ import annotations

import numpy as np
import pytest

from caspectra.ca.eca import ECASimulator
from caspectra.ca.eca import complement as eca_complement
from caspectra.ca.eca import reflect as eca_reflect
from caspectra.ca.range_ca import (
    RangeCA,
    canonical,
    complement,
    embed_eca,
    n_rules,
    orbit,
    reflect,
    sample_rules,
    table_size,
)


def _brute_step(rule: int, radius: int, row: np.ndarray) -> np.ndarray:
    """Reference update: per-cell Python loop, leftmost neighbour = MSB."""
    width = row.size
    out = np.empty(width, dtype=np.uint8)
    for i in range(width):
        index = 0
        for k, offset in enumerate(range(-radius, radius + 1)):
            index |= int(row[(i + offset) % width]) << (2 * radius - k)
        out[i] = (rule >> index) & 1
    return out


def test_range1_matches_eca_bitforbit() -> None:
    """RangeCA(rule, 1) must equal ECASimulator(rule) exactly."""
    rng = np.random.default_rng(0)
    for rule in (0, 30, 90, 110, 184, 204):
        ic = rng.integers(0, 2, size=61, dtype=np.uint8)
        a = ECASimulator(rule).evolve(ic, 40)
        b = RangeCA(rule, 1).evolve(ic, 40)
        np.testing.assert_array_equal(a, b)


def test_range2_step_matches_brute_force() -> None:
    rng = np.random.default_rng(1)
    for _ in range(20):
        rule = int(rng.integers(0, n_rules(2)))
        row = rng.integers(0, 2, size=37, dtype=np.uint8)
        got = RangeCA(rule, 2).step(row)
        want = _brute_step(rule, 2, row)
        np.testing.assert_array_equal(got, want)


def test_table_and_space_sizes() -> None:
    assert table_size(1) == 8 and n_rules(1) == 256
    assert table_size(2) == 32 and n_rules(2) == 2**32


def test_symmetry_generalizes_eca() -> None:
    """reflect/complement at radius 1 reproduce the ECA definitions."""
    for rule in (0, 18, 30, 54, 110, 150):
        assert reflect(rule, 1) == eca_reflect(rule)
        assert complement(rule, 1) == eca_complement(rule)


def test_symmetry_involutions_and_orbit_size() -> None:
    rng = np.random.default_rng(2)
    for _ in range(50):
        rule = int(rng.integers(0, n_rules(2)))
        assert reflect(reflect(rule, 2), 2) == rule
        assert complement(complement(rule, 2), 2) == rule
        o = orbit(rule, 2)
        assert 1 <= len(o) <= 4
        assert canonical(rule, 2) == min(o)
        # Reflection and complement map the orbit onto itself.
        assert reflect(rule, 2) in o and complement(rule, 2) in o


def test_embed_eca_reproduces_eca_dynamics() -> None:
    """An embedded ECA rule ignores the outer neighbours -> identical diagrams.

    This is the M4 continuity control in simulator form: range-2 must contain
    the ECAs as an exact sub-family.
    """
    rng = np.random.default_rng(3)
    for eca_rule in (0, 30, 54, 90, 110, 204):
        embedded = embed_eca(eca_rule, radius=2)
        ic = rng.integers(0, 2, size=63, dtype=np.uint8)
        a = ECASimulator(eca_rule).evolve(ic, 50)
        b = RangeCA(embedded, 2).evolve(ic, 50)
        np.testing.assert_array_equal(a, b)


def test_sample_rules_returns_distinct_canonical_reps() -> None:
    rng = np.random.default_rng(4)
    rules = sample_rules(200, 2, rng)
    assert len(rules) == 200
    assert len(set(rules)) == 200
    # Every returned rule is its own orbit representative, so no two are
    # reflection/complement partners.
    assert all(canonical(r, 2) == r for r in rules)


def test_validation_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        RangeCA(n_rules(2), 2)  # one past the top
    with pytest.raises(ValueError):
        RangeCA(-1, 2)
    with pytest.raises(ValueError):
        embed_eca(256)
