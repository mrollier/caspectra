"""Invariant-regression model — Lever A (FOUNDATIONS.md §4).

An encoder plus a linear head that predicts the per-rule damage-spreading
invariants (:mod:`caspectra.data.targets`) from a **single spacetime diagram**.
This is "physics-supervised" amortization, not self-supervision in the purist
sense: the labels come from twin-run simulation, not humans, and are not
computable from the input diagram — which is exactly why criterion 6
(leave-rules-out transfer) is a meaningful gate.

The head is linear on the globally-pooled embedding, so — because global
average pooling commutes with a linear map — the same head applied to each
position of the pre-GAP feature map yields **per-patch predictions whose
spatial mean is exactly the global prediction**. That per-patch mode
(:meth:`InvariantRegressor.predict_map`) is the payoff that direct twin-run
invariants structurally cannot provide: spatially-resolved phenotype maps for
non-uniform CAs.
"""

from __future__ import annotations

import torch
import torch.nn as nn

__all__ = ["InvariantRegressor"]


class InvariantRegressor(nn.Module):
    """Encoder + linear head predicting standardized invariant targets.

    Parameters
    ----------
    encoder:
        Any encoder exposing ``forward(x) -> (B, embedding_dim)`` and
        ``.embedding_dim``; for :meth:`predict_map` it must also expose
        ``feature_map(x) -> (B, embedding_dim, h, w)`` (the CNN encoders do;
        ResNet does not yet).
    n_targets:
        Number of invariant targets (4 damage-spreading features by default).

    Predictions live in **standardized-target space**; the scaler (per-feature
    mean/std fitted on train-split rules only) is stored in the checkpoint by
    the trainer and applied at evaluation time.
    """

    def __init__(self, encoder: nn.Module, n_targets: int = 4) -> None:
        super().__init__()
        self.encoder = encoder
        self.n_targets = n_targets
        self.head = nn.Linear(encoder.embedding_dim, n_targets)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Global prediction ``(B, n_targets)`` in standardized-target space."""
        return self.head(self.encoder(x))

    def extract_embedding(self, x: torch.Tensor) -> torch.Tensor:
        """Encoder output ``(B, embedding_dim)`` — mirrors the BYOL/SimSiam API
        so :func:`caspectra.eval.embed.extract_embeddings` and the salience
        diagnostics work unchanged on this model."""
        return self.encoder(x)

    def predict_map(self, x: torch.Tensor) -> torch.Tensor:
        """Per-patch predictions ``(B, n_targets, h, w)``.

        The linear head applied at every spatial position of the pre-GAP
        feature map. Identity: ``predict_map(x).mean(dim=(-2, -1)) ==
        forward(x)`` (up to float error), since GAP∘linear = mean of per-patch
        linear outputs.
        """
        fmap = self.encoder.feature_map(x)  # (B, D, h, w)
        weight = self.head.weight  # (n_targets, D)
        out = torch.einsum("bdhw,td->bthw", fmap, weight)
        return out + self.head.bias.view(1, -1, 1, 1)
