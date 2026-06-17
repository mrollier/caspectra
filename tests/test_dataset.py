"""Tests for data/dataset.py (BUILD_BRIEF.md §3.2)."""

from __future__ import annotations

import torch

from caspectra.data.augmentations import AugmentationConfig, TwoViewTransform
from caspectra.data.dataset import SpacetimeDataset


def _small_dataset(tmp_path, transform=None, **kwargs):
    defaults = dict(
        rules=[0, 90, 110],
        n_ic_per_rule=2,
        grid_size=16,
        cache_dir=str(tmp_path),
        seed=7,
        transform=transform,
    )
    defaults.update(kwargs)
    return SpacetimeDataset(**defaults)


def test_length_is_rules_times_ic(tmp_path) -> None:
    ds = _small_dataset(tmp_path)
    assert len(ds) == 3 * 2


def test_single_view_item_shape_and_range(tmp_path) -> None:
    ds = _small_dataset(tmp_path)
    image, metadata = ds[0]
    assert image.shape == (1, 16, 16)
    assert image.dtype == torch.float32
    assert float(image.min()) >= 0.0 and float(image.max()) <= 1.0


def test_metadata_contains_rule_and_equiv_rep(tmp_path) -> None:
    ds = _small_dataset(tmp_path)
    _, metadata = ds[0]
    assert "rule" in metadata
    assert "equiv_class_rep" in metadata
    # Rule 90's reflection/complement class representative is itself (90).
    rules = {ds[i][1]["rule"] for i in range(len(ds))}
    assert rules == {0, 90, 110}


def test_two_view_item_returns_pair(tmp_path) -> None:
    transform = TwoViewTransform(AugmentationConfig())
    ds = _small_dataset(tmp_path, transform=transform)
    item = ds[0]
    assert len(item) == 3  # (view1, view2, metadata)
    v1, v2, metadata = item
    assert v1.shape == (1, 16, 16)
    assert v2.shape == (1, 16, 16)
    assert "rule" in metadata


def test_default_rules_are_the_88_independent(tmp_path) -> None:
    ds = SpacetimeDataset(
        rules=None, n_ic_per_rule=1, grid_size=16, cache_dir=str(tmp_path), seed=1
    )
    assert len(ds) == 88


def test_generation_is_reproducible_with_seed(tmp_path) -> None:
    ds1 = _small_dataset(tmp_path / "a", seed=99)
    ds2 = _small_dataset(tmp_path / "b", seed=99)
    img1, _ = ds1[3]
    img2, _ = ds2[3]
    assert torch.equal(img1, img2)


def test_cache_is_written_and_reused(tmp_path) -> None:
    ds1 = _small_dataset(tmp_path)
    cache_files = list(tmp_path.glob("*.npz"))
    assert len(cache_files) == 1  # cache written on first construction
    # Second construction with identical config loads from cache.
    ds2 = _small_dataset(tmp_path)
    assert ds2.loaded_from_cache is True
    assert torch.equal(ds1[0][0], ds2[0][0])


def test_discard_transient_changes_diagram(tmp_path) -> None:
    base = _small_dataset(tmp_path / "base", discard_transient=0)
    skipped = _small_dataset(tmp_path / "skip", discard_transient=4)
    # Skipping the transient should change the resulting image for rule 110.
    assert not torch.equal(base[4][0], skipped[4][0])
