"""Dataclass configuration for experiments, with YAML load/save (§3.9).

The configs are plain ``@dataclass`` objects so they are easy to read, diff and
serialise. Every script takes ``--config path.yaml`` and writes the resolved
config into its output directory for reproducibility.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from caspectra.data.augmentations import AugmentationConfig

__all__ = [
    "DataConfig",
    "ModelConfig",
    "TrainConfig",
    "EvalConfig",
    "ExperimentConfig",
]


@dataclass
class DataConfig:
    """Dataset generation and augmentation settings."""

    rules: list[int] | None = None  # None -> the 88 independent representatives
    n_ic_per_rule: int = 256
    # Odd (non-power-of-two) on purpose: a power-of-two side length makes additive
    # rules such as rule 90 collapse to a homogeneous state under periodic
    # boundaries (see caspectra.utils.warn_if_pathological_grid). 127 is a Mersenne prime.
    grid_size: int = 127
    discard_transient: int = 0
    cache_dir: str = "cache"
    seed: int = 0
    augmentation: AugmentationConfig = field(default_factory=AugmentationConfig)


@dataclass
class ModelConfig:
    """Encoder and SSL-method settings."""

    method: str = "byol"  # "byol" or "simsiam"
    encoder: str = "resnet18"  # "resnet18" or "smallcnn"
    width_multiplier: float = 1.0
    small_input: bool = False
    norm_layer: str = "group"  # "group" (default) or "batch"
    num_groups: int = 8
    embedding_dim: int = 256  # SmallCNN only
    projection_hidden: int = 4096
    projection_out: int = 256
    prediction_hidden: int = 4096


@dataclass
class TrainConfig:
    """Training-loop settings."""

    epochs: int = 100
    batch_size: int = 128
    lr: float = 1e-3
    weight_decay: float = 1e-6
    optimizer: str = "adamw"  # "adamw" or "sgd"
    momentum: float = 0.9  # SGD only
    tau_base: float = 0.996  # BYOL EMA momentum, cosine-annealed toward 1.0
    checkpoint_every: int = 10
    num_workers: int = 2
    output_dir: str = "runs/exp"


@dataclass
class EvalConfig:
    """Evaluation settings (probes, clustering, visualisation)."""

    checkpoint: str = ""
    rule_labels_csv: str = "rule_labels.csv"
    batch_size: int = 256
    umap_components: int = 10
    umap_metric: str = "cosine"
    hdbscan_min_cluster_size: int = 15
    hdbscan_min_samples: int = 5
    output_dir: str = "runs/exp/eval"


@dataclass
class ExperimentConfig:
    """Top-level config bundling all sections plus a global seed."""

    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    seed: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_yaml(self, path: str | Path) -> None:
        Path(path).write_text(yaml.safe_dump(self.to_dict(), sort_keys=False))

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ExperimentConfig:
        data = dict(d.get("data", {}))
        aug = data.pop("augmentation", {})
        return cls(
            data=DataConfig(**data, augmentation=AugmentationConfig(**aug)),
            model=ModelConfig(**d.get("model", {})),
            train=TrainConfig(**d.get("train", {})),
            eval=EvalConfig(**d.get("eval", {})),
            seed=d.get("seed", 0),
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> ExperimentConfig:
        return cls.from_dict(yaml.safe_load(Path(path).read_text()))
