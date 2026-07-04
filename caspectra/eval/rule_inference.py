"""Read the local rule off a diagram, then simulate its damage response.

The mechanistic reference method of the benchmark (EVALUATION_CRITERIA.md rev 7,
R4). The referee's central mechanistic question is: *because the local rule is
readable from a single space-time diagram, is the damage-response target
recoverable by simply inferring the rule and running the twin-run simulator?* If
so, a **matched-model system-identification** estimator reaches the achievable
Monte-Carlo agreement, and the deep amortiser has nothing to add — the paper's
positive result. (The estimator is *not* parameter-free: it carries a prior over
unobserved rule-table entries; see the completion policies below, rev-8 C3.)

``infer_rule`` inverts the forward map of :class:`caspectra.ca.range_ca.RangeCA`
(and its ``radius = 1`` special case :class:`caspectra.ca.eca.ECASimulator`): it
tabulates every observed ``neighbourhood -> next-cell`` transition in the diagram
and rebuilds the ``2**(2r+1)``-bit rule table with the *same* bit convention
(``index |= neighbour << (radius - offset)``; the leftmost neighbour is the MSB).
Entries never exercised by the diagram are **unobserved**. ``infer_rule_table``
exposes the observed mask so a **completion policy** can be chosen for them; the
second referee (concern 3) rightly noted that the ``rev-7`` default-zero fill is
an unacknowledged prior. :func:`complete_table` implements default-0 / default-1 /
empirical-MAP fills, and :func:`mechanistic_estimate_posterior` marginalises over
the unobserved entries under an empirical Bernoulli prior to yield an
**uncertainty-aware** estimate with a predictive interval.

``mechanistic_estimate`` feeds the completed rule to
:func:`caspectra.eval.dynamics.damage_spreading_features` under the identical
observation protocol but an **independent** RNG, so when inference is exact its
prediction is a second independent Monte-Carlo estimate of the same target — its
agreement with the cached target is therefore bounded by the **independent-replicate
agreement** (rev-8 C2), not by ICC and not by any learned capacity.
"""

from __future__ import annotations

import itertools

import numpy as np

from caspectra.eval.dynamics import damage_spreading_features

__all__ = [
    "infer_rule",
    "infer_rule_table",
    "neighbourhood_indices",
    "complete_table",
    "table_to_rule",
    "mechanistic_estimate",
    "mechanistic_estimate_posterior",
]


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


def infer_rule_table(diagram: np.ndarray, radius: int = 1) -> tuple[np.ndarray, np.ndarray, bool]:
    """Infer the local rule *table* and which entries the diagram observed.

    ``diagram`` is an ``(n_steps, width)`` binary image with row 0 at the top and
    time increasing downward (the :class:`SpacetimeDataset` convention); any two
    consecutive rows are a set of ``neighbourhood -> output`` observations, and
    the update is time-invariant, so a transient-trimmed diagram is fine.

    Returns ``(table, observed, consistent)``: ``table`` holds the majority output
    per entry (``0`` where unobserved — a placeholder, *not* a completion choice),
    ``observed`` is the boolean mask of exercised entries, and ``consistent`` is
    ``False`` only if some neighbourhood was seen mapping to *both* outputs
    (impossible for a clean deterministic CA; a guard against noisy/partial input).
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
    consistent = bool(np.all((ones == 0) | (ones == total) | ~observed))
    return table, observed, consistent


def table_to_rule(table: np.ndarray) -> int:
    """Rule number from a completed truth ``table`` (entry ``i`` is bit ``i``)."""
    return int(sum(int(b) << i for i, b in enumerate(np.asarray(table, dtype=np.uint8))))


def _empirical_one_frequency(table: np.ndarray, observed: np.ndarray) -> float:
    """Marginal frequency of output ``1`` among *observed* entries (0.5 fallback)."""
    if not observed.any():
        return 0.5
    return float(np.asarray(table)[observed].mean())


def complete_table(
    table: np.ndarray,
    observed: np.ndarray,
    policy: str = "zero",
    *,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Fill unobserved rule-table entries under a named completion ``policy``.

    ``"zero"`` / ``"one"`` fill missing entries with a constant (the rev-7 default
    was ``"zero"``); ``"empirical"`` fills them with the MAP bit under the observed
    marginal frequency; ``"sample"`` draws each missing bit ``~ Bernoulli(p)`` with
    ``p`` the observed marginal (used by the posterior estimator). The returned
    table is a copy; observed entries are never altered.
    """
    table = np.asarray(table, dtype=np.uint8).copy()
    missing = ~np.asarray(observed, dtype=bool)
    if not missing.any():
        return table
    if policy == "zero":
        table[missing] = 0
    elif policy == "one":
        table[missing] = 1
    elif policy == "empirical":
        table[missing] = 1 if _empirical_one_frequency(table, observed) >= 0.5 else 0
    elif policy == "sample":
        p = _empirical_one_frequency(table, observed)
        gen = rng if rng is not None else np.random.default_rng()
        table[missing] = (gen.random(int(missing.sum())) < p).astype(np.uint8)
    else:
        raise ValueError(f"unknown completion policy {policy!r}")
    return table


def infer_rule(diagram: np.ndarray, radius: int = 1) -> tuple[int, float, bool]:
    """Infer the local rule number (default-zero completion) — the R4 estimator.

    Returns ``(rule, coverage, consistent)`` with ``coverage`` the fraction of the
    ``2**(2r+1)`` entries the diagram exercised. Thin wrapper over
    :func:`infer_rule_table` with the pre-registered ``"zero"`` completion, kept
    for backward compatibility; use :func:`infer_rule_table` +
    :func:`complete_table` to vary the completion (rev-8 C3).
    """
    table, observed, consistent = infer_rule_table(diagram, radius)
    rule = table_to_rule(complete_table(table, observed, "zero"))
    return rule, float(observed.mean()), consistent


def _simulate(
    rule: int,
    radius: int,
    *,
    width: int,
    n_pairs: int,
    ic_density: float,
    rng: np.random.Generator | None,
) -> np.ndarray:
    """Damage-response features of ``rule`` under the protocol (radius-agnostic)."""
    if radius == 1:
        return damage_spreading_features(
            rule, width=width, n_pairs=n_pairs, ic_density=ic_density, rng=rng
        )
    from caspectra.ca.range_ca import RangeCA

    return damage_spreading_features(
        simulator=RangeCA(rule, radius),
        width=width,
        n_pairs=n_pairs,
        ic_density=ic_density,
        rng=rng,
    )


def mechanistic_estimate(
    diagram: np.ndarray,
    radius: int = 1,
    *,
    width: int = 127,
    n_pairs: int = 256,
    ic_density: float = 0.5,
    completion: str = "zero",
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, int, float]:
    """Estimate the four damage-response statistics by *reading and simulating*.

    Infers the rule table from ``diagram``, fills unobserved entries under
    ``completion`` (default ``"zero"``, the rev-7 policy; rev-8 C3 also compares
    ``"one"`` and ``"empirical"``), then runs the twin-run simulator under the
    given protocol with an **independent** ``rng`` (pass a generator not shared
    with the target cache, so a correct inference yields an independent MC estimate
    rather than a trivially identical one). Returns ``(features, rule, coverage)``.
    """
    table, observed, _ = infer_rule_table(diagram, radius)
    rule = table_to_rule(complete_table(table, observed, completion, rng=rng))
    feats = _simulate(rule, radius, width=width, n_pairs=n_pairs, ic_density=ic_density, rng=rng)
    return feats, rule, float(observed.mean())


def mechanistic_estimate_posterior(
    diagram: np.ndarray,
    radius: int = 1,
    *,
    width: int = 127,
    n_pairs: int = 256,
    ic_density: float = 0.5,
    max_enumerate: int = 6,
    n_samples: int = 24,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray, int, float, int]:
    """Uncertainty-aware estimate: marginalise over unobserved rule-table entries.

    Places an empirical Bernoulli(``p``) prior on each unobserved entry (``p`` the
    observed marginal frequency of output 1). If ``k`` entries are unobserved and
    ``k <= max_enumerate`` the ``2**k`` completions are **enumerated** and
    prior-weighted; otherwise ``n_samples`` completions are **sampled** from the
    prior. Each completion is simulated with an independent draw of ``rng`` and the
    four features are averaged. Returns ``(mean, std, map_rule, coverage,
    n_missing)`` — ``std`` is the predictive spread induced by table uncertainty
    (rev-8 C3), zero when the table is fully covered.
    """
    gen = rng if rng is not None else np.random.default_rng()
    table, observed, _ = infer_rule_table(diagram, radius)
    coverage = float(observed.mean())
    missing = np.flatnonzero(~observed)
    k = int(missing.size)
    map_rule = table_to_rule(complete_table(table, observed, "empirical"))

    def sim(tbl: np.ndarray) -> np.ndarray:
        return _simulate(
            table_to_rule(tbl),
            radius,
            width=width,
            n_pairs=n_pairs,
            ic_density=ic_density,
            rng=gen,
        )

    if k == 0:
        feats = sim(table)
        return feats, np.zeros_like(feats), map_rule, coverage, 0

    p = _empirical_one_frequency(table, observed)
    feats_list: list[np.ndarray] = []
    weights: list[float] = []
    if k <= max_enumerate:
        for bits in itertools.product((0, 1), repeat=k):
            tbl = table.copy()
            tbl[missing] = np.asarray(bits, dtype=np.uint8)
            w = float(np.prod([p if b else (1.0 - p) for b in bits]))
            feats_list.append(sim(tbl))
            weights.append(w)
    else:
        for _ in range(n_samples):
            tbl = complete_table(table, observed, "sample", rng=gen)
            feats_list.append(sim(tbl))
            weights.append(1.0)

    feats_arr = np.stack(feats_list)
    w = np.asarray(weights)
    w = w / w.sum()
    mean = np.average(feats_arr, axis=0, weights=w)
    var = np.average((feats_arr - mean) ** 2, axis=0, weights=w)
    return mean, np.sqrt(var), map_rule, coverage, k
