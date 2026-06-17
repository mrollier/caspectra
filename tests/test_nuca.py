"""Tests for ca/nuca.py — the non-uniform CA interface stub (BUILD_BRIEF.md §3.9)."""

from __future__ import annotations

import numpy as np
import pytest

from caspectra.ca.nuca import NonUniformCA


def test_nuca_is_constructible_with_a_rule_mask() -> None:
    mask = np.array([0, 1, 0, 1], dtype=np.uint8)
    nuca = NonUniformCA(rule_a=110, rule_b=54, rule_mask=mask)
    assert nuca.rule_a == 110
    assert nuca.rule_b == 54


def test_nuca_evolve_is_not_implemented() -> None:
    nuca = NonUniformCA(rule_a=110, rule_b=54, rule_mask=np.zeros(4, dtype=np.uint8))
    with pytest.raises(NotImplementedError):
        nuca.evolve(np.zeros(4, dtype=np.uint8), n_steps=4)


def test_nuca_random_diagram_is_not_implemented() -> None:
    nuca = NonUniformCA(rule_a=110, rule_b=54, rule_mask=np.zeros(4, dtype=np.uint8))
    with pytest.raises(NotImplementedError):
        nuca.random_diagram(width=4, n_steps=4, rng=np.random.default_rng(0))
