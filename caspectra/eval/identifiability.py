"""Observation-degradation primitives for the identifiability phase diagram (C4).

The second referee's highest-value request (concerns 3, 4, 7): quantify *when*
reading the local rule off a diagram is possible, rather than reporting a single
recovery percentage. The mechanistic estimator's accuracy is gated by whether the
diagram exercises (and cleanly reveals) the rule table; as the observation is
shortened, sub-sampled, or corrupted, exact reconstruction fails and a learned
direct estimator may degrade more gracefully.

This module provides the degradations — truncation, bit-flip observation noise,
and random cell masking (partial observation) — and a **mask-aware** rule-table
inference that drops transitions touching a masked cell. It contains *no* neural
training: the phase diagram evaluates the mechanistic inverter, the five-statistic
baseline, and the **frozen** CNN checkpoint on the degraded diagrams (the CNN only
on axes that preserve its fixed input geometry, i.e. noise and masking).
"""

from __future__ import annotations

import numpy as np

from caspectra.eval.rule_inference import neighbourhood_indices

__all__ = ["degrade_diagram", "masked_infer_table"]


def degrade_diagram(
    diagram: np.ndarray,
    *,
    n_rows: int | None = None,
    flip_p: float = 0.0,
    mask_p: float = 0.0,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray | None]:
    """Return a degraded copy of ``diagram`` and its observed-cell mask.

    ``n_rows`` truncates to the first ``n_rows`` time steps (fewer observations);
    ``flip_p`` flips each cell independently (observation noise on the *values*);
    ``mask_p`` marks a fraction of cells unobserved (partial observation). The
    returned mask is ``None`` when ``mask_p == 0`` (all cells observed). The same
    degraded diagram is what both the inverter and the frozen CNN see, so the
    comparison is fair.
    """
    d = diagram if n_rows is None else diagram[:n_rows]
    d = np.array(d, dtype=np.uint8, copy=True)
    if flip_p > 0.0:
        d ^= (rng.random(d.shape) < flip_p).astype(np.uint8)
    observed = None
    if mask_p > 0.0:
        observed = rng.random(d.shape) >= mask_p
    return d, observed


def masked_infer_table(
    diagram: np.ndarray,
    radius: int,
    observed: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Infer the rule table, excluding transitions that touch a masked cell.

    A ``neighbourhood -> output`` transition at ``(t, i)`` is used only if the
    output cell ``(t+1, i)`` and every cell within ``radius`` of ``(t, i)`` are
    observed. Returns ``(table, entry_observed)`` where ``table`` holds the
    majority output per exercised entry (``0`` placeholder elsewhere) and
    ``entry_observed`` is the boolean mask of exercised table entries. With
    ``observed=None`` this reduces to full inference over all transitions.
    """
    diagram = np.asarray(diagram, dtype=np.uint8)
    height, width = diagram.shape
    tsize = 1 << (2 * radius + 1)
    idx = np.concatenate([neighbourhood_indices(diagram[t], radius) for t in range(height - 1)])
    out = diagram[1:].reshape(-1).astype(np.int64)

    if observed is None:
        keep = np.ones(idx.shape[0], dtype=bool)
    else:
        observed = np.asarray(observed, dtype=bool)
        nb_ok = np.ones((height, width), dtype=bool)
        for offset in range(-radius, radius + 1):
            nb_ok &= np.roll(observed, -offset, axis=1)  # cell (t, i+offset) observed
        keep = (nb_ok[:-1] & observed[1:]).reshape(-1)

    idx, out = idx[keep], out[keep]
    total = np.bincount(idx, minlength=tsize)
    ones = np.bincount(idx, weights=out, minlength=tsize).astype(np.int64)
    entry_observed = total > 0
    table = (2 * ones > total).astype(np.uint8)
    return table, entry_observed
