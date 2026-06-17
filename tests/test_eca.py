"""Tests for ca/eca.py — ECA simulation and symmetry (BUILD_BRIEF.md §4)."""

from __future__ import annotations

import numpy as np
import pytest

from caspectra.ca.eca import (
    ECASimulator,
    complement,
    equivalence_class,
    independent_rules,
    reflect,
)

# ---------------------------------------------------------------------------
# Equivalence classes
# ---------------------------------------------------------------------------


def test_independent_rules_has_exactly_88_classes() -> None:
    """The 256 ECA rules reduce to exactly 88 classes under reflection
    + complementation (BUILD_BRIEF.md §3.1, §4)."""
    reps = independent_rules()
    assert len(reps) == 88


def test_independent_rules_are_canonical_and_unique() -> None:
    """Each rule maps to exactly one representative; reps are distinct and
    cover all 256 rules' classes."""
    reps = independent_rules()
    assert len(set(reps)) == len(reps)  # no duplicates
    # Every rule's class is represented by exactly one rep.
    rep_set = set(reps)
    for rule in range(256):
        cls = equivalence_class(rule)
        assert len(rep_set & cls) == 1


def test_reflect_is_an_involution() -> None:
    for rule in range(256):
        assert reflect(reflect(rule)) == rule


def test_complement_is_an_involution() -> None:
    for rule in range(256):
        assert complement(complement(rule)) == rule


def test_equivalence_class_contains_rule_and_its_images() -> None:
    cls = equivalence_class(110)
    assert 110 in cls
    assert reflect(110) in cls
    assert complement(110) in cls
    assert complement(reflect(110)) in cls
    # Class has at most 4 members (group of order 4).
    assert 1 <= len(cls) <= 4


# ---------------------------------------------------------------------------
# Simulation sanity diagrams
# ---------------------------------------------------------------------------


def test_rule_0_goes_to_all_zeros_after_one_step() -> None:
    sim = ECASimulator(0)
    ic = np.array([1, 0, 1, 1, 0], dtype=np.uint8)
    diagram = sim.evolve(ic, n_steps=4)
    assert diagram.shape == (4, 5)
    assert diagram.dtype == np.uint8
    np.testing.assert_array_equal(diagram[0], ic)  # row 0 = IC
    assert diagram[1:].sum() == 0  # everything below is zero


def test_rule_255_goes_to_all_ones_after_one_step() -> None:
    sim = ECASimulator(255)
    ic = np.array([1, 0, 0, 0], dtype=np.uint8)
    diagram = sim.evolve(ic, n_steps=3)
    np.testing.assert_array_equal(diagram[0], ic)
    np.testing.assert_array_equal(diagram[1:], np.ones((2, 4), dtype=np.uint8))


def test_rule_204_is_identity_copies_ic_down_every_row() -> None:
    sim = ECASimulator(204)
    ic = np.array([0, 1, 1, 0, 1], dtype=np.uint8)
    diagram = sim.evolve(ic, n_steps=6)
    for row in diagram:
        np.testing.assert_array_equal(row, ic)


def test_periodic_boundary_conditions_wrap_on_tiny_width() -> None:
    """Rule 240 sets each cell to its left neighbour: a single 1 marches
    rightward and must wrap around the periodic boundary."""
    sim = ECASimulator(240)
    ic = np.array([1, 0, 0, 0], dtype=np.uint8)
    diagram = sim.evolve(ic, n_steps=5)
    expected = np.array(
        [
            [1, 0, 0, 0],  # IC
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0],  # wrapped back across the boundary
        ],
        dtype=np.uint8,
    )
    np.testing.assert_array_equal(diagram, expected)


def test_evolve_output_is_binary_uint8() -> None:
    sim = ECASimulator(110)
    rng = np.random.default_rng(0)
    diagram = sim.evolve(rng.integers(0, 2, size=16, dtype=np.uint8), n_steps=16)
    assert diagram.dtype == np.uint8
    assert set(np.unique(diagram)).issubset({0, 1})


def test_random_diagram_shape_and_reproducibility() -> None:
    sim = ECASimulator(30)
    d1 = sim.random_diagram(width=20, n_steps=12, rng=np.random.default_rng(42))
    d2 = sim.random_diagram(width=20, n_steps=12, rng=np.random.default_rng(42))
    assert d1.shape == (12, 20)
    np.testing.assert_array_equal(d1, d2)  # same seed => same diagram


def test_invalid_rule_number_rejected() -> None:
    with pytest.raises(ValueError):
        ECASimulator(256)
    with pytest.raises(ValueError):
        ECASimulator(-1)
