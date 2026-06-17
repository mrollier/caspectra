"""Tests for data/augmentations.py (BUILD_BRIEF.md §3.3, §4)."""

from __future__ import annotations

import torch

from caspectra.data.augmentations import (
    AugmentationConfig,
    AugmentationStack,
    CoarseGrain,
    CyclicShift,
    HorizontalFlip,
    Invert,
    TwoViewTransform,
    build_augmentation_stack,
    default_augmentation_stack,
)


def _checker(h: int = 8, w: int = 8) -> torch.Tensor:
    """A reproducible non-trivial (1, h, w) image in [0, 1]."""
    g = torch.Generator().manual_seed(0)
    return (torch.rand(1, h, w, generator=g) > 0.5).float()


# ---------------------------------------------------------------------------
# CyclicShift
# ---------------------------------------------------------------------------


def test_cyclic_shift_preserves_multiset_of_column_sums() -> None:
    """A horizontal roll permutes columns cyclically, so the *multiset* of
    per-column sums is invariant (BUILD_BRIEF.md §4)."""
    torch.manual_seed(123)
    x = _checker()
    shifted = CyclicShift()(x)
    before = torch.sort(x.sum(dim=-2).flatten()).values
    after = torch.sort(shifted.sum(dim=-2).flatten()).values
    assert torch.allclose(before, after)


def test_cyclic_shift_preserves_shape_and_total_mass() -> None:
    x = _checker()
    shifted = CyclicShift()(x)
    assert shifted.shape == x.shape
    assert torch.isclose(shifted.sum(), x.sum())


# ---------------------------------------------------------------------------
# CoarseGrain
# ---------------------------------------------------------------------------


def test_coarse_grain_preserves_tensor_shape() -> None:
    """2x2 average-pool + upsample returns the original shape
    (BUILD_BRIEF.md §3.3, §4)."""
    x = _checker(16, 16)
    out = CoarseGrain()(x)
    assert out.shape == x.shape


def test_coarse_grain_blocks_are_constant() -> None:
    """After coarse-graining, each 2x2 block holds a single (averaged) value."""
    x = _checker(8, 8)
    out = CoarseGrain(kernel=2)(x)
    for i in range(0, 8, 2):
        for j in range(0, 8, 2):
            block = out[0, i : i + 2, j : j + 2]
            assert torch.allclose(block, block.flatten()[0].expand_as(block))


def test_coarse_grain_produces_multilevel_values() -> None:
    """Averaging mixed 2x2 blocks yields intermediate (non-binary) values."""
    x = _checker(16, 16)
    out = CoarseGrain()(x)
    intermediate = (out > 0.0) & (out < 1.0)
    assert intermediate.any()


def test_coarse_grain_p_zero_is_identity() -> None:
    """Stochastic coarse-graining with p=0 leaves the image untouched, so the
    encoder also sees fine detail (fixes the train/eval mismatch)."""
    x = _checker(16, 16)
    assert torch.allclose(CoarseGrain(p=0.0)(x), x)


def test_coarse_grain_p_one_always_applies() -> None:
    x = _checker(8, 8)
    out = CoarseGrain(p=1.0)(x)
    for i in range(0, 8, 2):
        for j in range(0, 8, 2):
            block = out[0, i : i + 2, j : j + 2]
            assert torch.allclose(block, block.flatten()[0].expand_as(block))


def test_default_coarse_grain_is_stochastic() -> None:
    """The default config applies coarse-graining with probability < 1, so some
    training views keep fine detail."""
    assert 0.0 < AugmentationConfig().coarse_grain_prob < 1.0


# ---------------------------------------------------------------------------
# Toggleable (default-OFF) augmentations
# ---------------------------------------------------------------------------


def test_horizontal_flip_mirrors_along_space_axis() -> None:
    x = _checker()
    flipped = HorizontalFlip(p=1.0)(x)
    assert torch.allclose(flipped, torch.flip(x, dims=[-1]))


def test_invert_maps_x_to_one_minus_x() -> None:
    x = _checker()
    inverted = Invert(p=1.0)(x)
    assert torch.allclose(inverted, 1.0 - x)


# ---------------------------------------------------------------------------
# Default stack composition
# ---------------------------------------------------------------------------


def test_default_stack_is_exactly_shift_then_coarse_grain() -> None:
    stack = default_augmentation_stack()
    types = [type(t) for t in stack.transforms]
    assert types == [CyclicShift, CoarseGrain]


def test_excluded_augmentations_not_in_default_stack() -> None:
    """Flip / invert / crop are experimental toggles, OFF by default
    (BUILD_BRIEF.md §3.3)."""
    stack = default_augmentation_stack()
    excluded = {HorizontalFlip, Invert}
    assert not any(type(t) in excluded for t in stack.transforms)


def test_toggles_add_optional_augmentations() -> None:
    cfg = AugmentationConfig(horizontal_flip=True, invert=True)
    stack = build_augmentation_stack(cfg)
    types = {type(t) for t in stack.transforms}
    assert HorizontalFlip in types
    assert Invert in types


# ---------------------------------------------------------------------------
# TwoViewTransform
# ---------------------------------------------------------------------------


def test_two_view_symmetric_returns_two_views_of_same_shape() -> None:
    torch.manual_seed(0)
    x = _checker(16, 16)
    transform = TwoViewTransform(AugmentationConfig())
    v1, v2 = transform(x)
    assert v1.shape == x.shape
    assert v2.shape == x.shape


def test_two_view_asymmetric_always_coarse_grains_view_b() -> None:
    """In asymmetric_coarse mode, view B is always coarse-grained while view A
    is only shifted (BUILD_BRIEF.md §3.3)."""
    torch.manual_seed(0)
    x = _checker(16, 16)
    cfg = AugmentationConfig(mode="asymmetric_coarse")
    transform = TwoViewTransform(cfg)
    _, view_b = transform(x)
    # View B is coarse-grained: each 2x2 block must be constant.
    for i in range(0, 16, 2):
        for j in range(0, 16, 2):
            block = view_b[0, i : i + 2, j : j + 2]
            assert torch.allclose(block, block.flatten()[0].expand_as(block))


def test_augmentation_stack_applies_in_order() -> None:
    stack = AugmentationStack([Invert(p=1.0), Invert(p=1.0)])
    x = _checker()
    # Two inversions cancel out.
    assert torch.allclose(stack(x), x)
