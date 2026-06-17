"""Tests for caspectra/utils.py (BUILD_BRIEF.md §1)."""

from __future__ import annotations

import numpy as np
import torch

from caspectra.utils import select_device, set_seed


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
