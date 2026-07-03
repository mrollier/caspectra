"""Cached per-rule invariant targets for Lever A (FOUNDATIONS.md §4).

The regression targets are the damage-spreading invariants
(:mod:`caspectra.eval.dynamics`): they require *twin simulations* (flip one IC
cell, evolve both copies), so they are genuinely not computable from a single
diagram — which is what makes amortizing them non-trivial. (By contrast,
``input_entropy_variance`` is a deterministic function of the diagram and is
therefore excluded as a target; it remains a diagnostic feature only.)

Targets are per *rule* under a fixed observation protocol (width, IC density —
FOUNDATIONS.md §1) and are cached to disk like the diagrams themselves
(:class:`caspectra.data.dataset.SpacetimeDataset`), keyed by a hash of the
protocol parameters. ``n_pairs`` defaults to 256, matching the bootstrap
precision measured in RESULTS.md (± ≈ 0.01 per feature).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from caspectra.ca.nuca import NonUniformCA, striped_mask
from caspectra.eval.dynamics import (
    DYNAMICS_FEATURE_NAMES,
    damage_spreading_features,
    dynamics_feature_matrix,
)

__all__ = [
    "TARGET_NAMES",
    "load_or_compute_invariant_targets",
    "load_or_compute_alloy_targets",
]

# The regression heads are indexed by these names, in this order.
TARGET_NAMES = list(DYNAMICS_FEATURE_NAMES)


def load_or_compute_invariant_targets(
    rules: list[int] | np.ndarray,
    *,
    width: int = 127,
    ic_density: float = 0.5,
    n_pairs: int = 256,
    seed: int = 0,
    cache_dir: str | Path = "cache",
    radius: int = 1,
) -> np.ndarray:
    """Return the ``(n_rules, len(TARGET_NAMES))`` target matrix, cached on disk.

    Rows follow the order of ``rules``. The cache key covers every parameter
    that affects the values, including the rule list itself. ``radius`` selects
    the rule space (1 = ECA, 2+ = range-r for M4) and is part of the key.

    Caveat (list-set dependence): :func:`dynamics_feature_matrix` spawns one RNG
    per rule *by position in the sorted list*, so the values are invariant to the
    requested order but **depend on which rules are in the list** — a strict
    subset gives slightly different (equally valid) invariants than the superset,
    because the per-rule IC streams differ. Every experiment therefore compares
    predictions against truth loaded for the *same* rule set the model was
    trained on (e.g. ``scripts/validate_complex_placement.py`` loads the full
    panel, not the held-out subset). A rule-identity RNG seed would remove this
    coupling; it is deferred because changing it would shift all cached values.
    """
    rules = [int(r) for r in rules]
    sorted_rules = sorted(rules)
    payload = json.dumps(
        {
            "rules": sorted_rules,
            "width": width,
            "ic_density": ic_density,
            "n_pairs": n_pairs,
            "seed": seed,
            "radius": radius,
        },
        sort_keys=True,
    )
    key = hashlib.sha256(payload.encode()).hexdigest()[:16]
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"targets_{key}.npz"

    if path.exists():
        data = np.load(path)
        matrix = data["targets"]
        cached_rules = [int(r) for r in data["rules"]]
    else:
        matrix = dynamics_feature_matrix(
            sorted_rules,
            width=width,
            n_pairs=n_pairs,
            ic_density=ic_density,
            seed=seed,
            radius=radius,
        )
        cached_rules = sorted_rules
        np.savez_compressed(path, targets=matrix, rules=np.array(sorted_rules))

    index = {r: i for i, r in enumerate(cached_rules)}
    return matrix[[index[r] for r in rules]]


def load_or_compute_alloy_targets(
    pairs: list[tuple[int, int]],
    period: int,
    *,
    width: int = 127,
    ic_density: float = 0.5,
    n_pairs: int = 256,
    seed: int = 0,
    cache_dir: str | Path = "cache",
) -> np.ndarray:
    """Twin-run invariants of striped two-rule "alloys", cached on disk.

    Row ``i`` is the damage-spreading feature vector of the composed system
    ``NonUniformCA(a, b, striped_mask(width, period))`` for ``pairs[i] =
    (a, b)``, measured under the identical protocol as the pure-rule cache
    (criterion 8b, EVALUATION_CRITERIA.md rev 4). The mask is used at offset 0
    only: Bernoulli ICs are translation-invariant on the ring, so the alloy's
    invariants do not depend on the stripe phase.

    Each alloy gets its own generator seeded by ``[seed, a, b, period]``, so a
    row never depends on which other pairs were requested together.
    """
    pairs = [(int(a), int(b)) for a, b in pairs]
    payload = json.dumps(
        {
            "pairs": sorted(pairs),
            "period": period,
            "width": width,
            "ic_density": ic_density,
            "n_pairs": n_pairs,
            "seed": seed,
        },
        sort_keys=True,
    )
    key = hashlib.sha256(payload.encode()).hexdigest()[:16]
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"alloy_targets_{key}.npz"

    if path.exists():
        data = np.load(path)
        matrix = data["targets"]
        cached_pairs = [tuple(int(v) for v in row) for row in data["pairs"]]
    else:
        cached_pairs = sorted(pairs)
        mask = striped_mask(width, period)
        matrix = np.stack(
            [
                damage_spreading_features(
                    simulator=NonUniformCA(a, b, mask),
                    width=width,
                    n_pairs=n_pairs,
                    ic_density=ic_density,
                    rng=np.random.default_rng([seed, a, b, period]),
                )
                for a, b in cached_pairs
            ]
        )
        np.savez_compressed(path, targets=matrix, pairs=np.array(cached_pairs))

    index = {p: i for i, p in enumerate(cached_pairs)}
    return matrix[[index[p] for p in pairs]]
