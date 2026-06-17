"""BYOL (default) and SimSiam (M4 fallback) SSL wrappers (BUILD_BRIEF.md §3.5).

Both wrap one of the encoders from :mod:`caspectra.models.encoder` and use
``lightly`` components for the projection/prediction heads, the momentum-update
helper, and the negative-cosine-similarity loss. The encoder, the loss
composition, and the training surface stay first-party so the project is
inspectable.

**Method choice on M4:** BYOL is the default but its accuracy degrades when the
batch drops below ~256. If M4 memory forces a smaller batch, switch to SimSiam
(no target network, less memory, small-batch native). Both expose the same
``forward(x0, x1) -> loss`` and ``extract_embedding(x) -> (B, embedding_dim)``
surface, so they are config-swappable.
"""

from __future__ import annotations

import copy

import torch
import torch.nn as nn
from lightly.loss import NegativeCosineSimilarity
from lightly.models.modules import (
    BYOLPredictionHead,
    BYOLProjectionHead,
    SimSiamPredictionHead,
    SimSiamProjectionHead,
)
from lightly.models.utils import deactivate_requires_grad, update_momentum

__all__ = ["BYOL", "SimSiam"]


class BYOL(nn.Module):
    """Bootstrap Your Own Latent.

    Online branch: ``encoder -> projection -> prediction``.
    Target branch: an EMA (momentum) copy of ``encoder -> projection`` with no
    predictor and stop-gradient. The symmetrised negative-cosine-similarity
    loss compares each online prediction to the other view's target projection.

    Parameters
    ----------
    encoder:
        A module exposing ``.embedding_dim`` and ``forward(x) -> (B, dim)``.
    projection_hidden, projection_out:
        Projection head dims (default 4096 / 256; brief also allows 2048 / 128).
    prediction_hidden:
        Predictor hidden dim (default 4096); predictor out = ``projection_out``.
    """

    def __init__(
        self,
        encoder: nn.Module,
        projection_hidden: int = 4096,
        projection_out: int = 256,
        prediction_hidden: int = 4096,
    ) -> None:
        super().__init__()
        self.encoder = encoder
        dim = encoder.embedding_dim
        self.projection_head = BYOLProjectionHead(dim, projection_hidden, projection_out)
        self.prediction_head = BYOLPredictionHead(projection_out, prediction_hidden, projection_out)

        # Target branch: momentum copies, frozen (updated only by EMA).
        self.target_encoder = copy.deepcopy(encoder)
        self.target_projection_head = copy.deepcopy(self.projection_head)
        deactivate_requires_grad(self.target_encoder)
        deactivate_requires_grad(self.target_projection_head)

        self.criterion = NegativeCosineSimilarity()

    def _online(self, x: torch.Tensor) -> torch.Tensor:
        return self.prediction_head(self.projection_head(self.encoder(x)))

    @torch.no_grad()
    def _target(self, x: torch.Tensor) -> torch.Tensor:
        return self.target_projection_head(self.target_encoder(x))

    def forward(self, x0: torch.Tensor, x1: torch.Tensor) -> torch.Tensor:
        """Return the symmetrised BYOL loss for a positive pair."""
        p0, p1 = self._online(x0), self._online(x1)
        z0, z1 = self._target(x0), self._target(x1)
        return 0.5 * (self.criterion(p0, z1) + self.criterion(p1, z0))

    @torch.no_grad()
    def update_target(self, tau: float) -> None:
        """EMA-update the target branch toward the online branch.

        ``tau`` is the momentum (target = tau*target + (1-tau)*online); it is
        typically cosine-annealed from ~0.996 toward 1.0 by the trainer.
        """
        update_momentum(self.encoder, self.target_encoder, m=tau)
        update_momentum(self.projection_head, self.target_projection_head, m=tau)

    def extract_embedding(self, x: torch.Tensor) -> torch.Tensor:
        """Return the encoder output (pre-projector), used for all evaluation."""
        return self.encoder(x)


class SimSiam(nn.Module):
    """SimSiam: a drop-in BYOL alternative with no momentum/target network.

    Both views go through ``encoder -> projection`` and a shared predictor; the
    loss is the symmetrised negative cosine similarity between each prediction
    and the *stop-gradient* projection of the other view. Lower memory and
    small-batch native. Watch for collapse: the loss should not crater to a
    trivial constant.
    """

    def __init__(
        self,
        encoder: nn.Module,
        projection_hidden: int = 2048,
        projection_out: int = 2048,
        prediction_hidden: int = 512,
    ) -> None:
        super().__init__()
        self.encoder = encoder
        dim = encoder.embedding_dim
        self.projection_head = SimSiamProjectionHead(dim, projection_hidden, projection_out)
        self.prediction_head = SimSiamPredictionHead(
            projection_out, prediction_hidden, projection_out
        )
        self.criterion = NegativeCosineSimilarity()

    def _forward_branch(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.projection_head(self.encoder(x))
        p = self.prediction_head(z)
        return z.detach(), p  # stop-gradient on the projection

    def forward(self, x0: torch.Tensor, x1: torch.Tensor) -> torch.Tensor:
        """Return the symmetrised SimSiam loss for a positive pair."""
        z0, p0 = self._forward_branch(x0)
        z1, p1 = self._forward_branch(x1)
        return 0.5 * (self.criterion(p0, z1) + self.criterion(p1, z0))

    def extract_embedding(self, x: torch.Tensor) -> torch.Tensor:
        """Return the encoder output (pre-projector), used for all evaluation."""
        return self.encoder(x)
