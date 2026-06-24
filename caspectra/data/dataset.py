"""Dataset of CA spacetime diagrams with on-disk caching (BUILD_BRIEF.md §3.2).

Diagrams are generated once (deterministically, given a seed) and cached to a
``.npz`` keyed by a hash of the generation config, so reconstructing a dataset
with the same settings skips regeneration.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import Dataset

from caspectra.ca.eca import ECASimulator, equivalence_class, independent_rules
from caspectra.utils import warn_if_pathological_grid

# A transform maps a (1, H, W) image to either a single tensor or a two-view
# pair. ``None`` means "return the raw image" (used for embedding extraction).
Transform = Callable[[torch.Tensor], Any]

__all__ = ["SpacetimeDataset"]


class SpacetimeDataset(Dataset):
    """Spacetime diagrams for a set of ECA rules.

    Each diagram is a square ``grid_size x grid_size`` image (height = number of
    time steps, width = number of cells) evolved from a random binary initial
    condition under periodic boundary conditions.

    Parameters
    ----------
    rules:
        ECA rule numbers to include. ``None`` (default) uses the 88 independent
        equivalence-class representatives.
    n_ic_per_rule:
        Number of random initial conditions per rule.
    grid_size:
        Side length of the square diagram (default 127; use 63 for smoke tests).
        Avoid powers of two: under periodic boundaries a ``2**k`` side makes
        additive rules such as rule 90 collapse to a homogeneous state — a warning
        is emitted (see :func:`caspectra.utils.warn_if_pathological_grid`).
    transform:
        A :class:`~caspectra.data.augmentations.TwoViewTransform` for training,
        or ``None`` for raw-image extraction.
    discard_transient:
        Number of leading time steps to drop before recording the diagram
        (default 0). Useful to skip start-up transients.
    cache_dir:
        Directory for the generated ``.npz`` cache.
    seed:
        Seed for the random initial conditions (reproducible generation).
    """

    def __init__(
        self,
        rules: list[int] | None = None,
        n_ic_per_rule: int = 256,
        grid_size: int = 127,
        transform: Transform | None = None,
        discard_transient: int = 0,
        cache_dir: str = "cache",
        seed: int = 0,
    ) -> None:
        warn_if_pathological_grid(grid_size)
        self.rules: list[int] = list(rules) if rules is not None else independent_rules()
        self.n_ic_per_rule = n_ic_per_rule
        self.grid_size = grid_size
        self.transform = transform
        self.discard_transient = discard_transient
        self.cache_dir = Path(cache_dir)
        self.seed = seed
        self.loaded_from_cache = False

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = self.cache_dir / f"spacetime_{self._config_hash()}.npz"
        if cache_path.exists():
            self._load_cache(cache_path)
            self.loaded_from_cache = True
        else:
            self._generate()
            self._save_cache(cache_path)

    # -- generation / caching ------------------------------------------------

    def _config_hash(self) -> str:
        """Stable hash of the generation-affecting config (not the transform —
        augmentations are applied on the fly and must not change the cache)."""
        payload = json.dumps(
            {
                "rules": sorted(self.rules),
                "n_ic_per_rule": self.n_ic_per_rule,
                "grid_size": self.grid_size,
                "discard_transient": self.discard_transient,
                "seed": self.seed,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _generate(self) -> None:
        rng = np.random.default_rng(self.seed)
        n_steps = self.grid_size + self.discard_transient
        images: list[np.ndarray] = []
        rule_ids: list[int] = []
        equiv_reps: list[int] = []
        for rule in self.rules:
            sim = ECASimulator(rule)
            rep = min(equivalence_class(rule))
            for _ in range(self.n_ic_per_rule):
                ic = rng.integers(0, 2, size=self.grid_size, dtype=np.uint8)
                diagram = sim.evolve(ic, n_steps)
                images.append(diagram[self.discard_transient :])
                rule_ids.append(rule)
                equiv_reps.append(rep)
        self.images = np.stack(images).astype(np.uint8)
        self.rule_ids = np.array(rule_ids, dtype=np.int64)
        self.equiv_reps = np.array(equiv_reps, dtype=np.int64)

    def _save_cache(self, path: Path) -> None:
        np.savez_compressed(
            path,
            images=self.images,
            rule_ids=self.rule_ids,
            equiv_reps=self.equiv_reps,
        )

    def _load_cache(self, path: Path) -> None:
        data = np.load(path)
        self.images = data["images"]
        self.rule_ids = data["rule_ids"]
        self.equiv_reps = data["equiv_reps"]

    # -- Dataset API ---------------------------------------------------------

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, index: int) -> Any:
        image = torch.from_numpy(self.images[index]).to(torch.float32).unsqueeze(0)
        metadata = {
            "rule": int(self.rule_ids[index]),
            "equiv_class_rep": int(self.equiv_reps[index]),
        }
        if self.transform is None:
            return image, metadata
        views = self.transform(image)
        if isinstance(views, tuple):
            return (*views, metadata)
        return views, metadata
