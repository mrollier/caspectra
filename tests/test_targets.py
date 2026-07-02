"""Tests for data/targets.py and data/splits.py (Lever A plumbing)."""

from __future__ import annotations

import numpy as np
import pytest

from caspectra.data.splits import leave_rules_out_split
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets


def test_targets_shape_and_cache_roundtrip(tmp_path) -> None:
    rules = [0, 30, 204]
    first = load_or_compute_invariant_targets(
        rules, width=31, n_pairs=4, seed=0, cache_dir=tmp_path
    )
    assert first.shape == (3, len(TARGET_NAMES))
    # Second call must hit the cache and reproduce the values exactly.
    files = list(tmp_path.glob("targets_*.npz"))
    assert len(files) == 1
    second = load_or_compute_invariant_targets(
        rules, width=31, n_pairs=4, seed=0, cache_dir=tmp_path
    )
    assert np.array_equal(first, second)
    assert len(list(tmp_path.glob("targets_*.npz"))) == 1


def test_targets_rows_follow_requested_order(tmp_path) -> None:
    a = load_or_compute_invariant_targets([0, 30], width=31, n_pairs=4, cache_dir=tmp_path)
    b = load_or_compute_invariant_targets([30, 0], width=31, n_pairs=4, cache_dir=tmp_path)
    assert np.array_equal(a[0], b[1])
    assert np.array_equal(a[1], b[0])


def test_targets_protocol_changes_cache_key(tmp_path) -> None:
    load_or_compute_invariant_targets([30], width=31, n_pairs=4, cache_dir=tmp_path)
    load_or_compute_invariant_targets(
        [30], width=31, n_pairs=4, ic_density=0.25, cache_dir=tmp_path
    )
    assert len(list(tmp_path.glob("targets_*.npz"))) == 2


# ---------------------------------------------------------------------------
# Leave-rules-out split
# ---------------------------------------------------------------------------

RULES = [0, 8, 18, 22, 30, 54, 90, 110, 178, 204]
CLASSES = [1, 1, 3, 3, 3, 4, 3, 4, 2, 2]


def test_split_is_disjoint_and_covers_all() -> None:
    train, holdout = leave_rules_out_split(RULES, CLASSES, holdout_fraction=0.3, seed=0)
    assert set(train) | set(holdout) == set(RULES)
    assert set(train) & set(holdout) == set()


def test_split_respects_forced_rules() -> None:
    train, holdout = leave_rules_out_split(
        RULES, CLASSES, force_holdout=(110,), force_train=(54,), seed=0
    )
    assert 110 in holdout
    assert 54 in train


def test_split_every_class_represented_in_holdout() -> None:
    _, holdout = leave_rules_out_split(RULES, CLASSES, holdout_fraction=0.2, seed=0)
    holdout_classes = {c for r, c in zip(RULES, CLASSES) if r in holdout}
    assert holdout_classes == {1, 2, 3, 4}


def test_split_rejects_contradictory_forcing() -> None:
    with pytest.raises(ValueError):
        leave_rules_out_split(RULES, CLASSES, force_holdout=(54,), force_train=(54,))
    with pytest.raises(ValueError):
        leave_rules_out_split(RULES, CLASSES, force_holdout=(99,))
