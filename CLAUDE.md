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
- `grid_size = 128` (use 64 only for smoke tests).
- Method: **BYOL** default; **SimSiam** if batch < ~256.
- `norm_layer`: GroupNorm when batch < 256.
- Augmentations: cyclic-shift + coarse-grain ON; flip + inversion are an
  experimental toggle (OFF). No time-flip, no rotation, no salt-and-pepper.

## Workflow rules
- Follow the build order in `BUILD_BRIEF.md` §5; **pause after each step for review.**
- Always run tests + a 64px smoke run before any long 128px run.
- **Ask before launching long training runs.**
- Type hints + docstrings (explain WHY); Black + Ruff; small single-purpose classes.
