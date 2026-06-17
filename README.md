# caspectra — Self-Supervised Behavioural Taxonomy of Cellular Automata

Discover an open-ended, label-free **behavioural** taxonomy of cellular-automaton
(CA) spacetime diagrams via self-supervised learning (SSL) + density-based
clustering.

The validation target is the **elementary CAs (ECAs)** — the 256 rules, reducible
to **88 equivalence classes** — which have known reference classifications
(Li–Packard, Wolfram) so we can *check* that the unsupervised pipeline recovers
behaviour rather than memorising the update rule.

## The one non-negotiable constraint

The encoder must learn **mesoscopic behaviour (the phenotype)**, *not* the local
update rule (the genotype). A model that secretly classifies by reconstructing
the rule table is the known failure mode and is a **failed run even at high
clustering accuracy**. Evaluation exists primarily to detect this:

- the **rule-identity linear probe** must be **well below 100%**;
- the genotype/phenotype diagnostic wants **`MI(cluster; rule)` low** but
  **`MI(cluster; LP class)` high**.

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

```bash
pip install -e .            # core deps are pinned in pyproject.toml
pip install -e ".[dev]"     # + pytest / black / ruff
```

If `hdbscan` or `umap-learn` fail to build via pip on arm64, install them from
**conda-forge** instead:

```bash
conda install -c conda-forge hdbscan umap-learn
```

## Quickstart

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1

# 1. (optional) pre-generate + cache the dataset
python scripts/generate_data.py --config configs/default.yaml

# 2. fast smoke run first (6 rules, 16 ICs, 64px, SimSiam, 3 epochs)
python scripts/train.py    --config configs/smoke.yaml
python scripts/evaluate.py --config configs/smoke.yaml

# 3. the real run (88 rules, 128px, BYOL + ResNet18)
python scripts/train.py    --config configs/default.yaml
python scripts/evaluate.py --config configs/default.yaml
```

Each script writes the resolved config and the chosen device into its output
directory. Training produces `loss_log.csv`, `loss_curve.png` and checkpoints;
evaluation produces `probes.csv`, `cluster_summary.txt`, `umap_scatter.png`,
per-cluster sample grids, `embeddings.npz` and `summary.json`.

> Always run the **smoke config first** to catch integration errors before
> committing to a full 128×128 run.

## Where to put `rule_labels.csv`

The LP/Wolfram parts of evaluation need an external `rule_labels.csv` (taken from
the Li–Packard publication). **Everything else runs without it** — the
rule-identity probe and clustering still work; only the LP/Wolfram probes,
metrics and the `MI(cluster; LP)` half of the diagnostic are skipped (with a
warning).

- **Default location:** the repository root (`./rule_labels.csv`), or set
  `eval.rule_labels_csv` in your config to any path.
- **Format** (header required):

  ```csv
  rule,lp_class,wolfram_class
  0,1,1
  90,4,3
  110,4,4
  ...
  ```

Rows with a blank class cell are simply omitted from that mapping.

## Defaults (and when to change them)

| Setting | Default | Note |
|---|---|---|
| `grid_size` | **128** | 64 is for smoke tests only |
| `encoder` | **anticheat** | 2×2 kernels + small signed bottleneck; resist rule memorisation. `resnet18`/`smallcnn` also available |
| method | **BYOL** | switch to **SimSiam** if M4 memory forces batch < ~256 |
| `norm_layer` | **GroupNorm** | BatchNorm degrades BYOL at small batch |
| augmentations | **cyclic-shift + stochastic coarse-grain** (`coarse_grain_prob=0.5`) | flip / inversion are experimental toggles (OFF) |

Excluded as positive-pair augmentations (by design): time/vertical flips,
rotations/transposes, salt-and-pepper noise — see `data/augmentations.py`.

## Diagnostics (how to tell success from the failure mode)

These were added to make "behaviour, not rule" *measurable* (see
`SELF_CRITICISM.md` for the reasoning):

- **The gap** (the headline) — `LP_probe_acc − rule_probe_acc`, reported by
  `evaluate.py`. Success is a *large positive* gap: behaviour is learned while the
  exact rule is suppressed. Mirrors the prior supervised paper's metric.
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
├── eval/       probes.py (gap) · cluster.py · baselines.py · visualize.py · embed.py · labels.py
├── config.py   dataclass configs (+ YAML)   utils.py  seeding / device / IO
scripts/        generate_data.py · train.py · evaluate.py
configs/        smoke.yaml · default.yaml
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
