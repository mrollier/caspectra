"""Tests for caspectra/config.py (BUILD_BRIEF.md §3.9)."""

from __future__ import annotations

from caspectra.config import (
    DataConfig,
    EvalConfig,
    ExperimentConfig,
    ModelConfig,
    TrainConfig,
)


def test_defaults_match_brief() -> None:
    cfg = ExperimentConfig()
    assert cfg.data.grid_size == 128
    assert cfg.data.n_ic_per_rule == 256
    assert cfg.model.method == "byol"
    assert cfg.model.norm_layer == "group"
    # Augmentations: shift + coarse-grain ON, flip + invert OFF.
    assert cfg.data.augmentation.cyclic_shift is True
    assert cfg.data.augmentation.coarse_grain is True
    assert cfg.data.augmentation.horizontal_flip is False
    assert cfg.data.augmentation.invert is False


def test_yaml_round_trip_preserves_config(tmp_path) -> None:
    cfg = ExperimentConfig(
        data=DataConfig(grid_size=64, n_ic_per_rule=16),
        model=ModelConfig(method="simsiam", encoder="smallcnn"),
        train=TrainConfig(epochs=3, batch_size=32),
        eval=EvalConfig(umap_components=20),
    )
    path = tmp_path / "config.yaml"
    cfg.to_yaml(path)
    loaded = ExperimentConfig.from_yaml(path)
    assert loaded.data.grid_size == 64
    assert loaded.data.n_ic_per_rule == 16
    assert loaded.model.method == "simsiam"
    assert loaded.model.encoder == "smallcnn"
    assert loaded.train.epochs == 3
    assert loaded.train.batch_size == 32
    assert loaded.eval.umap_components == 20


def test_yaml_round_trip_preserves_nested_augmentation(tmp_path) -> None:
    cfg = ExperimentConfig()
    cfg.data.augmentation.horizontal_flip = True
    cfg.data.augmentation.mode = "asymmetric_coarse"
    path = tmp_path / "config.yaml"
    cfg.to_yaml(path)
    loaded = ExperimentConfig.from_yaml(path)
    assert loaded.data.augmentation.horizontal_flip is True
    assert loaded.data.augmentation.mode == "asymmetric_coarse"
