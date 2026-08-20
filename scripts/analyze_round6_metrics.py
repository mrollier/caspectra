#!/usr/bin/env python3
"""Round-5 review-response re-analyses (EVALUATION_CRITERIA rev 13, item 5).

Every quantity here is a *re-expression* of an already-released measurement:
the script reads committed run artifacts and runs no simulation and no
training. It answers five points of the fourth referee report
(``manuscript/reviews/review_opus5_20aug26.md``):

A1 (§3.4) **rho = RMSE / sigma_e**, the estimator's error in units of the
   target's own Monte-Carlo error. Under the one-way decomposition this is
   ``rho = sqrt((1 - R2) / (1 - ICC))``, so ``rho = sqrt(2)`` is exactly the
   simulation-limited benchmark and ``rho = 1`` exactly the latent ceiling,
   per target, with no Gaussian identity and no panel-composition dependence.

A2 (§3.2) **per-panel reliability**. ICC depends on the between-rule variance,
   which is a property of the *panel*; the manuscript quoted one universe-sample
   value panel-wide. Recomputed inside each radius-two decomposition.

A3 (§3.5) **target dependence**. fill = E[N/ext] and (w/2rT)*fraction/rate
   agree up to Jensen; the referee asks for the empirical scatter, with the
   pre-committed reading that R2 > 0.95 would make fill a derived coordinate.

A4 (§3.16) **reduced-budget frontier ceilings**. The frontier scores an
   estimator simulating at ``n`` pairs against the *production* target cache at
   256 pairs (``build_frontier_grid.py`` loads targets at ``cfg.targets.n_pairs``
   while ``--n-pairs`` sets only the estimator's budget), so the ceiling is
   ``1 - (1 + 256/n)(1 - ICC)`` for the read-then-simulate family and ICC for a
   direct estimator -- *not* ``2*ICC - 1`` at reduced budget.

A5 (§3.14) **survival-band stratification**. R2 on a strongly one-sided target
   rewards mode assignment; restricting to the intermediate band separates
   resolution from mode calling.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from caspectra.utils import ensure_dir, save_json

TARGETS = ["damage_survival", "damage_fraction", "spreading_rate", "cone_fill"]
METHODS = ["mechanistic", "gbm", "cnn", "ridge"]
BAND = (0.1, 0.9)  # rev-13 A5 intermediate survival band
UNIVERSE_COMPLEX_PREVALENCE = 57 / 800  # signature-complex share of the sampling universe
FRONTIER_BUDGETS = {"identifiability_fig": 64, "frontier_fig": 48}
PRODUCTION_PAIRS = 256


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rev-13 zero-simulation re-analyses.")
    p.add_argument("--r2-preds", default="runs/m4_range2_seed0/held_out_preds_np256_mech.pkl")
    p.add_argument("--eca-preds", default="runs/lever_a_local_seed0/held_out_preds_np256_mech.pkl")
    p.add_argument("--r2-reliability", default="runs/m4_range2/reliability/summary.json")
    p.add_argument("--eca-reliability", default="runs/lever_a_local/reliability/summary.json")
    p.add_argument("--landscape", default="cache/s4_landscape.npz")
    p.add_argument(
        "--r2-sigma-e", default="runs/m4_range2/reliability_heldout/per_rule_sigma_e.npz"
    )
    p.add_argument(
        "--eca-sigma-e", default="runs/lever_a_local/reliability_heldout/per_rule_sigma_e.npz"
    )
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--output-dir", default="runs/analysis/round6_metrics")
    return p.parse_args()


def _load(path: str):
    import pickle

    with open(path, "rb") as fh:
        return pickle.load(fh)


def _r2(true: np.ndarray, pred: np.ndarray) -> np.ndarray:
    res = np.sum((true - pred) ** 2, axis=0)
    tot = np.sum((true - true.mean(axis=0)) ** 2, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 1.0 - res / tot


def _rho(err2: np.ndarray, var: np.ndarray) -> np.ndarray:
    """Pooled error in replicate-noise units: sqrt(sum err^2 / sum sigma_e^2).

    Pooling the *sums* rather than averaging per-rule ratios is what makes the
    two reference values exact. Under exchangeability (Eq. 1 of the paper)
    E[(Yhat_i - Y1_i)^2] = 2 sigma_e(i)^2, so the ratio tends to 2 and rho to
    sqrt(2); for a predictor of the latent mean it tends to 1. It is also the
    only form that survives rules with sigma_e = 0 -- the fully ordered rules,
    whose target carries no Monte-Carlo noise and on which the reconstructed
    rule reproduces the target exactly, so they add 0 to both sums.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.sqrt(err2.sum(axis=0) / var.sum(axis=0))


def _per_rule_sigma_e(path: str | None, hop, rel) -> tuple[np.ndarray, str]:
    """(n_rules, n_targets) Monte-Carlo SD, per rule where available.

    Per-rule is what rho needs: survival and cone fill are markedly
    heteroscedastic, so a panel-average sigma_e understates rho for quiet rules
    (it can even push a correct estimator below the rho = 1 latent ceiling,
    which is an artifact of the divisor, not a real result).
    """
    if path and Path(path).exists():
        z = np.load(path)
        lookup = {int(r): z["sigma_e"][i] for i, r in enumerate(z["rules"])}
        if all(int(r) in lookup for r in hop.held):
            return np.stack([lookup[int(r)] for r in hop.held]), "per_rule"
    panel = np.array([rel[t]["mc_noise_std"] for t in hop.target_names])
    return np.broadcast_to(panel, (len(hop.held), len(panel))).copy(), "panel_average"


def analysis_a1(hop, rel, n_boot: int, rng, sigma_path: str | None = None) -> dict:
    """rho per method per target, with rule-bootstrap CIs."""
    sigma_e, sigma_kind = _per_rule_sigma_e(sigma_path, hop, rel)
    n = len(hop.held)
    boot = rng.integers(0, n, size=(n_boot, n))
    var = sigma_e**2
    n_noiseless = int((sigma_e[:, 0] <= 0).sum())
    out: dict[str, dict] = {}
    for m in METHODS:
        if m not in hop.preds:
            continue
        pred, true = hop.preds[m], hop.true
        err2 = (true - pred) ** 2
        point = _rho(err2, var)
        draws = np.sqrt(err2[boot].sum(axis=1) / var[boot].sum(axis=1))  # (B, F)
        lo, hi = np.percentile(draws, [2.5, 97.5], axis=0)
        out[m] = {
            t: {
                "rho": round(float(point[j]), 3),
                "rho_ci95": [round(float(lo[j]), 3), round(float(hi[j]), 3)],
                "r2": round(float(_r2(true, pred)[j]), 4),
            }
            for j, t in enumerate(hop.target_names)
        }
        out[m]["median_rho"] = round(float(np.median(point)), 3)
    out["_reference"] = {
        "simulation_limited_benchmark": round(float(np.sqrt(2)), 3),
        "latent_ceiling": 1.0,
        "sigma_e_kind": sigma_kind,
        "n_rules_with_zero_sigma_e": n_noiseless,
        "sigma_e_median_per_target": {
            t: round(float(np.median(sigma_e[:, j])), 5) for j, t in enumerate(hop.target_names)
        },
    }
    return out


def analysis_a2(hop, rel) -> dict:
    """Replicate-agreement and ICC recomputed inside each panel decomposition.

    ICC = 1 - sigma_e^2 / Var(panel targets); sigma_e is a property of the
    measurement (fixed n_pairs), the between-rule variance is a property of the
    panel, so only the latter is re-estimated per panel.
    """
    cm = hop.complex_mask.astype(bool)
    panels = {
        "enriched_panel": np.ones(len(cm), dtype=bool),
        "random_subpanel": ~cm,
        "signature_subpanel": cm,
    }
    out: dict[str, dict] = {}
    # Post-stratified: the two strata reweighted to the sampling universe's
    # signature-complex prevalence, so the benchmark matches the row it scores.
    w_c = UNIVERSE_COMPLEX_PREVALENCE
    post = {}
    for j, t in enumerate(hop.target_names):
        se = rel[t]["mc_noise_std"]
        yc, yr = hop.true[cm, j], hop.true[~cm, j]
        mu = w_c * yc.mean() + (1 - w_c) * yr.mean()
        var = float(
            w_c * (yc.var(ddof=1) + yc.mean() ** 2)
            + (1 - w_c) * (yr.var(ddof=1) + yr.mean() ** 2)
            - mu**2
        )
        icc = max(0.0, 1.0 - se**2 / var) if var > 0 else float("nan")
        post[t] = {
            "icc": round(icc, 4),
            "two_icc_minus_one": round(2 * icc - 1, 4),
            "panel_sd": round(float(np.sqrt(var)), 4),
            "icc_universe_sample": round(float(rel[t]["icc"]), 4),
            "shift_vs_universe": round(icc - float(rel[t]["icc"]), 4),
        }
    post["median_icc"] = round(float(np.median([post[t]["icc"] for t in hop.target_names])), 4)
    post["median_two_icc_minus_one"] = round(
        float(np.median([post[t]["two_icc_minus_one"] for t in hop.target_names])), 4
    )
    out["post_stratified"] = post
    for name, mask in panels.items():
        if mask.sum() < 3:
            continue
        row = {}
        for j, t in enumerate(hop.target_names):
            se = rel[t]["mc_noise_std"]
            var = float(hop.true[mask, j].var(ddof=1))
            icc = max(0.0, 1.0 - se**2 / var) if var > 0 else float("nan")
            row[t] = {
                "icc": round(icc, 4),
                "two_icc_minus_one": round(2 * icc - 1, 4),
                "panel_sd": round(float(np.sqrt(var)), 4),
                "icc_universe_sample": round(float(rel[t]["icc"]), 4),
                "shift_vs_universe": round(icc - float(rel[t]["icc"]), 4),
            }
        row["median_icc"] = round(float(np.median([row[t]["icc"] for t in hop.target_names])), 4)
        row["median_two_icc_minus_one"] = round(
            float(np.median([row[t]["two_icc_minus_one"] for t in hop.target_names])), 4
        )
        out[name] = row
    out["_max_abs_icc_shift"] = round(
        max(
            abs(out[p][t]["shift_vs_universe"])
            for p in out
            if not p.startswith("_")
            for t in hop.target_names
        ),
        4,
    )
    return out


def analysis_a3(landscape: str, hop, radius: int, width: int, horizon: int) -> dict:
    """Empirical scatter of cone fill against (w/2rT) * fraction / rate."""
    k = width / (2 * radius * horizon)

    def _scatter(t: np.ndarray, label: str) -> dict:
        surv, frac, rate, fill = t[:, 0], t[:, 1], t[:, 2], t[:, 3]
        ok = (rate > 1e-6) & (surv > 0)
        pred, y = k * frac[ok] / rate[ok], fill[ok]
        r2 = 1.0 - float(((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())
        return {
            "label": label,
            "n": int(ok.sum()),
            "k_w_over_2rT": round(float(k), 4),
            "r2_fill_vs_ratio": round(r2, 4),
            "pearson_r": round(float(np.corrcoef(pred, y)[0, 1]), 4),
            "median_abs_residual": round(float(np.median(np.abs(y - pred))), 4),
            "fill_sd": round(float(y.std(ddof=1)), 4),
            "derived_coordinate_by_registered_rule": bool(r2 > 0.95),
        }

    out = {"registered_threshold_r2": 0.95, "panels": []}
    p = Path(landscape)
    if p.exists():
        d = np.load(p)
        out["panels"].append(_scatter(d["targets"], f"landscape_n{len(d['targets'])}"))
    out["panels"].append(_scatter(hop.true, f"held_out_panel_n{len(hop.held)}"))
    return out


def analysis_a4(rel, target_names) -> dict:
    """Frontier ceilings under the actual scoring convention."""
    out: dict[str, dict] = {
        "_convention": (
            "Targets are the production cache at n_pairs=256; the grid budget n sets only "
            "the estimator's own simulation. A fresh-simulation estimator at n therefore "
            "carries sigma_e^2(n) = (256/n) sigma_e^2(256) of its own noise on top of the "
            "target's, giving ceiling = 1 - (1 + 256/n)(1 - ICC). A direct estimator "
            "predicting the latent mean keeps the ICC ceiling at any grid budget."
        )
    }
    for fig, n in FRONTIER_BUDGETS.items():
        scale = PRODUCTION_PAIRS / n
        row = {}
        for t in target_names:
            icc = float(rel[t]["icc"])
            row[t] = {
                "icc_direct_estimator_ceiling": round(icc, 4),
                "read_then_simulate_ceiling": round(1.0 - (1.0 + scale) * (1.0 - icc), 4),
            }
        row["n_pairs"] = n
        row["median_read_then_simulate_ceiling"] = round(
            float(np.median([row[t]["read_then_simulate_ceiling"] for t in target_names])), 4
        )
        row["median_icc_ceiling"] = round(
            float(np.median([row[t]["icc_direct_estimator_ceiling"] for t in target_names])), 4
        )
        out[fig] = row
    return out


def analysis_a5(hop, rel, n_boot: int, rng, sigma_path: str | None = None) -> dict:
    """R2/rho restricted to the intermediate survival band, plus mode accuracy."""
    surv = hop.true[:, hop.target_names.index("damage_survival")]
    band = (surv >= BAND[0]) & (surv <= BAND[1])
    sigma_e, _ = _per_rule_sigma_e(sigma_path, hop, rel)
    out: dict[str, object] = {
        "band": list(BAND),
        "n_in_band": int(band.sum()),
        "n_panel": int(len(surv)),
        "frac_in_band": round(float(band.mean()), 4),
    }
    if band.sum() < 5:
        out["note"] = "too few rules in band for a stable estimate"
        return out
    j = hop.target_names.index("damage_survival")
    nb = int(band.sum())
    boot = rng.integers(0, nb, size=(n_boot, nb))
    per_method = {}
    for m in METHODS:
        if m not in hop.preds:
            continue
        p_all, t_all = hop.preds[m][:, j], hop.true[:, j]
        pb, tb = p_all[band], t_all[band]
        r2b = 1.0 - float(((tb - pb) ** 2).sum() / ((tb - tb.mean()) ** 2).sum())
        draws = 1.0 - (
            np.sum((tb[boot] - pb[boot]) ** 2, axis=1)
            / np.sum((tb[boot] - tb[boot].mean(axis=1, keepdims=True)) ** 2, axis=1)
        )
        # Mode call: is the rule on the high-survival side of the band midpoint?
        mode_true, mode_pred = t_all > 0.5, p_all > 0.5
        per_method[m] = {
            "r2_full_panel": round(float(_r2(hop.true, hop.preds[m])[j]), 4),
            "r2_in_band": round(r2b, 4),
            "r2_in_band_ci95": [
                round(float(np.percentile(draws, 2.5)), 4),
                round(float(np.percentile(draws, 97.5)), 4),
            ],
            "rho_in_band": round(float(np.sqrt(np.mean(((tb - pb) / sigma_e[band, j]) ** 2))), 3),
            "mode_accuracy_full_panel": round(float((mode_true == mode_pred).mean()), 4),
        }
    out["damage_survival"] = per_method
    return out


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    out_dir = ensure_dir(args.output_dir)

    summary: dict[str, dict] = {}
    spaces = [
        ("radius2", args.r2_preds, args.r2_reliability, args.r2_sigma_e, 2, 127, 30),
        ("eca", args.eca_preds, args.eca_reliability, args.eca_sigma_e, 1, 127, 62),
    ]
    for name, preds_path, rel_path, sig_path, radius, width, horizon in spaces:
        if not Path(preds_path).exists() or not Path(rel_path).exists():
            print(f"[rev13] skipping {name}: missing artifact")
            continue
        hop = _load(preds_path)
        rel = json.load(open(rel_path))["per_feature"]
        block = {
            "n_held": len(hop.held),
            "radius": radius,
            "A1_rho": analysis_a1(hop, rel, args.n_boot, rng, sig_path),
            "A4_frontier_ceilings": analysis_a4(rel, hop.target_names),
            "A5_survival_band": analysis_a5(hop, rel, args.n_boot, rng, sig_path),
        }
        if radius > 1:
            block["A2_per_panel_reliability"] = analysis_a2(hop, rel)
            block["A3_target_dependence"] = analysis_a3(args.landscape, hop, radius, width, horizon)
        summary[name] = block

    save_json(summary, Path(out_dir) / "summary.json")

    # Console report: the numbers that go into the manuscript.
    for space, block in summary.items():
        print(f"\n=== {space} (n={block['n_held']} held-out rules) ===")
        a1 = block["A1_rho"]
        print(f"{'target':17s} " + " ".join(f"{m:>12s}" for m in METHODS if m in a1))
        for t in TARGETS:
            cells = [f"{a1[m][t]['rho']:12.2f}" for m in METHODS if m in a1]
            print(f"{t:17s} " + " ".join(cells))
        print(
            "  rho reference: sqrt(2)=1.414 simulation-limited, 1.0 latent ceiling"
            f"  [sigma_e: {a1['_reference']['sigma_e_kind']}]"
        )
        if "A3_target_dependence" in block:
            for p in block["A3_target_dependence"]["panels"]:
                print(
                    f"  A3 {p['label']}: R2(fill vs k*fraction/rate)"
                    f" = {p['r2_fill_vs_ratio']}  (derived-coordinate rule fires: "
                    f"{p['derived_coordinate_by_registered_rule']})"
                )
        if "A2_per_panel_reliability" in block:
            a2 = block["A2_per_panel_reliability"]
            print(f"  A2 max |ICC shift| vs universe sample: {a2['_max_abs_icc_shift']}")
            for p in (
                "enriched_panel",
                "random_subpanel",
                "post_stratified",
                "signature_subpanel",
            ):
                if p in a2:
                    print(
                        f"     {p:20s} median 2ICC-1 = {a2[p]['median_two_icc_minus_one']}"
                        f"  median ICC = {a2[p]['median_icc']}"
                    )
        a4 = block["A4_frontier_ceilings"]
        for fig in FRONTIER_BUDGETS:
            print(
                f"  A4 {fig} (n={a4[fig]['n_pairs']}): read-then-simulate ceiling median "
                f"{a4[fig]['median_read_then_simulate_ceiling']}, direct-estimator (ICC) "
                f"{a4[fig]['median_icc_ceiling']}"
            )
        a5 = block["A5_survival_band"]
        if "damage_survival" in a5:
            print(f"  A5 survival band {a5['band']}: {a5['n_in_band']}/{a5['n_panel']} rules")
            for m, v in a5["damage_survival"].items():
                print(
                    f"     {m:12s} full-panel R2 {v['r2_full_panel']:6.3f} -> in-band "
                    f"{v['r2_in_band']:6.3f} {v['r2_in_band_ci95']}  rho {v['rho_in_band']:5.2f}"
                    f"  mode acc {v['mode_accuracy_full_panel']:.3f}"
                )
    print(f"\n[rev13] wrote {Path(out_dir) / 'summary.json'}")


if __name__ == "__main__":
    main()
