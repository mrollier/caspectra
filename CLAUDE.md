# CLAUDE.md — Project memory

Self-supervised behavioural taxonomy of cellular-automaton spacetime diagrams.
**Full build spec: see `BUILD_BRIEF.md` — read it before implementing.**

## Non-negotiable scientific constraint
The encoder must learn mesoscopic *behaviour* (phenotype), NOT the local update
rule (genotype). A model that classifies by reconstructing the rule table is a
FAILED run, even at high clustering accuracy. The evaluation module exists to
detect this: the rule-identity linear probe must be well below 100%, and we want
MI(cluster; rule) low but MI(cluster; LP class) high.

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
- `norm_layer`: GroupNorm when batch < 256.
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
