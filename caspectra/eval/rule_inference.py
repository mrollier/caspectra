"""Read the local rule off a diagram, then simulate its damage response.

The mechanistic reference method of the benchmark (EVALUATION_CRITERIA.md rev 7,
R4). The referee's central mechanistic question is: *because the local rule is
readable from a single space-time diagram, is the damage-response target
recoverable by simply inferring the rule and running the twin-run simulator?* If
so, an **interpretable, parameter-free** estimator reaches the reliability
ceiling, and the deep amortiser has nothing to add — the paper's positive result.

``infer_rule`` inverts the forward map of :class:`caspectra.ca.range_ca.RangeCA`
(and its ``radius = 1`` special case :class:`caspectra.ca.eca.ECASimulator`): it
tabulates every observed ``neighbourhood -> next-cell`` transition in the diagram
and rebuilds the ``2**(2r+1)``-bit rule table with the *same* bit convention
(``index |= neighbour << (radius - offset)``; the leftmost neighbour is the MSB).
Entries never exercised by the diagram are **unobserved**; per the
pre-registration they default to ``0`` and the observed **coverage** is reported,
so the estimator's failure mode (under-identified tables) is measured, not hidden.

``mechanistic_estimate`` then feeds the inferred rule to
:func:`caspectra.eval.dynamics.damage_spreading_features` under the identical
observation protocol but an **independent** RNG, so when inference is exact its
prediction is a second independent Monte-Carlo estimate of the same target — its
agreement with the cached target is therefore bounded by the test-retest
reliability (R3), not by any learned capacity.
"""

from __future__ import annotations

import numpy as np

from caspectra.eval.dynamics import damage_spreading_features

__all__ = ["infer_rule", "neighbourhood_indices", "mechanistic_estimate"]


def neighbourhood_indices(row: np.ndarray, radius: int) -> np.ndarray:
    """Neighbourhood index of every cell of ``row`` (periodic boundaries).

    Uses the exact convention of :meth:`RangeCA._neighbourhood_index`: the
    neighbour at ``offset`` contributes bit ``radius - offset`` (so the leftmost
    neighbour, ``offset = -radius``, is the most-significant bit). ``radius = 1``
    reproduces the ECA index ``4*left + 2*centre + right``.
    """
    row = np.asarray(row, dtype=np.uint8).ravel()
    index = np.zeros(row.shape[0], dtype=np.int64)
    for offset in range(-radius, radius + 1):
        neighbour = np.roll(row, -offset)  # neighbour[i] = row[i + offset]
        index |= neighbour.astype(np.int64) << (radius - offset)
    return index


def infer_rule(diagram: np.ndarray, radius: int = 1) -> tuple[int, float, bool]:
    """Infer the local rule number from a space-time ``diagram``.

    ``diagram`` is an ``(n_steps, width)`` binary image with row 0 at the top and
    time increasing downward (the :class:`SpacetimeDataset` convention); any two
    consecutive rows are a set of ``neighbourhood -> output`` observations, and
    the update is time-invariant, so a transient-trimmed diagram is fine.

    Returns ``(rule, coverage, consistent)`` where ``coverage`` is the fraction
    of the ``2**(2r+1)`` table entries the diagram exercised (unobserved entries
    default to ``0``) and ``consistent`` is ``False`` only if some neighbourhood
    was seen mapping to *both* outputs (impossible for a clean deterministic CA;
    a guard against noisy/partial inputs).
    """
    diagram = np.asarray(diagram, dtype=np.uint8)
    if diagram.ndim != 2 or diagram.shape[0] < 2:
        raise ValueError("diagram must be (n_steps>=2, width)")
    tsize = 1 << (2 * radius + 1)

    idx = np.concatenate(
        [neighbourhood_indices(diagram[t], radius) for t in range(len(diagram) - 1)]
    )
    out = diagram[1:].reshape(-1).astype(np.int64)

    total = np.bincount(idx, minlength=tsize)
    ones = np.bincount(idx, weights=out, minlength=tsize).astype(np.int64)
    observed = total > 0
    # Deterministic CA: every observation of an index agrees; majority is exact.
    table = (2 * ones > total).astype(np.uint8)
    table[~observed] = 0  # pre-registered default for unobserved entries
    consistent = bool(np.all((ones == 0) | (ones == total) | ~observed))

    rule = int(sum(int(b) << i for i, b in enumerate(table)))
    coverage = float(observed.mean())
    return rule, coverage, consistent


def mechanistic_estimate(
    diagram: np.ndarray,
    radius: int = 1,
    *,
    width: int = 127,
    n_pairs: int = 256,
    ic_density: float = 0.5,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, int, float]:
    """Estimate the four damage-response statistics by *reading and simulating*.

    Infers the rule from ``diagram`` (:func:`infer_rule`), then runs the twin-run
    simulator (:func:`damage_spreading_features`) under the given protocol with an
    **independent** ``rng`` (pass a generator not shared with the target cache, so
    a correct inference yields an independent MC estimate rather than a trivially
    identical one). Returns ``(features, inferred_rule, coverage)``.
    """
    rule, coverage, _ = infer_rule(diagram, radius)
    if radius == 1:
        feats = damage_spreading_features(
            rule, width=width, n_pairs=n_pairs, ic_density=ic_density, rng=rng
        )
    else:
        from caspectra.ca.range_ca import RangeCA

        feats = damage_spreading_features(
            simulator=RangeCA(rule, radius),
            width=width,
            n_pairs=n_pairs,
            ic_density=ic_density,
            rng=rng,
        )
    return feats, rule, coverage
