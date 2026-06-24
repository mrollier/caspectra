"""Hand-crafted, label-free feature baselines (SELF_CRITICISM.md v2 roadmap #4).

The ECA-classification literature already separates behaviours with a handful of
cheap descriptors. Before claiming the learned SSL embedding is worthwhile, it
should be shown to beat these on the rule-vs-class *gap* and on the rare classes.
This module computes a small, purely *diagram-derived* (phenotype-side) feature
vector per spacetime diagram, which can be fed to the same probes/clustering as
the embedding for a fair comparison.

Features (all label-free, computed from the image alone):

* ``mean_density``      — *polarity-folded* live fraction ``min(d, 1-d)`` (a famous
  strong baseline). Folded so it is invariant under 0↔1 complementation, matching
  the encoder's invert-invariance; otherwise the baseline would get an absolute
  density signal we deliberately deny the encoder, breaking the gap comparison.
* ``temporal_activity`` — fraction of cells that change between consecutive rows
  (≈ dynamism; near 0 for fixed/periodic, high for chaotic).
* ``compression_ratio`` — zlib-compressed size / raw size (texture complexity;
  low for ordered, high for chaotic/random).
* ``block_entropy``     — Shannon entropy (bits) of the 16 possible 2×2 block
  patterns (an "input-entropy"-style texture descriptor).

Symmetry note: ``temporal_activity`` and ``block_entropy`` are *exactly* invariant
under both reflection (left-right flip) and complementation (the two 88-class
generators) — complement/flip only permute the 2×2 pattern histogram, and row-wise
change counts are preserved — so they need no folding. ``compression_ratio`` is
approximately invariant. Only ``mean_density`` needed folding; do not "fix" the
others.
"""

from __future__ import annotations

import zlib

import numpy as np

__all__ = ["FEATURE_NAMES", "compute_baseline_features"]

FEATURE_NAMES = [
    "mean_density",
    "temporal_activity",
    "compression_ratio",
    "block_entropy",
]


def _mean_density(img: np.ndarray) -> float:
    # Polarity-folded: min(d, 1-d) so the feature is invariant under 0<->1
    # complementation (one of the two 88-class symmetries the encoder is now
    # trained to ignore). Reflection already leaves density unchanged.
    d = float(img.mean())
    return min(d, 1.0 - d)


def _temporal_activity(img: np.ndarray) -> float:
    if img.shape[0] < 2:
        return 0.0
    return float(np.mean(img[1:] != img[:-1]))


def _compression_ratio(img: np.ndarray) -> float:
    raw = np.ascontiguousarray(img.astype(np.uint8)).tobytes()
    return len(zlib.compress(raw, level=6)) / max(1, len(raw))


def _block_entropy(img: np.ndarray) -> float:
    h, w = img.shape
    h2, w2 = h - (h % 2), w - (w % 2)
    blocks = img[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2)
    # Pattern id in 0..15 from the four cells of each 2x2 block.
    codes = (
        blocks[:, 0, :, 0] * 1
        + blocks[:, 0, :, 1] * 2
        + blocks[:, 1, :, 0] * 4
        + blocks[:, 1, :, 1] * 8
    ).ravel()
    counts = np.bincount(codes, minlength=16).astype(float)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return float(-(probs * np.log2(probs)).sum())


def compute_baseline_features(images: np.ndarray) -> np.ndarray:
    """Return an ``(N, len(FEATURE_NAMES))`` matrix of per-diagram features.

    Accepts ``(N, H, W)`` or ``(N, 1, H, W)``; values are binarised at 0.5.
    """
    imgs = np.asarray(images)
    if imgs.ndim == 4:
        imgs = imgs[:, 0]
    imgs = (imgs > 0.5).astype(np.uint8)
    feats = [
        [
            _mean_density(img),
            _temporal_activity(img),
            _compression_ratio(img),
            _block_entropy(img),
        ]
        for img in imgs
    ]
    return np.asarray(feats, dtype=np.float64)
