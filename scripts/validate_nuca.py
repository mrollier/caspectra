#!/usr/bin/env python3
"""Criterion 7: compositional map transfer on non-uniform CAs (rev 3).

Grades a Lever A checkpoint's per-patch phenotype maps on two-region half/half
nuCA diagrams: does the mean map prediction inside each region match the pure
rule's direct twin-run invariants? Full measurement spec (panel, exclusion band,
bars) is pre-registered in EVALUATION_CRITERIA.md revision 3.

Order of operations mirrors the spec:

1. **Control (validity):** rule_a == rule_b nuCA diagrams must equal the pure
   ECA diagrams exactly, and their maps the uniform maps — otherwise abort.
2. **Primary panel (gated):** 120 unordered pairs of 16 pre-registered
   train-split rules, >= 8 ICs each with sides alternated; per-feature
   region-level R² -> median -> PASS (>= 0.5) / FAIL (< 0.2) / INCONCLUSIVE.
3. **Secondary diagnostics (reported, not gated):** held-out-rule pairs vs the
   anchors {0, 204, 30, 54}; spreading-rate ordering accuracy; interface-band
   means; striped-mask qualitative map panel.

Usage::

    python scripts/validate_nuca.py --config configs/lever_a.yaml
"""

from __future__ import annotations

import argparse
from itertools import combinations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from caspectra.ca.eca import ECASimulator  # noqa: E402
from caspectra.ca.nuca import NonUniformCA, half_mask, striped_mask  # noqa: E402
from caspectra.config import ExperimentConfig  # noqa: E402
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets  # noqa: E402
from caspectra.eval.nuca_metrics import (  # noqa: E402
    ordering_accuracy,  # noqa: E402
    region_columns,
    region_means,
)
from caspectra.factory import build_model  # noqa: E402
from caspectra.train.regression_trainer import r2_per_feature  # noqa: E402
from caspectra.utils import ensure_dir, save_json, select_device, set_seed  # noqa: E402

# Pre-registered (EVALUATION_CRITERIA.md rev 3). Do not edit without a revision.
PRIMARY_PANEL = [0, 4, 204, 184, 26, 73, 154, 90, 60, 30, 18, 45, 22, 41, 106, 54]
ANCHORS = [0, 204, 30, 54]
EXCLUSION_PX = 16.0  # receptive-field half-width of the 4-block AntiCheatCNN
RATE = TARGET_NAMES.index("spreading_rate")
STRIPE_PERIOD = 32
STRIPE_PAIRS = [(0, 30), (204, 30), (0, 54)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Criterion-7 nuCA map validation.")
    parser.add_argument("--config", required=True, help="Path to a YAML ExperimentConfig.")
    parser.add_argument("--checkpoint", default=None, help="Override eval.checkpoint.")
    parser.add_argument("--device", default="mps", help="Preferred device (mps/cpu/cuda).")
    parser.add_argument(
        "--output-dir", default=None, help="Default: <eval.output_dir>/../nuca_eval."
    )
    parser.add_argument("--n-ic", type=int, default=8, help="ICs per rule pair (spec: >= 8).")
    parser.add_argument(
        "--panel",
        type=int,
        nargs="*",
        default=None,
        help="Override the primary panel (smoke only — the gate requires the registered panel).",
    )
    parser.add_argument("--skip-secondary", action="store_true", help="Smoke: primary gate only.")
    parser.add_argument(
        "--exclusion-px",
        type=float,
        default=EXCLUSION_PX,
        help="Interface exclusion half-band in px (smoke only — the gate requires 16).",
    )
    return parser.parse_args()


def composed_diagram(
    rule_left: int, rule_right: int, mask: np.ndarray, width: int, seed_key: tuple[int, ...]
) -> np.ndarray:
    """One nuCA diagram (width rows incl. IC), reproducibly seeded by ``seed_key``."""
    rng = np.random.default_rng(list(seed_key))
    return NonUniformCA(rule_left, rule_right, mask).random_diagram(width, width, rng)


@torch.no_grad()
def predict_maps(
    model: torch.nn.Module,
    diagrams: list[np.ndarray],
    device: torch.device,
    scaler_mean: np.ndarray,
    scaler_std: np.ndarray,
    batch_size: int = 64,
) -> np.ndarray:
    """Un-standardized ``predict_map`` outputs ``(N, n_targets, h, m)``."""
    model.eval()
    out = []
    for start in range(0, len(diagrams), batch_size):
        batch = torch.from_numpy(np.stack(diagrams[start : start + batch_size]))
        batch = batch.to(torch.float32).unsqueeze(1).to(device)
        out.append(model.predict_map(batch).cpu().numpy())
    maps = np.concatenate(out)
    return maps * scaler_std[None, :, None, None] + scaler_mean[None, :, None, None]


def run_control(model, device, scaler_mean, scaler_std, width: int) -> float:
    """rule_a == rule_b must reproduce the uniform diagram (and map) exactly.

    Returns the max abs map difference; raises if the *diagrams* differ at all
    (that would be a simulator bug, not a model property).
    """
    worst = 0.0
    for rule in (0, 30, 54, 204):
        rng_u, rng_n = np.random.default_rng([1, rule]), np.random.default_rng([1, rule])
        uniform = ECASimulator(rule).random_diagram(width, width, rng_u)
        composed = NonUniformCA(rule, rule, half_mask(width)).random_diagram(width, width, rng_n)
        if not np.array_equal(uniform, composed):
            raise RuntimeError(f"control failed: rule_a==rule_b={rule} diagram != pure ECA")
        maps = predict_maps(model, [uniform, composed], device, scaler_mean, scaler_std)
        worst = max(worst, float(np.abs(maps[0] - maps[1]).max()))
    return worst


def measure_pairs(
    pairs: list[tuple[int, int]],
    model,
    device,
    scaler_mean,
    scaler_std,
    width: int,
    n_ic: int,
    targets_by_rule: dict[int, np.ndarray],
    exclusion_px: float,
) -> dict:
    """Region-mean predictions vs pure-rule truth for a list of rule pairs.

    Sides are alternated across ICs (even IC: (a, b), odd IC: (b, a)); region
    membership of each kept map column follows the mask, so the record for a
    rule always uses the columns that rule actually governed.
    """
    mask = half_mask(width)
    records_pred: list[np.ndarray] = []
    records_true: list[np.ndarray] = []
    record_rules: list[int] = []
    per_diagram_rate: list[tuple[float, float, float, float]] = []  # pred/true a,b
    interface_gap: list[float] = []
    columns_by_region: dict[int, np.ndarray] | None = None
    excluded_cols: np.ndarray | None = None

    diagrams, layout = [], []
    for a, b in pairs:
        for ic in range(n_ic):
            left, right = (a, b) if ic % 2 == 0 else (b, a)
            diagrams.append(composed_diagram(left, right, mask, width, (2, a, b, ic)))
            layout.append((left, right))
    maps = predict_maps(model, diagrams, device, scaler_mean, scaler_std)

    for pmap, (left, right) in zip(maps, layout):
        if columns_by_region is None:
            columns_by_region, excluded_cols = region_columns(mask, pmap.shape[-1], exclusion_px)
            if set(columns_by_region) != {0, 1}:
                raise RuntimeError(
                    f"no interface-free map columns for a region: map width "
                    f"{pmap.shape[-1]} at image width {width} with exclusion "
                    f"±{exclusion_px}px — lower --exclusion-px (smoke) or use a wider grid"
                )
        means = region_means(pmap, columns_by_region)
        by_rule = {left: means[0], right: means[1]}  # mask: 0 = left rule, 1 = right rule
        for rule, pred in by_rule.items():
            records_pred.append(pred)
            records_true.append(targets_by_rule[rule])
            record_rules.append(rule)
        per_diagram_rate.append(
            (
                float(by_rule[left][RATE]),
                float(by_rule[right][RATE]),
                float(targets_by_rule[left][RATE]),
                float(targets_by_rule[right][RATE]),
            )
        )
        if excluded_cols is not None and excluded_cols.size:
            band = pmap[:, :, excluded_cols].mean(axis=(1, 2))
            interface_gap.append(float(band[RATE] - (means[0][RATE] + means[1][RATE]) / 2.0))

    pred = np.stack(records_pred)
    true = np.stack(records_true)
    r2 = r2_per_feature(pred, true)
    pa, pb, ta, tb = (np.array(x) for x in zip(*per_diagram_rate))
    acc, n_used = ordering_accuracy(pa, pb, ta, tb)
    return {
        "n_records": int(len(pred)),
        "per_feature_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, r2)},
        "median_r2": round(float(np.nanmedian(r2)), 4),
        "rate_ordering_accuracy": None if np.isnan(acc) else round(acc, 4),
        "rate_ordering_n": n_used,
        "interface_band_rate_minus_region_mean": round(float(np.mean(interface_gap)), 4),
        "kept_columns_per_region": {
            str(k): [int(c) for c in v] for k, v in (columns_by_region or {}).items()
        },
        "_pred": pred,
        "_true": true,
        "_rules": np.array(record_rules),
    }


def scatter_figure(result: dict, path: str, title: str) -> None:
    pred, true = result["_pred"], result["_true"]
    fig, axes = plt.subplots(1, len(TARGET_NAMES), figsize=(15, 3.9))
    for i, (ax, name) in enumerate(zip(axes, TARGET_NAMES)):
        ax.scatter(true[:, i], pred[:, i], s=8, alpha=0.35, c="steelblue")
        lim = [-0.05, 1.05]
        ax.plot(lim, lim, "k--", lw=0.8, alpha=0.5)
        ax.set_xlim(lim), ax.set_ylim(lim)
        ax.set_xlabel("pure-rule direct invariant")
        if i == 0:
            ax.set_ylabel("region-mean map prediction")
        ax.set_title(f"{name}\nR² = {result['per_feature_r2'][name]}", fontsize=10)
    fig.suptitle(title, y=1.04)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def stripe_figure(model, device, scaler_mean, scaler_std, width: int, path: str) -> None:
    """Qualitative: striped masks are below the map's resolution by construction."""
    fig, axes = plt.subplots(2, len(STRIPE_PAIRS), figsize=(4 * len(STRIPE_PAIRS), 7))
    mask = striped_mask(width, STRIPE_PERIOD)
    for col, (a, b) in enumerate(STRIPE_PAIRS):
        diagram = NonUniformCA(a, b, mask).random_diagram(width, width, np.random.default_rng(3))
        pmap = predict_maps(model, [diagram], device, scaler_mean, scaler_std)[0]
        axes[0, col].imshow(diagram, cmap="binary", interpolation="nearest")
        axes[0, col].set_title(f"stripes({STRIPE_PERIOD}px): rules {a} | {b}", fontsize=10)
        im = axes[1, col].imshow(
            pmap[RATE], cmap="inferno", vmin=0, vmax=1, interpolation="nearest"
        )
        axes[1, col].set_title("predicted spreading rate", fontsize=9)
        for ax in axes[:, col]:
            ax.set_xticks([]), ax.set_yticks([])
    fig.colorbar(im, ax=axes[1, :].tolist(), fraction=0.02, pad=0.01)
    fig.suptitle("Secondary (qualitative): striped masks vs map resolution", y=0.98)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    checkpoint_path = args.checkpoint or cfg.eval.checkpoint
    default_out = str(ensure_dir(cfg.eval.output_dir).parent / "nuca_eval")
    output_dir = ensure_dir(args.output_dir or default_out)
    set_seed(cfg.seed)
    device = select_device(prefer=args.device)
    width = cfg.data.grid_size
    print(f"[nuca] device={device} checkpoint={checkpoint_path} width={width}")

    state = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    scaler_mean, scaler_std = state["scaler_mean"], state["scaler_std"]
    train_rules = {int(r) for r in state["train_rules"]}
    holdout_rules = [int(r) for r in state["holdout_rules"]]
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    model = model.to(device)

    panel = args.panel if args.panel is not None else PRIMARY_PANEL
    gated = args.panel is None
    missing = [r for r in panel if r not in train_rules]
    if gated and missing:
        raise RuntimeError(f"registered panel rules not in checkpoint train split: {missing}")

    all_rules = sorted(set(panel) | set(ANCHORS) | set(holdout_rules))
    targets = load_or_compute_invariant_targets(
        all_rules,
        width=width,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
    )
    targets_by_rule = {r: targets[i] for i, r in enumerate(all_rules)}

    # 1. Control gate — abort loudly rather than report on a broken harness.
    control_diff = run_control(model, device, scaler_mean, scaler_std, width)
    print(f"[nuca] control: rule_a==rule_b max |map diff| = {control_diff:.2e} (must be ~0)")
    if control_diff > 1e-5:
        raise RuntimeError(f"control failed: composed==uniform map diff {control_diff}")

    # 2. Primary panel (the gate).
    pairs = list(combinations(panel, 2))
    print(f"[nuca] primary panel: {len(panel)} rules, {len(pairs)} pairs, {args.n_ic} ICs each")
    primary = measure_pairs(
        pairs,
        model,
        device,
        scaler_mean,
        scaler_std,
        width,
        args.n_ic,
        targets_by_rule,
        args.exclusion_px,
    )
    median = primary["median_r2"]
    verdict = "PASS" if median >= 0.5 else ("FAIL" if median < 0.2 else "INCONCLUSIVE")
    if not gated or args.exclusion_px != EXCLUSION_PX:
        verdict += " (non-registered spec — smoke only)"
    print(f"[nuca] criterion 7: per-feature R² {primary['per_feature_r2']}")
    print(f"[nuca] criterion 7: median {median} -> {verdict}")
    scatter_figure(
        primary,
        str(output_dir / "criterion7_scatter.png"),
        f"Criterion 7 — region means vs pure-rule invariants (median R² = {median}, {verdict})",
    )

    summary = {
        "checkpoint": str(checkpoint_path),
        "width": width,
        "exclusion_px": args.exclusion_px,
        "n_ic_per_pair": args.n_ic,
        "panel": list(panel),
        "panel_is_registered": gated,
        "control_max_map_diff": control_diff,
        "criterion7": {k: v for k, v in primary.items() if not k.startswith("_")},
        "criterion7_verdict": verdict,
    }

    # 3. Secondary diagnostics (reported, not gated).
    if not args.skip_secondary:
        held_pairs = [(h, a) for h in holdout_rules for a in ANCHORS if h != a]
        print(f"[nuca] secondary: {len(held_pairs)} held-out×anchor pairs")
        secondary = measure_pairs(
            held_pairs,
            model,
            device,
            scaler_mean,
            scaler_std,
            width,
            args.n_ic,
            targets_by_rule,
            args.exclusion_px,
        )
        summary["secondary_heldout"] = {k: v for k, v in secondary.items() if not k.startswith("_")}
        print(
            f"[nuca] secondary (held-out rules composed): per-feature R² "
            f"{secondary['per_feature_r2']} median {secondary['median_r2']}"
        )
        scatter_figure(
            secondary,
            str(output_dir / "secondary_heldout_scatter.png"),
            "Secondary — held-out rules composed with anchors (not gated)",
        )
        stripe_figure(
            model, device, scaler_mean, scaler_std, width, str(output_dir / "stripes.png")
        )

    save_json(summary, output_dir / "summary.json")
    print(f"[nuca] wrote {output_dir}/summary.json")


if __name__ == "__main__":
    main()
