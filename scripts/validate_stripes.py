#!/usr/bin/env python3
"""Criterion 8: stripe resolution (8a) + alloy transfer (8b) on striped nuCAs.

Grades a frozen Lever A checkpoint's phenotype maps on striped two-rule masks
(rev 4, EVALUATION_CRITERIA.md — pre-registered before any striped measurement
beyond criterion 7's qualitative figure):

1. **Control (validity):** (r, r) striped nuCA diagrams must equal the pure
   ECA diagrams exactly, and the (r, r) "alloy" twin-run features must equal
   the pure rule's features bit-for-bit under the same rng — otherwise abort.
2. **8a — stripe resolution:** per-column spreading-rate contrast on stripes
   of period {32, 16, 8, 4, 2} (random phase per IC), normalized by the same
   pair's half/half contrast. Gate: relative contrast at period 32 positive
   (95% bootstrap CI over pairs). Resolution limit (reported, not gated):
   smallest period with median relative contrast >= 0.5.
3. **8b — alloy transfer:** below the map's resolution the composed system is
   a new homogeneous "alloy"; its own twin-run invariants are the truth. Gate:
   median per-feature R² of the global prediction across 120 pairs × {2, 4}
   periods × 8 ICs (>= 0.5 pass, < 0.2 fail; degenerate-truth features
   excluded per the registered rule). The constituent-mixture baseline is
   reported alongside (interpretation, not gated).

Usage::

    python scripts/validate_stripes.py --config configs/lever_a_local.yaml
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
from caspectra.data.targets import (  # noqa: E402
    TARGET_NAMES,
    load_or_compute_alloy_targets,
    load_or_compute_invariant_targets,
)
from caspectra.eval.dynamics import damage_spreading_features  # noqa: E402
from caspectra.eval.nuca_metrics import column_profile, stripe_contrast  # noqa: E402
from caspectra.factory import build_model  # noqa: E402
from caspectra.train.regression_trainer import r2_per_feature  # noqa: E402
from caspectra.utils import ensure_dir, save_json, select_device, set_seed  # noqa: E402

# Pre-registered (EVALUATION_CRITERIA.md rev 4). Do not edit without a revision.
PRIMARY_PANEL = [0, 4, 204, 184, 26, 73, 154, 90, 60, 30, 18, 45, 22, 41, 106, 54]
PERIODS_8A = [32, 16, 8, 4, 2]
PERIODS_8B = [2, 4]
RATE_GAP_MIN = 0.25  # 8a pair-selection threshold on cached pure-rule rates
MIN_HALF_CONTRAST = 0.05  # 8a: pairs below this half/half contrast are excluded
N_IC_CONTRAST = 16
N_IC_ALLOY = 8
TRUTH_STD_MIN = 0.05  # 8b degeneracy rule: features below this truth std not gated
GATE_PERIOD = 32
BOOTSTRAP = 10_000
RATE = TARGET_NAMES.index("spreading_rate")
CONTROL_RULES = [0, 30, 54, 204]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Criterion-8 stripe/alloy validation.")
    parser.add_argument("--config", required=True, help="Path to a YAML ExperimentConfig.")
    parser.add_argument("--checkpoint", default=None, help="Override eval.checkpoint.")
    parser.add_argument("--device", default="mps", help="Preferred device (mps/cpu/cuda).")
    parser.add_argument(
        "--output-dir", default=None, help="Default: <eval.output_dir>/../stripe_eval."
    )
    parser.add_argument(
        "--panel",
        type=int,
        nargs="*",
        default=None,
        help="Override the primary panel (smoke only — the gate requires the registered panel).",
    )
    parser.add_argument(
        "--periods", type=int, nargs="*", default=None, help="Override 8a periods (smoke only)."
    )
    parser.add_argument(
        "--n-ic-contrast", type=int, default=N_IC_CONTRAST, help="8a ICs (spec: >= 16)."
    )
    parser.add_argument("--n-ic-alloy", type=int, default=N_IC_ALLOY, help="8b ICs (spec: >= 8).")
    parser.add_argument(
        "--alloy-truth-pairs",
        type=int,
        default=256,
        help="Twin-run pairs per alloy truth vector (spec: 256; lower = smoke only).",
    )
    parser.add_argument(
        "--min-half-contrast",
        type=float,
        default=MIN_HALF_CONTRAST,
        help="8a pair-exclusion floor on half/half contrast (spec: 0.05; lower = smoke only).",
    )
    parser.add_argument("--skip-8b", action="store_true", help="Smoke: 8a only.")
    return parser.parse_args()


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


def run_control(width: int, n_pairs: int) -> None:
    """(r, r) striped systems must be indistinguishable from the pure rule.

    Checks both the diagrams (simulator level) and the twin-run feature vector
    (truth-harness level, same rng path). Raises on any mismatch — a failure
    here is a harness bug and voids every panel number.
    """
    for rule in CONTROL_RULES:
        for period in PERIODS_8B:
            mask = striped_mask(width, period)
            rng_u, rng_n = np.random.default_rng([9, rule]), np.random.default_rng([9, rule])
            uniform = ECASimulator(rule).random_diagram(width, width, rng_u)
            composed = NonUniformCA(rule, rule, mask).random_diagram(width, width, rng_n)
            if not np.array_equal(uniform, composed):
                raise RuntimeError(f"control failed: (r,r) diagram != pure ECA for rule {rule}")
            pure = damage_spreading_features(
                rule, width=width, n_pairs=n_pairs, rng=np.random.default_rng([9, rule, period])
            )
            alloy = damage_spreading_features(
                simulator=NonUniformCA(rule, rule, mask),
                width=width,
                n_pairs=n_pairs,
                rng=np.random.default_rng([9, rule, period]),
            )
            if not np.array_equal(pure, alloy):
                raise RuntimeError(f"control failed: (r,r) alloy truth != pure rule {rule}")


def measure_contrast(
    pairs: list[tuple[int, int]],
    periods: list[int],
    model,
    device,
    scaler_mean,
    scaler_std,
    width: int,
    n_ic: int,
    rates_by_rule: dict[int, float],
    min_half_contrast: float,
) -> dict:
    """8a: per-pair mean stripe contrast per period, normalized by half/half.

    Every diagram gets its own random mask phase (cyclic roll) so stripe
    boundaries are not accidentally aligned with the fixed patch grid; the
    half/half normalizer is phase-rolled identically for symmetry.
    """
    rng = np.random.default_rng(48)
    contrast: dict[str, dict[str, float]] = {}  # pair -> {"half": c, "32": c, ...}
    for a, b in pairs:
        hot_value = 0 if rates_by_rule[a] > rates_by_rule[b] else 1
        per_geometry: dict[str, float] = {}
        for label, base_mask in [("half", half_mask(width))] + [
            (str(p), striped_mask(width, p)) for p in periods
        ]:
            masks = [np.roll(base_mask, int(rng.integers(width))) for _ in range(n_ic)]
            diagrams = [
                NonUniformCA(a, b, m).random_diagram(
                    width, width, np.random.default_rng([4, a, b, i])
                )
                for i, m in enumerate(masks)
            ]
            maps = predict_maps(model, diagrams, device, scaler_mean, scaler_std)
            values = [
                stripe_contrast(column_profile(pmap)[RATE], m, hot_value)
                for pmap, m in zip(maps, masks)
            ]
            per_geometry[label] = float(np.mean(values))
        contrast[f"{a}|{b}"] = per_geometry

    halves = np.array([c["half"] for c in contrast.values()])
    usable = halves >= min_half_contrast
    excluded_pairs = [p for p, u in zip(contrast, usable) if not u]
    relative = {
        str(p): np.array([c[str(p)] for c in contrast.values()])[usable] / halves[usable]
        for p in periods
    }
    result = {
        "n_pairs": len(pairs),
        "n_pairs_used": int(usable.sum()),
        "min_half_contrast": min_half_contrast,
        "excluded_pairs_low_half_contrast": excluded_pairs,
        "half_contrast_median": round(float(np.median(halves)), 4),
        "_per_pair": contrast,
        "_relative": relative,
    }
    if not usable.any():
        # A weak model (smoke) can leave nothing above the floor; on a
        # registered run this means no spatial claim can be made at all.
        result["relative_contrast_median"] = None
        result["resolution_limit_px"] = None
        result["gate_period32"] = {"verdict": "INCONCLUSIVE (no usable pairs)"}
        return result
    result["relative_contrast_median"] = {
        p: round(float(np.median(r)), 4) for p, r in relative.items()
    }
    result["relative_contrast_mean"] = {p: round(float(np.mean(r)), 4) for p, r in relative.items()}
    # Resolution limit: smallest period whose median relative contrast >= 0.5.
    passing = [p for p in sorted(periods) if float(np.median(relative[str(p)])) >= 0.5]
    result["resolution_limit_px"] = min(passing) if passing else None

    if str(GATE_PERIOD) in relative:
        r32 = relative[str(GATE_PERIOD)]
        boot_rng = np.random.default_rng(7)
        boots = np.array(
            [r32[boot_rng.integers(len(r32), size=len(r32))].mean() for _ in range(BOOTSTRAP)]
        )
        lo, hi = np.percentile(boots, [2.5, 97.5])
        result["gate_period32"] = {
            "mean_relative_contrast": round(float(r32.mean()), 4),
            "ci95": [round(float(lo), 4), round(float(hi), 4)],
            "verdict": "PASS" if lo > 0 else "FAIL",
        }
    return result


def measure_alloys(
    pairs: list[tuple[int, int]],
    model,
    device,
    scaler_mean,
    scaler_std,
    width: int,
    n_ic: int,
    truth_pairs: int,
    targets_by_rule: dict[int, np.ndarray],
    cache_dir: str,
    seed: int,
) -> dict:
    """8b: global map reading vs the alloy's own twin-run invariants."""
    rng = np.random.default_rng(84)
    records_pred, records_true, records_mix = [], [], []
    truth_rows = []
    for period in PERIODS_8B:
        truth = load_or_compute_alloy_targets(
            pairs, period, width=width, n_pairs=truth_pairs, seed=seed, cache_dir=cache_dir
        )
        truth_rows.append(truth)
        base_mask = striped_mask(width, period)
        weight_a = float((base_mask == 0).mean())
        for (a, b), alloy_true in zip(pairs, truth):
            mixture = weight_a * targets_by_rule[a] + (1.0 - weight_a) * targets_by_rule[b]
            diagrams = [
                NonUniformCA(a, b, np.roll(base_mask, int(rng.integers(width)))).random_diagram(
                    width, width, np.random.default_rng([5, a, b, period, i])
                )
                for i in range(n_ic)
            ]
            maps = predict_maps(model, diagrams, device, scaler_mean, scaler_std)
            for pmap in maps:
                records_pred.append(pmap.mean(axis=(1, 2)))  # == global prediction (GAP identity)
                records_true.append(alloy_true)
                records_mix.append(mixture)

    pred, true, mix = (np.stack(x) for x in (records_pred, records_true, records_mix))
    r2_map = r2_per_feature(pred, true)
    r2_mix = r2_per_feature(mix, true)
    truth_std = np.concatenate(truth_rows).std(axis=0)
    gated = truth_std >= TRUTH_STD_MIN
    return {
        "n_alloys": len(pairs) * len(PERIODS_8B),
        "n_records": int(len(pred)),
        "periods": PERIODS_8B,
        "truth_twin_pairs": truth_pairs,
        "per_feature_r2_map": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, r2_map)},
        "per_feature_r2_mixture": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, r2_mix)},
        "alloy_truth_std": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, truth_std)},
        "features_gated": [n for n, g in zip(TARGET_NAMES, gated) if g],
        "median_r2_map_gated": round(float(np.median(r2_map[gated])), 4),
        "median_r2_mixture_gated": round(float(np.median(r2_mix[gated])), 4),
        "_pred": pred,
        "_true": true,
        "_mix": mix,
    }


def alloy_figure(result: dict, path: str, title: str) -> None:
    pred, true, mix = result["_pred"], result["_true"], result["_mix"]
    fig, axes = plt.subplots(2, len(TARGET_NAMES), figsize=(15, 7.5))
    for i, name in enumerate(TARGET_NAMES):
        for row, (est, label, key) in enumerate(
            [
                (pred, "map reading", "per_feature_r2_map"),
                (mix, "mixture baseline", "per_feature_r2_mixture"),
            ]
        ):
            ax = axes[row, i]
            ax.scatter(
                true[:, i], est[:, i], s=6, alpha=0.25, c="steelblue" if row == 0 else "darkorange"
            )
            lim = [-0.05, 1.05]
            ax.plot(lim, lim, "k--", lw=0.8, alpha=0.5)
            ax.set_xlim(lim), ax.set_ylim(lim)
            if row == 1:
                ax.set_xlabel("alloy twin-run invariant (direct)")
            if i == 0:
                ax.set_ylabel(label)
            ax.set_title(f"{name}\nR² = {result[key][name]}", fontsize=9)
    fig.suptitle(title, y=1.0)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def contrast_figure(result: dict, periods: list[int], path: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    xs = sorted(periods)
    rel = result["_relative"]
    med = [float(np.median(rel[str(p)])) for p in xs]
    q25 = [float(np.percentile(rel[str(p)], 25)) for p in xs]
    q75 = [float(np.percentile(rel[str(p)], 75)) for p in xs]
    ax.plot(xs, med, "o-", color="steelblue", label="median over pairs")
    ax.fill_between(xs, q25, q75, alpha=0.25, color="steelblue", label="IQR")
    ax.axhline(0.5, color="grey", ls="--", lw=0.8, label="resolution-limit threshold")
    ax.axhline(0.0, color="k", lw=0.8)
    ax.set_xscale("log", base=2)
    ax.set_xticks(xs), ax.set_xticklabels([str(p) for p in xs])
    ax.set_xlabel("stripe period (cells)")
    ax.set_ylabel("relative contrast R(p) = C(p) / C(half)")
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    checkpoint_path = args.checkpoint or cfg.eval.checkpoint
    default_out = str(ensure_dir(cfg.eval.output_dir).parent / "stripe_eval")
    output_dir = ensure_dir(args.output_dir or default_out)
    set_seed(cfg.seed)
    device = select_device(prefer=args.device)
    width = cfg.data.grid_size
    print(f"[stripes] device={device} checkpoint={checkpoint_path} width={width}")

    panel = args.panel if args.panel is not None else PRIMARY_PANEL
    periods = args.periods if args.periods is not None else PERIODS_8A
    gated = (
        args.panel is None
        and args.periods is None
        and args.n_ic_contrast >= N_IC_CONTRAST
        and args.n_ic_alloy >= N_IC_ALLOY
        and args.alloy_truth_pairs == 256
        and args.min_half_contrast == MIN_HALF_CONTRAST
    )
    tag = "" if gated else " (non-registered spec — smoke only)"

    state = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    scaler_mean, scaler_std = state["scaler_mean"], state["scaler_std"]
    train_rules = {int(r) for r in state["train_rules"]}
    missing = [r for r in panel if r not in train_rules]
    if gated and missing:
        raise RuntimeError(f"registered panel rules not in checkpoint train split: {missing}")
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    model = model.to(device)

    targets = load_or_compute_invariant_targets(
        panel,
        width=width,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
    )
    targets_by_rule = {r: targets[i] for i, r in enumerate(panel)}
    rates_by_rule = {r: float(t[RATE]) for r, t in targets_by_rule.items()}

    # 1. Control gate — abort loudly rather than report on a broken harness.
    run_control(width, n_pairs=64)
    print("[stripes] control: (r,r) striped diagrams and alloy truth match pure rules exactly")

    # 2. 8a — stripe resolution.
    all_pairs = list(combinations(panel, 2))
    contrast_pairs = [
        (a, b) for a, b in all_pairs if abs(rates_by_rule[a] - rates_by_rule[b]) >= RATE_GAP_MIN
    ]
    print(
        f"[stripes] 8a: {len(contrast_pairs)} pairs (rate gap >= {RATE_GAP_MIN}), "
        f"periods {periods}, {args.n_ic_contrast} ICs each"
    )
    resolution = measure_contrast(
        contrast_pairs,
        periods,
        model,
        device,
        scaler_mean,
        scaler_std,
        width,
        args.n_ic_contrast,
        rates_by_rule,
        args.min_half_contrast,
    )
    print(
        f"[stripes] 8a: {resolution['n_pairs_used']}/{resolution['n_pairs']} pairs above "
        f"half-contrast floor {args.min_half_contrast} "
        f"(median half contrast {resolution['half_contrast_median']})"
    )
    print(f"[stripes] 8a: median relative contrast {resolution['relative_contrast_median']}")
    print(f"[stripes] 8a: resolution limit = {resolution['resolution_limit_px']} px")
    if "gate_period32" in resolution:
        g = resolution["gate_period32"]
        g["verdict"] += tag
        if "mean_relative_contrast" in g:
            print(
                f"[stripes] 8a gate (period 32): mean R = {g['mean_relative_contrast']} "
                f"CI95 {g['ci95']} -> {g['verdict']}"
            )
        else:
            print(f"[stripes] 8a gate (period 32): {g['verdict']}")
    if resolution["n_pairs_used"] > 0:
        contrast_figure(
            resolution,
            periods,
            str(output_dir / "relative_contrast.png"),
            f"Criterion 8a — spatial contrast vs stripe period{tag}",
        )

    summary = {
        "checkpoint": str(checkpoint_path),
        "width": width,
        "panel": list(panel),
        "panel_is_registered": gated,
        "criterion8a": {k: v for k, v in resolution.items() if not k.startswith("_")},
    }

    # 3. 8b — alloy transfer.
    if not args.skip_8b:
        print(
            f"[stripes] 8b: {len(all_pairs)} pairs x periods {PERIODS_8B}, "
            f"{args.n_ic_alloy} ICs, truth from {args.alloy_truth_pairs} twin runs each"
        )
        alloys = measure_alloys(
            all_pairs,
            model,
            device,
            scaler_mean,
            scaler_std,
            width,
            args.n_ic_alloy,
            args.alloy_truth_pairs,
            targets_by_rule,
            cfg.data.cache_dir,
            cfg.targets.seed,
        )
        median = alloys["median_r2_map_gated"]
        verdict = ("PASS" if median >= 0.5 else ("FAIL" if median < 0.2 else "INCONCLUSIVE")) + tag
        print(f"[stripes] 8b: map R² {alloys['per_feature_r2_map']}")
        print(f"[stripes] 8b: mixture-baseline R² {alloys['per_feature_r2_mixture']}")
        print(
            f"[stripes] 8b: gated median {median} -> {verdict} "
            f"(mixture baseline median {alloys['median_r2_mixture_gated']})"
        )
        alloy_figure(
            alloys,
            str(output_dir / "alloy_scatter.png"),
            f"Criterion 8b — global reading vs alloy invariants (median R² = {median}, {verdict})",
        )
        summary["criterion8b"] = {k: v for k, v in alloys.items() if not k.startswith("_")}
        summary["criterion8b_verdict"] = verdict

    save_json(summary, output_dir / "summary.json")
    print(f"[stripes] wrote {output_dir}/summary.json")


if __name__ == "__main__":
    main()
