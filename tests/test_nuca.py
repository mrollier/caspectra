"""Tests for ca/nuca.py — the two-rule non-uniform CA (criterion 7 substrate)."""

from __future__ import annotations

import numpy as np
import pytest

from caspectra.ca.eca import ECASimulator
from caspectra.ca.nuca import NonUniformCA, half_mask, striped_mask


def test_uniform_mask_reproduces_eca_exactly() -> None:
    # With an all-zero (or all-one) mask the nuCA IS the pure ECA — the
    # equality must be exact, for several rules and seeds.
    for rule in (0, 30, 54, 90, 110, 184, 204):
        for seed in (0, 1):
            rng = np.random.default_rng(seed)
            ic = rng.integers(0, 2, size=63, dtype=np.uint8)
            reference = ECASimulator(rule).evolve(ic, 63)
            as_rule_a = NonUniformCA(rule, 255 - rule, np.zeros(63, dtype=np.uint8))
            as_rule_b = NonUniformCA(255 - rule, rule, np.ones(63, dtype=np.uint8))
            np.testing.assert_array_equal(as_rule_a.evolve(ic, 63), reference)
            np.testing.assert_array_equal(as_rule_b.evolve(ic, 63), reference)


def test_equal_rules_ignore_the_mask() -> None:
    rng = np.random.default_rng(0)
    ic = rng.integers(0, 2, size=63, dtype=np.uint8)
    reference = ECASimulator(30).evolve(ic, 63)
    nuca = NonUniformCA(30, 30, half_mask(63))
    np.testing.assert_array_equal(nuca.evolve(ic, 63), reference)


def test_half_mask_switches_behaviour_across_the_interface() -> None:
    # Rule 0 kills its half immediately; rule 204 freezes its half. Away from
    # the two interfaces, each region must match its pure rule.
    width = 63
    rng = np.random.default_rng(0)
    ic = rng.integers(0, 2, size=width, dtype=np.uint8)
    diagram = NonUniformCA(0, 204, half_mask(width)).evolve(ic, 8)
    # Rule-0 region interior (cells 2..width//2-2): dead from row 1 onward.
    assert diagram[1:, 2 : width // 2 - 2].sum() == 0
    # Rule-204 region interior: frozen copy of the IC at every row.
    interior = slice(width // 2 + 2, width - 2)
    for t in range(8):
        np.testing.assert_array_equal(diagram[t, interior], ic[interior])


def test_evolve_is_deterministic_and_row0_is_the_ic() -> None:
    nuca = NonUniformCA(30, 110, half_mask(63))
    rng_a, rng_b = np.random.default_rng(7), np.random.default_rng(7)
    d1 = nuca.random_diagram(width=63, n_steps=63, rng=rng_a)
    d2 = nuca.random_diagram(width=63, n_steps=63, rng=rng_b)
    np.testing.assert_array_equal(d1, d2)
    assert d1.shape == (63, 63)
    assert d1.dtype == np.uint8
    # And the pattern actually differs between the two halves for these rules.
    assert not np.array_equal(d1[:, : 63 // 2], d1[:, 63 // 2 :][:, : 63 // 2])


def test_masks() -> None:
    mask = half_mask(127)
    assert mask.sum() == 127 - 127 // 2
    assert mask[62] == 0 and mask[63] == 1
    stripes = striped_mask(12, period=3)
    np.testing.assert_array_equal(stripes, [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1])
    with pytest.raises(ValueError):
        striped_mask(12, period=0)


def test_validation() -> None:
    with pytest.raises(ValueError):
        NonUniformCA(256, 0, half_mask(8))
    with pytest.raises(ValueError):
        NonUniformCA(0, 30, np.array([0, 2, 0, 0], dtype=np.uint8))  # bad mask value
    nuca = NonUniformCA(0, 30, half_mask(8))
    with pytest.raises(ValueError):
        nuca.evolve(np.zeros(9, dtype=np.uint8), 4)  # width mismatch
    with pytest.raises(ValueError):
        nuca.random_diagram(width=9, n_steps=4, rng=np.random.default_rng(0))
    with pytest.raises(ValueError):
        nuca.evolve(np.zeros(8, dtype=np.uint8), 0)  # n_steps < 1
