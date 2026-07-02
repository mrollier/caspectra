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

from caspectra.eval.dynamics import DYNAMICS_FEATURE_NAMES, dynamics_feature_matrix

__all__ = ["TARGET_NAMES", "load_or_compute_invariant_targets"]

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
) -> np.ndarray:
    """Return the ``(n_rules, len(TARGET_NAMES))`` target matrix, cached on disk.

    Rows follow the order of ``rules``. The cache key covers every parameter
    that affects the values, including the rule list itself; per-rule RNG
    spawning inside :func:`dynamics_feature_matrix` keeps each row independent
    of the list order, but the cache is keyed on the sorted list for simplicity
    and rows are re-indexed to the requested order on load.
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
            sorted_rules, width=width, n_pairs=n_pairs, ic_density=ic_density, seed=seed
        )
        cached_rules = sorted_rules
        np.savez_compressed(path, targets=matrix, rules=np.array(sorted_rules))

    index = {r: i for i, r in enumerate(cached_rules)}
    return matrix[[index[r] for r in rules]]
