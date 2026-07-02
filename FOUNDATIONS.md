# FOUNDATIONS.md — what this project can and cannot claim

Distilled from the commissioned literature review
(`docs/literature/2026-07-02_deep_research_report.md`, 2026-07-02) and this repo's own
measurements (`RESULTS.md`). This file is the reference for every future debate about
goals and criteria; `EVALUATION_CRITERIA.md` operationalizes it.

---

## 1. The object of classification (the central fix)

**"The behaviour class of rule R" is not a well-defined quantity.** The literature contains
several inequivalent rigorous meanings of CA behaviour — Wolfram/Li–Packard empirical
classes, Kůrka's topological classes, Gilman's measure-theoretic classes, Hurley's
attractor types — which classify *different mathematical objects* and disagree on
borderline rules. Membership in formalized Wolfram-style classes is undecidable
(Culik & Yu 1988; Sutner's arithmetical-hierarchy placements), and the class observed in
practice depends explicitly on the initial-condition measure (Gilman 1987), the lattice
size and boundary conditions, and the observation horizon.

**What this repo actually classifies is therefore a protocol tuple:**

> *(rule orbit under reflection/complement, Bernoulli(1/2) IC measure, ring of 127 cells
> with periodic boundaries, horizon of 127 rows observed from t = 0)*

Every metric, label, and claim is indexed by this tuple. Changing any component may change
the answer — that is a property of the problem, not a bug. Our own "power-of-two trap"
(rule 90 collapsing on 2^k rings, README) is a small local instance of exactly this
protocol-dependence. `scripts/protocol_sensitivity.py` measures how sensitive our
dynamical features and taxonomy are to the IC density and lattice width;
`EVALUATION_CRITERIA.md` criterion 5 makes stability a reported gate.

## 2. Established / Contested / Unknown, mapped to this project

**Established (and now binding on us):**
- No bias-free clustering exists (Kleinberg's impossibility theorem; ugly-duckling
  theorem). A taxonomy appears only after a similarity is *chosen*. Our v1 augmentation
  stack was already such a choice — just one misaligned with dynamics.
- Image models prefer shortcut cues (Geirhos et al.), and SSL hard-codes
  augmentation-defined invariances while suppressing features the objective does not need
  (Xiao et al.; Wen & Li). v1's rule probe of 0.967 through an anti-cheat architecture is
  the expected outcome, not an accident.
- The best-surviving operationalizations of "complex/class IV" are dynamical, not visual:
  particle/domain structure (Crutchfield & Hanson, rule 54), damage spreading / Lyapunov
  measures (Shereshevsky; Bagnoli et al.; Vispoel, Daly & Baetens 2024), and Wuensche's
  input-entropy variance (with published finite-size caveats). Our M2 gate — 4 damage
  scalars isolating {54, 106, 110} while the 64-d texture embedding never isolates class
  IV — is these results reproduced in miniature.
- Rule-table vs spacetime-pattern classification is a recognized split (Vispoel, Daly &
  Baetens 2022), and the rule-identifiability cheat has direct prior art (Rollier, Daly,
  Bruno & Baetens).

**Contested (we must not lean on it):**
- λ / edge-of-chaos as a per-rule complexity coordinate (Mitchell–Hraber–Crutchfield
  re-examination stands).
- The exact membership of "class IV": Wolfram class IV in ECAs is essentially {54, 110};
  some schemes elevate 106; published results give rule 40 (class I) chaotic invariant
  subsets and rule 42 (class II) a chaotic global attractor. Hence the `borderline` flags
  in `rule_labels.csv` (40, 41, 42, 106) and the dual reporting in criterion 1.

**Unknown (open ends, not missing citations):**
- No canonical per-diagram definition of class IV exists.
- No theorem forces expressive image models to recover the rule — only strong practical
  expectation.
- No evidence that ECA-derived taxonomies transfer to non-uniform CA; the nuCA literature
  (Dennunzio, Formenti, Provillard) treats heterogeneity as a genuine enlargement in which
  the *rule distribution itself* belongs in the classification target.
- No complete published Kůrka/Gilman class table for all 88 orbits (only prototypes), so
  those columns cannot be added to `rule_labels.csv` yet.

## 3. The mission, reframed (decision record, 2026-07-02)

The original mission — "discover an open-ended, label-free behavioural taxonomy" — is not
defensible as stated (§2, impossibility results). The project's goal is now:

1. **An invariant-based taxonomy of protocol tuples**: cluster/organize rules by label-free
   *dynamical invariants* (damage spreading, input-entropy variance; later Lyapunov
   profiles), with Wolfram/LP agreement reported as a reference touchstone — never as
   ground truth.
2. **Amortized, spatially-resolved invariant estimation** (the learning component's
   defensible job): train an encoder to predict the dynamical invariants *from a single
   spacetime diagram*, validated leave-rules-out. The unique payoff — which the scalar
   flip-and-re-evolve baseline structurally cannot provide — is **per-patch phenotype
   maps** for non-uniform CA, where behaviour varies in space and twin-run global
   invariants are undefined or uninformative.
3. **The ECA texture-SSL result stands as a documented negative**: BYOL instance
   discrimination on spacetime textures recovers the genotype and misses computation
   (`RESULTS.md`, 2026-07-01). It is retained as the baseline all learning levers must
   visibly improve on.

## 4. The honest role of learning: two levers, one baseline, kill criteria

- **Lever A — physics-supervised amortizer (primary; next milestone).** Regress the
  dynamics feature vector (`caspectra/eval/dynamics.py` + `input_entropy_variance` in
  `eval/baselines.py`) from single diagrams. Not self-supervised in the purist sense —
  the labels come from the simulator, not humans. Success = criterion 6
  (leave-rules-out transfer); payoff = per-patch maps (test qualitatively on synthetic
  nuCA once the M4 simulator exists).
- **Lever B — predictive SSL along time (the one remaining discovery-flavoured
  experiment).** Masked future-row prediction; the predictability-vs-horizon profile is
  itself an order/chaos coordinate. This is the world-model direction the literature
  endorses for dynamical systems; it is the only objective we retain whose learned
  coordinate is *not* hand-chosen.
- **Baseline — BYOL instance discrimination**: frozen as the negative reference
  (`runs/default/`). No further augmentation-tuning runs: temporal-window positives are
  explicitly dropped as a standalone lever — they are still instance discrimination and
  inherit the same shortcut incentives that produced v1.
- **Kill criteria** (pre-registered): if Lever A fails criterion 6 *and* Lever B separates
  {54, 110} (106 reported both ways) no better than the direct damage features, the
  learning component concludes as a negative result — "texture and even dynamics-aware SSL
  add nothing over direct invariants on ECAs" — and effort moves to the larger rule space
  (M4), where class-IV-like rules are plentiful (Wuensche) and amortization has real
  computational value.

## 5. Ranked reading list (from the review; start at the top)

1. Culik II & Yu (1988), *Undecidability of CA Classification Schemes* — why a naïve
   "true class of a rule" is formally problematic.
2. Gilman (1987), *Classes of Linear Automata* — classification relative to a measure.
3. Kari (2005), *Theory of Cellular Automata: A Survey* — the map of undecidability and
   topological classes.
4. Mitchell, Hraber & Crutchfield (1993), *Revisiting the Edge of Chaos* — the standard
   corrective to edge-of-chaos narratives.
5. Crutchfield & Hanson — computational mechanics of rule 54 — complexity as particles,
   domains, interactions.
6. Wuensche (1999), *Classifying Cellular Automata Automatically* — input-entropy
   variance screening + finite-size caveats.
7. Israeli & Goldenfeld (2006), *Coarse-Graining of Cellular Automata, Emergence, and the
   Predictability of Complex Systems* — the rigorous phenotype-like hierarchy (emulation
   at larger scales), our main stretch direction.
8. Vispoel, Daly & Baetens (2022), *Progress, Gaps and Obstacles in the Classification of
   Cellular Automata* — the modern critical overview.
9. Rollier, Daly, Bruno & Baetens (2024), *CNNs for Automated CA Classification* — the
   identifiability trap, prior art.
10. Vispoel, Daly & Baetens (2024), *Damage Spreading and the Lyapunov Spectrum of
    Cellular Automata and Boolean Networks* — the bridge from perturbation metrics to an
    invariant-based taxonomy.

**Stretch directions** (tracked, not scheduled): Israeli–Goldenfeld emulation relations as
a reference partial order over rules; computational-mechanics domain/particle filters as a
per-diagram class-IV operationalization; 0–1 chaos test and Lyapunov profiles as further
invariant families.
