> **SIMULATED REVIEW** — ARS panel, 2026-07-05, Devil's Advocate. Not a real referee report.

Reviewed artifact: `manuscript/main.tex` (774 lines, REVTeX source; compiled PDF not consulted). Line numbers below refer to that file. Contract: `reviewer/reviewer_full/v1`, baseline v3.6.2. Phase 1 was drafted from contract + metadata only, before the manuscript was opened, and is reproduced unmodified.

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** The paper's experimental design must meet the peer-review bar of both communities it straddles: nonlinear dynamics and ML benchmark methodology. For a paper claiming that rule reconstruction from a single space–time diagram yields "simulation-limited" prediction of a finite-horizon damage response, this means the reconstruction protocol, the prediction target, the baselines, the train/test hygiene, the statistical reporting (error bars, seeds, multiple-comparison awareness), and the reproducibility affordances (code, configs, exact protocol parameters) must all be specified well enough that a competent reader could re-run the study and would trust the reported comparisons. Because the claim is comparative ("X-limited", implying an ordering of methods against a ceiling), the rigor question centers on whether the ceiling is measured rather than assumed, and whether every method was given a fair shot.

**D2 — domain_accuracy (mandatory).** Claims must align with what is actually known about elementary/finite cellular automata: undecidability and measure-dependence of behavioural classification, the damage-spreading literature, Lyapunov-exponent analogues for CA, and the ML-for-dynamical-systems literature. Prior work must be represented correctly — neither strawmanned (e.g., overstating what neural baselines are claimed to do elsewhere) nor overclaimed (e.g., asserting novelty for results that are folklore in the CA identification literature, where rule inference from spacetime data is a classical, often easy problem). Terminology (Wolfram classes, Langton-style parameters, damage response, finite horizon) must be used with the standard meanings or explicitly redefined.

**D3 — argumentative_coherence (mandatory).** The central thesis — reconstruction-then-simulation is the dominant strategy, making prediction "simulation-limited" — must be internally consistent and actually supported by the evidence presented. The key coherence risks for this kind of paper: (a) tautology, i.e., the conclusion is guaranteed by the setup (deterministic, fully observed, noiseless system with known interaction radius) rather than discovered; (b) asymmetric standards, i.e., interpretable methods evaluated in-regime while learned methods are evaluated out-of-regime or under handicaps; (c) verdict inflation, i.e., mixed or split experimental outcomes narrated as confirmation. The argument must survive the question "what would have falsified this?"

**D4 — cross_disciplinary_relevance (high).** Chaos readers are nonlinear-dynamics people, not ML people; ML readers who find this will judge the benchmark methodology. The framing, definitions ("simulation-limited", "damage response", "identifiability frontier" or similar), and implications must be accessible to both sides, and any interdisciplinary moral — e.g., lessons for ML-for-science benchmarks generally — must be substantiated rather than gestured at. A paper about elementary CA on a small ring must answer "so what?" for readers who care about continuous dynamical systems, real experimental data, or generic ML practice.

**D5 — writing_and_structure (normal).** At ~8,500 words in 9 two-column REVTeX pages, the manuscript must be tightly organised: claims traceable from abstract through results to conclusion, figures and tables legible and self-contained, notation consistent, venue conventions (AIP/Chaos style, lead paragraph, section structure) respected. A revised, round-3-ready draft is held to a higher polish bar: leftover revision scaffolding, hedging bloat, or abstract/body mismatches count against it.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: measured (not assumed) prediction ceiling; identical data budgets and tuning effort across compared methods; explicit protocol tuple (ICs, boundary, size, horizon); seeds/error bars for every headline number; pre-registration or at least post-hoc-labelled analyses; code/data availability.
- **what_triggers_block**: a headline comparison where the losing method was demonstrably under-resourced or under-tuned relative to the winner and the conclusion depends on it; or the "limit"/ceiling is asserted without measurement; or train/test leakage.
- **what_triggers_warn**: single-seed or unreported-variance headline numbers; hyperparameter effort asymmetry acknowledged but unquantified; ceiling measured only in the favourable regime.

### D2: domain_accuracy
- **what_to_look_for**: correct use of CA-theory results (undecidability, class schemes, damage spreading); fair citation of prior rule-identification work (rule inference from spacetime diagrams is classical); accurate characterisation of what neural approaches claim elsewhere.
- **what_triggers_block**: a factual domain error that a Chaos referee would flag as disqualifying (e.g., misstating what Wolfram classes are, claiming novelty for known-easy rule inference without acknowledgement, misreporting a cited result the argument depends on).
- **what_triggers_warn**: novelty framing that under-cites the CA-identification literature; loose analogies (e.g., to Lyapunov exponents or chaos proper) presented as more than analogies; borderline-class handling glossed over.

### D3: argumentative_coherence
- **what_to_look_for**: an explicit statement of what "simulation-limited" rules out and what evidence could have refuted it; symmetric treatment of hypotheses that were confirmed vs. refuted; the neural baseline's failure attributed via ablation/diagnosis rather than narrative.
- **what_triggers_block**: the central claim is circular (true by construction of the benchmark) and the paper does not acknowledge or defuse this; or split experimental verdicts are reported as clean confirmation in abstract/conclusions; or the "interpretable methods dominate" moral is generalised beyond the tested regime in the paper's own claim sentences.
- **what_triggers_warn**: tautology risk acknowledged but underexplored; alternative explanations for neural failure (capacity, budget, author-imposed architecture constraints) mentioned but not tested; favourable spin on mixed results confined to framing language rather than claim sentences.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: a concrete "so what" for Chaos readers (link to damage spreading / stability analysis traditions) and for ML readers (benchmark-design lesson); definitions readable by both; honest scoping to elementary CA.
- **what_triggers_block**: the interdisciplinary moral (e.g., "interpretable methods dominate") is offered as a general lesson with no bridge argument from the toy system, such that an adjacent-field reader would be actively misled about applicability.
- **what_triggers_warn**: the lesson is scoped only in caveats while the framing sells generality; key ML or CA jargon unexplained for the other audience.

### D5: writing_and_structure
- **what_to_look_for**: abstract–body–conclusion consistency; figure/table self-containedness; 8,500 words justified by content; REVTeX/Chaos conventions; revision seams.
- **what_triggers_block**: structural incoherence that prevents evaluation (claims unlocatable, figures contradicting text).
- **what_triggers_warn**: bloat, redundant hedging, figures that require the text to decode, terminology drift between sections.

[CONTRACT-ACKNOWLEDGED]

## Dimension Scores

*No Scoring Plan Dissent: the Phase-1 triggers are applied as committed.*

### D1 — methodology_rigor: **warn**
The core measurement apparatus (three-way ceiling decomposition, K=20 replicates, disjoint random streams, rule-level cluster bootstrap, TOST margins, lines 169–259, 667–691) is above the bar, but warn triggers fire: the frontier comparison gives the read-then-simulate family two purpose-built degraded-regime repairs while direct amortization stays frozen and clean-trained (lines 441–442, 494–527); the CNN's split variance is explicitly not measured (lines 255–257); the stacking base R² is irreconcilable with the headline tables (Table IV line 397 vs Table III line 331); and Appendix A's registration taxonomy omits the rev-9 items §V.E claims as registered (lines 667–691 vs 495–498).

### D2 — domain_accuracy: **warn**
I found no disqualifying domain error — the CA theory (undecidability line 86, measure dependence lines 86–89, orbit symmetries, borderline rule 106 handling lines 589–592) is used correctly — but the warn trigger fires on citation grounding: the benchmark practice the paper's general lesson targets is entirely uncited ("benchmarks are usually posed", lines 101–103), "amortization" is used as a term of art without citing the amortized/simulation-based-inference literature it comes from, and the damage-spreading concept is cited only through two recent group-adjacent works (line 93) rather than its statistical-mechanics lineage.

### D3 — argumentative_coherence: **block**
Per the committed trigger ("split experimental verdicts are reported as clean confirmation in abstract/conclusions"): the abstract assigns the degraded regime — "observation noise above ∼2%, heavy masking, or extreme initial-condition densities" — to "the regime in which direct amortization has a rationale" (lines 55–59), while the paper's own §V.E shows read-then-simulate variants dominating most of that regime (posterior 0.85 vs 0.24 at 40% masking, 0.59 vs −0.77 at 50%, 0.77 vs 0.08 at density 0.1; lines 503–507) and the Discussion asserts the rule-reader "is the only estimator that retains signal" in degraded regimes (lines 642–644), contradicted two sentences later by the paper's own guidance that the posterior "holds to ∼3% noise, 50% masking, and extreme densities" (lines 655–657). The body's §V.E verdict reporting is honest; the abstract- and conclusion-level statements are not consistent with it.

### D4 — cross_disciplinary_relevance: **warn**
The lesson comes with a genuine bridge argument ("whenever the observation encodes the generator", lines 626–630) and the boundary of applicability is mapped empirically rather than asserted, so no block; but the warn trigger fires because the interdisciplinary claim is substantiated by zero citations to the ML-for-dynamics or amortized-inference benchmarks it addresses, and the abstract's "$2\,\mathrm{ICC}-1$ under additive noise" compression (line 47) presumes measurement-theory fluency the Chaos readership is not guaranteed to have.

### D5 — writing_and_structure: **pass**
The paper is dense but claims are traceable, tables carry per-target CIs as promised (line 246–247), and captions are self-contained; residual defects (TODO markers at lines 19–21, "and--- we believe---" at line 624, the 80-vs-160 held-out-rules discrepancy between Fig. 1's caption at line 445 and Table III at line 337, a CI printed as "[+0.00,+0.20] excluding 0" at lines 358–359) are minor-grade and do not prevent evaluation.

## Failure Condition Checks

Evaluated from my own dimension scores per the contract expressions (D1–D3 mandatory, D4 high-priority, D5 normal):

- **F1** (severity 90, "any mandatory dimension scores 'block'"): **fired: true** — D3 = block. Action: `editorial_decision=reject_or_major_revision`.
- **F2** (severity 70, "two or more mandatory dimensions score 'warn' or worse"): **fired: true** — D1 warn, D2 warn, D3 block. Action: `editorial_decision=major_revision`.
- **F3** (severity 60, "any high-priority dimension scores 'block'"): **fired: false** — D4 = warn, not block.
- **F0** (severity 10, "every mandatory dimension scores 'pass'"): **fired: false**.

Highest-severity fired condition: F1 → `reject_or_major_revision`.

## Review Body

*Devil's Advocate Stress-Test Report — dedicated format.*

Two sentences of fairness first: the measurement hygiene here — three explicitly distinguished reliability ceilings, disjoint random streams engineered against contamination, registered-vs-post-hoc-vs-exploratory labels with a disclosed deviation, and inconclusive verdicts reported as inconclusive — is better than the large majority of ML-for-science papers, and the ICC vs. $2\,\mathrm{ICC}-1$ distinction is a genuinely exportable contribution. Everything below should be read against that baseline of unusual honesty.

### Strongest Counter-Argument

Strip the apparatus and the central result is a corollary of the setup. In a fully observed, noiseless, binary, synchronous, known-radius CA, a 127×127 diagram contains ~16,000 neighbourhood→cell transitions; under Bernoulli(1/2) ICs each of the 32 radius-two table entries is exercised hundreds of times in expectation, so exact table recovery is a near-certainty before any experiment is run — and the paper's own numbers confirm the identity: the exact-reconstruction rate (97.5%) coincides exactly with table coverage (156/160 fully covered, lines 219–222, 344–347). Once the table is exact, the "mechanistic estimator" is not a predictor of the damage response; it *is* the damage-response measurement — same rule, same protocol, independent stream. That it attains the independent-replicate benchmark $2\,\mathrm{ICC}-1$ is true by construction, which the paper itself states ("statistically indistinguishable from having re-measured the ground truth itself", lines 275–277). Worse for the framing: the target family is simulation-defined — all four statistics are *defined* as short protocol re-runs — so no accuracy benchmark in this family could ever favour amortization; the paper concedes this only at §V.F (lines 557–560). What remains as empirical content is (i) a negative result about one 31,524-parameter network the authors deliberately constrained, for a rationale they themselves retire (line 427), with the ~22-minute unconstrained control never run; (ii) an exploratory frontier in which read-then-simulate receives two purpose-built repairs while direct amortization stays frozen; and (iii) by-products whose headline validation is inconclusive (maps, lines 571–576) or rests on a two-element reference set (landscape, lines 586–592). The general lesson is then addressed to benchmarks the paper never cites. On this reading, the paper is a meticulous measurement of a foregone conclusion plus honest negative results — a methods note, not a discovery.

### Issue List

#### CRITICAL

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| C1 | D3 | Conclusions-level statements contradict the paper's own frontier results. (a) The abstract assigns the degraded regime (noise >~2%, heavy masking, extreme IC densities) to "the regime in which direct amortization has a rationale", but §V.E shows the Bayesian rule-posterior (read-then-simulate) dominating the masking and density axes (0.85 vs 0.24 at 40% masking; 0.59 vs −0.77 at 50%; 0.77 vs 0.08 at density 0.1) and the dead zone belonging to the sampled rule-reader — *learned system identification*, not direct amortization; the abstract omits these rev-9 estimators entirely, presenting a conclusion the full analysis supersedes. (b) The Discussion asserts the rule-reader is "the only estimator that retains signal" in "the degraded regimes where exact inversion is unavailable" — false under masking and density per §V.E, and contradicted in the next paragraph by the paper's own guidance ("the Bayesian posterior holds to ∼3% noise, 50% masking, and extreme densities"). Abstract-level readers will take away the wrong recommendation for the degraded regime; that meets the "publishing would mislead readers" bar. The fix is localized (rewrite the abstract's final third and one Discussion sentence to match §V.E). | Abstract lines 55–59; Discussion lines 641–644 vs lines 654–657; §V.E lines 494–538 | — (internal contradiction; no field norm involved) | — |

#### MAJOR

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| M1 | D1 | Asymmetric repair budget on the identifiability frontier: the read-then-simulate family receives two estimators purpose-built for degradation (Bayesian posterior; a rule-reader *trained on degradation-augmented diagrams*, line 515–516), while direct amortization is represented only by a CNN frozen at its clean-training state ("no retraining", line 442). The symmetric control — the same CNN retrained with the same degradation augmentation given to the reader — is absent, so the registered claim "at no grid cell with high table recovery does any direct amortizer beat the best read-then-simulate estimator" (lines 531–533) and the three-tier practical guidance (lines 653–659) compare adaptation-budgeted SI against adaptation-naive amortization. The scope disclaimer at lines 237–240 covers architecture/budget, not this specific augmentation asymmetry. | §III(iii) lines 232–243; §V.E lines 441–442, 514–533; Discussion 653–659 | Equal-adaptation-budget norm in ML benchmarking: comparisons are informative only when compared method families receive comparable tuning/adaptation effort (Lipton & Steinhardt 2019, *Queue* 17(1), "Troubling Trends in ML Scholarship"; Musgrave et al. 2020, ECCV, metric-learning "reality check"). | The paper's degraded-regime recommendation is derived directly from grid cells where one family was augmentation-trained for the test distribution and the other was not; the ordering at those cells is exactly what the missing control would test. |
| M2 | D1/D3 | Unexplained inconsistency between the stacking analysis's base-model R² and the same method's headline R²: five statistics score 0.809 (survival) and 0.596 (cone fill) in Table III but enter the stacking table at 0.56 and 0.14 respectively. The abstract-quoted "+0.32" complementarity (line 54–55, lines 397, 380–383) is computed from the weaker 0.56 base; a reader cannot reconcile the two tables, and the increment's magnitude at the headline baseline strength is unknown. Needs an explicit reconciliation (presumably the cross-fitting protocol) and, if the discrepancy is protocol-induced, a statement of the increment under the headline protocol. | Table IV lines 391–408 vs Table III lines 325–342; abstract lines 53–55 | — (internal consistency) | — |
| M3 | D1 | Registration bookkeeping is internally inconsistent — damaging for a paper whose rigor apparatus is a selling point. Appendix A's authoritative registered/post-hoc/exploratory taxonomy (lines 679–687) omits the rev-9 frontier registrations that §V.E and the Fig. 2 caption invoke; §V.E simultaneously labels the same experiments "registered numbers-free as rev.~9 before measurement", "post-hoc confirmatory", and "exploratory" (lines 495–498, 488–490); and three "registered hypotheses" are referenced by ordinal ("the third registered hypothesis", line 531) without ever being enumerated, so their verdicts cannot be audited against the registration. | App. A lines 667–691; §V.E lines 495–498, 527–533; Fig. 2 caption lines 488–490 | The paper's own declared standard (lines 128–131, 676–679); no external norm needed. | — |
| M4 | D2/D4 | The general lesson targets an uncited antagonist. "The observation model in which such benchmarks are usually posed" (lines 101–103) names no benchmark; no ML-for-dynamical-systems prediction benchmark (learned Lyapunov/chaos-class predictors, learned surrogate simulators) is cited anywhere; and "amortization" — used ~15 times including the title's framing — is borrowed from the amortized/simulation-based-inference literature without a single citation to it. Likewise, nobody who "easily conflate[s]" ICC with replicate agreement (lines 47–48) is cited. Without one concrete instance, the abstract's closing "general lesson for machine-learning benchmarks on deterministic dynamical systems" (lines 62–64) is a corrective aimed at an undocumented practice. | Intro lines 99–107; abstract lines 62–64; Discussion lines 624–630; reference list (13 cited keys) | Universal scholarly standard that characterizations of a literature's practice require citations (AIP/Chaos author guidelines; COPE discussion-of-prior-work expectations). | The existence and character of the criticized benchmark practice is the load-bearing premise of the paper's stated general lesson; it is the one premise supported by no evidence in the manuscript. |
| M5 | D3 | The headline result's empirical content is thinner than its framing: because all four targets are simulation-defined (short protocol re-runs), reconstruct-and-simulate is the target's own definition applied to an estimated rule, so benchmark attainment follows from coverage alone — and the paper's numbers confirm the identity (97.5% exact recovery ≡ 156/160 covered tables). The paper concedes the pieces (assumptions "load bearing", line 151; "statistically indistinguishable from having re-measured", lines 275–277; amortization's case "must rest on degraded-observation regimes ... not on accuracy", lines 557–560) but presents attainment as "the central, positive ... finding" (lines 624–626) rather than a near-corollary, and the corollary structure surfaces only in §V.F. Partial concession acknowledged; the residual demand is to state in the Introduction that on simulation-defined targets amortization can never win on accuracy, only on cost/robustness — which reframes what the benchmark can, in principle, show. | Title; abstract lines 40–46; §V.A lines 264–280; §V.F lines 555–560; Discussion 620–630 | — (framing/logic, not a field norm) | — |
| M6 | D1/D3 | The matched-regime negative result ("direct estimators fall far short") rests solely on a 31,524-parameter network carrying an author-imposed first-layer constraint whose motivating claim the paper itself retires ("The 2×2 first layer therefore does *not* prevent rule recovery; we retired that claim", lines 425–427) — yet the constrained architecture is kept and the obvious control (a same-budget unconstrained CNN, ~22 min/seed per line 726–727) is never run. The scoping concession (lines 237–240, 632–636) is acknowledged and prevents this being CRITICAL; but a negative result whose only tested instance was deliberately handicapped, for a reason now void, under-determines even the scoped conclusion, and the control is cheap enough that round 3 should include it. | §III(iii) lines 232–243; §V.D lines 411–432; App. B lines 718–727; Discussion 632–641 | Baseline-fairness norm as in M1 (Lipton & Steinhardt 2019; Musgrave et al. 2020). | The abstract's "fall far short" (lines 52–54) and the practical guidance derive from this single handicapped instance; the retired justification removes the design reason for not running the fair variant. |

#### MINOR

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| m1 | D1/D5 | A CI printed as "$[+0.00,+0.20]$ excluding $0$" is self-contradictory as typeset; print more decimals or rephrase. | Line 358–359 |
| m2 | D5 | Fig. 1 and Fig. 2 captions say 80 held-out rules; Table III and §V.B say 160. If the sweeps subsample, say so and say how. | Lines 445, 478 vs 337, 355 |
| m3 | D2 | "The signature earns considerable trust" from selecting {54, 106, 110}: sensitivity 1.0 is computed on a two-element reference set and precision 2/3 on three selections; the language outruns n, though the surrounding disclaimers are good. | Lines 586–592 |
| m4 | D2 | Damage spreading is cited only via two recent CA-specific works (both adjacent to the authors' group; 3 of 13 cited keys are group self-citations); the statistical-mechanics lineage of the concept is absent. Flagged here as a citation-selection signal; completeness is R2's remit. | Line 93, reference list |
| m5 | D5 | Round-3-ready draft retains TODO markers (ORCIDs, corresponding email) and a typesetting glitch ("and--- we believe---"). | Lines 19–21, 624 |
| m6 | D1 | The baseline of record is "the stronger" of two fitted regressors, but the data on which "stronger" was judged (train vs. held-out) is unstated; with two candidates the risk is small but the criterion should be stated. | Lines 228–230, 729–731 |
| m7 | D3 | Calling the reader hypothesis "confirmed on the noise axis... in a weak sense" is generous for an estimator whose best regime is median R² ∈ [−0.04, 0.17]; "failed least badly" is the accurate verdict. The in-sentence concession ("moves the frontier without restoring identification") is acknowledged — hence MINOR. | Lines 522–531 |
| m8 | D4 | The abstract is a full page of compressed jargon ("$2\,\mathrm{ICC}-1$ under additive noise", "cross-fitted stacking") that presumes ML-methodology fluency; Chaos's nonlinear-dynamics readership needs one plainer sentence per result. | Lines 30–65 |

### Ignored Alternative Explanations / Paths

1. **Denoise-then-invert.** On the noise axis the parsimonious repair is a consistency-based diagram denoiser (even majority vote over repeated neighbourhood observations) followed by exact inversion; the Bayesian posterior partially subsumes this, but the explicit pipeline was never benchmarked and could dominate the 3–7% band where the posterior collapses. Its absence weakens the claim that the dead zone belongs to learned methods.
2. **Degradation-augmented direct CNN** (the M1 control): the frontier ordering in the outer tiers could invert if the direct amortizer received the same augmentation as the rule-reader; the paper's guidance assumes it would not, without testing.
3. **Objective mismatch, not information deficit, for cone fill.** The CNN's 0.337±0.109 on radius-two cone fill (line 334) — with 30% relative seed spread — is the signature of optimization instability on a conditional, heteroscedastic target (targets set to 0 when no pair survives, lines 713–716), not necessarily of missing information in the representation. A two-stage (classify-survival-then-regress) head is the standard fix and was not tried; the "direct estimators fall far short" narrative absorbs what may be a loss-design artifact.
4. **Unconstrained/modestly larger CNN at matched budget** (the M6 control): at ~22 min/seed, this is the cheapest experiment that could falsify the capacity/constraint explanation for the matched-regime gap.
5. **Test-time adaptation of the frozen CNN** (entropy minimization or batch-norm recalibration on degraded inputs) is a zero-retraining alternative that competes directly with the "frozen network degrades more gracefully" narrative and was not considered.

### Missing Stakeholder Perspectives

*(Named only; elaboration is R3's remit.)*

- The amortized-inference / simulation-based-inference community, whose term and framing the paper borrows and whose benchmark practice it corrects, uncited.
- Designers of existing ML-for-dynamical-systems benchmarks (learned Lyapunov/chaos-classification/surrogate tasks) — the addressees of the "general lesson".
- Experimentalists with real spatiotemporal data (excitable media, biological pattern formation), for whom every load-bearing assumption of the matched observation model fails simultaneously rather than one axis at a time.
- The stochastic/asynchronous-CA and statistical-mechanics damage-spreading communities, for whom "damage response" has a decades-old meaning in systems where the generator is *not* encoded in the observation.

### Unexamined Premise (Frame-Lock Detection)

The entire benchmark presumes that "behaviour worth predicting" is exhausted by statistics *defined as short simulations under the fixed protocol*. Any target so defined is computable by simulation once the rule is known — so the deck is stacked: within this target family, "simulation-limited" is the only possible verdict for a successful identifier, and amortization can compete only on cost or robustness, never on accuracy. The paper discovers this in §V.F ("the network's case must rest on degraded-observation regimes ... or on extreme-throughput screening, not on accuracy", lines 557–560) but never confronts it as a design premise: phenotype descriptors *not* expressible as cheap protocol re-runs (long-horizon particle censuses, computational-capability measures — which the paper explicitly declines to validate, lines 595–598) are exactly the targets on which the ordering could differ, and they are absent from the benchmark by construction.

### Observations (Non-Defects)

- The ICC vs. $2\,\mathrm{ICC}-1$ distinction (lines 169–194) is correct, cleanly derived, and is the paper's most exportable single contribution; the $16\times$ reference simulation closing the loop (lines 277–280) is exactly the right verification.
- The leakage surface appears genuinely engineered away: identity-keyed target streams with prime seed offsets, force-held complex panel, orbit deduplication, non-power-of-two ring (lines 670–675, 696–706). I looked for a contamination path and did not find one.
- The disclosed registration deviation (panel-position seeding bug, lines 687–691) and the honest inconclusive/underpowered verdicts (ECA panel, lines 362–365; phenotype-map advantage, lines 571–578) are the opposite of spin and should be credited.
- The "deliberately constrained" CNN is not deception: the constraint is disclosed in the abstract itself (line 55–56) and its failure to prevent rule decoding is reported and the original claim retired (line 427). The defect is the missing control (M6), not concealment.
- Table I's four-target medians look like smoothing, but the paper keeps its promise (lines 246–247) that per-target tables with CIs carry every claim; I verified the medians against Tables II–III and they are consistent.
- Reporting the mechanistic estimator as carrying "a weak, testable prior — not as assumption-free" (lines 349–350), and quantifying the known-radius assumption's cost (~0.12 R², lines 512–514), pre-empts two attacks I would otherwise have made.

### Rubric Dimension Scores (adversarial-but-honest)

| Dimension | Weight | Score | Rationale (band per quality_rubrics.md) |
|---|---|---|---|
| Originality | 0.20 | 66 | Adequate band: the ceiling bookkeeping and identifiability frontier are novel in framing; the core result formalizes a folklore fact (the rule is in the diagram) already published for this system class (line 82–84). |
| Methodological Rigor | 0.25 | 72 | Adequate-high: exemplary hygiene and uncertainty reporting, offset by missing fairness controls (M1, M6), the stacking reconciliation gap (M2), unmeasured CNN split variance, and registration bookkeeping (M3). |
| Evidence Sufficiency | 0.25 | 74 | Internal evidence for internal claims is strong (per-target CIs everywhere); the one uncited load-bearing external premise (M4) and n=3 landscape validation cap it. Source-count bands not applied mechanically — internal-measurement paper (field-norm gate, #215). |
| Argument Coherence | 0.15 | 62 | Adequate band: tight chains in the body, but two conclusions-level contradictions (C1) and a frame-lock premise surfaced only at §V.F (M5). |
| Writing Quality | 0.15 | 80 | Strong band: precise, dense, well-structured; abstract over-compressed, minor typographical residue. |
| **Weighted average** | | **71.0** | |

Reconciliation note: 71.0 falls in the rubric's minor-revision band, but per the sprint contract the failure conditions are the sole authority for the editorial decision, and F1 fired on D3. A paper can be aggregate-good and still carry an abstract that misleads; that is precisely this case.

### Recommendation

**Major Revision.** Confidence: **4/5** (full source read and cross-checked internally; compiled figures judged from captions only; repository numbers not independently re-run). The CRITICAL issue is a localized rewrite (abstract + one Discussion sentence brought into line with §V.E); the MAJOR issues need two cheap experiments (unconstrained CNN; degradation-augmented CNN), one reconciliation (stacking bases), one bookkeeping pass (App. A), one citation pass (the benchmark antagonist), and one framing paragraph (the simulation-defined-targets corollary, moved to the Introduction). All are feasible in one cycle; none threatens the core measurements, which I probed and could not break.

## Editorial Decision

F1 fired (D3 block, severity 90) → contract action `reject_or_major_revision`, resolved to **Major Revision**: the misleading statements are conclusions-level and localized, the underlying measurements are sound, and every listed issue is addressable in a single revision cycle.
