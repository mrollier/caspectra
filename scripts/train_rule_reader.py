#!/usr/bin/env python3
"""F2 (EVALUATION_CRITERIA.md rev 9): train the learned rule-reader.

Supervised: diagram -> the generating rule's table bits (BCE per entry), on
**training-split rules only** (the registered leave-rules-out split from the
config/checkpoint; held-out rules are never seen). Degradation augmentation is
applied on the fly with ranges **fixed here, before training** (rev-9 F2):
each training view independently receives bit-flip noise with p ~ U(0, 0.15)
and cell masking (zero-fill) with p ~ U(0, 0.5), each applied with probability
1/2. Symmetry augmentations are deliberately OFF — the target is the literal
table of the generating rule.

Gated per CLAUDE.md: run the 63 px / smoke config first, then ask before the
full 127 px run.

Usage::

    python scripts/train_rule_reader.py --config configs/m4_range2_smoke.yaml --epochs 4
    python scripts/train_rule_reader.py --config configs/m4_range2.yaml --epochs 15
"""

from __future__ import annotations

import argparse
import time

import numpy as np
import torch
from torch import nn

from caspectra.config import ExperimentConfig
from caspectra.data.splits import leave_rules_out_split
from caspectra.eval.labels import load_rule_labels
from caspectra.factory import build_dataset
from caspectra.models.rule_reader import RuleReader
from caspectra.utils import ensure_dir, save_json, select_device, set_seed

# Registered augmentation ranges (rev-9 F2) — fixed before training; the F3
# grid's test corruption levels are not tuned on.
AUG_NOISE_MAX = 0.15
AUG_MASK_MAX = 0.5
AUG_APPLY_P = 0.5


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="F2 rule-reader training (rev 9; gated).")
    p.add_argument("--config", required=True)
    p.add_argument("--epochs", type=int, default=15)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--channels", type=int, default=64)
    p.add_argument("--hidden", type=int, default=128)
    p.add_argument("--device", default="mps")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--output", default=None, help="Checkpoint path (default under output_dir).")
    return p.parse_args()


def _augment(batch: torch.Tensor, rng: np.random.Generator) -> torch.Tensor:
    """Bit-flip + mask degradation, per registered ranges. ``batch``: (B,1,H,W) 0/1.

    Vectorised: per-sample corruption levels p ~ U(0, max), each family applied
    with probability ``AUG_APPLY_P`` (gate folded into p by zeroing it).
    """
    B = batch.shape[0]
    shape = (B, 1, 1, 1)
    p_noise = rng.uniform(0.0, AUG_NOISE_MAX, size=shape) * (rng.random(shape) < AUG_APPLY_P)
    p_mask = rng.uniform(0.0, AUG_MASK_MAX, size=shape) * (rng.random(shape) < AUG_APPLY_P)
    flips = torch.from_numpy((rng.random(batch.shape) < p_noise).astype(np.float32))
    keep = torch.from_numpy((rng.random(batch.shape) >= p_mask).astype(np.float32))
    return ((batch + flips) % 2.0) * keep


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out_dir = ensure_dir(cfg.train.output_dir)
    ckpt_path = args.output or str(out_dir / f"rule_reader_seed{args.seed}.pt")
    set_seed(args.seed)
    radius = cfg.data.radius
    tsize = 1 << (2 * radius + 1)

    ds = build_dataset(cfg.data, training=False)  # raw diagrams; no symmetry augs
    reps = np.asarray(ds.equiv_reps)
    images = ds.images
    rules = sorted({int(r) for r in reps})

    labels = load_rule_labels(cfg.eval.rule_labels_csv)
    strata = (
        np.array([int(labels.wolfram.get(int(r), -1)) for r in rules])
        if labels and labels.has_wolfram
        else np.zeros(len(rules))
    )
    train_rules, holdout_rules = leave_rules_out_split(
        rules,
        strata,
        holdout_fraction=cfg.train.holdout_fraction,
        seed=cfg.train.holdout_seed,
        force_holdout=cfg.train.force_holdout_rules,
        force_train=cfg.train.force_train_rules,
    )
    tr_mask = np.isin(reps, train_rules)
    X = torch.from_numpy(images[tr_mask].astype(np.float32)).unsqueeze(1)
    bits = np.stack([[(int(r) >> k) & 1 for k in range(tsize)] for r in reps[tr_mask]]).astype(
        np.float32
    )
    Y = torch.from_numpy(bits)
    # Validation on held-in rules' held-out diagrams is unnecessary; the F3 grid
    # is the real test. A small train-split tail monitors optimisation only.
    n_val = max(64, len(X) // 20)
    perm = torch.randperm(len(X), generator=torch.Generator().manual_seed(args.seed))
    X, Y = X[perm], Y[perm]
    Xv, Yv, X, Y = X[:n_val], Y[:n_val], X[n_val:], Y[n_val:]
    print(
        f"[f2] radius={radius} table={tsize} bits  train diagrams={len(X)} "
        f"(rules={len(train_rules)}; {len(holdout_rules)} held-out rules untouched)"
    )

    device = select_device(prefer=args.device)
    model = RuleReader(radius=radius, channels=args.channels, hidden=args.hidden).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-6)
    lossf = nn.BCEWithLogitsLoss()
    rng = np.random.default_rng(args.seed)
    print(f"[f2] RuleReader params={n_params:,} device={device}")

    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        t0 = time.perf_counter()
        order = torch.randperm(len(X))
        total_loss, n_batches = 0.0, 0
        for s in range(0, len(X), args.batch_size):
            idx = order[s : s + args.batch_size]
            xb = _augment(X[idx], rng).to(device)
            yb = Y[idx].to(device)
            opt.zero_grad()
            loss = lossf(model(xb), yb)
            loss.backward()
            opt.step()
            total_loss += float(loss.item())
            n_batches += 1
        model.eval()
        with torch.no_grad():
            val_logits = model(Xv.to(device))
            val_bits = (torch.sigmoid(val_logits) >= 0.5).float().cpu()
            bit_acc = float((val_bits == Yv).float().mean())
            exact = float((val_bits == Yv).all(dim=1).float().mean())
        dt = time.perf_counter() - t0
        history.append(
            {
                "epoch": epoch,
                "loss": round(total_loss / n_batches, 4),
                "val_bit_acc": round(bit_acc, 4),
                "val_exact": round(exact, 4),
            }
        )
        print(
            f"[f2] epoch {epoch:>3}: loss {total_loss / n_batches:.4f}  "
            f"val bit-acc {bit_acc:.4f}  val exact-table {exact:.4f}  ({dt:.1f}s)"
        )

    torch.save(
        {
            "model_state": model.state_dict(),
            "radius": radius,
            "channels": args.channels,
            "hidden": args.hidden,
            "train_rules": [int(r) for r in train_rules],
            "holdout_rules": [int(r) for r in holdout_rules],
            "aug": {"noise_max": AUG_NOISE_MAX, "mask_max": AUG_MASK_MAX, "apply_p": AUG_APPLY_P},
            "history": history,
        },
        ckpt_path,
    )
    save_json(
        {"checkpoint": ckpt_path, "params": n_params, "history": history},
        out_dir / f"rule_reader_seed{args.seed}_log.json",
    )
    print(f"[f2] wrote {ckpt_path}")


if __name__ == "__main__":
    main()
