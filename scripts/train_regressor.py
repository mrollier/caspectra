#!/usr/bin/env python3
"""Train the Lever A invariant regressor (FOUNDATIONS.md §4; criterion 6).

Thin CLI mirroring ``scripts/train.py``: parse a YAML config, build the
leave-rules-out split, the cached invariant targets and the model via the
factory, and run the :class:`~caspectra.train.regression_trainer.RegressionTrainer`.

Example
-------
    PYTORCH_ENABLE_MPS_FALLBACK=1 python scripts/train_regressor.py \
        --config configs/lever_a_smoke.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from torch.utils.data import Subset

from caspectra.config import ExperimentConfig
from caspectra.data.splits import leave_rules_out_split
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.labels import load_rule_labels
from caspectra.factory import build_dataloader, build_dataset, build_model, build_optimizer
from caspectra.train.regression_trainer import RegressionTrainer
from caspectra.utils import ensure_dir, save_json, select_device, set_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the invariant regressor (Lever A).")
    parser.add_argument("--config", required=True, help="Path to a YAML ExperimentConfig.")
    parser.add_argument("--device", default="mps", help="Preferred device (mps/cpu/cuda).")
    parser.add_argument("--output-dir", default=None, help="Override train.output_dir.")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override cfg.seed (weight init + minibatch/augmentation order). The data "
        "split, diagram cache and targets are keyed on their own seeds, so a --seed sweep "
        "measures pure optimisation-seed variance (S2 error bars, EVALUATION_CRITERIA rev 6).",
    )
    parser.add_argument(
        "--selection-frac",
        type=float,
        default=0.0,
        help="Rev-13 M9: fraction of each TRAINING rule's diagrams held out as an inner "
        "fold for validation-based checkpoint selection (writes checkpoint_selected.pt). "
        "0.0 (default) reproduces the rev-10 final-epoch protocol exactly. The held-out "
        "RULE panel is never used for selection — that would be selection on the test set; "
        "holding out diagrams instead keeps every training rule in the training set, so "
        "the selection rule is the only variable that changes.",
    )
    parser.add_argument(
        "--selection-seed",
        type=int,
        default=13,
        help="Seed for the inner-fold diagram draw (fixed before measurement, rev 13).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    if cfg.model.method != "regressor":
        raise SystemExit(f"model.method must be 'regressor', got {cfg.model.method!r}")
    if args.output_dir is not None:
        cfg.train.output_dir = args.output_dir
    if args.seed is not None:
        cfg.seed = args.seed

    set_seed(cfg.seed)
    device = select_device(prefer=args.device)
    output_dir = ensure_dir(cfg.train.output_dir)
    cfg.to_yaml(output_dir / "config.yaml")
    save_json({"device": str(device)}, output_dir / "device.json")
    print(f"[lever-a] device={device} output_dir={output_dir}")

    # Two dataset views over the same cached diagrams: augmented single-view for
    # training, raw for held-out validation (matches eval-time extraction).
    ds_train = build_dataset(cfg.data, training=True, single_view=True)
    ds_raw = build_dataset(cfg.data, training=False)
    rules = sorted({int(r) for r in ds_train.equiv_reps})

    # Leave-rules-out split, stratified by Wolfram class when labels exist.
    labels = load_rule_labels(cfg.eval.rule_labels_csv)
    strata = (
        labels.wolfram_array(rules) if (labels and labels.has_wolfram) else np.zeros(len(rules))
    )
    train_rules, holdout_rules = leave_rules_out_split(
        rules,
        strata,
        holdout_fraction=cfg.train.holdout_fraction,
        seed=cfg.train.holdout_seed,
        force_holdout=cfg.train.force_holdout_rules,
        force_train=cfg.train.force_train_rules,
    )
    print(f"[lever-a] split: {len(train_rules)} train rules, {len(holdout_rules)} held out")
    print(f"[lever-a] held-out rules: {holdout_rules}")

    # Per-rule invariant targets under the same observation protocol (cached).
    matrix = load_or_compute_invariant_targets(
        rules,
        width=cfg.data.grid_size,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=cfg.data.radius,
    )
    targets_by_rule = {r: matrix[i] for i, r in enumerate(rules)}

    train_mask = np.isin(ds_train.equiv_reps, train_rules)
    train_idx = np.flatnonzero(train_mask)

    # Rev-13 M9 inner selection fold: a fixed-seed, per-rule-stratified slice of
    # the training diagrams. Disjoint from both the training batches and the
    # held-out rule panel, so selecting on it leaks nothing.
    select_idx: np.ndarray = np.empty(0, dtype=int)
    if args.selection_frac > 0:
        if not 0 < args.selection_frac < 0.5:
            raise SystemExit(f"--selection-frac must be in (0, 0.5), got {args.selection_frac}")
        rng = np.random.default_rng(np.random.SeedSequence([args.selection_seed, cfg.seed]))
        reps_train = np.asarray(ds_train.equiv_reps)[train_idx]
        picked = []
        for rule in train_rules:
            rule_pos = np.flatnonzero(reps_train == rule)
            if rule_pos.size < 2:  # never strip a rule of all its diagrams
                continue
            k = max(1, int(round(args.selection_frac * rule_pos.size)))
            k = min(k, rule_pos.size - 1)
            picked.append(rng.choice(rule_pos, size=k, replace=False))
        select_pos = np.sort(np.concatenate(picked)) if picked else np.empty(0, dtype=int)
        select_idx = train_idx[select_pos]
        train_idx = np.setdiff1d(train_idx, select_idx)
        print(
            f"[lever-a] rev-13 selection fold: {len(select_idx)} diagrams held out of "
            f"{len(train_idx) + len(select_idx)} training diagrams "
            f"({len(train_rules)} training rules all retained)"
        )

    train_loader = build_dataloader(
        Subset(ds_train, train_idx.tolist()),
        batch_size=cfg.train.batch_size,
        shuffle=True,
        num_workers=cfg.train.num_workers,
        drop_last=True,
    )
    val_loader = build_dataloader(
        Subset(ds_raw, np.flatnonzero(~train_mask).tolist()),
        batch_size=cfg.eval.batch_size,
        shuffle=False,
        num_workers=cfg.train.num_workers,
    )
    select_loader = (
        build_dataloader(
            Subset(ds_raw, select_idx.tolist()),
            batch_size=cfg.eval.batch_size,
            shuffle=False,
            num_workers=cfg.train.num_workers,
        )
        if select_idx.size
        else None
    )
    print(
        f"[lever-a] {len(train_idx)} train diagrams "
        f"({len(train_loader)} batches/epoch), {int((~train_mask).sum())} val diagrams"
    )

    model = build_model(cfg.model)
    optimizer = build_optimizer(model, cfg.train)
    trainer = RegressionTrainer(
        model,
        train_loader,
        val_loader,
        optimizer,
        device,
        cfg.train,
        targets_by_rule=targets_by_rule,
        train_rules=train_rules,
        holdout_rules=holdout_rules,
        target_names=TARGET_NAMES,
        select_loader=select_loader,
    )
    history = trainer.train()
    final_r2 = trainer.val_r2_history[-1]
    print(f"[lever-a] done. train MSE {history[0]:.4f} -> {history[-1]:.4f}")
    print(
        "[lever-a] final held-out R² per feature: "
        + ", ".join(f"{n}={v:.3f}" for n, v in zip(TARGET_NAMES, final_r2))
    )
    print(f"[lever-a] artifacts in {Path(output_dir).resolve()}")


if __name__ == "__main__":
    main()
