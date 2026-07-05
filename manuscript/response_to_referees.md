# Response to the referee (second round)

We thank the referee for a second exceptionally careful report. Its two central
technical points — that our narrative contradicted our own tables, and that the
reliability ceiling we cited is not the correct benchmark for an
independent-simulation estimator — were both correct, and both are now fixed at
the root rather than papered over. The manuscript has been rewritten around the
spine the referee identified as the defensible one: *a single space–time diagram
identifies the local rule under the matched observation model, and
reconstruct-and-simulate is then simulation-limited-optimal*. The title is now
"Rule reconstruction from a single space–time diagram yields simulation-limited
prediction of the finite-horizon damage response of cellular automata." All new
decision and reporting rules were committed numbers-free before measurement
(repository revision 8); "C1–C8" below name them.

---

## 1. The central narrative is internally inconsistent

**Agreed, and retired (C1).** "Never beats," "three tiers, one ordering,"
"dominates deep networks," and "compute the cheap features and skip the network"
are gone from the title, abstract, headings, captions and Discussion. The
CNN-vs-five-statistic comparison is now reported per target with paired CIs and
the registered verdict labels, and the honest summary is the referee's: **no
stable ordering** — the CNN is ahead on survival (Δ = +0.08, CI [+0.00, +0.20],
below the superiority margin), the baseline is superior on cone fill
(Δ = −0.21), fraction and rate are inconclusive at δ = 0.05. The stacking result
is promoted, not minimized: the CNN adds large, significant survival information
(+0.32, raising the stacked model from 0.56 to 0.88), and the manuscript now
names the statistics+CNN hybrid as the natural practical choice for
survival-like targets where rule reconstruction is unavailable (Secs. IV.B–C,
Discussion). The recommendation is stated conditionally on the observation
model, never as "skip the network."

## 2. The reliability ceiling is not the correct ceiling

**Agreed — this was our most consequential error, and fixing it made the result
stronger (C2).** The manuscript now distinguishes three quantities, each with
rule-bootstrap CIs (Sec. II.C): (1) latent-target reliability ICC; (2)
**empirical independent-replicate agreement** (the referee's 2·ICC−1; we verify
the algebraic prediction empirically — they match to four decimals); (3) a
**large-simulation reference** at 16× the Monte-Carlo budget. The mechanistic
estimator is judged against (2), the benchmark appropriate to a
fresh-simulation estimator, and sits *at* it on every target in both spaces
(e.g. ECA survival 0.985 vs 0.987 [0.978, 0.992]; radius-two cone fill 0.985 vs
0.959 [0.900, 0.987]). Scored against the near-noise-free reference (3), the
same predictions rise to the ICC ceiling (ECA survival 0.9943 vs ICC 0.9936;
radius-two 0.9877 vs 0.987) — the referee's diagnosis was exactly right: the
apparent shortfall was the comparison target's noise. "Reaches the reliability
ceiling" has been replaced throughout; survival's heteroscedasticity is noted
and all reliability intervals are bootstrap-based rather than Gaussian.

## 3. The mechanistic estimator's privileged assumptions and completion prior

**Agreed; both are now explicit (C3).** The estimator is introduced as
**matched-model system identification**, with the full assumption list
(deterministic, synchronous, binary, fully observed, noiseless, spatially
uniform, known radius) stated in the Methods and flagged in the abstract's first
claims. "Parameter-free" is retired. The default-zero completion is exposed as a
prior and tested: coverage is reported per rule space (ECA 18/18 fully covered;
radius-two 156/160, the four exceptions missing one entry each), the
default-0/default-1/empirical-prior completions move the radius-two median R²
by <0.001, and a **posterior-averaged variant** (exact enumeration of the 2^k
completions for small k, sampling otherwise) propagates table uncertainty into
predictive intervals — available precisely where reconstruction fails.

**Identifiability curve → phase diagram: done (C4).** This was the referee's
most valuable suggestion and is now a headline figure (Fig. 2). On the
radius-two held-out rules we sweep observation length, bit-flip noise, random
masking, and IC density, reporting coverage, exact-reconstruction rate, and the
median R² of the mechanistic inverter, the five statistics, and the frozen CNN
(on axes preserving its input geometry). The result quantifies the referee's
intuition: reconstruction is exact from as few as 4 observed rows when clean,
but collapses at ~2–5% observation noise and ~40% masking, where the frozen CNN
degrades more gracefully and *overtakes* the inverter — the regime where direct
amortization has a rationale, now delineated rather than asserted away. We did
not sweep IC correlation length, label noise or unknown radius this round;
the figure is labelled exploratory and those axes are named as extensions.

## 4. The paper does not "prove" why the CNN fails

**Agreed; language corrected.** "Prove(s) the mechanism" is gone; the probes are
presented as establishing **accessibility, not causal use** (Sec. IV.D states
this explicitly), and "any statistic that is a smooth function of the rule" has
been deleted — the argument now rests only on the fact the referee endorsed:
once the exact rule is known, the finite-horizon target can be directly
simulated. The rule-scrubbing, rule-provision, and learned rule-reader→simulator
interventions are named in the Discussion as the tests that would establish
causality; we have not run them and do not claim their conclusions.

## 5. The probe results need definition

**Provided (Sec. IV.D).** The two probe tasks are now specified separately:
*identity probes* (88/800 classes; stratified split over diagrams, so train and
test diagrams are disjoint but rule classes are shared — within-rule decoding
across new diagrams; majority baseline ≈ 0.011/0.001) and *truth-table-bit
probes* (leave-rules-out GroupKFold, so test rules are never seen — out-of-rule
transfer; chance 0.5; bits evaluated separately and averaged). Both are linear
(logistic) probes on the bottleneck vs the five statistics, with the
deterministic tabulation result reported alongside as the raw-diagram
reference. The manuscript no longer speaks of classifying "unseen identities."

## 6. The statistical analysis is incomplete

**Completed (C5).** Table III now gives the full radius-two per-target results:
held-out count, each method's R² with rule-bootstrap 95% CIs, the CNN's
mean ± s.d. over all five seeds (no more single "reference seed"), with paired
ΔR², CIs and verdicts in Sec. IV.B and the replicate-agreement and ICC columns
alongside. Split uncertainty beyond the registered split is quantified for the
deterministic methods — **leave-one-orbit-out over all 88 ECA orbits** and **20
repeated radius-two outer splits** (survival 0.76 with 5th–95th range
0.56–0.84; fill 0.68, 0.55–0.75) — and the mechanistic estimator is
split-invariant by construction (no trained parameters). We state explicitly
that CNN retraining across splits was not performed and that its seed spread
does not capture split variance. TOST margins are reported at δ ∈ {0.02, 0.05,
0.10} (verdict changes listed in the appendix; no superiority verdict moves).
"Tie"/"equivalent" now appear only where TOST passes; the spatial-map result is
relabelled **inconclusive** (see §8).

## 7. One constrained CNN does not represent deep networks

**Claims narrowed (the referee's option 1).** Every neural claim is scoped to
"this architecture under this training budget" (Sec. III, Discussion), the full
architecture (layer table, 31,524 parameters, receptive field, optimizer,
schedule, augmentations, training cost) is in the supplement, and the
Discussion names the missing comparators — above all a learned rule-table
predictor feeding a simulator — as open questions rather than settled ones. We
did not run a model suite; with the narrowed claims none of our conclusions
require one. The identifiability diagram additionally identifies the regimes
where such learned system identifiers would be the interesting competitors.

## 8. The spatial-map conclusion is too strong

**Corrected (C7).** The result is now labelled by the registered framework:
**inconclusive** (Δ = +0.047, 95% CI [−0.002, +0.102], 90% CI [+0.005, +0.092]
— neither superiority nor equivalence), described as "a small, statistically
unresolved edge for the learned map." "Training-free" is corrected to "no
additional training at deployment." The protocol details the referee asked for
are in the supplement: 16-rule panel, pairs with rate gap ≥ 0.25, 8 ICs per
pair, half/half mosaics, validation/test split of pairs (window selected once
on validation, per-pair best window reported only as a labelled oracle
sensitivity), independent random streams for the local ground truth, and —
importantly — the **unit of resampling is the composed system** (per-pair
mean-over-IC Spearman values are bootstrapped; columns never enter the
inference as independent observations). Extending the mechanistic contribution
to a local system-identification map is named as future work; we agree it is
the on-thesis extension.

## 9. The landscape should be a damage-signature landscape

**Renamed and validated with confusion matrices (C6).** Title, abstract,
Discussion and the figure caption now say **damage-signature landscape**, and
the prevalence is stated as "7.8% (Wilson CI [6.9, 8.8]%) satisfying the
registered finite-horizon damage-signature criterion under the stated sampling
distribution." The ECA validation is now a full confusion matrix against the
literature class-IV ground truth: the signature has sensitivity 1.0,
specificity 0.988, precision 2/3 (its one false positive being the documented
borderline rule 106), balanced accuracy 0.994 — raw agreement is no longer the
headline. The same reporting shows the *independent detector* is the weak
instrument (sensitivity 0.5 — it misses rule 54's light-speed ether — precision
0.17), which is exactly why we do not promote the radius-two band to a glider
region: there the detector agrees with the signature at balanced accuracy 0.39
(precision 0.05). The curated long-horizon radius-two validation the referee
sketches is the right way to earn a complexity claim; we have not done it and
make no such claim.

## 10. Pre-registration is unauditable during review

**De-emphasized and labelled, with one candid limitation.** The paper no longer
leans on "pre-registered" as its warrant: the word is used sparingly, and
Appendix A now **labels every analysis** as registered / post-hoc confirmatory /
exploratory, including the honest placement of this revision's own additions
(the replicate-agreement correction and reference simulation: post-hoc
confirmatory; the identifiability diagram and Pareto curve: exploratory). The
one deviation from the original registration (the target-stream RNG fix)
remains disclosed with its measured effect. On review-time access: we have kept
the repository private during review to protect anonymity, and we acknowledge
plainly that this limits auditability; the complete timestamped history
(criteria revisions, code, cached predictions and targets) is released with the
article, and we are glad to provide the editor an anonymized archive on
request.

## 11. Report the compute trade-off

**Done (C8; Sec. IV.F).** Per-diagram latency: mechanistic 283 ms at the
production 256-pair budget (single CPU core, embarrassingly parallel) vs 2.2 ms
for a CNN forward pass and 1.4 ms for the five statistics; one-time costs
≈22 min training per CNN seed vs 15 s for the boosted baseline; break-even
≈4,700 queries. The accuracy-vs-budget curve is the informative part: at a
16-pair budget (17 ms) the mechanistic median R² is 0.924 — above both direct
estimators at any cost — so under the matched observation model the estimator
is simultaneously the most accurate at every budget we measured. The practical
recommendation now carries this price tag explicitly.

## 12. Missing methodological detail

**Supplement added (Appendix B).** It contains every item on the referee's
list: diagrams per rule per split and stream independence (no shared random
numbers across methods); the full CNN layer table with parameter count and
receptive field; optimizer, schedule, batch size, augmentations, and the
absence of early stopping; ridge/GBM settings and the baseline-of-record rule;
the exact split protocol including the force-held complex panel; the exact
target formulas including perturbation-cell selection and the
no-surviving-damage convention; the panel-overlap disclosure (the 800-rule
estimator panel is a subset of the 3,000-rule landscape sample); the detector
definition and thresholds; and the composed-system construction.

---

## Editorial points

1. **Slash notation**: removed; every paired value names its rule space.
2. **Table I caption**: rewritten; it states the aggregation rule, points to
   the per-target tables, and makes no ordering claim about the CNN and the
   baseline.
3. **Reference-seed CNN**: all tables report mean ± s.d. over the five seeds.
4. **Stacking table**: now carries 95% CIs and the full stacked-model R²
   (base → stacked) alongside each increment.
5. **"Deterministic given the protocol"**: corrected to "reproducible under a
   fixed seed but Monte-Carlo limited."
6. **"Smooth function of the rule"**: deleted (no smoothness claim is needed
   or made).
7. **Companion sensitivity analysis**: the free-floating reference is removed;
   protocol dependence is shown directly in Fig. 2(d) and the released code
   contains the full protocol sweep.
8. **Assumptions visible early**: the observation model (fully observed,
   noiseless, deterministic, binary, known radius) appears in the abstract and
   in Methods before any result.
9. **Vispoel citations**: completed with volume, pages and DOIs
   (Chaos, Solitons & Fractals **184**, 114989, 2024,
   doi:10.1016/j.chaos.2024.114989; Physica D **432**, 133074, 2022,
   doi:10.1016/j.physd.2021.133074).
10. **Figure 1**: caption rewritten — sample size and Wilson CI stated, panel
    overlap disclosed, embedded anchor rules identified, and an explicit
    statement that the red band is not an independently validated glider
    region.
11. **Verdict language**: "no evidence of superiority," "practical
    equivalence," and "inconclusive" are used strictly per the registered
    definitions everywhere (including the spatial map, which is inconclusive).

---

## Summary of what is new in this revision

C2 corrected reliability benchmarks (ICC vs replicate agreement vs
large-simulation reference, with CIs); C3 coverage/completion sensitivity and a
posterior-averaged uncertainty-aware mechanistic variant; C4 the
identifiability phase diagram (new Fig. 2); C5 complete per-target tables for
both spaces with seed spreads, repeated-split/leave-one-orbit-out uncertainty,
and TOST margin sensitivity; C6 confusion-matrix validation and the
damage-signature reframing of the landscape; C7 the corrected (inconclusive)
spatial-map verdict with full protocol disclosure; C8 the accuracy–compute
Pareto analysis. The manuscript was rewritten around rule identifiability and
simulation-limited prediction, with every neural claim scoped to the tested
architecture and every analysis labelled by its registration status.

---

# Round-3 supplement (prepared in advance; folded into the concern structure)

Everything below was produced after the round-2 revision was frozen, on a
separate branch so the submitted PDF is untouched; each block is filed under
the round-2 concern it continues. Decision rules were committed numbers-free
before each measurement (repository revisions 9 and 10; the full
registration-history extract is Appendix L1 of this letter).

## Cross-reference: concern → response → manuscript location

| Concern | Round-2 response | Round-3 continuation | Manuscript |
|---|---|---|---|
| 1 narrative consistency | §1 (retired, C1) | — | §IV.A–B, Table I |
| 2 reliability ceiling | §2 (C2) | — | §II.C |
| 3 assumptions + identifiability | §3 (C3, C4) | frontier estimators + the two axes deferred at round 2 (→ §3-bis) | §IV.D–E, Figs. 2–3 |
| 4 mechanism not proven | §4 | — | §IV.D |
| 5 probe definitions | §5 | — | §IV.D |
| 6 statistics incomplete | §6 (C5) | — | Tables II–III |
| 7 one constrained CNN | §7 | learned rule-reader + two fairness controls (→ §7-bis) | §III(iii), §IV.E |
| 8 spatial map | §8 (C7) | — | §IV.G |
| 9 landscape naming | §9 (C6) | — | §IV.G, Fig. 4 |
| 10 registration auditability | §10 | corrected access rationale + attached history (→ §10-bis) | App. A |
| 11 compute | §11 (C8) | — | §IV.F |
| 12 methods detail | §12 | — | App. B |

## §3-bis. The identifiability frontier, completed (continues concern 3)

Round 2 deferred two axes ("we did not sweep … label noise or unknown radius
this round"). Both are now measured, together with the estimators the phase
diagram called for, pre-registered numbers-free as revision 9 with three
hypotheses whose verdicts are reported as earned (one split, one refuted in
half — manuscript Appendix A enumerates them):

- **Bayesian rule-posterior (no training)**: restores identification across
  the intermediate band — masking tolerance extended from ~25% to 50% of
  cells, IC-density extremes rescued, exact polarity invariance — and is best
  of all methods up to ~3% bit-flip noise. Self-estimated noise rate matches
  the supplied-rate variant throughout.
- **Label-polarity axis**: the read-then-simulate family is exactly
  invariant; the frozen CNN and the stack degrade.
- **Unknown-radius axis**: smallest-consistent selection costs ~0.12 median
  R² on clean diagrams and degrades under noise — the known-radius
  assumption now carries a measured price.
- The registered calibration of the posterior's 1σ predictive intervals is
  reported per cell (manuscript §IV.E), completing the one reporting item
  that was outstanding from the rev-9 registration.

## §7-bis. The learned rule-reader and two fairness controls (continues concern 7)

The referee three times asked what a *learned* rule-reader would do where
exact inversion fails. We benchmarked it (registered as exploratory, gated
single-seed training): its MAP table fails everywhere (per-bit accuracy 0.73
never yields an exact table, and one mostly-right table is a badly wrong
dynamical system), while *sampling* its per-bit posterior is the only
estimator that does not collapse beyond 5% noise (median R² ≈ 0 out to 20%,
all others −1 to −5.6). It moves the frontier without restoring
identification; under masking it adds nothing.

Because the reader is degradation-trained while the direct CNN of the
submitted manuscript is clean-trained and architecturally constrained, we
also ran the two symmetric controls this comparison owes the reader of the
degraded-regime guidance (pre-registered as revision 10 before measurement):
**(C-i)** the same direct CNN retrained with the reader's registered
degradation augmentation, and **(C-ii)** an unconstrained same-budget
`resnet18` CNN — the architecture the anti-shortcut constraint was designed
against, whose motivating claim round 2 retired.

The controls changed one conclusion and confirmed the other, and we report
both plainly. **Changed:** the noise "dead zone" was an adaptation artifact,
not an estimator-family boundary — the degradation-trained direct CNN holds
median R² 0.51–0.62 across 3–15% noise, where no previously tested estimator
exceeded 0.17; our earlier statement that learned system identification is
the only class retaining signal there is withdrawn and replaced by the
measured one (what decides the noise band is training for the corruption,
at a ~0.14 clean-diagram cost). **Confirmed:** at every grid cell where the
rule is recoverable (per-bit ≥ 0.95), the best read-then-simulate estimator
remains unbeaten with both controls included — zero violations of the
registered hypothesis — and the unconstrained 11.2M-parameter network is no
better on clean diagrams than the 31k constrained one (0.55 vs 0.65) while
degrading faster under noise, so the matched-regime negative result is not
an artifact of the constraint. The Bayesian posterior still owns the
intermediate masking and density band against both controls. Manuscript:
Sec. IV E(iii), Table V, Discussion; measured record: RESULTS.md rev-10
section with artifacts under `runs/m4_range2_degaug/`,
`runs/m4_range2_resnet/`, and `runs/m4_range2/frontier_grid_controls/`.

## §10-bis. Registration auditability, corrected (continues concern 10)

Two updates. First, our round-2 rationale for the private repository
("to protect anonymity") was wrong and we withdraw it: the byline is signed
and the manuscript cites our own group, so anonymity was never the
constraint. The repository is private because it is the submission history
of an unpublished article; that is a choice, and it does limit auditability
during review. Second, instead of offering an archive "on request", we now
attach the registration evidence directly: Appendix L1 reproduces the
complete commit history of the criteria file (revision, timestamp, subject),
so the numbers-free-before-measurement ordering for every load-bearing
revision is checkable from this letter alone, and the full timestamped
repository is released with the article.

One honest caveat belongs in this list: for criterion 7 (the nuCA
validation, a by-product) the registration and the measurement were
committed together, so for that one criterion the ordering is attested
rather than git-auditable. Every criterion the paper's claims rest on
(revisions 7–10) has the committed numbers-free ordering shown in
Appendix L1.

## Correction disclosed (found by internal audit, fixed at the source)

An internal pre-submission audit found that one manuscript number and six
cells of the internal measured record still carried values from the
discarded wrong-checkpoint frontier run that RESULTS.md itself documents
(the run was re-measured with the canonical checkpoint before any rev-9
number was reported, but the in-session reproduction check covered the
shared columns, not those six cells). The manuscript value "frozen CNN to
−1.1" is corrected to the canonical −0.93; no bolded comparison, verdict, or
conclusion changes. A programmatic audit
(`scripts/audit_manuscript_numbers.py`) now re-derives every §IV.E prose and
table number from the released artifact and fails on mismatch; it runs clean
on the revised manuscript.

## Appendix L1 — registration-history extract (EVALUATION_CRITERIA.md)

Complete `git log --follow` of the criteria file (newest first). Each
revision commit is numbers-free; measurements follow in separate commits.

| Commit | Timestamp | Subject |
|---|---|---|
| c16cc2b | 2026-07-05 20:26 | Pre-register round-3 fairness controls + reporting completions (rev 10) |
| 8f5cb56 | 2026-07-05 01:43 | Pre-register identifiability-frontier controls (rev 9) |
| 75e1d42 | 2026-07-04 20:40 | Pre-register round-2 review-response controls (rev 8) |
| a809b2a | 2026-07-04 14:27 | Pre-registration rev 7: review-response controls (numbers-free) |
| 516866b | 2026-07-04 01:21 | Pre-register rev 6: baseline & robustness controls (S1–S3), numbers-free |
| e2dd185 | 2026-07-04 00:15 | Pre-register M4 (criterion 9) + range-2 harness, no measured numbers |
| ead0fcf | 2026-07-03 18:58 | Pre-register criterion 8: stripe resolution (8a) + alloy transfer (8b) |
| c2b99cb | 2026-07-03 01:52 | nuCA validation: criterion 7 pre-registered, measured, and passed (registration and measurement in one commit — the caveat disclosed in §10-bis) |
| a7789b4 | 2026-07-02 11:21 | (pre-criteria bootstrap) |

First measurement commits following each load-bearing revision: rev 8 →
fa994da (2026-07-05 00:52); rev 9 → 111e3df (2026-07-05 10:00) and 0f8e691
(2026-07-05 14:04); rev 10 → the control-training commits recorded in the
repository history accompanying this revision.
