# caspectra — Behavioural Taxonomy of Cellular Automata via Dynamical Invariants

Build a **behavioural (phenotype) taxonomy** of cellular-automaton spacetime
diagrams from **label-free dynamical invariants** (damage spreading,
input-entropy variance), and train encoders that **estimate those invariants
from a single diagram** — amortized, and eventually *spatially resolved*, so
that behaviour can be mapped locally in non-uniform CAs where global twin-run
invariants do not apply.

**Why not "discover the taxonomy with SSL"?** That was this project's original
mission, and it is not defensible: there is no bias-free clustering
(Kleinberg's impossibility theorem), formalized CA classes are undecidable
(Culik & Yu), the observed class depends on the initial-condition measure and
observation protocol (Gilman), and instance-discrimination SSL provably prefers
shortcut cues — which our first full run confirmed (rule probe 0.967 through an
anti-cheat architecture; a 4-scalar physics baseline beat the learned embedding
at its own goal). The full argument, with sources and decision records, is in
**`FOUNDATIONS.md`**; the measured record is in `RESULTS.md`. The texture-SSL
result is retained as the documented **negative baseline**.

The validation setting is the **elementary CAs (ECAs)** — 256 rules, 88
equivalence classes — where reference classifications (Li–Packard, Wolfram)
exist as *touchstones* (not ground truth: see the borderline-rule flags in
`rule_labels.csv`).

## What exactly is being classified

"The behaviour class of rule R" is not a well-defined quantity — it depends on
the observation protocol (see `FOUNDATIONS.md` §1). What this repo classifies
is the tuple:

> *(rule orbit under reflection/complement, Bernoulli(1/2) IC measure, ring of
> 127 cells with periodic boundaries, horizon of 127 rows from t = 0)*

Every metric and label is indexed by this tuple; `scripts/protocol_sensitivity.py`
measures how sensitive the invariants and the taxonomy are to the IC density and
lattice width (criterion 5 in `EVALUATION_CRITERIA.md`).

## The one non-negotiable constraint

The pipeline must surface **mesoscopic behaviour (the phenotype)**, *not* the
local update rule (the genotype). Success is judged at the **geometry/cluster
level**, against the pre-registered criteria in `EVALUATION_CRITERIA.md`
(revision 2):

- discovered clusters must **track behaviour classes** (per-class recall,
  including Wolfram class IV = {54, 110}, with borderline rules 40/41/42/106
  flagged and reported both ways), not the 88 rule orbits;
- clusters must carry ≈ no rule information beyond the behaviour class
  (**`MI(cluster; orbit | class)` ≈ 0**);
- learned representations are compared against the **direct dynamical
  invariants** (damage spreading; `eval/dynamics.py`) — the learning component
  must *match them out-of-sample and add spatial resolution*, or it concludes
  as a negative result (kill criteria in `FOUNDATIONS.md` §4);
- the taxonomy must be **stable under the observation protocol** (criterion 5).

The **rule(orbit)-identity probe** is still reported prominently, but as a
*diagnostic*, not pass/fail: any expressive encoder identifies rules from
texture statistics alone, so low rule decodability is not an achievable — or
well-aimed — bar. The failure mode that matters is behavioural structure being
present but **not salient** (v1: density dominated the geometry and clustering
followed it).

## Requirements & environment

- **Python 3.11+ (arm64), PyTorch.** Target hardware: **Apple Silicon (M4)**.
- Device selection prefers **MPS**, falling back to **CPU** (behind one
  `select_device()` util so CUDA can be added later). **AMP/autocast is OFF**
  (fp32) — MPS autocast is unreliable.
- **Always set `PYTORCH_ENABLE_MPS_FALLBACK=1`** so any op MPS lacks falls back
  to CPU instead of crashing:

  ```bash
  export PYTORCH_ENABLE_MPS_FALLBACK=1
  ```

- DataLoader uses modest `num_workers` (2–4) with `persistent_workers=True`;
  high worker counts can be flaky on macOS.

## Install

**Always install into a dedicated environment** — never your conda `base`. The
deps are version-pinned (`torch==2.12.0`, `numpy==2.2.5`, …) and installing them
into a shared env risks breaking other projects (and being broken by them).

```bash
# 1. create + activate an isolated env (Python 3.11, arm64)
conda create -n ssl-ecas python=3.11 -y
conda activate ssl-ecas

# 2. install the package (editable) and its pinned deps
pip install -e .             # core deps are pinned in pyproject.toml
pip install -e ".[dev]"      # + pytest / black / ruff
pip install -e ".[notebook]" # + nbconvert / ipykernel (to run notebooks/)
```

Re-run `conda activate ssl-ecas` in every new shell before using the project.
(`venv` works too: `python3.11 -m venv .venv && source .venv/bin/activate`.)

If `hdbscan` or `umap-learn` fail to build via pip on arm64, install them from
**conda-forge** into the same env instead:

```bash
conda install -c conda-forge hdbscan umap-learn
```

## Quickstart

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1

# 1. (optional) pre-generate + cache the dataset
python scripts/generate_data.py --config configs/default.yaml

# 2. fast smoke run first (6 rules, 16 ICs, 63px, SimSiam, 3 epochs)
python scripts/train.py    --config configs/smoke.yaml
python scripts/evaluate.py --config configs/smoke.yaml

# 3. the real run (88 rules, 127px, BYOL + ResNet18)
python scripts/train.py    --config configs/default.yaml
python scripts/evaluate.py --config configs/default.yaml
```

Each script writes the resolved config and the chosen device into its output
directory. Training produces `loss_log.csv`, `loss_curve.png` and checkpoints;
evaluation produces `probes.csv`, `cluster_summary.txt`, `umap_scatter.png`,
per-cluster sample grids, `embeddings.npz` and `summary.json`.

> Always run the **smoke config first** to catch integration errors before
> committing to a full 127×127 run.

## Where to put `rule_labels.csv`

The LP/Wolfram parts of evaluation need an external `rule_labels.csv`. The
committed table has **LP classes for all 88 representatives transcribed from
Li & Packard (1990), Table 2** — see `rule_labels_PROVENANCE.md` for the source,
the verification checks, and the corrections made to the earlier best-effort
table. **Everything else runs without it** — the rule-identity probe and
clustering still work; only the LP/Wolfram probes and metrics are skipped (with
a warning).

- **Default location:** the repository root (`./rule_labels.csv`), or set
  `eval.rule_labels_csv` in your config to any path.
- **Format** (header required):

  ```csv
  rule,lp_class,wolfram_class
  0,1,1
  90,5,3
  110,5,4
  ...
  ```

Rows with a blank class cell are simply omitted from that mapping.

> **Class-IV caveat:** Li–Packard classify the complex rules 54 and 110 as
> *chaotic* (class 5) — LP has no "complex" class. Any class-IV metric must use
> the `wolfram_class` column (4 = complex).

## Defaults (and when to change them)

| Setting | Default | Note |
|---|---|---|
| `grid_size` | **127** | odd on purpose (see below); 63 is for smoke tests only |
| `encoder` | **anticheat** | 2×2 kernels + small signed bottleneck; resist rule memorisation. `resnet18`/`smallcnn` also available |
| method | **BYOL** | switch to **SimSiam** if M4 memory forces batch < ~256 |
| `norm_layer` | **GroupNorm** | BatchNorm degrades BYOL at small batch |
| augmentations | **cyclic-shift + stochastic coarse-grain + flip + inversion** | flip/inversion are the class-defining symmetries (see below); ablate via `configs/no_symmetry.yaml` |

Excluded as positive-pair augmentations (by design): time/vertical flips,
rotations/transposes, salt-and-pepper noise — see `data/augmentations.py`.

### Why flip + inversion are ON (the symmetry that defines the classes)

The 256 ECAs reduce to 88 classes under exactly two operations: **left↔right
reflection** and **0↔1 complementation** (`caspectra.ca.eca.reflect` /
`complement`). Diagrams related by these are *the same automaton* — they share a
behaviour class by construction. So `horizontal_flip` and `invert` are not
arbitrary augmentations: they are the **group action whose orbits *are* the
equivalence classes**, and a flipped/inverted view is an *exact*, valid diagram of
the orbit partner (unlike lossy coarse-grain). Enforcing SSL invariance to them is
the most principled prior we have.

**Honest caveat:** because we only simulate the 88 representatives, these
invariances do **not** by themselves suppress the genotype cheat — that is the job
of coarse-grain + the 2×2 anti-cheat kernels + the small bottleneck. They impose a
*correct prior* (the encoder stops using chirality/polarity as cheap
discriminators) and they redefine "genotype" as the **orbit**. Accordingly:

- the genotype linear probe and `MI(cluster; ·)` diagnostics use the
  **equivalence-class representative** (e.g. `{0, 255}` → rep `0`), not the
  individual rule — success is clusters mapping to the *coarser* LP behaviour
  classes, not collapsing onto the 88 orbits;
- the `mean_density` hand-crafted baseline is **polarity-folded** (`min(d, 1−d)`)
  so it doesn't get an absolute-density feature the invert-invariant encoder is
  denied, keeping the gap comparison apples-to-apples.

Run `configs/no_symmetry.yaml` (identical but with both OFF) alongside the default
to measure the effect.

### Why `grid_size` is odd (the power-of-two trap)

Reference ECA classifications (Li–Packard, Wolfram) assume an **infinite**
lattice, but we simulate a **finite ring** (periodic boundaries). The canonical
victim is **rule 90** (`xᵢ' = xᵢ₋₁ ⊕ xᵢ₊₁`), linear over GF(2):
`T = S + S⁻¹ = S⁻¹(S + I)²`. When the ring length is a power of two,
`xᴺ − 1 = (x + 1)ᴺ` over GF(2), so `(S + I)` is **nilpotent** and *every* initial
condition collapses to the all-zero homogeneous state within ≤ N steps. So at
`grid_size = 128` (or 64) rule 90 — a canonical class-3 chaotic rule — renders as
a **blank diagram**, contradicting its label and silently corrupting the gap /
`MI(cluster; rule | LP)` diagnostics. (The effect is specific, not generic to
additive rules: rule **150**, symbol `1 + x + x²`, stays invertible on a `2ᵏ`
ring and does *not* collapse.) An odd, ideally prime side length (**127**, or
**63** for smoke) breaks the nilpotency and restores the expected dynamics.
`SpacetimeDataset` emits a warning if you pass a power-of-two `grid_size`
(`caspectra.utils.warn_if_pathological_grid`).

This is about the **spatial grid only**. Keep **batch size, channel counts and
embedding dim** as powers of two — that is where hardware (SIMD/warp/tensor-core
tiling and memory alignment) actually benefits; the convolution's spatial extent
does not.

## Diagnostics (how to tell success from the failure mode)

These make "behaviour, not rule" *measurable* (reasoning in `SELF_CRITICISM.md`;
**pass/fail thresholds are pre-registered in `EVALUATION_CRITERIA.md`** — the
headline criteria are cluster-level: per-class recall incl. class IV, excess
genotype info ≈ 0, beating the physics baseline, stability):

- **The gap** — `LP_probe_acc − rule_probe_acc`, reported by
  `evaluate.py`. A *large positive* gap means behaviour is learned while the
  exact rule is suppressed. Mirrors the prior supervised paper's metric; kept as
  a diagnostic for continuity (no longer the pass/fail headline).
- **Hand-crafted baseline** — the embedding is compared against cheap descriptors
  (density, temporal activity, compression ratio, 2×2 block entropy;
  `eval/baselines.py`). If the embedding doesn't beat the baseline on the gap, the
  deep pipeline isn't earning its keep.
- **Collapse metric** — the trainer logs `embedding_std` each epoch (CSV + loss
  PNG). It → 0 on representational collapse, which would otherwise *also* minimise
  the loss; the smoke gate asserts it stays > 0.
- **Excess rule information** — `MI(cluster; rule | LP)` (= `MI(cluster;rule) −
  MI(cluster;LP)`, ≥ 0). Want **≈ 0** (clusters carry no rule info beyond the
  behavioural class). This replaces an earlier diagnostic that was mathematically
  impossible to satisfy.
- **Per-class / balanced metrics & leave-rules-out** — probes report balanced
  accuracy and macro-F1 (the classes are very imbalanced), and LP/Wolfram probes
  can hold out *entire rules* (`lp_split="rules"`) to test transfer to unseen rules.
- **Cluster-count stability** — `evaluate.py` sweeps `min_cluster_size`; the count
  is a hyperparameter, not an emergent constant.

## Repository layout

```
caspectra/
├── ca/         eca.py (simulation + 88-class symmetry) · nuca.py (stub)
├── data/       dataset.py (+ caching) · augmentations.py (stochastic coarse-grain)
├── models/     encoder.py (AntiCheatCNN / ResNet18 / SmallCNN) · byol.py (BYOL / SimSiam)
├── train/      trainer.py (loop, EMA, checkpoints, CSV + loss PNG, collapse metric)
├── eval/       probes.py (gap) · cluster.py · baselines.py · salience.py (criteria 1&2,
│               effective rank, density R²) · dynamics.py (damage-spreading physics
│               baseline) · visualize.py · embed.py · labels.py
├── config.py   dataclass configs (+ YAML)   utils.py  seeding / device / IO
scripts/        generate_data.py · train.py · evaluate.py · protocol_sensitivity.py
configs/        smoke.yaml · default.yaml
FOUNDATIONS.md  what can and cannot be claimed (lit-review distillate + decision records)
RESULTS.md      measured record & decision gates   EVALUATION_CRITERIA.md  pre-registered thresholds
docs/literature/  the commissioned deep-research report (verbatim)
tests/          test_eca · test_augment · test_dataset · test_shapes · test_models ·
                test_trainer · test_config · test_utils · test_eval · test_baselines · test_nuca
```

## Tests

```bash
pytest -q
```

The suite asserts the **88-class** count, the ECA sanity diagrams and periodic
boundaries, augmentation invariants, encoder/model shapes, that **training
reduces the loss on a tiny subset**, and the full probe/cluster/visualise
evaluation path.

## Out of scope (not built)

Non-uniform CA generation/training (interface stub only in `ca/nuca.py`);
experiment-tracking frameworks (logging is CSV + PNG only); distributed /
multi-GPU; CUDA-specific paths (the device util stays extensible);
hyperparameter search.
