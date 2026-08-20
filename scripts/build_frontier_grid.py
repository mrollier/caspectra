#!/usr/bin/env python3
"""F3 (EVALUATION_CRITERIA.md rev 9): the identifiability-frontier grid.

Compares every registered estimator on degraded observations of the rev-8
identifiability panel: the deterministic inverter, the F1 Bayesian
rule-posterior simulator (eps known / eps self-consistency-estimated), the
frozen direct CNN, the five-statistic GBM, a train-rule-fitted stats+CNN stack,
and (when ``--reader-checkpoint`` is given) the F2 learned rule-reader ->
simulator in MAP and sampled variants. Axes: bit-flip noise (dense), masking,
IC density, state-label (polarity) noise, and unknown radius. Per cell: median
held-out R^2 per estimator (with rule-bootstrap CIs on the leaders), exact
reconstruction / per-bit accuracy, and for the radius axis the selected-radius
distribution.

Numbers only after the rev-9 registration commit; no training happens here.

Usage::

    python scripts/build_frontier_grid.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt --max-rules 80
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import torch
from matplotlib.lines import Line2D  # noqa: E402
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from caspectra.ca.eca import ECASimulator
from caspectra.ca.range_ca import RangeCA, embed_eca
from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.baselines import compute_baseline_features
from caspectra.eval.dynamics import damage_spreading_features
from caspectra.eval.identifiability import (
    degrade_diagram,
    masked_transition_counts,
    project_table_radius3_to_2,
    select_radius,
)
from caspectra.eval.rule_inference import (
    complete_table,
    noisy_table_posterior,
    table_to_rule,
)
from caspectra.factory import build_dataset, build_model
from caspectra.train.regression_trainer import r2_per_feature
from caspectra.utils import ensure_dir, save_json, select_device, set_seed

warnings.filterwarnings("ignore", message=".*encountered in matmul")

NOISE = [0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20]
MASK = [0.0, 0.10, 0.25, 0.40, 0.50, 0.75, 0.90]
DENSITY = [0.1, 0.25, 0.5, 0.75, 0.9]
LABEL_FLIP = [0.0, 0.5, 1.0]
RADIUS_NOISE = [0.0, 0.01, 0.02, 0.05]  # unknown-radius axis, at these noise levels


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="F3 identifiability-frontier grid (rev 9).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True, help="Frozen direct-CNN checkpoint.")
    p.add_argument("--reader-checkpoint", default=None, help="F2 rule-reader checkpoint.")
    p.add_argument("--device", default="mps")
    p.add_argument("--n-pairs", type=int, default=48, help="MC pairs per simulation.")
    p.add_argument("--n-samples", type=int, default=8, help="Posterior table samples (F1/F2).")
    p.add_argument("--max-rules", type=int, default=80)
    p.add_argument("--n-boot", type=int, default=2000)
    p.add_argument("--axes", nargs="*", default=["noise", "mask", "density", "label", "radius"])
    p.add_argument("--output-dir", default=None)
    p.add_argument("--write-figure", action="store_true", help="Write manuscript figure.")
    p.add_argument(
        "--replot-from",
        default=None,
        help="Redraw the figure from a committed summary.json without re-running any "
        "sweep. Figure-only changes (labels, shared legend, benchmark lines) should "
        "never cost a grid re-simulation.",
    )
    p.add_argument(
        "--manuscript-axes",
        default=None,
        help="Comma-separated axes to draw in the manuscript figure. The polarity axis is "
        "four flat lines (the read-then-simulate family is exactly invariant by "
        "construction) and does not earn a panel; the full four-axis figure is still "
        "written to the run directory.",
    )
    p.add_argument(
        "--force-overwrite",
        action="store_true",
        help="Allow a sweep to replace an existing summary.json in the output directory.",
    )
    p.add_argument(
        "--reliability-summary",
        default="runs/m4_range2/reliability/summary.json",
        help="Source of the per-target ICCs used to draw the panel ceilings.",
    )
    p.add_argument(
        "--extra-cnn",
        action="append",
        default=[],
        metavar="NAME=CKPT",
        help="Additional frozen direct-CNN checkpoint (rev-10 control) evaluated per cell; "
        "its architecture is read from the config.yaml saved next to the checkpoint.",
    )
    p.add_argument(
        "--direct-only",
        action="store_true",
        help="Rev-10 fast path: evaluate only the --extra-cnn estimators (no read-family "
        "re-simulation; the degraded diagrams are regenerated identically from the same "
        "seeds). Verdicts are joined against --reference-summary.",
    )
    p.add_argument(
        "--reference-summary",
        default=None,
        help="Canonical grid summary.json; supplies the read-family cells for the "
        "rev-10 verdict joins in --direct-only mode.",
    )
    p.add_argument(
        "--calibrate-f1",
        action="store_true",
        help="Rev-9 outstanding reporting item: per-cell empirical coverage of the "
        "eps-estimated posterior's nominal 1-sigma predictive interval. Tag arithmetic "
        "matches the canonical run, so the recomputed medians double as a bit-exact "
        "reproduction check of the released grid.",
    )
    p.add_argument(
        "--rule-subsample",
        choices=("seed0", "complement"),
        default="seed0",
        help="Rev-11 M7: 'seed0' is the canonical fixed-seed frontier subsample; "
        "'complement' evaluates the held-out rules that subsample excluded (an "
        "independent rule panel at identical budgets, for replication).",
    )
    return p.parse_args()


PRODUCTION_PAIRS = 256
# REVTeX two-column \textwidth, in inches: the manuscript figure's true width.
TEXTWIDTH_IN = 7.1
# Vertical band reserved below the axes for the shared legend, in inches.
LEGEND_BAND_IN = 0.6  # cfg.targets.n_pairs: the budget the cached targets were measured at


def _ceilings(args):
    """Panel ceilings under the ACTUAL scoring convention (referee 4, §3.16).

    The grid scores an estimator that simulates at ``args.n_pairs`` against the
    production target cache at ``PRODUCTION_PAIRS``. A fresh-simulation
    estimator therefore carries sigma_e^2(n) = (256/n) sigma_e^2(256) of its own
    noise on top of the target's, so its ceiling is 1 - (1 + 256/n)(1 - ICC) --
    NOT 2*ICC - 1 evaluated at the reduced budget, which would be the ceiling
    if the targets had been recomputed at n too. A direct estimator predicting
    the latent mean keeps the ICC ceiling at any grid budget.
    """
    path = Path(args.reliability_summary)
    if not path.exists():
        return None
    per = json.loads(path.read_text())["per_feature"]
    iccs = [float(v["icc"]) for v in per.values()]
    scale = PRODUCTION_PAIRS / args.n_pairs
    rts = [1.0 - (1.0 + scale) * (1.0 - i) for i in iccs]
    return {
        "read_then_simulate": float(np.median(rts)),
        "direct": float(np.median(iccs)),
    }


# Readable estimator names. The rev-9 artifact keys (``f1_eps_known`` etc.) are
# not names a reader can follow, and the fourth referee report (§7) is right
# that they should not appear in a published legend.
ESTIMATOR_LABELS = {
    "det": "deterministic inverter",
    "f1_eps_known": r"pseudo-posterior ($\varepsilon$ given)",
    "f1_eps_estimated": r"pseudo-posterior ($\varepsilon$ estimated)",
    "f2_map": "learned reader (MAP)",
    "f2_sampled": "learned reader (sampled)",
    "cnn": "direct CNN (frozen)",
    "gbm": "5 statistics",
    "stack": "5 stats + CNN stack",
    "degaug": "direct CNN (degradation-trained)",
    "degaug_sel": "direct CNN (degradation-trained, selected)",
    "resnet18": r"\texttt{resnet18} (unconstrained)",
}
AXIS_LABELS = {
    "noise": "bit-flip noise rate",
    "mask": "masked cell fraction",
    "density": "initial-condition density",
    "label": "label-polarity flip fraction",
}


def plot_grid(grid, radius, out, write_figure, ceilings=None, axes_shown=None):
    """Draw the frontier figure from a grid dict (live or reloaded).

    ``ceilings`` is ``{"read_then_simulate": float, "direct": float}``: the
    panels score an estimator simulating at the grid budget against the
    production target cache, so neither family's ceiling is 1 and the curves
    are unreadable without them drawn (referee 4, §3.16).
    """
    wanted = axes_shown or ("noise", "mask", "density", "label")
    panels = [a for a in wanted if a in grid]
    if not panels:
        return
    ncol = 3 if len(panels) == 3 else 2
    nrow = int(np.ceil(len(panels) / ncol))
    # The manuscript figure is included at \textwidth (7.1 in in the two-column
    # REVTeX layout). Drawing it wider and letting LaTeX scale it down shrinks
    # every font by the same factor -- a 3-panel row drawn at 9.9 in lands at
    # 5 pt type. Size the canvas to the destination instead.
    panel_w = TEXTWIDTH_IN / ncol if axes_shown else 3.3
    fig, axes_arr = plt.subplots(
        nrow, ncol, figsize=(panel_w * ncol, 0.95 * panel_w * nrow + LEGEND_BAND_IN), squeeze=False
    )
    styles = {
        "det": ("^-", "C2"),
        "f1_eps_known": ("v-", "C3"),
        "f1_eps_estimated": ("v--", "C3"),
        "f2_map": ("D-", "C4"),
        "f2_sampled": ("D--", "C4"),
        "cnn": ("o-", "C0"),
        "gbm": ("s-", "C1"),
        "stack": ("*-", "C5"),
        "degaug": ("P-", "C6"),
        "degaug_sel": ("P-", "C8"),
        "resnet18": ("X-", "C7"),
    }
    handles, labels = [], []
    for i, axis_name in enumerate(panels):
        ax = axes_arr[i // ncol][i % ncol]
        cells = grid[axis_name]
        xs = [c["value"] for c in cells]
        if ceilings:
            ax.axhline(ceilings["read_then_simulate"], color="0.35", lw=0.8, ls="-.", zorder=0)
            ax.axhline(ceilings["direct"], color="0.6", lw=0.8, ls=":", zorder=0)
        for est, (fmt, col) in styles.items():
            ys = [c["estimators"].get(est, {}).get("median_r2") for c in cells]
            if any(v is not None for v in ys):
                (line,) = ax.plot(
                    xs, ys, fmt, color=col, label=ESTIMATOR_LABELS.get(est, est), ms=4
                )
                if ESTIMATOR_LABELS.get(est, est) not in labels:
                    handles.append(line)
                    labels.append(ESTIMATOR_LABELS.get(est, est))
        ax.set_xlabel(AXIS_LABELS.get(axis_name, axis_name))
        ax.set_ylabel("median held-out $R^2$")
        ax.set_ylim(-0.05, 1.05)
    for j in range(len(panels), nrow * ncol):
        axes_arr[j // ncol][j % ncol].set_visible(False)
    if ceilings:
        handles.append(Line2D([], [], color="0.35", lw=0.8, ls="-."))
        labels.append("read-then-simulate ceiling (grid budget)")
        handles.append(Line2D([], [], color="0.6", lw=0.8, ls=":"))
        labels.append("direct-estimator ceiling (ICC)")
    # One shared legend outside the axes: the eight-entry legend repeated in
    # every panel cost most of the plot area (referee 4, §7).
    legend_ncol = 3
    legend_rows = int(np.ceil(len(labels) / legend_ncol))
    fig.legend(
        handles,
        labels,
        fontsize=7,
        loc="lower center",
        ncol=legend_ncol,
        frameon=False,
        bbox_to_anchor=(0.5, -0.01),
    )
    fig.suptitle(f"Identifiability frontier (radius {radius})")
    # Reserve the legend's height in inches, not as a fixed fraction: the
    # manuscript figure is short enough that a 10% band would overlap the axes.
    fig.tight_layout(rect=(0, min(0.35, 0.15 * legend_rows / fig.get_figheight()), 1, 1))
    fig.savefig(out / "frontier.pdf")
    if write_figure:
        fig.savefig("manuscript/figures/identifiability_v2.pdf")


def main() -> None:  # noqa: C901 - one orchestration function, sectioned below
    args = parse_args()
    if args.replot_from:
        # Figure-only changes must never cost a grid re-simulation: the committed
        # summary.json already holds every plotted number.
        src = Path(args.replot_from)
        payload = json.loads(src.read_text())
        plot_grid(
            payload["grid"],
            payload.get("radius", 2),
            Path(ensure_dir(args.output_dir or str(src.parent))),
            args.write_figure,
            _ceilings(args),
            tuple(args.manuscript_axes.split(",")) if args.manuscript_axes else None,
        )
        print(f"[f3] replotted from {src} (no simulation)")
        return
    cfg = ExperimentConfig.from_yaml(args.config)
    # The rev-10 modes must never clobber the canonical released artifact.
    if args.direct_only:
        default_out = f"{cfg.train.output_dir}/frontier_grid_controls"
    elif args.calibrate_f1:
        default_out = f"{cfg.train.output_dir}/frontier_grid_calibration"
    else:
        default_out = f"{cfg.train.output_dir}/frontier_grid"
    if args.rule_subsample == "complement":
        default_out += "_complement"  # never clobber a canonical-panel artifact
    out = ensure_dir(args.output_dir or default_out)
    # A sweep must never silently replace a released artifact. This directory is
    # gitignored, so an accidental overwrite is unrecoverable and invisible to
    # `git status` -- which is exactly how the canonical grid was once lost to a
    # run whose --replot-from flag had failed to take effect.
    existing = Path(out) / "summary.json"
    if existing.exists() and not args.force_overwrite:
        raise SystemExit(
            f"{existing} already exists. Sweeps do not overwrite released artifacts: "
            "pass --output-dir to write elsewhere, --replot-from to redraw the figure "
            "without simulating, or --force-overwrite if you really mean to replace it."
        )
    lean_mode = args.direct_only or args.calibrate_f1
    set_seed(cfg.seed)
    radius, width = cfg.data.radius, cfg.data.grid_size
    density0 = cfg.targets.ic_density

    ds = build_dataset(cfg.data, training=False)
    reps = np.asarray(ds.equiv_reps)
    images = ds.images
    rules = sorted({int(r) for r in reps})
    horizon = images.shape[1]

    targets = load_or_compute_invariant_targets(
        rules,
        width=width,
        ic_density=density0,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=radius,
    )
    true_by_rule = {r: targets[i] for i, r in enumerate(rules)}

    state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    held = [int(r) for r in state["holdout_rules"] if int(r) in set(rules)]
    train_rules = [r for r in rules if r not in set(held)]
    if args.max_rules and len(held) > args.max_rules:
        # Same subsample rule as the rev-8 identifiability run (fixed seed 0).
        sub = sorted(np.random.default_rng(0).choice(held, args.max_rules, replace=False).tolist())
        if args.rule_subsample == "complement":
            # Rev-11 M7: the excluded rules form an independent replication panel
            # (per-rule RNG streams are identity-keyed, so budgets match exactly).
            held = sorted(set(held) - set(sub))[: args.max_rules]
        else:
            held = sub
    held_diag = {r: images[np.flatnonzero(reps == r)[0]] for r in held}
    true_held = np.stack([true_by_rule[r] for r in held])
    true_tables = {r: np.array([(r >> k) & 1 for k in range(1 << (2 * radius + 1))]) for r in held}
    print(
        f"[f3] radius={radius} width={width} held={len(held)} "
        f"n_pairs={args.n_pairs} n_samples={args.n_samples} axes={args.axes}"
    )

    # --- Frozen direct CNN + train-fitted baseline & stack. --------------------
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    device = select_device(prefer=args.device)
    model = model.to(device).eval()
    s_mean, s_std = state["scaler_mean"], state["scaler_std"]

    # Rev-10 control checkpoints: independent scalers, architecture from the
    # config saved in each run dir. Evaluated as frozen forward passes only.
    extra_cnns: dict[str, tuple] = {}
    for spec in args.extra_cnn:
        name, ckpt = spec.split("=", 1)
        e_state = torch.load(ckpt, map_location="cpu", weights_only=False)
        e_cfg = ExperimentConfig.from_yaml(str(Path(ckpt).parent / "config.yaml"))
        e_model = build_model(e_cfg.model)
        e_model.load_state_dict(e_state["model_state"])
        extra_cnns[name] = (
            e_model.to(device).eval(),
            e_state["scaler_mean"],
            e_state["scaler_std"],
        )
        if sorted(int(r) for r in e_state["holdout_rules"]) != sorted(
            int(r) for r in state["holdout_rules"]
        ):
            raise SystemExit(f"control {name!r} was trained on a different holdout split")

    @torch.no_grad()
    def extra_cnn_preds(e_model, e_mean, e_std, diagrams: dict[int, np.ndarray]) -> np.ndarray:
        outp = []
        for r in held:
            b = torch.from_numpy(diagrams[r].astype(np.float32))[None, None].to(device)
            outp.append(e_model(b).cpu().numpy()[0] * e_std + e_mean)
        return np.stack(outp)

    feats_all = compute_baseline_features(images, radius=radius) if not lean_mode else None
    tr = np.isin(reps, train_rules)
    if not lean_mode:
        scaler = StandardScaler().fit(feats_all[tr])
        y = np.stack([true_by_rule[int(r)] for r in reps])
        gbms = [
            GradientBoostingRegressor(random_state=0).fit(scaler.transform(feats_all[tr]), y[tr, j])
            for j in range(len(TARGET_NAMES))
        ]

    @torch.no_grad()
    def cnn_preds(diagrams: dict[int, np.ndarray]) -> np.ndarray:
        outp = []
        for r in held:
            b = torch.from_numpy(diagrams[r].astype(np.float32))[None, None].to(device)
            outp.append(model(b).cpu().numpy()[0] * s_std + s_mean)
        return np.stack(outp)

    def gbm_preds(diagrams: dict[int, np.ndarray]) -> np.ndarray:
        f = scaler.transform(
            compute_baseline_features(np.stack([diagrams[r] for r in held]), radius=radius)
        )
        return np.stack([g.predict(f) for g in gbms], axis=1)

    # Stats+CNN stack, fitted on TRAIN rules' clean diagrams only (deployable hybrid).
    if not lean_mode:
        with torch.no_grad():
            cnn_tr = []
            for i in np.flatnonzero(tr):
                b = torch.from_numpy(images[i].astype(np.float32))[None, None].to(device)
                cnn_tr.append(model(b).cpu().numpy()[0] * s_std + s_mean)
        stack_X_tr = np.hstack([scaler.transform(feats_all[tr]), np.stack(cnn_tr)])
        stack_models = [
            Ridge(alpha=1.0).fit(stack_X_tr, y[tr, j]) for j in range(len(TARGET_NAMES))
        ]

    def stack_preds(diagrams: dict[int, np.ndarray]) -> np.ndarray:
        f = scaler.transform(
            compute_baseline_features(np.stack([diagrams[r] for r in held]), radius=radius)
        )
        X = np.hstack([f, cnn_preds(diagrams)])
        return np.stack([m.predict(X) for m in stack_models], axis=1)

    # --- Optional F2 learned rule-reader. --------------------------------------
    reader = None
    if args.reader_checkpoint:
        from caspectra.models.rule_reader import load_rule_reader

        reader = load_rule_reader(args.reader_checkpoint, device)

    def _rng(r: int, tag: int) -> np.random.Generator:
        return np.random.default_rng(
            np.random.SeedSequence([int(cfg.targets.seed) + 224747, int(r), tag])
        )

    def simulate(rule_number: int, rr: int, gen) -> np.ndarray:
        if rr == 1:
            return damage_spreading_features(
                rule_number, width=width, n_pairs=args.n_pairs, ic_density=density0, rng=gen
            )
        return damage_spreading_features(
            simulator=RangeCA(rule_number, rr),
            width=width,
            n_pairs=args.n_pairs,
            ic_density=density0,
            rng=gen,
        )

    # --- Estimators (each returns preds (N,4) + diagnostics). ------------------
    def det_estimate(diagrams, masks, tag):
        preds, exact = [], []
        for r in held:
            ones, total = masked_transition_counts(diagrams[r], radius, masks.get(r))
            obs = total > 0
            table = (2 * ones > total).astype(np.uint8)
            rule = table_to_rule(complete_table(table, obs, "zero"))
            exact.append(rule == r)
            preds.append(simulate(rule, radius, _rng(r, tag)))
        return np.stack(preds), {"exact": float(np.mean(exact))}

    def f1_estimate(diagrams, masks, tag, eps=None, calibrate=False):
        preds, exact, bitacc, covered = [], [], [], []
        for r in held:
            ones, total = masked_transition_counts(diagrams[r], radius, masks.get(r))
            if eps is None:
                seen = total > 0
                if seen.any():
                    minority = np.minimum(ones[seen], total[seen] - ones[seen])
                    disagree = float(minority.sum() / total[seen].sum())
                else:
                    disagree = 0.0
                from caspectra.eval.rule_inference import EPS_GRID

                e = float(min(EPS_GRID, key=lambda v: abs(v - disagree)))
            else:
                e = float(eps)
            p_bits = noisy_table_posterior(ones, total, e)
            map_table = (p_bits >= 0.5).astype(np.uint8)
            exact.append(table_to_rule(map_table) == r)
            bitacc.append(float(np.mean(map_table == true_tables[r])))
            gen = _rng(r, tag)
            sims = []
            for _ in range(args.n_samples):
                tbl = (gen.random(p_bits.shape[0]) < p_bits).astype(np.uint8)
                sims.append(simulate(table_to_rule(tbl), radius, gen))
            arr = np.stack(sims)
            preds.append(arr.mean(axis=0))
            if calibrate:
                # Rev-9 registered reporting: does the nominal 1-sigma
                # predictive interval (posterior-sample spread) cover the
                # production target the estimator is scored against?
                sigma = arr.std(axis=0, ddof=0)
                covered.append(np.abs(true_by_rule[r] - arr.mean(axis=0)) <= sigma)
        diag = {
            "exact": float(np.mean(exact)),
            "bit_accuracy": float(np.mean(bitacc)),
        }
        if calibrate:
            cov = np.stack(covered)
            diag["interval_coverage_1sigma"] = round(float(cov.mean()), 4)
            diag["interval_coverage_per_target"] = {
                n: round(float(v), 4) for n, v in zip(TARGET_NAMES, cov.mean(axis=0))
            }
        return np.stack(preds), diag

    def f2_estimate(diagrams, tag, sampled: bool):
        assert reader is not None
        preds, exact, bitacc = [], [], []
        for r in held:
            p_bits = reader.predict_bits(diagrams[r])
            map_table = (p_bits >= 0.5).astype(np.uint8)
            exact.append(table_to_rule(map_table) == r)
            bitacc.append(float(np.mean(map_table == true_tables[r])))
            gen = _rng(r, tag)
            if sampled:
                sims = []
                for _ in range(args.n_samples):
                    tbl = (gen.random(p_bits.shape[0]) < p_bits).astype(np.uint8)
                    sims.append(simulate(table_to_rule(tbl), radius, gen))
                preds.append(np.mean(sims, axis=0))
            else:
                preds.append(simulate(table_to_rule(map_table), radius, gen))
        return np.stack(preds), {
            "exact": float(np.mean(exact)),
            "bit_accuracy": float(np.mean(bitacc)),
        }

    def radius_selecting_estimate(diagrams, tag, bayes_eps=None):
        """Deterministic (or F1) estimate with the radius chosen by consistency."""
        preds, sel = [], []
        for r in held:
            r_hat, _ = select_radius(diagrams[r])
            sel.append(r_hat)
            from caspectra.eval.rule_inference import transition_counts

            ones, total = transition_counts(diagrams[r], r_hat)
            if bayes_eps is not None:
                p_bits = noisy_table_posterior(ones, total, bayes_eps)
                table = (p_bits >= 0.5).astype(np.uint8)
            else:
                obs = total > 0
                table = complete_table((2 * ones > total).astype(np.uint8), obs, "zero")
            # Lift/project to the panel radius (2) so the simulated protocol matches.
            if r_hat == radius:
                rule = table_to_rule(table)
            elif r_hat < radius:
                rule = embed_eca(table_to_rule(table), radius)
            else:
                rule = table_to_rule(project_table_radius3_to_2(table, total))
            preds.append(simulate(rule, radius, _rng(r, tag)))
        hist = {int(k): int(v) for k, v in zip(*np.unique(sel, return_counts=True))}
        return np.stack(preds), {"selected_radius_hist": hist}

    # --- Scoring. ---------------------------------------------------------------
    boot_rng = np.random.default_rng(0)
    boot_idx = boot_rng.integers(0, len(held), size=(args.n_boot, len(held)))

    def score(preds: np.ndarray) -> dict:
        per = r2_per_feature(preds, true_held)
        med_boot = np.nanmedian(
            np.clip(
                1.0
                - np.sum((true_held[boot_idx] - preds[boot_idx]) ** 2, axis=1)
                / np.sum(
                    (true_held[boot_idx] - true_held[boot_idx].mean(axis=1, keepdims=True)) ** 2,
                    axis=1,
                ),
                -1.0,
                1.0,
            ),
            axis=1,
        )
        return {
            "median_r2": round(float(np.nanmedian(per)), 4),
            "median_ci95": [
                round(float(np.nanpercentile(med_boot, 2.5)), 4),
                round(float(np.nanpercentile(med_boot, 97.5)), 4),
            ],
            "per_target_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per)},
        }

    grid: dict[str, list] = {}

    def run_cell(axis, value, diagrams, masks, cell_tag, include_direct=True, radius_axis=False):
        cell = {"value": value, "estimators": {}}
        if radius_axis:
            preds, diag = radius_selecting_estimate(diagrams, cell_tag)
            cell["estimators"]["det_radius_selected"] = {**score(preds), **diag}
            preds, diag = radius_selecting_estimate(diagrams, cell_tag + 1, bayes_eps=value)
            cell["estimators"]["f1_radius_selected"] = {**score(preds), **diag}
            preds, diag = det_estimate(diagrams, masks, cell_tag + 2)
            cell["estimators"]["det_radius_known"] = {**score(preds), **diag}
        elif args.calibrate_f1:
            # Same tag as the canonical run's eps-estimated pass, so the
            # medians reproduce the released grid bit-exactly.
            preds, diag = f1_estimate(diagrams, masks, cell_tag + 2, eps=None, calibrate=True)
            cell["estimators"]["f1_eps_estimated"] = {**score(preds), **diag}
        elif not args.direct_only:
            preds, diag = det_estimate(diagrams, masks, cell_tag)
            cell["estimators"]["det"] = {**score(preds), **diag}
            eps_known = value if axis in ("noise",) else 0.0
            preds, diag = f1_estimate(diagrams, masks, cell_tag + 1, eps=eps_known)
            cell["estimators"]["f1_eps_known"] = {**score(preds), **diag}
            preds, diag = f1_estimate(diagrams, masks, cell_tag + 2, eps=None)
            cell["estimators"]["f1_eps_estimated"] = {**score(preds), **diag}
            if reader is not None:
                preds, diag = f2_estimate(diagrams, cell_tag + 3, sampled=False)
                cell["estimators"]["f2_map"] = {**score(preds), **diag}
                preds, diag = f2_estimate(diagrams, cell_tag + 4, sampled=True)
                cell["estimators"]["f2_sampled"] = {**score(preds), **diag}
        if include_direct and not lean_mode:
            cell["estimators"]["cnn"] = score(cnn_preds(diagrams))
            cell["estimators"]["gbm"] = score(gbm_preds(diagrams))
            cell["estimators"]["stack"] = score(stack_preds(diagrams))
        if include_direct and not radius_axis:
            for name, (e_model, e_mean, e_std) in extra_cnns.items():
                cell["estimators"][name] = score(extra_cnn_preds(e_model, e_mean, e_std, diagrams))
        best = max(cell["estimators"].items(), key=lambda kv: kv[1]["median_r2"])
        cell["best"] = best[0]
        print(
            f"[f3] {axis}={value}: best={best[0]} ({best[1]['median_r2']:.3f})  "
            + "  ".join(f"{k}={v['median_r2']:.3f}" for k, v in cell["estimators"].items())
        )
        return cell

    tag = 0
    if "noise" in args.axes:
        grid["noise"] = []
        for p in NOISE:
            deg = {r: degrade_diagram(held_diag[r], flip_p=p, rng=_rng(r, 9000))[0] for r in held}
            grid["noise"].append(run_cell("noise", p, deg, {}, tag))
            tag += 10
    if "mask" in args.axes:
        grid["mask"] = []
        for p in MASK:
            deg, masks = {}, {}
            for r in held:
                d, o = degrade_diagram(held_diag[r], mask_p=p, rng=_rng(r, 9100))
                deg[r] = d if o is None else (d * o).astype(np.uint8)
                if o is not None:
                    masks[r] = o
            grid["mask"].append(run_cell("mask", p, deg, masks, tag))
            tag += 10
    if "density" in args.axes:
        grid["density"] = []
        for p in DENSITY:
            deg = {}
            for r in held:
                ic = (_rng(r, 9200).random(width) < p).astype(np.uint8)
                sim = ECASimulator(r) if radius == 1 else RangeCA(r, radius)
                deg[r] = sim.evolve(ic, horizon)
            grid["density"].append(run_cell("density", p, deg, {}, tag))
            tag += 10
    if "label" in args.axes:
        grid["label"] = []
        for p in LABEL_FLIP:
            flip_rng = np.random.default_rng(93)
            deg = {
                r: (1 - held_diag[r]).astype(np.uint8) if flip_rng.random() < p else held_diag[r]
                for r in held
            }
            grid["label"].append(run_cell("label", p, deg, {}, tag))
            tag += 10
    if "radius" in args.axes:
        grid["radius"] = []
        for p in RADIUS_NOISE:
            deg = {r: degrade_diagram(held_diag[r], flip_p=p, rng=_rng(r, 9300))[0] for r in held}
            grid["radius"].append(
                run_cell("radius", p, deg, {}, tag, include_direct=False, radius_axis=True)
            )
            tag += 10

    summary = {
        "radius": radius,
        "width": width,
        "n_held": len(held),
        "rule_subsample": args.rule_subsample,
        "n_pairs": args.n_pairs,
        "n_samples": args.n_samples,
        "reader_checkpoint": args.reader_checkpoint,
        "extra_cnns": {s.split("=", 1)[0]: s.split("=", 1)[1] for s in args.extra_cnn},
        "grid": grid,
    }

    # Rev-10 verdict joins: control cells against the canonical read-family
    # record. A hypothesis-(iii) violation = control point above the best
    # read-family estimator's CI_high at a cell with per-bit recovery >= 0.95;
    # dead-zone extension = control CI_low above the F2-sampled point value.
    if args.direct_only and args.reference_summary:

        ref = json.loads(open(args.reference_summary).read())["grid"]
        read_family = ("det", "f1_eps_known", "f1_eps_estimated", "f2_map", "f2_sampled")
        verdicts: dict[str, list] = {"h3_violations": [], "dead_zone": []}
        for axis_name, cells in grid.items():
            for cell in cells:
                ref_cell = next(
                    (c for c in ref.get(axis_name, []) if c["value"] == cell["value"]), None
                )
                if ref_cell is None:
                    continue
                ests = ref_cell["estimators"]
                reads = {k: v for k, v in ests.items() if k in read_family}
                if not reads:
                    continue
                best_name, best_read = max(reads.items(), key=lambda kv: kv[1]["median_r2"])
                bitacc = ests.get("f1_eps_estimated", {}).get("bit_accuracy")
                for name in extra_cnns:
                    ctrl = cell["estimators"][name]
                    if bitacc is not None and bitacc >= 0.95:
                        if ctrl["median_r2"] > best_read["median_ci95"][1]:
                            verdicts["h3_violations"].append(
                                {
                                    "axis": axis_name,
                                    "value": cell["value"],
                                    "control": name,
                                    "control_median": ctrl["median_r2"],
                                    "best_read": best_name,
                                    "best_read_ci_high": best_read["median_ci95"][1],
                                }
                            )
                    f2s = ests.get("f2_sampled")
                    if axis_name == "noise" and f2s is not None:
                        verdicts["dead_zone"].append(
                            {
                                "value": cell["value"],
                                "control": name,
                                "extends": bool(ctrl["median_ci95"][0] > f2s["median_r2"]),
                                "control_ci_low": ctrl["median_ci95"][0],
                                "f2_sampled_median": f2s["median_r2"],
                            }
                        )
        summary["rev10_verdicts"] = verdicts
        n_viol = len(verdicts["h3_violations"])
        n_ext = sum(1 for d in verdicts["dead_zone"] if d["extends"])
        print(f"[f3] rev-10 verdicts: h3 violations={n_viol}, dead-zone extensions={n_ext}")

    save_json(summary, out / "summary.json")

    # Figure: one panel per continuous axis, one curve per estimator.
    if not lean_mode:
        plot_grid(grid, radius, out, args.write_figure, _ceilings(args))

    print(f"[f3] wrote {out}/summary.json and {out}/frontier.pdf")


if __name__ == "__main__":
    main()
