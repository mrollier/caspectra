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

__all__ = [
    "degrade_diagram",
    "masked_infer_table",
    "masked_transition_counts",
    "select_radius",
    "project_table_radius3_to_2",
]


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


def masked_transition_counts(
    diagram: np.ndarray,
    radius: int,
    observed: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Per-entry ``(ones, total)`` counts, excluding transitions touching a mask.

    A ``neighbourhood -> output`` transition at ``(t, i)`` is used only if the
    output cell ``(t+1, i)`` and every cell within ``radius`` of ``(t, i)`` are
    observed. With ``observed=None`` all transitions are used. These are the
    sufficient statistics for both the deterministic majority inference and the
    rev-9 F1 noise-aware posterior on partially observed diagrams.
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
    return ones, total


def masked_infer_table(
    diagram: np.ndarray,
    radius: int,
    observed: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Infer the rule table, excluding transitions that touch a masked cell.

    Returns ``(table, entry_observed)`` where ``table`` holds the majority
    output per exercised entry (``0`` placeholder elsewhere) and
    ``entry_observed`` is the boolean mask of exercised table entries. With
    ``observed=None`` this reduces to full inference over all transitions.
    """
    ones, total = masked_transition_counts(diagram, radius, observed)
    entry_observed = total > 0
    table = (2 * ones > total).astype(np.uint8)
    return table, entry_observed


def select_radius(
    diagram: np.ndarray,
    candidates: tuple[int, ...] = (1, 2, 3),
    margin: float = 0.005,
) -> tuple[int, dict[int, float]]:
    """Select the neighbourhood radius by observation self-consistency (rev-9 F3).

    For each candidate radius the *disagreement fraction* is the share of
    transitions contradicting their entry's majority output; a rule of radius r
    fits perfectly at every candidate >= r, so the registered parsimony rule
    picks the **smallest** candidate whose disagreement is within ``margin`` of
    the best. Returns ``(selected_radius, disagreement_by_radius)``.
    """
    from caspectra.eval.rule_inference import transition_counts

    disagreement: dict[int, float] = {}
    for r in candidates:
        ones, total = transition_counts(diagram, r)
        seen = total > 0
        if not seen.any():
            disagreement[r] = 1.0
            continue
        minority = np.minimum(ones[seen], total[seen] - ones[seen])
        disagreement[r] = float(minority.sum() / total[seen].sum())
    best = min(disagreement.values())
    for r in sorted(candidates):
        if disagreement[r] <= best + margin:
            return r, disagreement
    return max(candidates), disagreement  # unreachable; keeps the signature total


def project_table_radius3_to_2(table3: np.ndarray, total3: np.ndarray | None = None) -> np.ndarray:
    """Project a 128-entry radius-3 table onto 32 radius-2 entries.

    Groups radius-3 entries by their middle five bits (offsets -2..+2 are bits
    5..1 under the ``radius - offset`` convention, so the radius-2 index is
    ``(idx3 >> 1) & 0b11111``) and takes the observation-count-weighted majority
    over the two outer cells. Exact when the generating rule is genuinely
    radius-2 expressible; a lossy summary otherwise.
    """
    table3 = np.asarray(table3, dtype=np.int64)
    weights = np.asarray(total3, dtype=np.int64) if total3 is not None else np.ones_like(table3)
    idx3 = np.arange(128)
    idx2 = (idx3 >> 1) & 0b11111
    ones = np.bincount(idx2, weights=table3 * weights, minlength=32)
    tot = np.bincount(idx2, weights=weights, minlength=32)
    with np.errstate(invalid="ignore"):
        out = (2 * ones > tot).astype(np.uint8)
    out[tot == 0] = 0  # nothing observed for this group: zero completion
    return out
