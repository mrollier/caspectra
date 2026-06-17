"""Extract encoder embeddings for evaluation (BUILD_BRIEF.md §3.6).

The encoder is frozen (no gradients) and we use ``extract_embedding`` so the
**pre-projector** feature is returned — that 512-d (or encoder-dim) vector is
what all evaluation operates on.
"""

from __future__ import annotations

import numpy as np
import torch
from torch.utils.data import DataLoader

__all__ = ["extract_embeddings"]


def extract_embeddings(
    model: torch.nn.Module, dataloader: DataLoader, device: torch.device
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(embeddings, rules, equiv_reps)`` for a single-view dataset.

    ``dataloader`` must yield ``(image, metadata)`` batches (i.e. the dataset's
    transform is ``None``). ``metadata`` carries collated ``rule`` and
    ``equiv_class_rep`` tensors.
    """
    model = model.to(device)
    model.eval()
    embeddings: list[np.ndarray] = []
    rules: list[np.ndarray] = []
    reps: list[np.ndarray] = []
    with torch.no_grad():
        for image, metadata in dataloader:
            feature = model.extract_embedding(image.to(device))
            embeddings.append(feature.cpu().numpy())
            rules.append(np.asarray(metadata["rule"]))
            reps.append(np.asarray(metadata["equiv_class_rep"]))
    return (
        np.concatenate(embeddings, axis=0),
        np.concatenate(rules, axis=0),
        np.concatenate(reps, axis=0),
    )
