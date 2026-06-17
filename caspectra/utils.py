"""Shared utilities: seeding, device selection, IO (BUILD_BRIEF.md §1).

Device selection lives behind a single :func:`select_device` so other backends
(e.g. CUDA) can be added later without touching model or training code. On
Apple Silicon the preference is **MPS, falling back to CPU**.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch

__all__ = ["set_seed", "select_device", "save_json", "ensure_dir"]


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
