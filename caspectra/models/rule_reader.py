"""F2 (EVALUATION_CRITERIA.md rev 9): the learned rule-reader.

The referee's requested comparator: a network that predicts the generating
rule's *table bits* from a (possibly degraded) diagram, whose output then feeds
the exact simulator — learned system identification, separating "identify the
rule" from "map rule to response".

The architecture is the deliberate opposite of the anti-cheat amortiser: the
first convolution's kernel is ``(2, 2r+1)`` — exactly one
``neighbourhood -> output`` transition window (the "T-tetromino" the amortiser
was forbidden) — followed by 1x1 mixing layers, global average pooling (input
geometry agnostic, so the same model runs on truncated diagrams), and a linear
head with one logit per table entry. Under clean observation this is an easy
supervised task; the scientific question is how gracefully the *learned* reader
degrades where the deterministic tabulation snaps (noise, masking), which is
why training uses degradation augmentation (ranges fixed in the training
script, per the rev-9 registration).
"""

from __future__ import annotations

import numpy as np
import torch
from torch import nn

__all__ = ["RuleReader", "load_rule_reader"]


class RuleReader(nn.Module):
    """Predict per-entry rule-table logits from a spacetime diagram."""

    def __init__(self, radius: int = 2, channels: int = 64, hidden: int = 128) -> None:
        super().__init__()
        self.radius = radius
        self.table_size = 1 << (2 * radius + 1)
        # One transition window per position: 2 rows x full neighbourhood width.
        self.transition = nn.Conv2d(1, channels, kernel_size=(2, 2 * radius + 1), bias=True)
        self.mix = nn.Sequential(
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, hidden, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(hidden, hidden, kernel_size=1),
            nn.ReLU(inplace=True),
        )
        self.head = nn.Linear(hidden, self.table_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """``(B, 1, H, W)`` diagram -> ``(B, table_size)`` bit logits."""
        h = self.mix(self.transition(x))
        h = h.mean(dim=(2, 3))  # GAP: aggregate transition evidence everywhere
        return self.head(h)

    @torch.no_grad()
    def predict_bits(self, diagram: np.ndarray) -> np.ndarray:
        """Per-entry ``P(bit = 1)`` for one ``(H, W)`` uint8/float diagram."""
        device = next(self.parameters()).device
        b = torch.from_numpy(np.asarray(diagram, dtype=np.float32))[None, None].to(device)
        return torch.sigmoid(self.forward(b)).cpu().numpy()[0]


def load_rule_reader(path: str, device) -> RuleReader:
    """Load a trained reader checkpoint (written by ``scripts/train_rule_reader.py``)."""
    state = torch.load(path, map_location="cpu", weights_only=False)
    model = RuleReader(
        radius=int(state["radius"]),
        channels=int(state["channels"]),
        hidden=int(state["hidden"]),
    )
    model.load_state_dict(state["model_state"])
    return model.to(device).eval()
