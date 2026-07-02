"""Tests for the Lever A invariant regressor: model, trainer, config."""

from __future__ import annotations

import numpy as np
import torch
from torch.utils.data import Subset

from caspectra.config import ExperimentConfig, TrainConfig
from caspectra.data.augmentations import AugmentationConfig, SingleViewTransform
from caspectra.data.dataset import SpacetimeDataset
from caspectra.data.splits import leave_rules_out_split
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.factory import build_dataloader
from caspectra.models.encoder import AntiCheatCNN, SmallCNNEncoder
from caspectra.models.regressor import InvariantRegressor
from caspectra.train.regression_trainer import RegressionTrainer, r2_per_feature
from caspectra.utils import set_seed

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


def test_regressor_shapes() -> None:
    model = InvariantRegressor(AntiCheatCNN(embedding_dim=32), n_targets=4)
    x = torch.rand(3, 1, 63, 63)
    assert model(x).shape == (3, 4)
    assert model.extract_embedding(x).shape == (3, 32)
    pmap = model.predict_map(x)
    assert pmap.shape[:2] == (3, 4)
    assert pmap.shape[2] > 1 and pmap.shape[3] > 1


def test_predict_map_mean_equals_global_prediction() -> None:
    """GAP∘linear = mean of per-patch linear outputs — the identity that makes
    the per-patch phenotype maps consistent with the trained global head."""
    for encoder in (AntiCheatCNN(embedding_dim=16), SmallCNNEncoder(embedding_dim=16)):
        model = InvariantRegressor(encoder, n_targets=3).eval()
        x = torch.rand(2, 1, 63, 63)
        with torch.no_grad():
            global_pred = model(x)
            map_mean = model.predict_map(x).mean(dim=(-2, -1))
        assert torch.allclose(global_pred, map_mean, atol=1e-5)


def test_shallow_encoder_channels() -> None:
    """3 blocks -> one fewer pooling stage -> 15x15 map at 127px (vs 7x7), and
    the predict_map identity must survive the depth change."""
    from caspectra.config import ModelConfig
    from caspectra.factory import build_model

    cfg = ModelConfig(
        method="regressor", encoder="anticheat", embedding_dim=16, encoder_channels=[8, 16, 32]
    )
    model = build_model(cfg).eval()
    x = torch.rand(2, 1, 127, 127)
    with torch.no_grad():
        pmap = model.predict_map(x)
        assert pmap.shape == (2, 4, 15, 15)
        assert torch.allclose(model(x), pmap.mean(dim=(-2, -1)), atol=1e-5)
    # Default (None) keeps the 4-block geometry.
    deep = build_model(
        ModelConfig(method="regressor", encoder="anticheat", embedding_dim=16)
    ).eval()
    with torch.no_grad():
        assert deep.predict_map(x).shape == (2, 4, 7, 7)


# ---------------------------------------------------------------------------
# r2 helper
# ---------------------------------------------------------------------------


def test_r2_per_feature_perfect_and_constant() -> None:
    y = np.array([[0.0, 1.0], [1.0, 1.0], [2.0, 1.0]])
    r2 = r2_per_feature(y.copy(), y)
    assert r2[0] == 1.0
    assert np.isnan(r2[1])  # constant target column -> undefined, not a crash


# ---------------------------------------------------------------------------
# Trainer (tiny end-to-end run on CPU)
# ---------------------------------------------------------------------------


def _tiny_setup(tmp_path):
    rules = [0, 30, 110, 204]
    common = dict(
        rules=rules, n_ic_per_rule=8, grid_size=31, cache_dir=str(tmp_path / "cache"), seed=0
    )
    ds_train = SpacetimeDataset(
        **common, transform=SingleViewTransform(AugmentationConfig(coarse_grain=False))
    )
    ds_raw = SpacetimeDataset(**common, transform=None)
    matrix = load_or_compute_invariant_targets(
        rules, width=31, n_pairs=8, cache_dir=tmp_path / "cache"
    )
    targets_by_rule = {r: matrix[i] for i, r in enumerate(rules)}
    train_rules, holdout_rules = leave_rules_out_split(
        rules, [1, 3, 4, 2], holdout_fraction=0.25, force_holdout=(110,), force_train=(30,)
    )
    train_idx = np.flatnonzero(np.isin(ds_train.equiv_reps, train_rules)).tolist()
    val_idx = np.flatnonzero(np.isin(ds_raw.equiv_reps, holdout_rules)).tolist()
    train_loader = build_dataloader(
        Subset(ds_train, train_idx), batch_size=8, shuffle=True, num_workers=0, drop_last=True
    )
    val_loader = build_dataloader(
        Subset(ds_raw, val_idx), batch_size=8, shuffle=False, num_workers=0
    )
    return train_loader, val_loader, targets_by_rule, train_rules, holdout_rules


def test_regression_trainer_end_to_end(tmp_path) -> None:
    set_seed(0)
    train_loader, val_loader, targets_by_rule, train_rules, holdout_rules = _tiny_setup(tmp_path)
    model = InvariantRegressor(SmallCNNEncoder(embedding_dim=16), n_targets=len(TARGET_NAMES))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    cfg = TrainConfig(epochs=3, output_dir=str(tmp_path / "run"), checkpoint_every=2)
    trainer = RegressionTrainer(
        model,
        train_loader,
        val_loader,
        optimizer,
        torch.device("cpu"),
        cfg,
        targets_by_rule=targets_by_rule,
        train_rules=train_rules,
        holdout_rules=holdout_rules,
        target_names=TARGET_NAMES,
    )
    history = trainer.train()
    assert len(history) == 3
    assert history[-1] < history[0]  # loss decreased

    out = tmp_path / "run"
    lines = (out / "loss_log.csv").read_text().strip().splitlines()
    expected = (
        "epoch,train_loss," + ",".join(f"val_r2_{n}" for n in TARGET_NAMES) + ",val_r2_median"
    )
    assert lines[0] == expected
    assert len(lines) == 1 + 3
    assert (out / "loss_curve.png").exists()

    # Checkpoint carries everything evaluation needs.
    ckpt = torch.load(out / "checkpoint_final.pt", weights_only=False)
    assert ckpt["holdout_rules"] == holdout_rules
    assert ckpt["scaler_mean"].shape == (len(TARGET_NAMES),)
    model2 = InvariantRegressor(SmallCNNEncoder(embedding_dim=16), n_targets=len(TARGET_NAMES))
    model2.load_state_dict(ckpt["model_state"])  # loads without error


def test_scaler_fit_on_train_rules_only(tmp_path) -> None:
    """The leakage guard: held-out rules must not influence the standardization."""
    set_seed(0)
    train_loader, val_loader, targets_by_rule, train_rules, holdout_rules = _tiny_setup(tmp_path)
    model = InvariantRegressor(SmallCNNEncoder(embedding_dim=16), n_targets=len(TARGET_NAMES))
    trainer = RegressionTrainer(
        model,
        train_loader,
        val_loader,
        torch.optim.AdamW(model.parameters()),
        torch.device("cpu"),
        TrainConfig(epochs=1, output_dir=str(tmp_path / "run2")),
        targets_by_rule=targets_by_rule,
        train_rules=train_rules,
        holdout_rules=holdout_rules,
        target_names=TARGET_NAMES,
    )
    expected_mean = np.stack([targets_by_rule[r] for r in train_rules]).mean(axis=0)
    assert np.allclose(trainer.scaler_mean, expected_mean)


# ---------------------------------------------------------------------------
# Config round-trip (also validates the committed YAML files)
# ---------------------------------------------------------------------------


def test_lever_a_configs_parse() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    for path in (
        root / "configs/lever_a.yaml",
        root / "configs/lever_a_smoke.yaml",
        root / "configs/lever_a_shallow.yaml",
        root / "configs/lever_a_shallow_smoke.yaml",
        root / "configs/lever_a_local.yaml",
        root / "configs/lever_a_local_smoke.yaml",
    ):
        cfg = ExperimentConfig.from_yaml(path)
        assert cfg.model.method == "regressor"
        assert cfg.model.n_targets == len(TARGET_NAMES)
        assert cfg.train.force_holdout_rules == [110]
        assert cfg.train.force_train_rules == [54]
        assert cfg.data.augmentation.coarse_grain is False
        assert cfg.targets.n_pairs >= 64
        if "shallow" in path.name:
            assert cfg.model.encoder_channels == [16, 32, 64]
        if "local" in path.name:
            assert cfg.model.norm_layer == "batch"
