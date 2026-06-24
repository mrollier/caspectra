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


# --- Invariance under the two 88-class symmetries (so the gap stays fair once
# the encoder is trained to be reflection/complement-invariant). ---

_SYM_IMGS = np.stack([_diagram(30), _diagram(110), _diagram(90), _diagram(184)])


def test_features_invariant_under_complement() -> None:
    """0<->1 complementation must not change any feature.

    mean_density is polarity-folded; temporal_activity / block_entropy / (binary)
    compression are exactly invariant under a global 2-symbol relabel.
    """
    base = compute_baseline_features(_SYM_IMGS)
    comp = compute_baseline_features(1 - _SYM_IMGS)
    assert np.allclose(base, comp, atol=1e-9)


def test_symmetric_features_invariant_under_reflection() -> None:
    """Left-right reflection leaves the structurally-symmetric features unchanged.

    (compression_ratio is only *approximately* reflection-invariant — reversing
    column order perturbs LZ77 matches — so it is intentionally not asserted here.)
    """
    base = compute_baseline_features(_SYM_IMGS)
    refl = compute_baseline_features(_SYM_IMGS[:, :, ::-1])
    for name in ("mean_density", "temporal_activity", "block_entropy"):
        j = FEATURE_NAMES.index(name)
        assert np.allclose(base[:, j], refl[:, j], atol=1e-9), name


def test_mean_density_is_polarity_folded() -> None:
    """mean_density returns min(d, 1-d): a >50%-live diagram folds below 0.5."""
    dense = np.ones((1, 8, 8), dtype=np.uint8)
    dense[0, 0, 0] = 0  # density = 63/64
    feats = compute_baseline_features(dense)[0]
    assert feats[FEATURE_NAMES.index("mean_density")] == 1.0 / 64.0
