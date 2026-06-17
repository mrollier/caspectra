# Claude Code Brief — Self-Supervised Behavioural Taxonomy of Cellular Automata

Use this as the build spec for a **fresh repository**. It is self-contained: it encodes every design decision, because you (Claude Code) do not have access to the planning conversations.

---

## 0. What you are building

A clean, object-oriented Python project that discovers an **open-ended, label-free behavioural taxonomy** of cellular automaton (CA) spacetime diagrams via self-supervised learning (SSL) + density-based clustering.

**Validation stage (build for this first):** elementary CAs (ECAs) — the 256 rules, reducible to **88 equivalence classes**. ECAs have known reference classifications (Li-Packard, Wolfram), so they let us *check* that the unsupervised pipeline recovers behaviour rather than memorising the update rule.

**Eventual target (design for extensibility, do not implement yet):** non-uniform CAs (nuCAs) — two ECA rules mixed per cell (e.g. 50% rule 110 / 50% rule 54).

**The central scientific constraint (do not violate):** the encoder must learn *mesoscopic behaviour* (the phenotype), **not** the local update rule (the genotype). A model that secretly classifies by reconstructing the rule table is the known failure mode for this problem and is considered a *failed* run even at high clustering accuracy. The evaluation module exists primarily to detect this.

---

## 1. Tech stack and environment

- **Python 3.11+ (arm64)**, **PyTorch**.
- **Target hardware: Apple Silicon (MacBook Pro M4) only, for now.** Device selection: prefer **MPS**, fall back to **CPU**. Put device selection behind a single `select_device()` util so other backends (CUDA) can be added later without touching model/training code.
  - **AMP/autocast OFF by default** (MPS autocast is unreliable) — run fp32.
  - Set `PYTORCH_ENABLE_MPS_FALLBACK=1` in the scripts and document it in the README, so any op MPS lacks falls back to CPU instead of crashing.
  - DataLoader: modest `num_workers` (2-4) with `persistent_workers=True`; high worker counts can be flaky on macOS.
- **SSL building blocks:** use the `lightly` library for the BYOL/SimSiam loss, projection/prediction heads, and momentum-update helper (well-tested, portable, pure-PyTorch). Keep the encoder, data, training loop, and all evaluation as **first-party OOP code** so the project is inspectable and not framework-locked. Do **not** use solo-learn (Lightning/DALI, CUDA-oriented, poor MPS support).
- Other deps: `numpy`, `scikit-learn`, `umap-learn`, `hdbscan`, `matplotlib`. Pin versions in `pyproject.toml`. **Install note:** if `hdbscan`/`umap-learn` fail to build via pip on arm64, install them from conda-forge.
- **Logging:** minimal — CSV files + matplotlib PNGs. No Weights & Biases, no TensorBoard, no MLflow.
- **Style:** type hints throughout, docstrings on every public class/method (this project is read by domain scientists, not just ML engineers — explain *why*, not just *what*). Black + Ruff. Small, single-responsibility classes.
- **Reproducibility:** a single `set_seed(seed)` utility seeding Python/NumPy/Torch; record the seed and full config in every run's output directory.

---

## 2. Repository layout

```
caspectra/                     # package (rename if you prefer)
├── ca/
│   ├── eca.py                 # ECASimulator, equivalence-class logic
│   └── nuca.py                # STUB for non-uniform CAs (interface only, NotImplemented)
├── data/
│   ├── dataset.py            # SpacetimeDataset, generation + caching
│   └── augmentations.py      # augmentation transforms + TwoViewTransform
├── models/
│   ├── encoder.py            # ResNet18-1ch and a small custom-CNN alternative
│   └── byol.py               # BYOL + SimSiam wrappers
├── train/
│   └── trainer.py            # Trainer: loop, checkpoint, CSV log, loss plot
├── eval/
│   ├── probes.py            # linear probes (rule / LP / Wolfram)
│   ├── cluster.py          # UMAP + HDBSCAN + cluster metrics + MI diagnostic
│   └── visualize.py        # UMAP scatter (3 colourings) + per-cluster samples
├── config.py                 # dataclass configs (+ optional YAML load/save)
├── utils.py                  # seeding, device selection, IO
scripts/
├── generate_data.py
├── train.py
└── evaluate.py
tests/
└── test_eca.py, test_augment.py, ...
README.md
pyproject.toml
```

---

## 3. Module specifications

### 3.1 `ca/eca.py` — ECA simulation and symmetry

- `class ECASimulator`:
  - Constructor takes a Wolfram rule number (0-255). Build the 8-entry rule table from its binary expansion.
  - `evolve(initial_row: np.ndarray, n_steps: int) -> np.ndarray` returns a `(n_steps, width)` binary array. **Periodic boundary conditions** (use `np.roll` for neighbours). Vectorise across the row (no per-cell Python loop).
  - `random_diagram(width, n_steps, rng) -> np.ndarray` with a random binary initial row.
  - Convention: row 0 = initial condition at top; time increases downward. Output dtype `uint8` in {0,1}.
- Equivalence classes (compute programmatically — fully defined, no external data):
  - `reflect(rule) -> int` (left-right mirror) and `complement(rule) -> int` (0<->1), and their composition.
  - `equivalence_class(rule) -> frozenset[int]` and `independent_rules() -> list[int]` (one canonical representative per class). **Assert exactly 88 classes** — use this as a unit test.
- Do **not** put Li-Packard / Wolfram class labels here; those are empirical and supplied externally (see §3.6).

### 3.2 `data/dataset.py` — dataset

- `class SpacetimeDataset(torch.utils.data.Dataset)`:
  - Generates diagrams on construction (or loads from a cache dir). Config: list of rules (default = the 88 independent rules), `n_ic_per_rule`, `grid_size` (square; height=width=`grid_size`), `transform` (a `TwoViewTransform` for training, or `None` for embedding extraction).
  - Each item returns `(view1, view2, metadata)` when a two-view transform is set, else `(image, metadata)`. `metadata` is a dict: `rule`, `equiv_class_rep`. (LP/Wolfram labels are attached later at eval time from the external table, keyed by `rule`.)
  - Images returned as float tensors shape `(1, grid_size, grid_size)`, values in [0,1].
  - Cache generated tensors to disk (`.npz` or `.pt`) keyed by a hash of the generation config, so regeneration is skipped.
- **Defaults:** `grid_size = 128` (chosen so the full complex behaviour is visible; 64 is available only for fast smoke tests). `n_ic_per_rule = 256` for development (scalable to 1024). `discard_transient` config (default 0; expose it).

### 3.3 `data/augmentations.py` — augmentations (the scientifically load-bearing part)

Implement each as a small callable class operating on a `(1,H,W)` float tensor:

- `CyclicShift` — roll along the **horizontal (space) axis** by a random offset. Exact symmetry under periodic BC; preserves all information. **Default-on, primary augmentation.**
- `CoarseGrain` — 2x2 average-pool then nearest-neighbour upsample back to original size (shape preserved; values become multi-level). Destroys microscopic/rule detail while keeping mesoscopic structure. **Default-on, primary augmentation — this is the key invariance for genotype-suppression.**
- `HorizontalFlip` — left-right mirror. **Toggleable, OFF by default** (experimental condition: maps a rule to its equivalence-class partner).
- `Invert` — `x -> 1 - x`. **Toggleable, OFF by default** (experimental condition; also an equivalence map).
- `RandomResizedCropConservative` — optional, scale range default `(0.6, 1.0)`. **OFF by default.** Docstring note: unlike natural images, a crop here still contains the full rule table, so it does *not* suppress genotype; conservative scale only.
- **Do not implement** vertical/time flips, 90-degree rotations/transposes, or salt-and-pepper noise as positive-pair augmentations (time is not reversible; rotation mixes the space/time axes; noise was found to hurt without helping). Leave clearly-commented stubs marked `# intentionally excluded — see brief §3.3`.

- `class TwoViewTransform`: applies the configured augmentation stack twice (independently) to produce a positive pair. Two modes via config:
  - `symmetric` (default): both views drawn from the same stochastic stack (shift + coarse-grain by default). Standard, well-established BYOL setup.
  - `asymmetric_coarse` (experimental toggle, OFF): view A lightly augmented (shift only), view B always coarse-grained. Explicitly trains invariance to microscopic detail. A hypothesis to ablate, not the default.

### 3.4 `models/encoder.py` — encoders

- `class ResNet18Encoder(nn.Module)`: a torchvision ResNet-18 adapted to **1 input channel** (replace `conv1`), output = the 512-d global-average-pooled feature (drop the classification head). Config:
  - `width_multiplier` (default 1.0; allow 0.5 for a lighter, less rule-memorising variant).
  - `small_input` flag (default False): when grid_size <= 64 (smoke tests only) replace the 7x7/stride-2 stem with a 3x3/stride-1 conv and drop the initial max-pool. **At the default 128, keep the standard ImageNet-style stem.**
  - `norm_layer`: default **GroupNorm** (see below); BatchNorm selectable.
- `class SmallCNNEncoder(nn.Module)`: a 5-6 layer custom CNN (~0.5-2M params) as a lighter ablation alternative. Both encoders expose `.embedding_dim` and `forward(x) -> (B, embedding_dim)`.
- **Normalisation guidance (M4-specific):** at 128x128 on unified memory you may not fit batch >= 256. BatchNorm degrades and can destabilise BYOL at small batch, so **default to GroupNorm when batch < 256**; expose both and record the choice in the config.

### 3.5 `models/byol.py` — BYOL (default) and SimSiam (M4 fallback)

- `class BYOL(nn.Module)` using `lightly` components:
  - Online branch: `encoder -> BYOLProjectionHead -> BYOLPredictionHead`.
  - Target branch: momentum copy of `encoder -> BYOLProjectionHead` (no predictor), updated by EMA via lightly's `update_momentum`. Stop-gradient on the target.
  - Projection head `512 -> 4096 -> 256` (expose dims; allow `512 -> 2048 -> 128`). Predictor `256 -> 4096 -> 256`.
  - Loss: lightly's negative-cosine-similarity, symmetrised over the two views.
  - EMA momentum `tau`: config, default 0.996, cosine-annealed toward 1.0.
  - `extract_embedding(x)` returns the **encoder output (512-d, pre-projector)**, used for all evaluation.
- `class SimSiam(nn.Module)`: drop-in alternative (no momentum/target network; predictor + stop-grad). Lower memory, designed for batch-256 + SGD.
- **Method choice on M4:** default is **BYOL**, but BYOL accuracy degrades when batch drops below ~256. **If M4 memory forces batch < ~256, switch to SimSiam** — it needs no target network (less memory) and is small-batch-native. Both are config-swappable; pick whichever fits the batch size you can run. (Watch SimSiam for collapse: confirm the loss does not crater to a trivial constant.)

### 3.6 `eval/probes.py` — linear probes (lead evaluation)

- Load an external `rule_labels.csv` (columns: `rule, lp_class, wolfram_class`), supplied by the user (taken from the Li-Packard publication). If absent, skip LP/Wolfram probes with a clear warning but still run the rule-identity probe (rule is always known).
- Freeze the encoder, extract embeddings for a held-out set, fit `sklearn` logistic-regression probes:
  - **embedding -> rule identity** (256-way or 88-way): **want clearly below 100%.** Near-perfect => the encoder learned the update rule (the failure mode). Report prominently.
  - **embedding -> Li-Packard class** and **embedding -> Wolfram class**: **want well above chance** (compute and report the majority-class baseline).
- Output a small CSV + console summary.

### 3.7 `eval/cluster.py` — clustering + the genotype/phenotype diagnostic

- Pipeline: extract embeddings -> L2-normalise -> **UMAP** (cosine metric, `n_components` ~10-50) -> **HDBSCAN** (`min_cluster_size`, `min_samples` configurable; cluster count **emerges**, outliers labelled noise). Also run HDBSCAN directly on the L2-normalised embeddings as a cross-check (UMAP can distort densities).
- Metrics vs supplied labels (when available): Adjusted Rand Index, Normalised Mutual Information, cluster **purity** against LP and Wolfram classes.
- **Genotype/phenotype scalar diagnostic:** `MI(cluster; exact_rule)` vs `MI(cluster; LP_class)`. Desired: low former, high latter. Report both; complements the rule-identity probe.
- Report discovered cluster count vs known class counts (5 LP, 4 Wolfram); contingency tables.

### 3.8 `eval/visualize.py`

- A 2-D UMAP scatter rendered three times side-by-side, coloured by (a) rule identity, (b) LP class, (c) discovered HDBSCAN cluster. Save as one PNG.
- For each discovered cluster, save a grid of representative diagrams (nearest the cluster's densest core) for manual inspection.

### 3.9 `config.py`, `scripts/`, `ca/nuca.py`

- `config.py`: `@dataclass` configs (`DataConfig`, `ModelConfig`, `TrainConfig`, `EvalConfig`, `ExperimentConfig`) with optional YAML load/save. Every script takes `--config path.yaml` and writes the resolved config into its output dir.
- `scripts/generate_data.py`, `scripts/train.py`, `scripts/evaluate.py`: thin CLIs over the classes above. `train.py` checkpoints periodically and on completion; `evaluate.py` loads a checkpoint and runs §3.6-3.8.
- `ca/nuca.py`: **interface stub only** — a `NonUniformCA` class mirroring `ECASimulator`'s `evolve`/`random_diagram` surface, taking a rule-assignment mask (which cell follows which of two rules), raising `NotImplementedError`, with a docstring describing the intended per-cell mixing. Documents the extension point without building it.

---

## 4. Tests (minimal but include these)

- `test_eca.py`: (1) `independent_rules()` returns exactly **88**; (2) reproduce known diagrams — rule 0 -> all zeros after one step, rule 255 -> all ones, rule 204 (identity) -> IC repeated down every row; (3) periodic BC wraps correctly on a tiny width.
- `test_augment.py`: `CyclicShift` preserves the multiset of column sums; `CoarseGrain` preserves tensor shape; excluded augmentations are not registered in the default stack.
- `test_shapes.py`: dataset item and both encoders produce expected shapes for `grid_size in {64, 128}`.

---

## 5. Build order (suggested)

1. `ca/eca.py` + `test_eca.py` (verify the 88 and the sanity diagrams **before** anything else).
2. `data/` (+ caching) and `data/augmentations.py` + `test_augment.py`.
3. `models/encoder.py`, `models/byol.py`.
4. `train/trainer.py` + `scripts/train.py`; confirm loss decreases on a tiny subset before any long run.
5. `eval/` + `scripts/evaluate.py`.
6. `README.md` with quickstart, the MPS notes (incl. `PYTORCH_ENABLE_MPS_FALLBACK=1`), and where to place `rule_labels.csv`.

After each step, run the relevant tests and a **fast smoke run** (a handful of rules, few ICs, `grid_size=64`, 1-2 epochs) to catch integration errors before committing to a full 128x128 run.

---

## 6. Acceptance criteria

- Tests pass; the 88-class assertion holds.
- A smoke run trains end-to-end on MPS (or CPU) without error and produces a decreasing loss curve PNG and a CSV log.
- `evaluate.py` produces: rule-identity probe accuracy, LP/Wolfram probe accuracies (when labels present), HDBSCAN cluster count + ARI/NMI/purity, the MI diagnostic, and the 3-panel UMAP PNG + per-cluster sample grids.
- Code is OOP, typed, documented, runs on Apple Silicon (MPS->CPU).

## 7. Out of scope (do not build now)

nuCA generation/training (stub only); experiment-tracking frameworks; distributed/multi-GPU; CUDA-specific paths (keep the device util extensible but don't implement CUDA yet); hyperparameter-search frameworks; the manuscript.

## 8. Notes to surface back to the user

- `rule_labels.csv` (rule -> LP class, Wolfram class, from Li-Packard) is required for the LP/Wolfram parts of evaluation; the README must say where it goes. Everything else runs without it.
- Defaults: `grid_size=128`, method=BYOL (switch to SimSiam if batch < ~256), augmentations = cyclic-shift + coarse-grain (flip/inversion OFF, experimental).
- If an op fails on MPS even with the fallback flag, print a clear message and continue on CPU where possible.
