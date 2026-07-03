#!/usr/bin/env python3
"""Criterion 9: complex-regime placement in the range-2 space (M4; rev 5).

The direct test of the RESULTS.md §6 two-member-club caveat. On ECAs the
amortizer placed a held-out complex rule with a strongly *signed* error (pulled
toward the nearest populated regime) because it had seen ~1 complex example.
Here the regime is populated: a whole *set* of signature-complex range-2 rules
is held out, and the checkpoint must (a) predict their invariants well
(criterion-6 median R² ≥ 0.5) and (b) show **no systematic pull** (mean signed
spreading-rate error |·| ≤ 0.10). Both gate.

The general (non-complex) hold-out and the ECA §6 baseline biases are reported
alongside for context. The embedded-ECA continuity control lives in
``tests/test_range_ca.py`` (diagram bit-for-bit) and is asserted there.

Usage::

    python scripts/validate_complex_placement.py --config configs/m4_range2.yaml
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from caspectra.config import ExperimentConfig  # noqa: E402
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets  # noqa: E402
from caspectra.factory import build_dataloader, build_dataset, build_model  # noqa: E402
from caspectra.train.regression_trainer import r2_per_feature  # noqa: E402
from caspectra.utils import ensure_dir, save_json, select_device, set_seed  # noqa: E402

RATE = TARGET_NAMES.index("spreading_rate")
# Pre-registered gate bounds (EVALUATION_CRITERIA.md rev 5).
MEDIAN_R2_PASS = 0.5
MEDIAN_R2_FAIL = 0.2
SIGNED_BIAS_MAX = 0.10
# The ECA §6 baseline signed rate errors, for the head-to-head (RESULTS.md 2026-07-02).
ECA_BASELINE_SIGNED_RATE_ERROR = {"rule110_held": +0.17, "rule54_held": -0.26}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Criterion-9 complex-placement validation (M4).")
    p.add_argument("--config", required=True, help="Path to the range-2 YAML ExperimentConfig.")
    p.add_argument("--checkpoint", default=None, help="Override eval.checkpoint.")
    p.add_argument("--device", default="mps", help="Preferred device (mps/cpu/cuda).")
    p.add_argument("--output-dir", default=None, help="Default: <train.output_dir>/complex_eval.")
    return p.parse_args()


@torch.no_grad()
def predict_all(model, loader, device, scaler_mean, scaler_std) -> np.ndarray:
    model.eval()
    preds = [model(image.to(device)).cpu().numpy() for image, _ in loader]
    return np.concatenate(preds) * scaler_std + scaler_mean


def rule_means(values: np.ndarray, reps: np.ndarray, rules: list[int]) -> np.ndarray:
    return np.stack([values[reps == r].mean(axis=0) for r in rules])


def scatter_figure(pred, true, mask, path, title) -> None:
    fig, axes = plt.subplots(1, len(TARGET_NAMES), figsize=(15, 3.9))
    for i, (ax, name) in enumerate(zip(axes, TARGET_NAMES)):
        ax.scatter(true[~mask, i], pred[~mask, i], s=14, alpha=0.3, c="steelblue", label="general")
        ax.scatter(true[mask, i], pred[mask, i], s=26, alpha=0.7, c="crimson", label="complex")
        lim = [-0.05, 1.05]
        ax.plot(lim, lim, "k--", lw=0.8, alpha=0.5)
        ax.set_xlim(lim), ax.set_ylim(lim)
        ax.set_xlabel("direct invariant")
        if i == 0:
            ax.set_ylabel("amortized (held out)"), ax.legend(fontsize=7)
        ax.set_title(name, fontsize=10)
    fig.suptitle(title, y=1.04)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    checkpoint_path = args.checkpoint or cfg.eval.checkpoint
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/complex_eval")
    set_seed(cfg.seed)
    device = select_device(prefer=args.device)
    print(f"[c9] device={device} checkpoint={checkpoint_path}")

    state = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    scaler_mean, scaler_std = state["scaler_mean"], state["scaler_std"]
    holdout_rules = [int(r) for r in state["holdout_rules"]]
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    model = model.to(device)

    dataset = build_dataset(cfg.data, training=False)
    reps = dataset.equiv_reps
    loader = build_dataloader(
        dataset, batch_size=cfg.eval.batch_size, shuffle=False, num_workers=cfg.train.num_workers
    )
    pred_diagram = predict_all(model, loader, device, scaler_mean, scaler_std)

    # Truth is loaded for the FULL rule list (not the held-out subset): the
    # per-rule RNG in dynamics_feature_matrix is seeded by list position, so a
    # subset would yield slightly different invariants than the values the model
    # was trained against. Loading the whole list hits the same cache the
    # landscape/trainer used, giving the identical truth the model was fit to.
    all_rules = sorted({int(r) for r in cfg.data.rules})
    truth_all = load_or_compute_invariant_targets(
        all_rules,
        width=cfg.data.grid_size,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=cfg.data.radius,
    )
    truth_by_rule = {r: truth_all[i] for i, r in enumerate(all_rules)}

    held = [r for r in holdout_rules if r in set(int(x) for x in reps)]
    truth = np.stack([truth_by_rule[r] for r in held])
    pred = rule_means(pred_diagram, reps, held)

    # The complex hold-out is the PRE-REGISTERED set (the landscape's
    # signature-selected rules, forced out in the config) — not re-derived here,
    # so it matches exactly the set used to define the split (criterion 9 spec).
    complex_set = {int(r) for r in cfg.train.force_holdout_rules}
    is_complex = np.array([r in complex_set for r in held], dtype=bool)
    n_complex = int(is_complex.sum())
    print(f"[c9] held-out rules: {len(held)} ({n_complex} pre-registered complex)")
    if n_complex == 0:
        raise SystemExit(
            "[c9] no complex rules in the hold-out — criterion 9 needs the leave-complex-out "
            "config from analyze_range2_landscape.py (or a larger/denser sample)."
        )

    # (a) criterion-6 median R² on the complex hold-out.
    r2_complex = r2_per_feature(pred[is_complex], truth[is_complex])
    r2_general = r2_per_feature(pred[~is_complex], truth[~is_complex])
    median_complex = float(np.nanmedian(r2_complex))
    # (b) signed spreading-rate error (pull), complex hold-out.
    signed_rate_err = float((pred[is_complex, RATE] - truth[is_complex, RATE]).mean())
    signed_rate_err_general = float((pred[~is_complex, RATE] - truth[~is_complex, RATE]).mean())

    gate_r2 = median_complex >= MEDIAN_R2_PASS
    gate_bias = abs(signed_rate_err) <= SIGNED_BIAS_MAX
    verdict = (
        "PASS"
        if (gate_r2 and gate_bias)
        else ("FAIL" if median_complex < MEDIAN_R2_FAIL else "INCONCLUSIVE")
    )

    print(
        f"[c9] complex hold-out per-feature R²: "
        f"{ {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, r2_complex)} }"
    )
    print(f"[c9] complex median R² {median_complex:.4f} (bar ≥ {MEDIAN_R2_PASS}) -> {gate_r2}")
    print(
        f"[c9] complex signed rate error {signed_rate_err:+.4f} "
        f"(|·| ≤ {SIGNED_BIAS_MAX}) -> {gate_bias}  "
        f"[ECA §6 baseline: 110 {ECA_BASELINE_SIGNED_RATE_ERROR['rule110_held']:+.2f}, "
        f"54 {ECA_BASELINE_SIGNED_RATE_ERROR['rule54_held']:+.2f}]"
    )
    print(
        f"[c9] general hold-out median R² {float(np.nanmedian(r2_general)):.4f}, "
        f"signed rate error {signed_rate_err_general:+.4f}"
    )
    print(f"[c9] criterion 9 -> {verdict}")

    scatter_figure(
        pred,
        truth,
        is_complex,
        str(out / "complex_placement.png"),
        f"Criterion 9 — held-out placement (complex = red); "
        f"median R² {median_complex:.3f}, {verdict}",
    )
    summary = {
        "checkpoint": str(checkpoint_path),
        "radius": cfg.data.radius,
        "n_held_out": len(held),
        "n_complex": n_complex,
        "complex_per_feature_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, r2_complex)},
        "complex_median_r2": round(median_complex, 4),
        "complex_signed_rate_error": round(signed_rate_err, 4),
        "general_median_r2": round(float(np.nanmedian(r2_general)), 4),
        "general_signed_rate_error": round(signed_rate_err_general, 4),
        "eca_section6_baseline_signed_rate_error": ECA_BASELINE_SIGNED_RATE_ERROR,
        "gate_median_r2_pass": bool(gate_r2),
        "gate_signed_bias_pass": bool(gate_bias),
        "criterion9_verdict": verdict,
    }
    save_json(summary, out / "summary.json")
    print(f"[c9] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
