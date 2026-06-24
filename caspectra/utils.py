"""Shared utilities: seeding, device selection, IO (BUILD_BRIEF.md §1).

Device selection lives behind a single :func:`select_device` so other backends
(e.g. CUDA) can be added later without touching model or training code. On
Apple Silicon the preference is **MPS, falling back to CPU**.
"""

from __future__ import annotations

import json
import random
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import torch

__all__ = [
    "set_seed",
    "select_device",
    "save_json",
    "ensure_dir",
    "is_power_of_two",
    "warn_if_pathological_grid",
]


def is_power_of_two(n: int) -> bool:
    """Return True iff ``n`` is a positive power of two (1, 2, 4, 8, ...)."""
    return n > 0 and (n & (n - 1)) == 0


def warn_if_pathological_grid(grid_size: int) -> None:
    """Warn if ``grid_size`` is a power of two — a known finite-size trap.

    WHY this matters: reference ECA classifications (Li-Packard, Wolfram) assume
    an *infinite* lattice, but we simulate a *finite ring* (periodic boundaries).
    The canonical victim is **rule 90** (``x_i' = x_{i-1} XOR x_{i+1}``), linear
    over GF(2): ``T = S + S^-1 = S^-1 (S + I)**2``. When the ring length is a
    power of two, ``x**N - 1 = (x + 1)**N`` over GF(2), so ``(S + I)`` is
    *nilpotent* and **every** initial condition collapses to the all-zero
    homogeneous state within <= N steps. (Not every additive rule collapses --
    rule 150, symbol ``1 + x + x**2``, stays invertible on a 2**k ring and does
    *not*; the effect is specific to symbols that are non-invertible there.)

    Concretely, at ``grid_size in {64, 128, ...}`` rule 90 (a canonical class-3
    "chaotic" rule) renders as a blank diagram, contradicting its reference label
    and silently corrupting the gap / ``MI(cluster; rule | LP)`` diagnostics.

    The fix is to use an odd (ideally prime) side length such as 127 or 63, which
    breaks the nilpotency and restores the expected dynamics. Note this is about
    the *spatial* grid only: batch size, channel counts and embedding dim should
    still be powers of two (that is where hardware alignment actually helps).
    """
    if is_power_of_two(grid_size):
        warnings.warn(
            f"grid_size={grid_size} is a power of two. Under periodic boundaries "
            "this makes additive ECAs such as rule 90 collapse to a homogeneous "
            "state, diverging from the infinite-lattice reference classifications "
            "and corrupting the cheat-detection diagnostics. "
            "Use an odd, non-power-of-two side length such as 127 (or 63 for "
            "smoke tests) instead.",
            UserWarning,
            stacklevel=2,
        )


def set_seed(seed: int) -> None:
    """Seed Python, NumPy and Torch for reproducible runs.

    Record the seed in every run's output directory (the scripts do this).
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def select_device(prefer: str = "mps") -> torch.device:
    """Return the best available device, preferring ``prefer`` then CPU.

    Order: the requested backend if available, else MPS, else CPU. Keeping this
    in one place means adding CUDA later is a one-line change here, not a
    project-wide edit.
    """
    if prefer == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    if prefer == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    if prefer == "cpu":
        return torch.device("cpu")
    # Fall back through the preference order.
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def ensure_dir(path: str | Path) -> Path:
    """Create ``path`` (and parents) if needed and return it as a ``Path``."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_json(obj: Any, path: str | Path) -> None:
    """Write ``obj`` to ``path`` as pretty JSON."""
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True))
