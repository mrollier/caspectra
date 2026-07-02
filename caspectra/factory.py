"""Builders that turn config dataclasses into concrete objects (§3.9).

Keeping construction in one place lets the scripts stay thin CLIs: they parse a
config, call these builders, and run. No business logic lives in the scripts.
"""

from __future__ import annotations

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from caspectra.config import DataConfig, ModelConfig, TrainConfig
from caspectra.data.augmentations import SingleViewTransform, TwoViewTransform
from caspectra.data.dataset import SpacetimeDataset
from caspectra.models.byol import BYOL, SimSiam
from caspectra.models.encoder import AntiCheatCNN, ResNet18Encoder, SmallCNNEncoder
from caspectra.models.regressor import InvariantRegressor

__all__ = [
    "build_encoder",
    "build_model",
    "build_optimizer",
    "build_dataset",
    "build_dataloader",
]


def build_encoder(cfg: ModelConfig) -> nn.Module:
    """Construct the encoder named in ``cfg``."""
    if cfg.encoder == "resnet18":
        return ResNet18Encoder(
            width_multiplier=cfg.width_multiplier,
            small_input=cfg.small_input,
            norm_layer=cfg.norm_layer,
            num_groups=cfg.num_groups,
        )
    if cfg.encoder == "smallcnn":
        return SmallCNNEncoder(
            embedding_dim=cfg.embedding_dim,
            norm_layer=cfg.norm_layer,
            num_groups=cfg.num_groups,
        )
    if cfg.encoder == "anticheat":
        return AntiCheatCNN(
            embedding_dim=cfg.embedding_dim,
            norm_layer=cfg.norm_layer,
            num_groups=cfg.num_groups,
        )
    raise ValueError(
        f"Unknown encoder {cfg.encoder!r}; expected 'resnet18', 'smallcnn' or 'anticheat'."
    )


def build_model(cfg: ModelConfig) -> nn.Module:
    """Construct the method wrapper (BYOL / SimSiam / InvariantRegressor)."""
    encoder = build_encoder(cfg)
    if cfg.method == "byol":
        return BYOL(
            encoder,
            projection_hidden=cfg.projection_hidden,
            projection_out=cfg.projection_out,
            prediction_hidden=cfg.prediction_hidden,
        )
    if cfg.method == "simsiam":
        return SimSiam(encoder)
    if cfg.method == "regressor":
        return InvariantRegressor(encoder, n_targets=cfg.n_targets)
    raise ValueError(f"Unknown method {cfg.method!r}; expected 'byol', 'simsiam' or 'regressor'.")


def build_optimizer(model: nn.Module, cfg: TrainConfig) -> torch.optim.Optimizer:
    """Construct the optimizer named in ``cfg``."""
    if cfg.optimizer == "adamw":
        return torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    if cfg.optimizer == "sgd":
        return torch.optim.SGD(
            model.parameters(),
            lr=cfg.lr,
            momentum=cfg.momentum,
            weight_decay=cfg.weight_decay,
        )
    raise ValueError(f"Unknown optimizer {cfg.optimizer!r}; expected 'adamw' or 'sgd'.")


def build_dataset(
    cfg: DataConfig, training: bool, *, single_view: bool = False
) -> SpacetimeDataset:
    """Build a dataset; ``training`` toggles augmentation.

    For SSL training a :class:`TwoViewTransform` produces positive pairs; with
    ``single_view=True`` (the Lever A regressor) the same stack is applied once
    per sample instead. For embedding extraction (evaluation) the transform is
    ``None`` so raw images are returned.
    """
    if not training:
        transform = None
    elif single_view:
        transform = SingleViewTransform(cfg.augmentation)
    else:
        transform = TwoViewTransform(cfg.augmentation)
    return SpacetimeDataset(
        rules=cfg.rules,
        n_ic_per_rule=cfg.n_ic_per_rule,
        grid_size=cfg.grid_size,
        discard_transient=cfg.discard_transient,
        cache_dir=cfg.cache_dir,
        seed=cfg.seed,
        transform=transform,
    )


def build_dataloader(
    dataset: SpacetimeDataset,
    batch_size: int,
    *,
    shuffle: bool,
    num_workers: int = 2,
    drop_last: bool = False,
) -> DataLoader:
    """Build a DataLoader with macOS-friendly worker settings.

    ``persistent_workers`` is only enabled when workers are actually used.
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        persistent_workers=num_workers > 0,
        drop_last=drop_last,
    )
