#!/usr/bin/env python3
"""M4 Part 5 — the range-2 invariant landscape (review gate before training).

Samples canonical range-2 rules, computes their damage-spreading invariants
under the range-2 protocol (radius-aware horizon; `caspectra.eval.dynamics`),
and reports **how populated the complex regime actually is** — the central
empirical question M4 turns on (RESULTS.md §6 two-member-club caveat). Also
writes the leave-complex-out training config so the split is a deterministic
artifact of this analysis, not a hand-picked set.

Nothing here trains a model. Run it, review the complex count / anchor
placements, then launch the (ask-gated) training run.

Usage::

    python scripts/analyze_range2_landscape.py --n 800 --grid 127 \
        --out-config configs/m4_range2.yaml
    python scripts/analyze_range2_landscape.py --n 40 --grid 63 --epochs 3 \
        --n-ic 16 --n-pairs 64 --smoke --out-config configs/m4_range2_smoke.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import yaml  # noqa: E402

from caspectra.ca.range_ca import RangeCA, sample_rules  # noqa: E402
from caspectra.config import ExperimentConfig  # noqa: E402
from caspectra.data.targets import (  # noqa: E402
    TARGET_NAMES,
    load_or_compute_invariant_targets,
)
from caspectra.eval.dynamics import damage_spreading_features  # noqa: E402
from caspectra.eval.regimes import COMPLEX_SIGNATURE, complex_mask, curated_anchors, is_complex
from caspectra.utils import ensure_dir, save_json  # noqa: E402

RADIUS = 2
RATE = TARGET_NAMES.index("spreading_rate")
FILL = TARGET_NAMES.index("cone_fill")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Range-2 invariant landscape (M4 review gate).")
    p.add_argument(
        "--n", type=int, default=800, help="Number of canonical range-2 rules to sample."
    )
    p.add_argument("--grid", type=int, default=127, help="Ring width / diagram side.")
    p.add_argument("--n-pairs", type=int, default=256, help="Twin-run pairs per target vector.")
    p.add_argument("--n-ic", type=int, default=64, help="ICs per rule for the training config.")
    p.add_argument("--epochs", type=int, default=60, help="Epochs for the training config.")
    p.add_argument("--sample-seed", type=int, default=0, help="Rule-sampling seed.")
    p.add_argument("--targets-seed", type=int, default=0, help="Target-measurement seed.")
    p.add_argument("--cache-dir", default="cache", help="Diagram/target cache directory.")
    p.add_argument("--output-dir", default="runs/m4_range2/landscape", help="Report output dir.")
    p.add_argument("--out-config", default=None, help="Write a leave-complex-out training config.")
    p.add_argument("--smoke", action="store_true", help="Label the config/report as smoke.")
    return p.parse_args()


def anchor_report(width: int, n_pairs: int, seed: int) -> dict:
    """Where the named embedded-ECA anchors land under the range-2 protocol."""
    out = {}
    for name, rule in curated_anchors(RADIUS).items():
        v = damage_spreading_features(
            simulator=RangeCA(rule, RADIUS),
            width=width,
            n_pairs=n_pairs,
            rng=np.random.default_rng([seed, rule % (2**31)]),
        )
        out[name] = {
            "rule": int(rule),
            "invariants": {n: round(float(x), 4) for n, x in zip(TARGET_NAMES, v)},
            "is_complex": bool(is_complex(v)),
        }
    return out


def landscape_figure(targets: np.ndarray, mask: np.ndarray, anchors: dict, path: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.scatter(
        targets[~mask, RATE], targets[~mask, FILL], s=10, alpha=0.3, c="steelblue", label="other"
    )
    ax.scatter(
        targets[mask, RATE],
        targets[mask, FILL],
        s=16,
        alpha=0.7,
        c="crimson",
        label=f"complex signature ({int(mask.sum())})",
    )
    for name, rec in anchors.items():
        if not name.startswith("eca"):
            continue
        x, y = rec["invariants"]["spreading_rate"], rec["invariants"]["cone_fill"]
        ax.scatter([x], [y], marker="*", s=180, c="gold", edgecolor="k", zorder=5)
        ax.annotate(
            name.replace("eca", "").split("_")[0],
            (x, y),
            textcoords="offset points",
            xytext=(5, 4),
            fontsize=8,
        )
    ax.axvspan(
        COMPLEX_SIGNATURE["rate_lo"], COMPLEX_SIGNATURE["rate_hi"], color="crimson", alpha=0.05
    )
    ax.set_xlabel("spreading rate (÷ light-cone speed)")
    ax.set_ylabel("cone fill")
    ax.set_title("Range-2 invariant landscape (rate × fill); stars = embedded ECA anchors")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def write_config(path: str, rules: list[int], complex_rules: list[int], args) -> None:
    """Emit a leave-complex-out regressor config (rules + forced complex holdout)."""
    cfg = ExperimentConfig()
    cfg.data.rules = [int(r) for r in rules]
    cfg.data.radius = RADIUS
    cfg.data.n_ic_per_rule = args.n_ic
    cfg.data.grid_size = args.grid
    cfg.data.cache_dir = args.cache_dir
    cfg.data.augmentation.coarse_grain = False  # regressor: keep signal (lever_a convention)
    cfg.model.method = "regressor"
    cfg.model.encoder = "anticheat"
    cfg.model.embedding_dim = 64
    cfg.model.n_targets = 4
    cfg.model.norm_layer = "batch"  # regressor locality requirement (RESULTS.md 2026-07-03)
    cfg.train.epochs = args.epochs
    cfg.train.batch_size = 128
    cfg.train.output_dir = "runs/m4_range2_smoke" if args.smoke else "runs/m4_range2"
    cfg.train.force_holdout_rules = [int(r) for r in complex_rules]  # criterion 9 holdout
    cfg.train.force_train_rules = []
    cfg.targets.n_pairs = args.n_pairs
    cfg.eval.checkpoint = f"{cfg.train.output_dir}/checkpoint_final.pt"
    cfg.eval.output_dir = f"{cfg.train.output_dir}/eval"
    ensure_dir(str(Path(path).parent))
    Path(path).write_text(yaml.safe_dump(cfg.to_dict(), sort_keys=False))


def main() -> None:
    args = parse_args()
    out = ensure_dir(args.output_dir)
    print(f"[m4] sampling {args.n} canonical range-2 rules (seed {args.sample_seed})")
    rules = sample_rules(args.n, RADIUS, np.random.default_rng(args.sample_seed))

    print(f"[m4] computing targets: width {args.grid}, n_pairs {args.n_pairs} (cached)")
    targets = load_or_compute_invariant_targets(
        rules,
        width=args.grid,
        n_pairs=args.n_pairs,
        seed=args.targets_seed,
        cache_dir=args.cache_dir,
        radius=RADIUS,
    )
    # Re-index targets to the sampled order (loader returns sorted order).
    order = {r: i for i, r in enumerate(sorted(rules))}
    targets = targets[[order[r] for r in rules]]

    mask = complex_mask(targets)
    complex_rules = [int(r) for r, m in zip(rules, mask) if m]
    anchors = anchor_report(args.grid, args.n_pairs, args.targets_seed)

    print(f"\n[m4] complex regime: {mask.sum()}/{len(rules)} = {mask.mean():.3f} of sampled rules")
    print("[m4] per-feature distribution (sampled range-2 rules):")
    for i, n in enumerate(TARGET_NAMES):
        col = targets[:, i]
        print(
            f"   {n:>16}: mean {col.mean():.3f}  p10 {np.percentile(col, 10):.3f}  "
            f"median {np.median(col):.3f}  p90 {np.percentile(col, 90):.3f}"
        )
    print("[m4] embedded-ECA anchor placements (range-2 protocol):")
    for name, rec in anchors.items():
        inv = rec["invariants"]
        print(
            f"   {name:>18}: rate {inv['spreading_rate']:.3f} fill {inv['cone_fill']:.3f} "
            f"surv {inv['damage_survival']:.3f} -> complex={rec['is_complex']}"
        )

    landscape_figure(targets, mask, anchors, str(out / "landscape.png"))
    summary = {
        "n_rules": len(rules),
        "radius": RADIUS,
        "grid": args.grid,
        "n_pairs": args.n_pairs,
        "sample_seed": args.sample_seed,
        "complex_signature": COMPLEX_SIGNATURE,
        "n_complex": int(mask.sum()),
        "complex_fraction": round(float(mask.mean()), 4),
        "complex_rules": complex_rules,
        "feature_stats": {
            n: {
                "mean": round(float(targets[:, i].mean()), 4),
                "p10": round(float(np.percentile(targets[:, i], 10)), 4),
                "median": round(float(np.median(targets[:, i])), 4),
                "p90": round(float(np.percentile(targets[:, i], 90)), 4),
            }
            for i, n in enumerate(TARGET_NAMES)
        },
        "anchors": anchors,
    }
    save_json(summary, out / "summary.json")
    print(f"[m4] wrote {out}/summary.json and landscape.png")

    if args.out_config:
        write_config(args.out_config, rules, complex_rules, args)
        print(
            f"[m4] wrote {args.out_config} "
            f"({len(rules)} rules, {len(complex_rules)} forced to the complex holdout)"
        )


if __name__ == "__main__":
    main()
