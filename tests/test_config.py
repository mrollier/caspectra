"""Tests for caspectra/config.py (BUILD_BRIEF.md §3.9)."""

from __future__ import annotations

from pathlib import Path

from caspectra.config import (
    DataConfig,
    EvalConfig,
    ExperimentConfig,
    ModelConfig,
    TrainConfig,
)

_CONFIGS = Path(__file__).resolve().parent.parent / "configs"


def test_defaults_match_brief() -> None:
    cfg = ExperimentConfig()
    assert cfg.data.grid_size == 127  # odd on purpose; powers of two collapse additive rules
    assert cfg.data.n_ic_per_rule == 256
    assert cfg.model.method == "byol"
    assert cfg.model.norm_layer == "group"
    # Augmentations: shift + coarse-grain ON, plus the two class-defining
    # symmetries flip (reflection) + invert (complementation) ON by default.
    assert cfg.data.augmentation.cyclic_shift is True
    assert cfg.data.augmentation.coarse_grain is True
    assert cfg.data.augmentation.horizontal_flip is True
    assert cfg.data.augmentation.invert is True


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


def test_shipped_configs_enable_the_symmetry_augmentations() -> None:
    """default.yaml and smoke.yaml turn the class-defining symmetries ON."""
    for name in ("default.yaml", "smoke.yaml"):
        aug = ExperimentConfig.from_yaml(_CONFIGS / name).data.augmentation
        assert aug.horizontal_flip is True, name
        assert aug.invert is True, name


def test_no_symmetry_config_is_the_ablation_arm() -> None:
    """no_symmetry.yaml is the with/without-symmetry ablation: both OFF."""
    aug = ExperimentConfig.from_yaml(_CONFIGS / "no_symmetry.yaml").data.augmentation
    assert aug.horizontal_flip is False
    assert aug.invert is False


def test_yaml_round_trip_preserves_nested_augmentation(tmp_path) -> None:
    cfg = ExperimentConfig()
    cfg.data.augmentation.horizontal_flip = True
    cfg.data.augmentation.mode = "asymmetric_coarse"
    path = tmp_path / "config.yaml"
    cfg.to_yaml(path)
    loaded = ExperimentConfig.from_yaml(path)
    assert loaded.data.augmentation.horizontal_flip is True
    assert loaded.data.augmentation.mode == "asymmetric_coarse"
