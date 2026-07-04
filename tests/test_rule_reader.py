"""Tests for the F2 learned rule-reader (rev 9)."""

from __future__ import annotations

import numpy as np
import torch

from caspectra.ca.eca import ECASimulator
from caspectra.models.rule_reader import RuleReader


def test_reader_shapes_and_geometry_agnostic():
    """Logit head matches the table size; GAP makes input geometry free."""
    model = RuleReader(radius=2, channels=8, hidden=16).eval()
    for h, w in [(127, 127), (30, 127), (63, 63)]:
        x = torch.zeros(2, 1, h, w)
        assert model(x).shape == (2, 32)
    p = model.predict_bits(np.zeros((40, 63), dtype=np.uint8))
    assert p.shape == (32,) and np.all((p >= 0) & (p <= 1))


def test_reader_overfits_two_rules():
    """A tiny reader separates two ECA rules' tables in a few steps —
    the supervised task is learnable end-to-end."""
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    model = RuleReader(radius=1, channels=16, hidden=32)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
    lossf = torch.nn.BCEWithLogitsLoss()
    rules = [30, 110]
    X = torch.stack(
        [
            torch.from_numpy(
                ECASimulator(r).evolve(rng.integers(0, 2, 63, dtype=np.uint8), 40)
            ).float()
            for r in rules
            for _ in range(8)
        ]
    ).unsqueeze(1)
    Y = torch.tensor(
        [[(r >> k) & 1 for k in range(8)] for r in rules for _ in range(8)], dtype=torch.float32
    )
    for _ in range(150):
        opt.zero_grad()
        loss = lossf(model(X), Y)
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        pred = (torch.sigmoid(model(X)) >= 0.5).float()
    assert float((pred == Y).float().mean()) == 1.0
