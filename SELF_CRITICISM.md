# SELF_CRITICISM.md — A critical reflection, and a design basis for v2

This document is two things at once: an adversarial review of the project as it
stands, and a **forward-looking design brief** for the next iteration. It is
deliberately harsh and specific, but every criticism is paired (where possible)
with a concrete direction so it can seed further development rather than just
discourage it.

**How this was produced.** I applied the rigor of the `requesting-code-review`
superpower skill inline (no git repo to diff; the task was to critique, not to
spawn agents). Severity tags follow that skill's convention — **[Critical]**
(invalidates a result or claim), **[Important]** (materially weakens it; fix
before any real run), **[Minor]** (polish). Mathematical and code claims were
checked against the actual implementation and, where possible, verified
empirically.

**This revision also incorporates the prior supervised-learning paper**
("Convolutional neural networks for automated cellular automaton classification,"
Rollier, Daly, Bruno & Baetens), which the SSL repo is the direct follow-up to —
that paper's Discussion explicitly names self-supervised learning as "the topic
of our forthcoming work." The paper supplies the conceptual frame for the
genotype/phenotype distinction and several **empirically grounded design
principles that this repo does not yet honour.** Per the user's note, the paper
is treated as *framing*, not as ground truth.

> **Empirical update (2026-06-25).** The first full-scale run now exists
> (`runs/default/`). It confirms the predicted failure mode *and* sharpens the
> diagnosis in a way that was not obvious before the run: the model recovers the
> genotype, and the only behaviour it surfaces unsupervised is **homogeneous vs.
> non-homogeneous**. Crucially, the complexity signal is *present but not salient*.
> See **Level 5** for the numbers and a complexity-targeted roadmap — read it
> alongside the conceptual cautions in Levels 1–4, which it makes concrete.

---

## Context inherited from the prior supervised work (read this first)

These facts from the paper reframe everything below; future development should
treat them as the starting premises.

1. **Genotype vs phenotype is a standard CA-classification distinction**, not a
   biological metaphor. Following Vispoel et al., the field separates *properties
   of the local update rule* (genotype) from *properties of the spacetime
   diagram* (phenotype). "Learn phenotype, not genotype" precisely means: classify
   from emergent mesoscopic structure, **not** by reading the rule table off the
   pixels. This is well-posed as a statement about *what information the model is
   allowed to exploit*.

2. **There is a concrete, devastating cheat: rule reconstruction.** A spacetime
   diagram almost always contains every one of the 8 neighbourhood→output
   mappings (the paper calls each a "T-tetromino": 3 input cells + the output cell
   below). The paper shows a plain grid-scan reconstructs the full rule table with
   ~99.9% accuracy, and that a CNN with a 3×2 first-layer kernel can be made to do
   exactly this by hand. **Any high-accuracy ECA classifier is presumed to be a
   rule-reconstructor unless it is specifically prevented from being one.** This is
   the entire reason the genotype-suppression constraint exists.

3. **The supervised success metric is a *gap*, measured with labels.** The paper's
   trimmed CNN + coarse-graining reached **LP-class accuracy ≈98%** while
   **independent-rule accuracy fell to ≈61%** — a deliberate, large gap. Success is
   *not* "class accuracy high" alone (a rule-reader gets that too) and *not* "rule
   accuracy low" alone (a blurrer gets that); it is **both at once**. Keep this
   number as the yardstick: roughly LP≈98% / rule≈61% is the supervised reference
   the SSL pipeline is implicitly trying to reproduce *without labels*.

4. **The augmentation menu was chosen empirically, and the repo's choices match:**
   coarse-graining (2×2 average) was *by far* the strongest rule-suppressor
   (rule acc 71%→16%, LP barely moved); salt-and-pepper noise hurt everything
   without widening the gap (hence rightly excluded); mirror and inversion merely
   remap a rule to its equivalence-class partner (hence treated as
   equivalence-class operations / experimental toggles). The brief's augmentation
   design is therefore **well-grounded in the user's own results** — this is a
   genuine strength, not a guess.

5. **The hard, interesting cases are exactly where the supervised model is
   weakest.** Its confusion matrix shows *locally chaotic* is the least accurate
   class (92.7%) and chaotic↔locally-chaotic is the main confusion; the paper
   itself notes LP "is [not obviously] the most useful... especially when it comes
   to pinpointing Wolfram's class-IV complex behaviour." So the part everyone
   cares about (complexity / class IV) is the part the prior method struggled with.

6. **Why SSL at all:** the paper motivates SSL as a way to avoid "mind-numbing and
   (at least partially) subjective manual labelling" and to let the algorithm
   "decide for itself which phenomenologies are to be grouped together." **The
   point of the SSL project is therefore not to reproduce LP, but to discover
   groupings without committing to LP/Wolfram a priori** — possibly revealing
   structure those schemes miss. This single fact reframes the "validation against
   subjective labels" worry (see Level 1).

---

## Level 0 — The single most important code/design defect

**[Critical] The genotype/phenotype MI diagnostic is mathematically impossible as
stated.** The brief, `CLAUDE.md`, and `eval/cluster.py` say we want
**`MI(cluster; rule)` low** but **`MI(cluster; LP_class)` high**. Because the LP
class is a *deterministic function of the rule* (`LP = f(rule)`), the variables
form a Markov chain `LP – rule – cluster`, and the Data Processing Inequality
forces, for **every** clustering:

```
MI(cluster; rule)  >=  MI(cluster; LP_class)
```

I verified this: a clustering that tracks LP perfectly gives *equal* MIs
(1.609 vs 1.609 nats); any noisier clustering makes `MI(rule)` strictly larger.
The desired inequality (`MI_LP > MI_rule`) is unachievable, so the scalar cannot
distinguish success from failure.

- **Constructive fix, tied to the paper's gap concept.** The supervised paper
  already gives the right instrument: the *gap* between class accuracy and rule
  accuracy. The SSL analogue is **already present** in `eval/probes.py` — compare
  the **rule linear-probe accuracy (want low)** against the **LP linear-probe
  accuracy / LP cluster purity (want high)** on the *same* embeddings. That gap is
  the validated, label-based success signal; lean on it.
- If a single information-theoretic scalar is still wanted, use the **conditional**
  MI `MI(cluster; rule | LP)` (information about the exact rule *beyond* the LP
  class — want ≈ 0), or a normalised measure that accounts for the 88-vs-5
  cardinality mismatch. Delete the "rule low, LP high" framing and the test
  (`test_genotype_phenotype_diagnostic_orders_mi`) that encodes the impossible
  assumption.

---

## Level 1 — The research question

**[Reframed] The genotype/phenotype goal is well-posed — but the language in the
repo overstates it.** Given the paper, this is *not* an ill-posed biological
claim; it is the standard "classify from the diagram's emergent structure, not by
reading the rule table." My earlier objection (the pattern is fully determined by
rule+IC) is real only as a reminder that genotype and phenotype information are
*entangled in the same pixels* — which is precisely why suppression must be
engineered, not assumed. **Action for v2:** state the goal in the field's terms
(suppress rule-table readability while preserving mesoscopic discriminability) and
drop the implication of a causal genotype→phenotype separation.

**[Important] LP/Wolfram as a *yardstick* is fine; LP/Wolfram as a *success
criterion* contradicts the project's own premise.** The paper's whole rationale
for SSL is that hand labels are subjective and possibly wrong, especially for
class IV. So scoring the SSL pipeline by ARI/NMI/purity *against LP* and calling
high agreement "success" quietly re-imposes the prior the project set out to
escape. **The genuinely valuable SSL outcome may be a clustering that *disagrees*
with LP** — e.g. splitting "chaotic" into sub-behaviours, or isolating class-IV
rules that LP lumps elsewhere. **Action for v2:** keep LP/Wolfram as *diagnostic
references* (and as the "good side" of the gap), but define success primarily as
(a) a large rule-vs-class probe gap and (b) *stable, interpretable* structure —
not as maximal LP agreement. Treat LP disagreement as a result to investigate,
not a failure.

**[Important] No hand-crafted-feature baseline — and the paper makes this gap
sharper.** The literature (Langton's λ, input/output entropy, LZ/compression,
mean-field density, texture descriptors — the paper cites several) classifies
ECAs cheaply and well. A probe/clustering on a handful of such scalars is the
baseline the SSL embedding must beat *on the gap and on the hard classes*, or the
deep pipeline is unjustified for an 88-rule problem. **Action for v2:** implement
a `baseline_features.py` (≈5 scalars) and require the learned embedding to
outperform it, reported per behavioural class.

**[Important, corroborated by the paper] Aggregate metrics will hide failure on
the rare, interesting classes.** Among the 88 representatives the LP classes are
severely imbalanced (Null 24, Fixed-point 97, Periodic 89, Locally-chaotic 10,
Chaotic 36 across all 256; the interesting "complex/class-IV" rules are a
handful). ARI/NMI/purity are dominated by the easy bulk, and the paper's own
confusion matrix shows locally-chaotic/chaotic is where even the supervised model
breaks. **Action for v2:** always report **per-class** purity/recall and weight or
stratify the headline metric; treat class-IV/locally-chaotic resolution as the
primary success target, not aggregate ARI.

**[Important] The taxonomy is an artifact of the coarse-graining choice.** 2×2
average-pool is one arbitrary "mesoscopic" lens; a different kernel/operator
yields a different taxonomy. The paper validates 2×2 as *effective for
suppression*, but effectiveness at suppression is not the same as canonicality of
the resulting grouping. **Action for v2:** ablate the coarse-graining
(kernel size, pooling type, multi-scale) and report how stable the discovered
taxonomy is to that choice; present the taxonomy as lens-dependent.

**[Minor] IC-dependence and finite size/time are averaged/clipped away.** One
random density-0.5 IC per diagram, 128×128 periodic, `discard_transient=0`. Some
behaviours are IC- and size-sensitive; the paper deliberately worked at 64×64
(where its "rule is reconstructable from one row" argument is exact). **Action for
v2:** expose and sweep IC density and `discard_transient`; consider multiple ICs
per embedding (e.g. average embeddings over ICs to represent "rule behaviour").

---

## Level 2 — The approach / methodology

**[Critical] The "loss decreases" gate cannot distinguish learning from
collapse.** Negative cosine similarity is minimised (→ −1) by a *constant*
encoder. So the §5 acceptance gate, the smoke run's −0.107→−0.850, and
`test_training_reduces_loss_on_tiny_subset` are all equally consistent with
collapse. **Action for v2:** log a collapse signal every epoch (per-dimension std
of L2-normalised embeddings → 0 on collapse; or effective rank) and make the
smoke gate assert *non-collapse*, not merely decreasing loss. This is independent
of the supervised paper but essential before any SSL claim.

**[Critical, newly concrete] The encoder violates the paper's two anti-cheating
architecture principles, so it is *built to be able to* read the rule.** The paper
identifies two design rules that make rule-reconstruction hard:
  1. *The first-layer kernel must not span a full neighbourhood-and-its-output (a
     T-tetromino).* They used **2×2** (cannot fit the 3-wide neighbourhood + the
     output below). **`ResNet18Encoder` uses a 7×7 stem (or 3×3 in `small_input`),
     both of which comfortably envelope a T-tetromino** → the first layer can learn
     rule-table detectors directly.
  2. *The layer before the head must be too small to encode the rule.* They used a
     **16-node** dense layer. **My encoders emit 256–512-d embeddings** — vastly
     more than enough to linearly encode an 8-bit rule. The smoke run's **rule
     probe = 1.000** is the predicted symptom.

  The SSL design imported the *augmentations* from the supervised work but not the
  *architecture constraints*, and the augmentations alone may not compensate for an
  encoder that is structurally a rule-reader. **Action for v2:** prefer the
  `SmallCNNEncoder` path and redesign it around these principles — 2×2 first-layer
  kernels (no T-tetromino), an explicit small bottleneck before the projector, and
  a documented receptive-field argument. Make "rule probe well below 100%" an
  architectural guarantee, not a hoped-for training outcome.

**[Important] Genotype suppression rests entirely on coarse-graining — and it is
applied to *every* view.** In the default stack, cyclic-shift preserves the whole
rule table (all T-tetrominoes remain), so **only coarse-grain suppresses
genotype**; the scientific load sits on one augmentation (consistent with the
paper, where coarse-grain was the only strong suppressor). Worse, my `CoarseGrain`
is deterministic (p=1), so the encoder is trained *exclusively* on blurred inputs,
while `evaluate.py` extracts embeddings from **raw** diagrams — a train/eval
distribution shift. The paper instead augments *stochastically* (each diagram has
probability 1/(N+1) of being left untouched). **Action for v2:** apply
coarse-graining stochastically (sometimes identity) so the encoder also sees fine
detail, and/or evaluate on coarse-grained inputs; explicitly test sensitivity to
this.

**[Important] A trivial density shortcut survives both default augmentations.**
Global live-cell fraction is invariant to cyclic shift and ≈preserved by
average-pool. The encoder can score respectably by learning "density + a few
low-frequency stats," which correlates with LP class (null/sparse vs chaotic/dense)
without learning anything deep. **Action for v2:** add a density-only baseline and
check whether the embedding beats it; consider density-matched negatives or
density normalisation to force the model past it.

**[Important] BYOL/SimSiam on ~22k low-diversity images is collapse-prone and
small.** Only 88 distinct dynamics, heavy redundancy, no negatives. Combined with
the collapse-blind trainer (above), this is the highest-risk part of the pipeline.
**Action for v2:** monitor collapse, consider a method with an explicit
anti-collapse term (e.g. VICReg/Barlow Twins) as a comparison, and scale ICs for
diversity.

**[Important] "Cluster count emerges" is overstated — it is a hyperparameter.**
HDBSCAN `min_cluster_size`/`min_samples` and UMAP `n_components`/`n_neighbors`/seed
strongly determine the count, and UMAP is stochastic. **Action for v2:** report
cluster-count stability across these knobs and across the UMAP-vs-direct
cross-check; do not headline a single number.

**[Minor] Probes hold out ICs, not rules.** For the LP/Wolfram probes a
**leave-rules-out** split is a far stronger test of transferable behaviour (does
the embedding generalise to *unseen rules* of a known class) and mirrors the real
nuCA goal. **Action for v2:** add a leave-rules-out evaluation mode.

---

## Level 3 — The code (specific defects)

- **[Critical]** `train/trainer.py` logs no collapse diagnostic (see Level 2).
- **[Critical]** `eval/cluster.py::genotype_phenotype_diagnostic` + `ClusterReport.summary()`
  implement and print the impossible "rule low / LP high" comparison (see Level 0).
- **[Important]** **Encoder kernels/embedding-dim ignore the paper's anti-cheating
  principles** (`models/encoder.py`): 7×7/3×3 first-layer kernel envelopes a
  T-tetromino; 256–512-d embedding can encode the rule (see Level 2).
- **[Important]** **Always-on coarse-graining** (`data/augmentations.py::CoarseGrain`,
  p=1) creates a train/eval mismatch with raw-image extraction in
  `factory.build_dataset(..., training=False)` (see Level 2).
- **[Important]** **Post-ReLU non-negative embeddings.** Both encoders end on ReLU
  before global-average-pooling, so embeddings sit in the non-negative orthant;
  after L2-normalisation all pairwise cosines are ≥0 and angular spread ≤90°,
  compressing exactly the geometry cosine-UMAP/HDBSCAN rely on. Consider returning
  the pre-final-ReLU feature from `extract_embedding`.
- **[Important]** **BatchNorm hides in the lightly projection/prediction heads**,
  so the small-batch-BN instability the GroupNorm encoder choice was meant to avoid
  is still present at batch 128 (< 256). Document or replace.
- **[Important]** **Partial seeding / repro caveats.** `set_seed` omits
  `PYTHONHASHSEED` and `torch.use_deterministic_algorithms`; there is no DataLoader
  `worker_init_fn`. The per-item augmentation path uses the *torch* RNG (which
  DataLoader reseeds per worker) and generation uses an explicit NumPy `Generator`,
  so the classic NumPy-in-workers duplication bug does **not** bite — but MPS
  kernels, UMAP/numba and HDBSCAN are not bit-reproducible across machines. Qualify
  the README's "reproducible" claim.
- **[Important]** **Dataset memory.** `_generate` builds a Python list then
  `np.stack`s (≈2× peak); the full array is ~370 MB uint8 at defaults (~1.5 GB at
  1024 ICs), loaded whole from `.npz`. On unified memory this competes with the
  model. Consider memmap / chunked generation.
- **[Minor]** Raw `mutual_info_score` (nats) is unnormalised → incomparable across
  cardinalities even ignoring the DPI issue; prefer AMI/NMI or normalise.
- **[Minor]** Probes report plain accuracy + majority baseline; with the severe
  imbalance, **balanced accuracy / macro-F1 + per-class numbers** are the honest
  headline.
- **[Minor]** `visualize.py` uses `tab20` (20 colours) for up to 88 rules → colour
  aliasing makes the "by rule" panel unreadable at full scale.
- **[Minor]** Per-cluster "densest core" uses Euclidean distance on un-normalised
  embeddings while clusters formed under cosine/L2 geometry — inconsistent metric.
- **[Minor]** `evolve` counts the IC inside `n_steps` (off-by-one vs "N evolved
  rows"); internally consistent but worth documenting.
- **[Minor]** Redundant import paths (`conftest.py` shim *and* editable install);
  over-pinned exact dependency versions may hinder installs on some arm64 setups.

---

## Level 4 — Likely outcomes, against the supervised yardstick

**The yardstick.** Supervised, with labels and an anti-cheating architecture, the
prior work reached **LP≈98% / independent-rule≈61%**. The SSL pipeline should be
judged on whether, *without labels*, it produces embeddings whose **LP-probe/cluster
purity approaches that high side while the rule-probe stays low** — i.e. whether it
reproduces a comparable *gap*.

**Most probable result as currently built.** Because the encoder is structurally a
rule-reader (Level 2/3) and the only suppressor (coarse-grain) is also applied at
train-but-not-eval, the likely outcomes are one of:
  - the **rule probe stays high** (genotype leakage; the failure mode), the
    clusters track rule/density, and LP agreement looks "fine" for the wrong
    reason; or
  - over-aggressive suppression **destroys discriminability**, the rule probe
    drops *and* LP purity drops, and HDBSCAN shatters into noise — i.e. a small or
    negative gap.
  Either way, the **interesting class-IV/locally-chaotic distinction is the first
  thing to fail**, exactly as in the supervised confusion matrix.

**Collapse can masquerade as success** until a collapse metric exists: it yields
the best loss curve and then a degenerate embedding.

**The most valuable *positive* outcome** would be SSL structure that is stable,
beats the hand-crafted baseline on the gap, and **reveals groupings LP does not
have** (sub-types of chaos, an isolated complexity cluster). That is the
project's real upside and is currently neither targeted nor measured.

**Transfer to nuCAs** (the eventual goal, and the reason SSL is preferred over
supervised labelling) is unsupported by anything in the ECA validation; `nuca.py`
buys structural extensibility only.

---

## Level 5 — Empirical update: what the first full run actually showed (2026-06-25)

The full `default.yaml` run (88 reps × 256 ICs, 127px, 100 epochs, BYOL +
`AntiCheatCNN`, symmetry augmentations ON) was executed and evaluated. The results
move several Level 1–4 *predictions* into the column of *measured facts*, and add one
diagnosis that changes the v2 direction.

### 5.1 The measured facts

- **The genotype cheat survived the anti-cheat architecture.** Rule-identity probe
  (88 orbits) **acc = 0.967** (baseline 0.011). The 2×2 kernels + 64-d signed
  bottleneck dropped the *smoke* probe from 1.000 → ~0.97 but did **not** suppress
  rule-readability at full scale. The encoder is still essentially a rule lookup.
- **The deep embedding is a *better* rule-reader than cheap texture stats.** The
  4-scalar hand-crafted baseline scores 0.721 on the same rule probe; the encoder
  scores 0.967. On the dimension we wanted suppressed, the deep model is worse than
  the baseline — the opposite of "earning its keep."
- **Clusters ≈ rules.** HDBSCAN finds ~95 clusters for 88 rules (sweep 66–131);
  cluster→rule purity median ≈ 1.0; ~half the clusters are a single rule. The
  unsupervised taxonomy is the rule table at fine scale.
- **The only emergent *behavioural* axis is trivial.** Coarsening the 95 clusters
  into super-groups cleanly isolates the **class-1 "dies to uniform"** rules
  (0,8,32,40,128,136,160,168) into their own region, but collapses **all** of
  periodic + chaotic + complex into one ~89% blob. The macro-structure is
  *homogeneous vs. non-homogeneous* — not order vs. chaos, and certainly not an
  isolated class-IV cluster.

### 5.2 The diagnosis that matters: the signal is present, just not salient

This is the non-obvious part. The complexity information **is in the embedding** —
it is simply not the axis the unsupervised geometry is built on:

- **complex-vs-chaotic linear probe** (rules {54,110} vs the 12 chaotic reps):
  **balanced acc 0.968.** A linear readout separates class-IV from class-III almost
  perfectly. (This is unsurprising given rule acc 0.967 — if you can name the rule
  you can name its class — but it is the decisive point: *detectability is not the
  bottleneck.*)
- **embedding → density R² = 0.947; embedding → temporal-activity R² = 0.955.** The
  embedding encodes the global density/activity nuisance almost perfectly.
- **The geometry is density-dominated.** The top principal component is 24% of the
  embedding variance and correlates **0.61** with mean density (top-10 PCs = 85%).
  So the largest direction the clustering "sees" is essentially *how much stuff is on
  the diagram*. UMAP+HDBSCAN coarsen along that axis; the low-variance,
  behaviourally-meaningful complexity coordinate is swamped.

**Conclusion:** "filter out complex behaviour with SSL" is currently failing not
because the model *can't tell* complex from chaotic, but because nothing in the
pipeline makes complexity a **high-variance, metric-aligned** direction. Removing the
genotype cheat (Levels 2–3) is necessary but **not sufficient** — even a perfectly
genotype-blind encoder would still cluster by density unless complexity is made
salient.

### 5.3 Weaknesses in the theoretical assumptions (made concrete by the run)

- **[Critical] "Suppress the genotype → behaviour emerges" is a non-sequitur.** The
  project's load-bearing assumption is that the interesting taxonomy is what remains
  after the rule cheat is removed. The run shows the residual structure is dominated
  by a *different* trivial shortcut (density/activity), which Level 2 already flagged
  as surviving the augmentations. Suppression creates room for behaviour; it does not
  *point at* complexity. A salience/aligning mechanism is missing from the theory.
- **[Critical] "Complexity" is not expressible as invariance to any augmentation.**
  SSL learns to be invariant to its augmentations and to discriminate on everything
  else. Shift/coarse-grain/flip/invert define the *equivalence* we impose; none of
  them has "all edge-of-chaos diagrams" as an orbit. There is therefore **no
  inductive bias toward the order/chaos axis** anywhere in the objective. The hope
  that the algorithm will "decide which phenomenologies group together" is
  under-determined: it groups by whatever maximises view-agreement-minus-collapse,
  which here is rule-texture + density.
- **[Important] A static 2-D image model has no notion of *computation*.** Class-IV
  behaviour is *dynamical* — long transients, propagating localized structures,
  particle collisions, long-range space-time correlation. A 2-D CNN reads the
  spacetime diagram as a **texture**; the time axis carries no special causal status.
  We encode a dynamical process as a still image and hope a texture model recovers
  "computation." This is a representational mismatch, not a tuning problem.
- **[Important] The measurement under-expresses complexity.** One random density-0.5
  IC, `discard_transient=0`, fixed 127×127. From a random IC, rule 110 looks like a
  busy soup, not clean gliders; class-IV structure is often clearest from *structured*
  ICs and *longer* evolution. The early rows are dominated by IC noise we never
  discard. So even the data may not show the model what we want it to find.
- **[Important] The target class is rare and ill-defined.** Class IV is ~2 of 88
  reps; HDBSCAN (density-based) structurally cannot carve a rare, subtle class out of
  a dominant texture axis (Level 1 rare-class point, now realized). And "edge of
  chaos" has no crisp per-diagram definition or ground truth — we are asking an
  unsupervised method to find a category we cannot ourselves label per-instance.
- **[Minor] Evaluation circularity.** Every behaviour reference (LP/Wolfram) is
  constant within a rule, so "behaviour clustering" is still graded against a
  rule-derived target. We have no per-diagram complexity label to validate against.

### 5.4 How to proceed — making complexity *salient* (prioritised)

Ordered by leverage-per-effort. Tiers 1–2 are the realistic near-term path.

1. **[Cheap, do first] Project out the density/activity axis, then re-cluster.**
   Since density is ~95% linearly recoverable and PC1 is density-aligned, regress
   density+activity out of the embedding (or whiten and drop the density-correlated
   components) and re-run UMAP/HDBSCAN. This *directly tests* the salience diagnosis:
   if behavioural sub-structure (incl. a class-IV island) appears once density is
   removed, the problem was geometry, not content. *Honest caveat:* complexity is one
   of many residual axes — it may sharpen without fully separating.

2. **[The main lever] Inject a physics-based complexity prior (no human labels
   needed).** The order/chaos axis has well-studied, *label-free* estimators; use one
   to shape the representation rather than hoping it emerges:
   - **Damage / difference-pattern spreading** — the canonical edge-of-chaos probe:
     flip one IC cell, evolve both copies, measure how the damage cone grows. Dies
     (class 1/2), space-fills ballistically (class 3), propagates along localized
     structures sub-ballistically (class 4). This is the single most discriminating
     signal for class IV and is purely dynamical.
   - Also: input-entropy / Langton's λ trajectory, spatial mutual-information decay,
     multi-scale block entropy, compressibility across coarse-grainings.
   Use it two ways: (a) **directly** — cluster on a handful of these scalars and check
   whether they already separate class IV *better than the SSL embedding does* (if so,
   the deep pipeline is not justified for this task — an honest possible outcome); or
   (b) as an **auxiliary self-supervised target / metric** — add a head that regresses
   the proxy, or do metric learning so "similar" means "similar complexity," shaping
   the embedding toward the axis we care about.

3. **[Principled redesign] Predictive / world-model SSL along the time axis.** Replace
   instance discrimination with *forecasting*: predict future rows from past rows
   (masked space-time / next-block prediction). The **predictability profile** — how
   residual error or residual entropy scales with horizon — is itself an order/chaos
   coordinate (trivially predictable → periodic → irreducibly unpredictable, with
   class IV intermediate / long-memory). This makes the encoder dynamics-aware and
   aligns the learned axis with computation instead of texture.

4. **[Supporting] Fix the measurement.** `discard_transient` > 0; evolve longer; add
   structured/single-seed ICs alongside random ones; represent a *rule* by the
   distribution/average of its per-IC embeddings (denoises IC nuisance); oversample
   the class-IV neighbourhood of rule space (and consider sampling beyond the 88 reps
   there). These help any of 1–3.

5. **[Honesty / scope] Re-state the deliverable.** A *fully* unsupervised "complexity
   detector" may be ill-posed without injecting any complexity signal; the realistic
   product is **SSL + a physics-grounded complexity prior**, scored by **per-class
   recall of class IV against the damage-spreading baseline**, not aggregate ARI. If
   the baseline wins, that is a publishable, honest result about the limits of texture
   SSL for computation-detection.



- **No pre-registered success criterion.** Define, in advance and per behavioural
  class: what rule-vs-LP probe gap, what stability, and what baseline margin count
  as success *and* as failure. Otherwise the many researcher degrees of freedom
  (augmentations, UMAP/HDBSCAN, encoder, seed) invite garden-of-forking-paths
  tuning toward LP.
- **The smoke run can launder false confidence:** its "successes" (loss down, 5
  clusters, rule probe 1.0) are precisely the uninformative-or-failure-coloured
  signals at full scale.

---

## What is genuinely sound (calibration)

The *engineering* is solid: the ECA simulator and 88-class symmetry are correct
and tested; the layers are cleanly separated, typed, documented, and covered by 79
passing tests; device handling, caching, config/YAML and the CLIs run end-to-end
on MPS. And — newly reinforced by the paper — the **augmentation design is
empirically justified by the user's own prior results** (coarse-grain as the
strong suppressor, salt-and-pepper rightly excluded, mirror/invert understood as
equivalence-class maps). The problems are about **measurement validity and
encoder design**, not about whether the code runs or whether the augmentation
hypothesis is reasonable.

---

## Roadmap for v2 (prioritised, development-ready)

> **Status update:** items 1–6 below have been **implemented** (see the
> "Implemented" notes). The conceptual cautions (Levels 1–4: subjective labels,
> rare-class dominance, taxonomy-as-artifact, pre-registration) remain open and
> are matters of *interpretation and experimental design*, not code.

1. **Make rule-suppression architectural, not hopeful.** Redesign `SmallCNNEncoder`
   around the paper's principles: 2×2 first-layer kernels (no T-tetromino), an
   explicit small bottleneck before the projector, documented receptive field.
   *(Critical; Levels 2–3.)* — **Implemented:** `AntiCheatCNN` (2×2 kernels, signed
   64-d bottleneck, no final ReLU); now the default `encoder` in `configs/`. Smoke
   rule-probe fell from 1.000 → ~0.97.
2. **Replace the broken MI diagnostic with the gap.** Headline = rule-probe vs
   LP-probe accuracy gap on the same embeddings (the paper's validated metric);
   optionally add `MI(cluster; rule | LP)`. Delete the impossible scalar and its
   test. *(Critical; Level 0.)* — **Implemented:** `ProbeReport.gap`;
   `genotype_phenotype_diagnostic` now returns the conditional MI
   `mi_rule_given_lp` (≥ 0, want ≈ 0); the impossible test was replaced.
3. **Add a collapse detector** (embedding std / effective rank) to the trainer and
   to the smoke gate. *(Critical; Level 2.)* — **Implemented:** `collapse_std`,
   logged to `loss_log.csv` + the loss PNG; the smoke gate asserts it stays > 0.
4. **Add hand-crafted baselines** (λ, input entropy, LZ, mean density) and require
   the embedding to beat them, **reported per class**. *(Important; Level 1.)* —
   **Implemented:** `eval/baselines.py` (density, temporal activity, compression
   ratio, block entropy); `evaluate.py` compares the embedding's gap to the
   baseline's.
5. **Fix the train/eval coarse-grain mismatch** (stochastic augmentation, as in the
   paper) and **test the density shortcut** explicitly. *(Important; Level 2.)* —
   **Implemented (partial):** `CoarseGrain(p=…)` + `coarse_grain_prob=0.5` default;
   the density-only baseline now exists for the shortcut check (a dedicated
   density-controlled ablation is still worthwhile).
6. **Re-aim evaluation:** per-class metrics, leave-rules-out splits, cluster-count
   stability, and treat LP/Wolfram as references — reward, don't penalise,
   interpretable disagreement (esp. around class IV). *(Important; Levels 1–2.)* —
   **Implemented (mechanics):** balanced accuracy + macro-F1 in probes,
   `lp_split="rules"` leave-rules-out, `cluster_count_stability`. The
   *interpretive* stance (treat LP as a reference, investigate disagreement) is a
   research-conduct choice that remains with the experimenter.

7. **Make complexity *salient*, not just present (NEW — Level 5).** The first full
   run shows class-IV is linearly decodable (0.968) but density-dominated geometry
   hides it. First experiment: **project out density/activity and re-cluster**
   (cheap). Then **inject a label-free complexity prior** — damage/difference-pattern
   spreading is the canonical edge-of-chaos estimator — either as a direct clustering
   feature or as an auxiliary SSL target/metric. *(Critical; Level 5.)*
8. **Add a dynamics-aware objective (NEW — Level 5).** Trial a predictive/world-model
   SSL head (forecast future rows from past) so the learned axis tracks
   *predictability/computation* rather than static texture. *(Important; Level 5.)*
9. **Score class IV explicitly against a physics baseline (NEW — Level 5).** Headline
   metric = per-class recall of class IV vs. a damage-spreading/entropy baseline; if
   the baseline wins, report that honestly as a limit of texture SSL. *(Important;
   Levels 1, 5.)*

**Bottom line.** With the prior paper in view, the augmentation strategy is the
project's strongest, best-justified component — but the repo imported the paper's
*augmentations* without its *anti-cheating architecture* and without a valid
analogue of its *gap* metric. As built, the pipeline can produce confident-looking
numbers that do not establish "behaviour, not rule." Honour the paper's two
encoder principles, replace the MI scalar with the rule-vs-class gap, instrument
for collapse, and define success per behavioural class — then a real run can be
trusted, and the genuinely novel SSL upside (structure beyond LP) becomes
measurable.

---

## Level 6 — Foundations verdict (2026-07-02)

A commissioned literature review
(`docs/literature/2026-07-02_deep_research_report.md`, distilled in
`FOUNDATIONS.md`) settled the question Levels 1–5 kept circling: **the original
goal was ill-posed as stated.** "The behaviour class of a rule" is not a single
well-defined object (Wolfram-style membership is undecidable — Culik & Yu; the
observed class depends on the IC measure and protocol — Gilman; rigorous schemes
classify different objects and disagree on borderline rules), and no bias-free
clustering exists (Kleinberg), so "let SSL discover the taxonomy" was never
available. This *validates* Level 1's "taxonomy is an artifact of the lens" and
Level 5's diagnosis, and it reframes the v1 failure and the M2 physics-baseline
win (`RESULTS.md`) as the literature-predicted outcome rather than engineering
accidents. Consequences (decision records in FOUNDATIONS.md §3–4 and
EVALUATION_CRITERIA.md rev 2): the classified object is now an explicit protocol
tuple; Wolfram/LP are touchstones with borderline flags, not ground truth; the
mission is invariant-based taxonomy + amortized, spatially-resolved invariant
estimation; texture-SSL is the frozen negative baseline; temporal-window
positives are dropped; and the remaining learning levers (invariant-regression
amortizer, predictive SSL) carry pre-registered kill criteria.
