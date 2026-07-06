> **SIMULATED REVIEW** — ARS panel, 2026-07-05, EIC perspective. Not a real referee report.

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** For a benchmark-style submission to *Chaos* whose title promises "simulation-limited prediction" of a finite-horizon damage response, methodological rigor means the experimental protocol (rule sets, initial conditions, horizons, train/test discipline) is fully specified and defensible, statistical reporting meets the nonlinear-dynamics community's bar (uncertainty, replication, held-out evaluation), and reproducibility affordances (code/data availability, any pre-commitment claims) are concrete. As EIC I check whether the design can support the headline claim at all; the deep statistical audit belongs to Reviewer 1.

**D2 — domain_accuracy (mandatory).** Claims must align with what is established about cellular-automaton dynamics — damage spreading, classification subtleties, finite-size caveats — and prior work in both the CA and the ML-for-dynamical-systems traditions must be represented without distortion. Factual errors in domain terminology, or a misattributed prior result that the argument leans on, would violate this dimension. I check headline-level accuracy; exhaustive CA-literature coverage is Reviewer 2's job.

**D3 — argumentative_coherence (mandatory).** The central thesis announced by the title — rule reconstruction from a single space–time diagram yields prediction limited only by simulation — must be internally consistent: "simulation-limited" must be defined and demonstrated rather than asserted; the abstract's promises must be traceable to specific results; any comparative claims about learned methods must actually follow from the evidence; no circularity (e.g., a performance ceiling defined by the very method being evaluated).

**D4 — cross_disciplinary_relevance (high).** *Chaos* serves a readership spanning physics, applied mathematics, and increasingly machine learning. A paper at the CA × ML-benchmark interface must be legible on both sides: ML concepts defined for dynamicists, CA concepts defined for ML readers, and the interdisciplinary lesson stated in a form that plausibly generalizes beyond the specific model class — with that generalization substantiated, not merely gestured at.

**D5 — writing_and_structure (normal).** A ~8,500-word, 9-page two-column REVTeX article for *Chaos* must follow the venue's conventions (including its distinctive front-matter expectations), have a title and abstract that accurately scope the contribution, figures that carry the argument, and prose economy. The long descriptive title is itself a signal to check: does the paper's organization deliver on each clause of that title without bloat?

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: complete protocol specification (rule spaces, initial-condition measure, lattice, horizon); replication/seed counts; uncertainty quantification on the headline comparisons; genuine out-of-sample discipline; a concrete code/data statement.
- `what_triggers_block`: the headline comparison is confounded (baselines tuned on test material, no held-out rules) or "simulation-limited" is claimed with no quantitative ceiling reference to compare against.
- `what_triggers_warn`: incomplete reporting on key comparisons (missing seeds/intervals), or a reproducibility statement too vague to act on.

### D2: domain_accuracy
- `what_to_look_for`: correct use of damage-spreading / classification / finite-horizon concepts; fair characterization of prior CA-identification and ML-for-dynamics work; no overstated priority claims.
- `what_triggers_block`: a factual error in a core domain claim, or a misrepresented prior result the argument depends on.
- `what_triggers_warn`: imprecise terminology, or missing caveats (finite size, measure dependence, undecidability) that a *Chaos* referee would demand.

### D3: argumentative_coherence
- `what_to_look_for`: abstract claims traceable to specific results; key terms ("simulation-limited", "damage response") fixed early and used consistently; comparisons that actually test the stated thesis; hedges present where evidence is weak, in the main text and not only in a limitations paragraph.
- `what_triggers_block`: the abstract promises more than the results deliver, or the performance ceiling is defined circularly by the evaluated method itself.
- `what_triggers_warn`: scope drift between sections, or conclusions stated more strongly than the section-level evidence.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: framing accessible to both dynamics and ML readers; explicit statement of what generalizes beyond the studied model class; benchmark artifacts (metrics, protocol, decision rules) reusable by others.
- `what_triggers_block`: the paper is readable only by one sub-community, or the interdisciplinary lesson is asserted with no support at all.
- `what_triggers_warn`: jargon-heavy passages that lock out one readership, or generalization claims that are hedged but not connected to the adjacent literature that would substantiate them.

### D5: writing_and_structure
- `what_to_look_for`: REVTeX/*Chaos* conventions (including front matter), figure quality and self-containedness, logical section flow, title/abstract alignment with content, length discipline.
- `what_triggers_block`: organization so disordered that the contribution cannot be assessed.
- `what_triggers_warn`: overlong or overloaded exposition (abstract, wall-of-text sections), figures or captions not interpretable standalone, venue-convention gaps.

[CONTRACT-ACKNOWLEDGED]

## Dimension Scores

### D1 — methodology_rigor: **pass**
The design directly supports the headline claim: decision rules, margins, and panels are committed in advance and every analysis is labelled *registered / post-hoc confirmatory / exploratory* (main.tex lines 128–131, 678–691, including a disclosed registration deviation at lines 687–691); the "simulation-limited" ceiling is defined non-circularly from 20 independent target replicates and verified against a 16×-larger reference simulation (lines 178–199, 276–280). Rule-level bootstrap intervals, TOST margins with sensitivity analysis, and per-target reporting (lines 245–259, 742–746) clear the EIC-level bar; residual items (CNN not retrained across splits, line 256; no concrete repository URL/DOI yet) are disclosed and minor.

### D2 — domain_accuracy: **pass**
The domain framing is unusually careful: class membership undecidability and measure dependence are cited and taken seriously (lines 86–91), all claims are indexed to an explicit protocol tuple (lines 147–153, 649–652), and the authors even retire one of their own prior claims when the probes contradict it (lines 428–429, "we retired that claim"). I found no factual error or misrepresented prior result; the thin engagement with the ML-for-dynamics literature is an omission, not a distortion, and is scored under D4.

### D3 — argumentative_coherence: **pass**
The three organizing results announced in the introduction (lines 109–126) map one-to-one onto Secs. IV.A, IV.B–D, and IV.E, and the abstract's quantitative promises (100%/97.5% reconstruction, survival 0.985 vs 0.987, +0.32 stacking increment, ~2% noise threshold) all appear with intervals in the results tables. The paper's most conflation-prone move — distinguishing the replicate-agreement benchmark (2·ICC−1) from the ICC ceiling (lines 169–194) — is exactly the kind of coherence discipline this thesis requires, and verdict labels ("superiority", "equivalence", "inconclusive") are used only where earned (lines 248–252, 571–578).

### D4 — cross_disciplinary_relevance: **warn**
The framing is genuinely bilingual (shortcut learning cited for ML readers at line 84, amortization defined for dynamicists at lines 98–101), but the paper's self-declared "general lesson for machine-learning benchmarks on deterministic dynamical systems" (lines 62–64, 625–630) is never connected to the literature that lesson addresses: the ~13-entry bibliography contains no sparse/symbolic system identification (SINDy and successors), no reservoir-computing or neural-operator surrogate benchmarking — the very *Chaos*-core communities for whom "system identification is the baseline to beat" is actionable. This matches my pre-committed warn trigger: a generalization claim hedged but not connected to the adjacent literature that would substantiate it.

### D5 — writing_and_structure: **warn**
The prose is precise but overloaded in places: the abstract runs to roughly 370 words in a single paragraph carrying every result including by-products (lines 30–65), the manuscript lacks the non-technical lead paragraph *Chaos* requires between abstract and introduction, Sec. IV.E's "Estimators for the degraded regime" is one ~45-line paragraph introducing two new estimators and three registered hypotheses (lines 494–538), and front matter still carries author-block TODOs (lines 19, 21) with no Acknowledgments / Author Declarations / Data Availability sections. None of this obscures the contribution (so no block), but it is squarely my pre-committed warn pattern.

## Failure Condition Checks

- **F1** (any mandatory dimension scores 'block'): D1 = pass, D2 = pass, D3 = pass → **fired: false**
- **F2** (two or more mandatory dimensions score 'warn' or worse): zero mandatory dimensions at warn or worse → **fired: false**
- **F3** (any high-priority dimension scores 'block'): D4 = warn, not block → **fired: false**
- **F0** (every mandatory dimension scores 'pass'): D1, D2, D3 all pass → **fired: true** (action: editorial_decision = accept)

## Review Body

# Peer Review Report

## Manuscript Information
- **Title**: Rule reconstruction from a single space–time diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata
- **Manuscript ID**: n/a (simulated panel)
- **Review Date**: 2026-07-05
- **Review Round**: Round 3 (revised draft, round-3-ready)

---

## Reviewer Information

### Reviewer Role
EIC (Editor-in-Chief perspective)

### Reviewer Identity
Senior editor at *Chaos: An Interdisciplinary Journal of Nonlinear Science* (AIP); 20+ years in nonlinear dynamics and complex systems; has handled the recent wave of machine-learning-for-dynamical-systems submissions and is wary of both ML hype and reflexive ML dismissal.

### Review Focus
(1) Journal fit and interest to the *Chaos* readership; (2) originality and significance of the "system identification is the baseline to beat" lesson; (3) whether claims and framing match what the abstract promises; (4) whether a benchmark paper — as opposed to a new-phenomenon paper — carries its weight for this venue. Methodological statistics are Reviewer 1's beat and CA-literature completeness is Reviewer 2's; I touch both only at headline level.

---

## Overall Assessment

### Recommendation
- [ ] **Accept**
- [x] **Minor Revision** — Minor revisions needed, no re-review after revision
- [ ] **Major Revision**
- [ ] **Reject**

### Confidence Score
4 — Mostly within my area of expertise (nonlinear dynamics, complex systems, editorial handling of ML-for-dynamics benchmarks); the fine details of the Bayesian rule-posterior estimator sit slightly outside it.

### Summary Assessment

This paper benchmarks three estimator families for predicting four finite-horizon damage-response statistics of cellular automata from a single space–time diagram, and shows that under the standard fully-observed noiseless observation model the transparent route — reconstruct the rule table, re-run the perturbation experiment — is statistically indistinguishable from re-measuring the ground truth, while two direct learned estimators fall well short. The execution is exemplary in claim discipline: pre-committed decision rules with registered/post-hoc/exploratory labels, a genuinely important distinction between the replicate-agreement benchmark (2·ICC−1) and the latent ICC ceiling, and an identifiability phase diagram that maps where the winning method fails rather than declaring victory and stopping. The stacking result (+0.32 incremental R² on damage survival) keeps the paper honest toward machine learning rather than triumphalist against it. The chief weakness, from an editorial standpoint, is positioning: the "system identification is the baseline to beat" lesson is aimed at exactly the ML-for-dynamical-systems communities *Chaos* serves, yet the ~13-entry bibliography never connects to sparse system identification, reservoir computing, or surrogate-model benchmarking. Secondary issues are venue-compliance ones: an overlong abstract, no *Chaos* lead paragraph, incomplete front/back matter. All are addressable in weeks without re-review; I recommend Minor Revision.

---

## Strengths

### S1: Exemplary claim discipline and registration transparency
The manuscript labels every analysis as *registered*, *post-hoc confirmatory*, or *exploratory* (main.tex lines 678–689), explains why it does not simply say "pre-registered" (an in-review private repository is not independently auditable, lines 676–679), and discloses a registration deviation together with its verified resolution (lines 687–691). For a benchmark paper — a genre prone to silent researcher degrees of freedom — this is the standard I wish more submissions met.

### S2: The three-benchmark reliability disambiguation is an exportable methodological contribution
Sec. II.C (lines 169–203) cleanly separates the latent ICC ceiling, the independent-replicate agreement benchmark (2·ICC−1), and a large-simulation reference, and proves the choice matters ("conflating the cases overstates or understates a method by several times the margins at stake", lines 172–174). This distinction applies verbatim to any surrogate-model benchmark against Monte-Carlo-estimated targets — reservoir computing, neural operators, agent-based models — and is, for the *Chaos* readership, arguably as valuable as the CA-specific results.

### S3: The identifiability phase diagram turns a negative-result benchmark into a constructive scope map
Rather than crowning the mechanistic estimator and stopping, Sec. IV.E (lines 434–538) sweeps observation noise, masking, rows observed, and IC density; identifies the ~2–5% noise collapse of exact reconstruction; and benchmarks the natural repairs (Bayesian rule-posterior, learned rule-reader) in the degraded regime. Figure 2's framing of these curves as "the paper's scope statement in graphical form" (lines 533–534) is exactly what makes a benchmark paper carry its weight at this venue.

### S4: Balanced, scoped treatment of the learned methods
The neural claims are explicitly bounded to "this architecture under this training budget" (lines 238–241), the cross-fitted stacking test grants the network a real, quantified edge on damage survival (+0.32, lines 377–384), and the discussion states plainly "We do not conclude that deep networks cannot close the gap" (line 638). This forestalls the strawman reading — "ML loses" — that sinks many benchmark submissions.

### S5: By-products reported at the strength their validation supports
The composed-system phenotype map is reported as *inconclusive* under the registered framework despite a positive point estimate (lines 570–578), and the 7.8% damage-signature band is explicitly not promoted to a "validated glider census" because the only independent detector is itself shown to be unreliable (lines 588–598). Conservative language backed by measurement of the instrument's own failure modes is rare and welcome.

---

## Weaknesses

### W1: The paper's general lesson is never connected to the ML-for-dynamical-systems literature it addresses
**Problem**: The abstract and discussion claim a "general lesson for machine-learning benchmarks on deterministic dynamical systems" (lines 62–64) and address "benchmark designers who intend to test representation learning" (lines 628–630), yet the bibliography (~13 entries, refs.bib via line 772) contains no sparse/symbolic system identification (SINDy lineage), no reservoir-computing or Koopman/neural-operator surrogate work, and no prior benchmark-design critique beyond shortcut learning.
**Why it matters**: *Chaos* readers who benchmark learned surrogates on Lorenz, Kuramoto–Sivashinsky, etc. are the audience for this lesson; without a bridge, they cannot tell whether the CA case is special (the observation literally contains the finite rule table) or representative. It also leaves the lesson's novelty unpositioned — model-recovery baselines are an existing practice in continuous-time system identification.
**Suggestion**: Add one paragraph to the Introduction or Discussion and ~8–12 references situating the result relative to sparse regression system identification, reservoir-computing prediction benchmarks, and surrogate-vs-simulator comparisons, and state precisely which structural condition ("the observation encodes the generator" over a finite model class) does or does not hold in those settings.
**Severity**: Major

### W2: Abstract overlong and overloaded; missing the *Chaos* lead paragraph
**Problem**: The abstract (lines 30–65) runs to roughly 370 words in one paragraph and carries every result, including both descriptive by-products and the ICC/2·ICC−1 technicality; the manuscript has no non-technical lead paragraph, which *Chaos* requires between abstract and Sec. I.
**Why it matters**: The abstract is the readership filter; at this density the central finding is buried, and non-compliance with the venue's signature front-matter element would bounce at the editorial office regardless of scientific merit.
**Suggestion**: Cut the abstract to ≤250 words around the three organizing results (identification solved; direct estimators short of benchmark; phase diagram of failure), moving by-products to a single clause; add a ~100–150-word lead paragraph in plain language.
**Severity**: Major (venue compliance; mechanically easy)

### W3: Sec. IV.E's degraded-regime material — the paper's most novel content — is structurally underserved
**Problem**: "Estimators for the degraded regime" is a single ~45-line paragraph (lines 494–538) introducing two new estimators, quantifying a known-radius ablation, and adjudicating three registered hypotheses, with key numbers embedded mid-sentence.
**Why it matters**: This is where the paper moves beyond "the inverter wins" to genuinely new territory (the Bayesian posterior's 40–50% masking tolerance; the sampled rule-reader as the only survivor beyond 5% noise); readers skimming for the frontier result will lose it in the wall of text.
**Suggestion**: Promote to its own subsection with sub-paragraphs per estimator, and add a small table (axis × best estimator × median R²) summarizing Fig. 2.
**Severity**: Minor

### W4: Front/back matter incomplete for AIP production, and the data-availability commitment lacks a concrete pointer
**Problem**: Author-block TODOs remain (lines 19, 21: ORCIDs, corresponding address); there are no Acknowledgments, Author Declarations (conflict of interest), or Data Availability sections; the repository is "released with the article" (lines 130–131, 679–680) but no URL, DOI, or archive is named.
**Why it matters**: AIP requires the declarations and data-availability statements; more substantively, the paper's registration-based credibility (S1) ultimately rests on the repository history being auditable, so the pointer is load-bearing, not cosmetic.
**Suggestion**: Complete the author metadata; add the three AIP-required statements; deposit the repository (with timestamped history) at a DOI-issuing archive (e.g., Zenodo) and cite it.
**Severity**: Minor (but blocking for production)

### W5: Stale/orphaned figure assets and figure–text terminology drift
**Problem**: `manuscript/figures/map_benchmark.pdf` exists but is never referenced in main.tex; `make_figures.py` (lines 33, 69) labels the landscape's red set "complex" and titles the map figure "the learned map has no advantage" — both contradicting the manuscript's current, carefully conservative language ("damage-signature criterion", lines 606–609; "small, statistically unresolved edge for the learned map", lines 577–578).
**Why it matters**: If these assets ship as supplementary material or are regenerated by a reader, they will assert claims the text deliberately retired — undermining exactly the claim discipline the paper is built on.
**Suggestion**: Regenerate or remove the orphaned figure; align script labels/titles with the manuscript's registered terminology; verify the shipped landscape.pdf legend says "damage-signature" rather than "complex".
**Severity**: Minor

---

## Detailed Comments

### Title & Abstract
The 24-word title is accurate but dense, and it undersells the paper's *Chaos*-relevant hook (the general benchmark lesson) in favor of the CA-specific finding; a shorter main title with the specifics demoted to the abstract would serve the readership better. Abstract: see W2 — accurate, traceable, but far too long and carrying the ICC technicality that belongs in Sec. II.C.

### Introduction
Strong. The genotype/phenotype framing (lines 75–84), the undecidability/measure-dependence grounding for the protocol-tuple stance (lines 86–96), and the three-results roadmap (lines 109–126) give both readerships what they need. The shortcut-learning citation (line 84) is the right bridge for ML readers; the missing bridge is the reverse one (W1).

### Literature Review / Theoretical Framework
Deferring completeness to Reviewer 2, but at editorial altitude: ~13 references is thin for a journal article making a field-level methodological claim, and the omission is systematic (all of ML-for-dynamics; W1). The CA-side citations that are present (damage spreading, classification) appear apt and are not misused.

### Methodology / Research Design
Reviewer 1's beat; from the bird's-eye view the design is coherent and the anti-conflation machinery (Sec. II.C) is a contribution in itself. Two items R1 should weigh: the CNN is evaluated only at the registered split with five seeds, with cross-split retraining explicitly not performed (lines 255–257 — disclosed, but it bounds the strength of the "no stable ordering" conclusion); and the compute comparison (Sec. IV.F) times the CNN on a Metal GPU against the mechanistic estimator on a single CPU core (lines 547–549), so the 4,700-query break-even is not hardware-matched.

### Results / Findings
The tables carry the argument well: headline medians (Table I) always accompanied by per-target intervals (Tables II–III), with the shortfall correctly localized to damage survival, "the least texture-like and least reliable target" (lines 320–321). The refusal to read a ranking into the underpowered ECA panel (lines 363–366) is exactly right. Sec. IV.E is the most original section and needs the structural help described in W3. Figure captions are self-contained; the Fig. 2 caption's "Registered numbers-free as rev.~9" (line 489) and the bracketed "[registered, rev.~8]" tags throughout are internal registration jargon an outside reader cannot decode — define the labelling scheme once in Appendix A and reference it.

### Discussion
The central claim is stated at the right strength ("whenever the observation encodes the generator, system identification is the baseline to beat", lines 626–630) and the practical guidance with its price tag (lines 652–659) is genuinely useful. The open problems (rule-scrubbing/provision interventions, joint reader–simulator training, lines 645–647) are concrete rather than decorative.

### Conclusion
There is no separate conclusion section; the final discussion paragraph (lines 649–663) does that duty adequately for *Chaos* conventions, though a two-sentence closing restatement of the general lesson and its boundary would strengthen the landing.

### References
Well-chosen but sparse (W1); formatting via apsrev4-2 is appropriate. Ensure the self-citation (rollier2024cnn, line 83) survives any anonymization requirements, and add the repository DOI once deposited (W4).

---

## Questions for Authors

1. **Boundary of the general lesson.** For continuous-state or noisy dynamical systems — where the observation does not encode a finite generator exactly — which parts of your argument survive? Can you state, even informally, the conditions under which "system identification is the baseline to beat" transfers to the benchmarks *Chaos* readers actually run (e.g., learned surrogates for Lorenz or Kuramoto–Sivashinsky, where SINDy-style identification is the natural analogue)?
2. **Hardware-matched break-even.** The 4,700-query break-even compares a GPU forward pass against a single-CPU-core simulation (lines 547–556). What does the break-even become on matched hardware (both CPU, or the simulator parallelized on the same GPU), and does the "most accurate at every budget" conclusion change?
3. **Auditability of the registration labels.** The credibility of the registered/post-hoc/exploratory labels rests on the "timestamped private repository... released with the article" (lines 679–680). Will the release include the timestamped commit history at a DOI-issuing archive, and can the rev.~7/8/9 tags used in the text be mapped to specific commits in an appendix table?

---

## Minor Issues

### Language / Grammar
- Line 624: "positive, and--- we believe---generalizable" — stray space after the em-dash ("and--- we" should be "and---we").
- Lines 494–538: sentence length and em-dash nesting in Sec. IV.E occasionally require re-reading; see W3.

### Citation Format
- Bibliography of ~13 entries is unusually sparse for the venue (see W1); `kleinberg2002` and `mitchell1993` are cited only in a closing list (line 663) — make their relevance explicit or cut.

### Figures and Tables
- `map_benchmark.pdf` is orphaned; `make_figures.py` labels contradict the manuscript's current conservative terminology (W5).
- Fig. 2 caption: decode "Registered numbers-free as rev.~9" for outside readers.
- Table I caption: the complex-subset row's "no separate reliability panel was drawn" disclosure is good; consider adding the same flag as a table footnote marker on the "≈0.98" entry.

### Layout
- Author-block TODO comments (lines 19, 21) must be resolved; Acknowledgments, Author Declarations, and Data Availability sections must be added per AIP requirements; the *Chaos* lead paragraph is missing (W2).
- Colored hyperlinks (line 9) should be switched to the journal's production defaults at submission.

---

## Dimension Scores

| Dimension | Score (0–100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 76 | Strong | The lesson itself echoes known shortcut-learning/system-id folk wisdom, but the simulation-limited-vs-ICC formalization, the pre-registered benchmark design, and the identifiability phase diagram are novel, exportable contributions |
| Methodological Rigor (25%) | 87 | Strong | Registration discipline, reliability decomposition, cross-fitting, disclosed deviation; docked for CNN single-split evaluation and hardware-mismatched compute comparison (both disclosed) |
| Evidence Sufficiency (25%) | 80 | Strong | Experimental evidence is comprehensive (20 replicates, bootstrap CIs, 16× reference, counter-evidence acknowledged); literature base thin, limiting triangulation with prior findings |
| Argument Coherence (15%) | 90 | Exceptional | Thesis, evidence, and scope statements aligned throughout; counterarguments pre-empted; verdict labels used only where earned |
| Writing Quality (15%) | 74 | Adequate | Precise but dense; overlong abstract, wall-of-text Sec. IV.E, missing lead paragraph, incomplete front/back matter |
| Literature Integration (optional) | — | deferred | Reviewer 2's focus; flagged here only for the ML-for-dynamics gap (W1) |
| Significance & Impact (optional) | — | deferred | Reviewer 3's focus |
| **Weighted Average** | **81.6** | **Accept-boundary (per mapping); recommendation refined to Minor Revision** | 76·0.20 + 87·0.25 + 80·0.25 + 90·0.15 + 74·0.15 = 81.55; per quality_rubrics.md calibration notes, scores are ordinal reference — remaining items are mandatory pre-publication fixes but need no re-review |

### Recommendation to Peer Reviewers
Reviewer 1: please stress-test the reliability decomposition (heteroscedasticity handling, bootstrap validity at n=18 ECA orbits) and the single-registered-split CNN evaluation. Reviewer 2: CA-side literature is apt but sparse — please assess coverage of the damage-spreading and rule-inference lineages; I have separately flagged the missing ML-for-dynamics bridge. Reviewer 3: the generalization boundary of the central lesson (Question 1) is the highest-value target for your perspective.

## Editorial Decision

Accept-track per contract (only F0 fired — all mandatory dimensions pass, no failure condition mandates revision): operationalized as **Minor Revision without external re-review**, conditional on the positioning paragraph (W1), venue-compliance items (W2, W4), and figure-asset hygiene (W5).
