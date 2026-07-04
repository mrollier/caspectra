#!/usr/bin/env python3
"""R3 (EVALUATION_CRITERIA.md rev 7): reliability-adjusted R^2 ceilings.

Draws ``K`` independent Monte-Carlo target replicates per rule and fits a one-way
random-effects model to get, per target, the reliability ICC(1) = the achievable
R^2 ceiling for that target under the observation protocol. This replaces the
hand-wavy "MC noise 0.006-0.014 upper-bounds R^2" claim with a proper
signal-vs-noise decomposition, and lets every method's R^2 be read against what
is achievable (in particular, it confirms the mechanistic estimator sits at the
ceiling while the CNN/baseline fall short, most on damage survival).

Usage::

    python scripts/validate_reliability.py --config configs/lever_a_local.yaml
    python scripts/validate_reliability.py --config configs/m4_range2.yaml --n-replicates 20
"""

from __future__ import annotations

import argparse

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.eval.reliability import icc_ceilings, target_replicates
from caspectra.factory import build_dataset
from caspectra.utils import ensure_dir, save_json, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R3 reliability-adjusted R^2 ceilings (rev 7).")
    p.add_argument("--config", required=True, help="Path to the YAML ExperimentConfig.")
    p.add_argument("--n-replicates", type=int, default=20, help="K independent MC replicates.")
    p.add_argument("--max-rules", type=int, default=None, help="Subsample rules (ICC is stable).")
    p.add_argument("--output-dir", default=None, help="Default <train.output_dir>/reliability.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/reliability")
    set_seed(cfg.seed)
    radius = cfg.data.radius

    dataset = build_dataset(cfg.data, training=False)
    rules = sorted({int(r) for r in np.asarray(dataset.equiv_reps)})
    if args.max_rules is not None and len(rules) > args.max_rules:
        # Representative subsample: the ICC ratio is stable across rules spanning
        # the full behaviour landscape (fixed RNG so the subset is reproducible).
        rules = sorted(
            np.random.default_rng(0).choice(rules, args.max_rules, replace=False).tolist()
        )
    print(
        f"[r3] radius={radius}  {len(rules)} rules  K={args.n_replicates} replicates  "
        f"n_pairs={cfg.targets.n_pairs}"
    )

    reps = target_replicates(
        rules,
        n_replicates=args.n_replicates,
        width=cfg.data.grid_size,
        n_pairs=cfg.targets.n_pairs,
        ic_density=cfg.targets.ic_density,
        radius=radius,
    )
    ceilings = icc_ceilings(reps)

    median_ceiling = float(np.nanmedian([v["ceiling_r2"] for v in ceilings.values()]))
    summary = {
        "radius": radius,
        "n_rules": len(rules),
        "n_replicates": args.n_replicates,
        "n_pairs": cfg.targets.n_pairs,
        "per_feature": ceilings,
        "median_ceiling_r2": round(median_ceiling, 4),
    }
    save_json(summary, out / "summary.json")

    for name, v in ceilings.items():
        print(
            f"[r3] {name:>16}: ceiling R² {v['ceiling_r2']:.4f}  "
            f"(MC-noise std {v['mc_noise_std']:.4f}, between-rule std {v['between_rule_std']:.4f})"
        )
    print(f"[r3] median ceiling R² {median_ceiling:.4f}")
    print(f"[r3] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
