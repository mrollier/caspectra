"""Tests for train/trainer.py (BUILD_BRIEF.md §3.5, §5)."""

from __future__ import annotations

import torch
from torch.utils.data import DataLoader

from caspectra.config import TrainConfig
from caspectra.data.augmentations import AugmentationConfig, TwoViewTransform
from caspectra.data.dataset import SpacetimeDataset
from caspectra.models.byol import BYOL, SimSiam
from caspectra.models.encoder import SmallCNNEncoder
from caspectra.train.trainer import Trainer, collapse_std
from caspectra.utils import set_seed


def test_collapse_std_is_zero_for_constant_embeddings() -> None:
    """A collapsed encoder emits identical vectors -> zero spread."""
    assert collapse_std(torch.ones(8, 16)) < 1e-6


def test_collapse_std_is_positive_for_varied_embeddings() -> None:
    torch.manual_seed(0)
    assert collapse_std(torch.randn(8, 16)) > 0.05


def _loader(tmp_path, n_ic: int = 8, grid: int = 32) -> DataLoader:
    ds = SpacetimeDataset(
        rules=[90, 110, 30],
        n_ic_per_rule=n_ic,
        grid_size=grid,
        cache_dir=str(tmp_path / "cache"),
        seed=0,
        transform=TwoViewTransform(AugmentationConfig()),
    )
    return DataLoader(ds, batch_size=8, shuffle=True, drop_last=True)


def _train_config(tmp_path, **kwargs) -> TrainConfig:
    defaults = dict(epochs=10, output_dir=str(tmp_path / "run"), checkpoint_every=5)
    defaults.update(kwargs)
    return TrainConfig(**defaults)


def test_training_reduces_loss_on_tiny_subset(tmp_path) -> None:
    """The §5 gate: loss must decrease on a tiny subset before any long run."""
    set_seed(0)
    loader = _loader(tmp_path)
    model = SimSiam(SmallCNNEncoder(embedding_dim=32))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    trainer = Trainer(model, loader, optimizer, torch.device("cpu"), _train_config(tmp_path))
    history = trainer.train()
    assert len(history) == 10
    assert history[-1] < history[0]  # loss decreased
    # Loss going down is not enough: the model must not have collapsed.
    assert len(trainer.std_history) == 10
    assert trainer.std_history[-1] > 1e-3  # embeddings retain spread


def test_trainer_writes_csv_checkpoint_and_plot(tmp_path) -> None:
    set_seed(0)
    loader = _loader(tmp_path)
    model = SimSiam(SmallCNNEncoder(embedding_dim=32))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    cfg = _train_config(tmp_path, epochs=4, checkpoint_every=2)
    trainer = Trainer(model, loader, optimizer, torch.device("cpu"), cfg)
    trainer.train()

    output_dir = tmp_path / "run"
    assert (output_dir / "loss_log.csv").exists()
    assert (output_dir / "loss_curve.png").exists()
    assert (output_dir / "checkpoint_final.pt").exists()

    # CSV has a header + one row per epoch, and logs the collapse metric.
    lines = (output_dir / "loss_log.csv").read_text().strip().splitlines()
    assert lines[0] == "epoch,loss,embedding_std"
    assert len(lines) == 1 + 4


def test_byol_training_runs_and_updates_target(tmp_path) -> None:
    set_seed(0)
    loader = _loader(tmp_path)
    model = BYOL(SmallCNNEncoder(embedding_dim=32))
    before = [p.clone() for p in model.target_encoder.parameters()]
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    cfg = _train_config(tmp_path, epochs=2)
    trainer = Trainer(model, loader, optimizer, torch.device("cpu"), cfg)
    history = trainer.train()
    assert len(history) == 2
    after = list(model.target_encoder.parameters())
    # EMA must have moved the target network during training.
    assert any(not torch.equal(a, b) for a, b in zip(after, before))


def test_checkpoint_is_loadable(tmp_path) -> None:
    set_seed(0)
    loader = _loader(tmp_path)
    model = SimSiam(SmallCNNEncoder(embedding_dim=32))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    cfg = _train_config(tmp_path, epochs=2)
    trainer = Trainer(model, loader, optimizer, torch.device("cpu"), cfg)
    trainer.train()
    ckpt = torch.load(tmp_path / "run" / "checkpoint_final.pt", weights_only=False)
    assert "model_state" in ckpt
    assert "epoch" in ckpt
    model2 = SimSiam(SmallCNNEncoder(embedding_dim=32))
    model2.load_state_dict(ckpt["model_state"])  # loads without error
