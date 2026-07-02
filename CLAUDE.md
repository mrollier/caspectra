# CLAUDE.md — Project memory

Behavioural taxonomy of cellular-automaton spacetime diagrams via **dynamical
invariants + amortized (eventually spatially-resolved) invariant estimation**.
The original "discover a label-free taxonomy with SSL" mission was reframed on
2026-07-02 after a foundations literature review — **read `FOUNDATIONS.md`
before proposing goals or criteria changes.** Texture-SSL (BYOL) is the frozen
negative baseline, not a lever. Original build spec: `BUILD_BRIEF.md`
(historical; superseded where it conflicts with FOUNDATIONS.md).

## Non-negotiable scientific constraint
The pipeline must surface mesoscopic *behaviour* (phenotype), NOT the local
update rule (genotype) — and every claim is about the **protocol tuple**
*(orbit, Bernoulli(1/2) ICs, ring 127, horizon 127)*, not "the rule" in the
abstract (undecidability + measure-dependence; FOUNDATIONS.md §1).
**Success/failure is pre-registered in `EVALUATION_CRITERIA.md` (revision 2)
and is judged at the geometry/cluster level** — clusters must track behaviour
classes, carry ≈ no rule info beyond the class (`MI(cluster; orbit | class)`
≈ 0), match the direct damage-spreading invariants out-of-sample (criterion 6),
and be stable under the observation protocol (criterion 5). The
rule(orbit)-identity probe is reported prominently as a *diagnostic*, but is
not pass/fail: v1 showed any expressive encoder identifies rules from texture
statistics alone (probe 0.967 through the anti-cheat architecture). Do NOT
quietly relax the pre-registered thresholds. Class-IV metrics use the
`wolfram_class` column with reference set {54, 110} and **borderline flags**
(40, 41, 42, 106) reported both ways — Li–Packard folds complex into "chaotic"
and no scheme is ground truth (see `rule_labels_PROVENANCE.md`).

## Stack & environment
- **Dedicated env only** — work in the `ssl-ecas` conda env (`conda activate
  ssl-ecas`), never `base`. Create with `conda create -n ssl-ecas python=3.11`
  then `pip install -e ".[dev]"`. See README "Install".
- Python 3.11+ (arm64), PyTorch. Device: **MPS → CPU only** (Apple Silicon M4).
- AMP off (fp32). Set `PYTORCH_ENABLE_MPS_FALLBACK=1`. Keep device selection
  behind one util so CUDA can be added later.
- SSL components from `lightly`; everything else first-party OOP.
- Logging: CSV + matplotlib only. No W&B / TensorBoard / Lightning / DALI.

## Defaults
- `grid_size = 127` (use 63 for smoke tests). **Avoid powers of two** — under
  periodic boundaries a `2^k` side makes additive rules such as rule 90 collapse
  to a homogeneous state, diverging from the infinite-lattice reference classes
  (`caspectra.utils.warn_if_pathological_grid` warns). Powers of two still belong
  on batch size / channels / embedding dim, not the spatial grid.
- Method: **BYOL** default; **SimSiam** if batch < ~256.
- `norm_layer`: GroupNorm when batch < 256 — **SSL encoders only**. Regression
  encoders (`method: regressor`) always use **BatchNorm**: GroupNorm normalizes
  over whole-image statistics, which leaks global context into `predict_map`
  and destroys map locality (measured via the rule-0 partner probe; RESULTS.md
  2026-07-03).
- Augmentations: cyclic-shift + coarse-grain ON; **flip + inversion also ON** —
  they are the *exact* reflection + complementation symmetries that define the 88
  equivalence classes, so a flipped/inverted view is a genuine orbit-partner
  diagram (the most principled invariance available). Ablate via
  `configs/no_symmetry.yaml`. Caveat: these do NOT suppress the genotype cheat by
  themselves (coarse-grain + anti-cheat kernels + bottleneck do); they only stop
  chirality/polarity shortcuts and make "genotype" mean the orbit. Consequently
  the genotype probe / MI use the equivalence-class representative (e.g. {0,255}→0),
  and the density baseline is polarity-folded. No time-flip, no rotation, no
  salt-and-pepper.

## Workflow rules
- Follow the build order in `BUILD_BRIEF.md` §5; **pause after each step for review.**
- Always run tests + a 63px smoke run before any long 127px run.
- **Ask before launching long training runs.**
- Type hints + docstrings (explain WHY); Black + Ruff; small single-purpose classes.
