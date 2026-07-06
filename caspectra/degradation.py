"""Input-degradation augmentation with the rev-9 registered ranges.

WHY this lives in the package: the rev-9 rule-reader (`scripts/train_rule_reader.py`)
and the rev-10 fairness-control CNN (EVALUATION_CRITERIA.md rev 10, C-i) must
apply the *same* degradation families and ranges — the whole point of C-i is
to hand the direct CNN exactly the adaptation budget the reader received.
Keeping one implementation here prevents the two from drifting. The constants
were fixed in rev 9 before the reader was trained and are not tunable.
"""

from __future__ import annotations

import numpy as np
import torch

__all__ = ["AUG_NOISE_MAX", "AUG_MASK_MAX", "AUG_APPLY_P", "degrade_batch"]

# Registered augmentation ranges (rev 9, reaffirmed rev 10) — fixed before any
# degradation-trained model was trained; the frontier grid's *test* corruption
# levels are not tuned on.
AUG_NOISE_MAX = 0.15
AUG_MASK_MAX = 0.5
AUG_APPLY_P = 0.5


def degrade_batch(batch: torch.Tensor, rng: np.random.Generator) -> torch.Tensor:
    """Bit-flip + zero-fill mask degradation. ``batch``: (B, 1, H, W) in {0, 1}.

    Per-sample corruption levels p ~ U(0, max), each family applied with
    probability ``AUG_APPLY_P`` (the gate is folded into p by zeroing it) —
    semantics identical to the rev-9 reader's ``_augment``.
    """
    shape = (batch.shape[0], 1, 1, 1)
    p_noise = rng.uniform(0.0, AUG_NOISE_MAX, size=shape) * (rng.random(shape) < AUG_APPLY_P)
    p_mask = rng.uniform(0.0, AUG_MASK_MAX, size=shape) * (rng.random(shape) < AUG_APPLY_P)
    flips = torch.from_numpy((rng.random(batch.shape) < p_noise).astype(np.float32))
    keep = torch.from_numpy((rng.random(batch.shape) >= p_mask).astype(np.float32))
    return ((batch + flips) % 2.0) * keep
