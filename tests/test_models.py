"""Tests for models/byol.py — BYOL and SimSiam wrappers (BUILD_BRIEF.md §3.5)."""

from __future__ import annotations

import torch

from caspectra.models.byol import BYOL, SimSiam
from caspectra.models.encoder import SmallCNNEncoder


def _encoder(dim: int = 64) -> SmallCNNEncoder:
    return SmallCNNEncoder(embedding_dim=dim)


def _pair(n: int = 4, grid: int = 64) -> tuple[torch.Tensor, torch.Tensor]:
    return torch.randn(n, 1, grid, grid), torch.randn(n, 1, grid, grid)


# ---------------------------------------------------------------------------
# BYOL
# ---------------------------------------------------------------------------


def test_byol_forward_returns_differentiable_scalar_loss() -> None:
    model = BYOL(_encoder())
    x0, x1 = _pair()
    loss = model(x0, x1)
    assert loss.dim() == 0
    loss.backward()
    # Online encoder receives gradients.
    assert any(p.grad is not None for p in model.encoder.parameters())


def test_byol_target_network_has_no_gradients() -> None:
    model = BYOL(_encoder())
    assert all(not p.requires_grad for p in model.target_encoder.parameters())
    assert all(not p.requires_grad for p in model.target_projection_head.parameters())


def test_byol_update_target_moves_target_toward_online() -> None:
    model = BYOL(_encoder())
    before = [p.clone() for p in model.target_encoder.parameters()]
    with torch.no_grad():
        for p in model.encoder.parameters():
            p.add_(1.0)  # perturb the online encoder
    model.update_target(tau=0.9)
    after = list(model.target_encoder.parameters())
    assert any(not torch.equal(a, b) for a, b in zip(after, before))


def test_byol_extract_embedding_is_preprojector() -> None:
    enc = _encoder(dim=64)
    model = BYOL(enc)
    emb = model.extract_embedding(torch.randn(3, 1, 64, 64))
    assert emb.shape == (3, enc.embedding_dim)


# ---------------------------------------------------------------------------
# SimSiam
# ---------------------------------------------------------------------------


def test_simsiam_forward_returns_differentiable_scalar_loss() -> None:
    model = SimSiam(_encoder())
    x0, x1 = _pair()
    loss = model(x0, x1)
    assert loss.dim() == 0
    loss.backward()
    assert any(p.grad is not None for p in model.encoder.parameters())


def test_simsiam_has_no_target_network() -> None:
    model = SimSiam(_encoder())
    assert not hasattr(model, "target_encoder")


def test_simsiam_extract_embedding_shape() -> None:
    enc = _encoder(dim=64)
    model = SimSiam(enc)
    emb = model.extract_embedding(torch.randn(2, 1, 64, 64))
    assert emb.shape == (2, enc.embedding_dim)
