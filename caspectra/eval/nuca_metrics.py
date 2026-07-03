"""Region-level metrics for the nuCA compositional-map validation (criterion 7).

The phenotype map produced by :meth:`InvariantRegressor.predict_map` tiles the
input diagram into an ``(h, m)`` grid of patches. On a two-rule composed
diagram, criterion 7 (EVALUATION_CRITERIA.md rev 3) compares the *per-region
mean* of the map against each pure rule's direct invariants — but only over
patches whose receptive field lies entirely inside one region: patches whose
centre is within the exclusion band of a rule interface see both rules and are
left out of the gate (and reported separately as the interface band).

All geometry here is on the ring: the mask wraps, so a half/half mask has two
interfaces.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "interface_positions",
    "region_columns",
    "region_means",
    "ordering_accuracy",
    "column_profile",
    "stripe_contrast",
]


def interface_positions(mask: np.ndarray) -> np.ndarray:
    """Boundary coordinates where the rule changes, in cell units on the ring.

    The interface between cell ``i`` and cell ``i+1`` sits at coordinate
    ``i + 1`` (cell ``i`` occupies ``[i, i+1)``). Includes the wrap-around
    boundary when ``mask[-1] != mask[0]``.
    """
    mask = np.asarray(mask)
    width = mask.size
    return np.array(
        [(i + 1) % width for i in range(width) if mask[i] != mask[(i + 1) % width]],
        dtype=float,
    )


def _ring_distance(a: float, b: np.ndarray, width: int) -> np.ndarray:
    d = np.abs(a - b)
    return np.minimum(d, width - d)


def region_columns(
    mask: np.ndarray, map_width: int, exclusion_px: float
) -> tuple[dict[int, np.ndarray], np.ndarray]:
    """Assign map columns to regions, excluding an interface band.

    Map column ``j`` is treated as a patch centred at ``(j + 0.5) * width /
    map_width`` (uniform tiling of the input width). A column is kept for the
    gate only if its centre is strictly more than ``exclusion_px`` from every
    rule interface; kept columns are labelled by the mask value under their
    centre.

    Returns ``({region_value: column indices}, excluded column indices)``.
    """
    mask = np.asarray(mask)
    width = mask.size
    boundaries = interface_positions(mask)
    centers = (np.arange(map_width) + 0.5) * width / map_width
    kept: dict[int, list[int]] = {0: [], 1: []}
    excluded: list[int] = []
    for j, c in enumerate(centers):
        if boundaries.size and _ring_distance(c, boundaries, width).min() <= exclusion_px:
            excluded.append(j)
            continue
        kept[int(mask[int(c) % width])].append(j)
    return (
        {k: np.asarray(v, dtype=int) for k, v in kept.items() if v},
        np.asarray(excluded, dtype=int),
    )


def region_means(
    pmap: np.ndarray, columns_by_region: dict[int, np.ndarray]
) -> dict[int, np.ndarray]:
    """Mean map prediction per region: ``(n_targets, h, m)`` → ``{region: (n_targets,)}``.

    Averages over all time rows and the region's kept columns — the amortized
    estimate of that region's invariant vector.
    """
    return {
        region: pmap[:, :, cols].mean(axis=(1, 2)) for region, cols in columns_by_region.items()
    }


def column_profile(pmap: np.ndarray) -> np.ndarray:
    """Time-averaged per-column readings: ``(n_targets, h, m)`` → ``(n_targets, m)``.

    The spatial signal criterion 8 grades — averaging over time rows keeps the
    column (spatial) axis, which is the axis stripes vary along.
    """
    return np.asarray(pmap).mean(axis=1)


def stripe_contrast(profile: np.ndarray, mask: np.ndarray, hot_value: int) -> float:
    """Hot-region minus cold-region mean of a per-column profile (one feature).

    ``profile`` is one feature's row of :func:`column_profile` (``(m,)``);
    each column is attributed to the mask value under its centre cell — **no
    interface exclusion**, because criterion 8a measures exactly the
    degradation that mixing at the patch scale causes. ``hot_value`` says
    which mask value (0 or 1) carries the hotter rule, so the sign of the
    contrast is meaningful (positive = hotter region read hotter).
    """
    profile = np.asarray(profile, dtype=float).ravel()
    mask = np.asarray(mask)
    if hot_value not in (0, 1):
        raise ValueError(f"hot_value must be 0 or 1, got {hot_value}")
    width, m = mask.size, profile.size
    centers = ((np.arange(m) + 0.5) * width / m).astype(int) % width
    values = mask[centers]
    if not ((values == 0).any() and (values == 1).any()):
        raise ValueError("mask assigns all column centres to one region — no contrast defined")
    return float(profile[values == hot_value].mean() - profile[values != hot_value].mean())


def ordering_accuracy(
    pred_a: np.ndarray,
    pred_b: np.ndarray,
    true_a: np.ndarray,
    true_b: np.ndarray,
    min_gap: float = 0.02,
) -> tuple[float, int]:
    """Fraction of comparisons where the predicted region ranking matches truth.

    Element-wise over paired scalar arrays (one feature, e.g. spreading rate);
    comparisons whose true values differ by ``min_gap`` or less are skipped —
    the ranking of near-ties is not meaningful. Returns ``(accuracy, n_used)``;
    accuracy is ``nan`` when nothing survives the gap filter.
    """
    pred_a, pred_b = np.asarray(pred_a, float), np.asarray(pred_b, float)
    true_a, true_b = np.asarray(true_a, float), np.asarray(true_b, float)
    usable = np.abs(true_a - true_b) > min_gap
    if not usable.any():
        return float("nan"), 0
    agree = np.sign(pred_a - pred_b)[usable] == np.sign(true_a - true_b)[usable]
    return float(agree.mean()), int(usable.sum())
