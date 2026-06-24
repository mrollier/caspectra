"""Tests for caspectra/utils.py (BUILD_BRIEF.md §1)."""

from __future__ import annotations

import warnings

import numpy as np
import pytest
import torch

from caspectra.utils import (
    is_power_of_two,
    select_device,
    set_seed,
    warn_if_pathological_grid,
)


def test_set_seed_makes_torch_reproducible() -> None:
    set_seed(123)
    a = torch.randn(5)
    set_seed(123)
    b = torch.randn(5)
    assert torch.equal(a, b)


def test_set_seed_makes_numpy_reproducible() -> None:
    set_seed(7)
    a = np.random.rand(5)
    set_seed(7)
    b = np.random.rand(5)
    assert np.array_equal(a, b)


def test_select_device_returns_valid_device() -> None:
    device = select_device()
    assert isinstance(device, torch.device)
    assert device.type in {"mps", "cpu", "cuda"}


def test_select_device_can_force_cpu() -> None:
    device = select_device(prefer="cpu")
    assert device.type == "cpu"


# ---------------------------------------------------------------------------
# Power-of-two grid trap (additive rules collapse on a 2^k ring under periodic BCs)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n", [1, 2, 4, 8, 64, 128, 256])
def test_is_power_of_two_true(n: int) -> None:
    assert is_power_of_two(n)


@pytest.mark.parametrize("n", [0, -4, 3, 63, 65, 127, 129])
def test_is_power_of_two_false(n: int) -> None:
    assert not is_power_of_two(n)


@pytest.mark.parametrize("grid", [64, 128])
def test_warns_on_power_of_two_grid(grid: int) -> None:
    with pytest.warns(UserWarning, match="power of two"):
        warn_if_pathological_grid(grid)


@pytest.mark.parametrize("grid", [63, 127])
def test_silent_on_odd_grid(grid: int) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # any warning becomes an error
        warn_if_pathological_grid(grid)  # must not raise
