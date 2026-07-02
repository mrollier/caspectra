"""Tests for eval/nuca_metrics.py — criterion-7 region geometry and metrics."""

from __future__ import annotations

import numpy as np

from caspectra.ca.nuca import half_mask
from caspectra.eval.nuca_metrics import (
    interface_positions,
    ordering_accuracy,
    region_columns,
    region_means,
)


def test_interface_positions_half_mask() -> None:
    # half_mask(127): 0-region on [0, 63), 1-region on [63, 127) -> boundaries
    # at x = 63 and at the wrap (x = 0).
    np.testing.assert_array_equal(sorted(interface_positions(half_mask(127))), [0.0, 63.0])
    # Uniform mask: no interfaces.
    assert interface_positions(np.zeros(16, dtype=np.uint8)).size == 0


def test_region_columns_width127_map7() -> None:
    # Patch centres for a 7-column map on width 127: 9.07, 27.2, 45.4, 63.5,
    # 81.6, 99.8, 117.9. With +-16px exclusion around x=0 and x=63, columns
    # 0 (9.07 from wrap), 3 (0.5 from 63) and 6 (9.1 from wrap) drop out.
    kept, excluded = region_columns(half_mask(127), map_width=7, exclusion_px=16.0)
    np.testing.assert_array_equal(kept[0], [1, 2])
    np.testing.assert_array_equal(kept[1], [4, 5])
    np.testing.assert_array_equal(excluded, [0, 3, 6])


def test_region_columns_width127_map15() -> None:
    # The shallow (3-block) encoder yields a 15-column map: more interior columns
    # survive, and the split stays symmetric between the two regions.
    kept, excluded = region_columns(half_mask(127), map_width=15, exclusion_px=16.0)
    assert len(kept[0]) == len(kept[1]) == 4
    assert set(excluded) == {0, 1, 6, 7, 8, 13, 14}
    centers = (np.array(sorted(np.concatenate([kept[0], kept[1]]))) + 0.5) * 127 / 15
    assert all(min(abs(c - 63), min(c, 127 - c)) > 16 for c in centers)


def test_region_columns_uniform_mask_keeps_everything() -> None:
    kept, excluded = region_columns(np.zeros(127, dtype=np.uint8), map_width=7, exclusion_px=16.0)
    np.testing.assert_array_equal(kept[0], np.arange(7))
    assert 1 not in kept
    assert excluded.size == 0


def test_region_means_exact() -> None:
    # Map (n_targets=2, h=2, m=4): region 0 owns columns {0,1}, region 1 {3}.
    pmap = np.zeros((2, 2, 4))
    pmap[0] = [[1.0, 3.0, 99.0, 5.0], [1.0, 3.0, 99.0, 5.0]]
    pmap[1] = [[0.0, 2.0, 99.0, 8.0], [4.0, 2.0, 99.0, 8.0]]
    means = region_means(pmap, {0: np.array([0, 1]), 1: np.array([3])})
    np.testing.assert_allclose(means[0], [2.0, 2.0])
    np.testing.assert_allclose(means[1], [5.0, 8.0])


def test_ordering_accuracy() -> None:
    true_a = np.array([0.9, 0.9, 0.5, 0.50])
    true_b = np.array([0.1, 0.1, 0.1, 0.49])  # last pair: gap 0.01 -> skipped
    pred_a = np.array([0.8, 0.2, 0.6, 0.0])
    pred_b = np.array([0.2, 0.7, 0.2, 1.0])  # first correct, second wrong, third correct
    acc, n = ordering_accuracy(pred_a, pred_b, true_a, true_b, min_gap=0.02)
    assert n == 3
    assert acc == 2 / 3
    acc_none, n_none = ordering_accuracy(pred_a, pred_b, true_a, true_a, min_gap=0.02)
    assert n_none == 0 and np.isnan(acc_none)
