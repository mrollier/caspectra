#!/usr/bin/env python3
"""Train an SSL model on CA spacetime diagrams (BUILD_BRIEF.md §3.9, §5).

Thin CLI: parse a YAML config, build the data/model/optimizer via the factory,
and run the :class:`~caspectra.train.trainer.Trainer`. The resolved config and
the chosen device are written into the run's output directory.

Example
-------
    PYTORCH_ENABLE_MPS_FALLBACK=1 python scripts/train.py --config configs/smoke.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path

from caspectra.config import ExperimentConfig
from caspectra.factory import build_dataloader, build_dataset, build_model, build_optimizer
from caspectra.train.trainer import Trainer
from caspectra.utils import ensure_dir, save_json, select_device, set_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train BYOL/SimSiam on CA diagrams.")
    parser.add_argument("--config", required=True, help="Path to a YAML ExperimentConfig.")
    parser.add_argument("--device", default="mps", help="Preferred device (mps/cpu/cuda).")
    parser.add_argument("--output-dir", default=None, help="Override train.output_dir.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    if args.output_dir is not None:
        cfg.train.output_dir = args.output_dir

    set_seed(cfg.seed)
    device = select_device(prefer=args.device)

    output_dir = ensure_dir(cfg.train.output_dir)
    cfg.to_yaml(output_dir / "config.yaml")
    save_json({"device": str(device)}, output_dir / "device.json")
    print(f"[train] device={device} output_dir={output_dir}")

    dataset = build_dataset(cfg.data, training=True)
    loader = build_dataloader(
        dataset,
        batch_size=cfg.train.batch_size,
        shuffle=True,
        num_workers=cfg.train.num_workers,
        drop_last=True,
    )
    print(f"[train] dataset: {len(dataset)} diagrams, {len(loader)} batches/epoch")

    model = build_model(cfg.model)
    optimizer = build_optimizer(model, cfg.train)
    trainer = Trainer(model, loader, optimizer, device, cfg.train)

    history = trainer.train()
    print(f"[train] done. loss {history[0]:.4f} -> {history[-1]:.4f}")
    print(f"[train] artifacts in {Path(output_dir).resolve()}")


if __name__ == "__main__":
    main()
