#!/usr/bin/env python3
"""Pre-generate (and cache) the spacetime-diagram dataset (§3.9).

Thin CLI so the (potentially slow) generation can be done once up front; later
training/eval runs with the same config load from the cache. Generation is
deterministic given ``data.seed``.

Example
-------
    python scripts/generate_data.py --config configs/default.yaml
"""

from __future__ import annotations

import argparse

from caspectra.config import ExperimentConfig
from caspectra.factory import build_dataset
from caspectra.utils import set_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate/cache CA diagrams.")
    parser.add_argument("--config", required=True, help="Path to a YAML ExperimentConfig.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    set_seed(cfg.seed)
    dataset = build_dataset(cfg.data, training=False)
    status = "loaded from cache" if dataset.loaded_from_cache else "generated"
    print(
        f"[generate_data] {len(dataset)} diagrams ({status}) "
        f"in {cfg.data.cache_dir} (grid={cfg.data.grid_size})"
    )


if __name__ == "__main__":
    main()
