"""Tests for eval/baselines.py — hand-crafted feature baselines.

SELF_CRITICISM.md v2 roadmap #4: the learned embedding must be shown to beat
cheap, label-free descriptors, or the deep pipeline is unjustified.
"""

from __future__ import annotations

import numpy as np

from caspectra.ca.eca import ECASimulator
from caspectra.eval.baselines import FEATURE_NAMES, compute_baseline_features


def _diagram(rule: int, w: int = 48, h: int = 48, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return ECASimulator(rule).evolve(rng.integers(0, 2, w, dtype=np.uint8), h)


def test_feature_matrix_shape() -> None:
    imgs = np.stack([_diagram(30), _diagram(90), _diagram(0)])
    feats = compute_baseline_features(imgs)
    assert feats.shape == (3, len(FEATURE_NAMES))


def test_accepts_channel_dim() -> None:
    imgs = np.stack([_diagram(110)])[:, None]  # (1, 1, H, W)
    feats = compute_baseline_features(imgs)
    assert feats.shape == (1, len(FEATURE_NAMES))


def test_null_diagram_has_zero_density_and_activity() -> None:
    # Rule 0 dies to all-zeros after the first row.
    img = _diagram(0)
    feats = compute_baseline_features(img[None])[0]
    density = feats[FEATURE_NAMES.index("mean_density")]
    activity = feats[FEATURE_NAMES.index("temporal_activity")]
    assert density < 0.05
    assert activity < 0.05


def test_chaotic_is_less_compressible_than_fixed_point() -> None:
    chaotic = compute_baseline_features(_diagram(30)[None])[0]
    fixed = compute_baseline_features(_diagram(232)[None])[0]
    ratio = FEATURE_NAMES.index("compression_ratio")
    assert chaotic[ratio] > fixed[ratio]


def test_chaotic_has_higher_block_entropy_than_null() -> None:
    chaotic = compute_baseline_features(_diagram(30)[None])[0]
    null = compute_baseline_features(_diagram(0)[None])[0]
    ent = FEATURE_NAMES.index("block_entropy")
    assert chaotic[ent] > null[ent]
