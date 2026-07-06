> **SIMULATED REVIEW** — ARS panel, 2026-07-05, Peer Reviewer 2 (Domain). Not a real referee report.

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** The study's design, data handling, statistical reporting, and reproducibility affordances must meet the peer-review bar of the field. For a paper claiming "rule reconstruction from a single space–time diagram" with "simulation-limited prediction" of a "finite-horizon damage response," this means the simulation protocol (initial conditions, lattice size, horizon, boundary conditions), the definition of the reconstruction task, and the prediction benchmark must be specified precisely enough to reproduce, and the claimed limits must be demonstrated rather than asserted. Per my panel role, I defer detailed ML-evaluation statistics to Reviewer 1 and assess D1 only where it touches domain-facing methodology: whether the CA simulation and damage-response measurement design are sound by the standards of the nonlinear-dynamics literature.

**D2 — domain_accuracy (mandatory).** Claims must align with current domain evidence; prior work must be correctly represented; there must be no factual errors in domain-specific terminology or results. This is my core dimension: for a cellular-automata paper the load-bearing objects are the Wolfram behavioural classes, any Li–Packard-style refinement or folding, rule equivalence classes (the 88 elementary orbits under reflection/complementation), damage-spreading and Lyapunov-style sensitivity definitions, and the combinatorics of the stated rule spaces (elementary radius-1 and any radius-2 space). Misstated class memberships, wrong orbit counts, incorrect damage-spreading formalism, or misattributed prior results would all count against D2, as would a bibliography so thin (13 references at ~8,500 words) that the paper's positioning misrepresents what the field already knows.

**D3 — argumentative_coherence (mandatory).** The core thesis — that reconstructing the rule from one diagram yields prediction of the damage response that is limited only by simulation (i.e., by re-running the reconstructed rule), over a finite horizon — must be internally consistent, with evidence actually supporting each link: reconstruction accuracy → simulation fidelity → damage-response prediction. Fallacies that would undermine it include equivocation between identifying the rule and predicting behaviour, silent generalization from the finite protocol to "the rule" in the abstract, or circularity between how the benchmark is defined and how success is measured.

**D4 — cross_disciplinary_relevance (high priority).** The paper straddles nonlinear dynamics/complex systems and ML benchmark methodology and targets Chaos. Framing and definitions must be readable by both audiences: a dynamical-systems reader should be able to follow the ML benchmark construction, and an ML reader should not be misled about CA-theoretic facts. Interdisciplinary claims (e.g., about what ML benchmarks should learn from CA identifiability) must be substantiated, not gestured at.

**D5 — writing_and_structure (normal priority).** Organisation, clarity of exposition, figure/table quality, and adherence to venue conventions (REVTeX two-column, ~9 pp, Chaos-style sectioning and abstract) must support rather than obstruct the argument. As the domain reviewer I weight this lowest, flagging only structural or expository problems that materially impede a domain reader.

## Scoring Plan

- **dimension_id: D1**
  - *what_to_look_for:* Precise specification of the simulation protocol (IC distribution, ring size, horizon, boundary conditions, number of samples); a well-defined reconstruction procedure from a single diagram; a damage-response observable defined operationally; evidence that the "simulation limit" is measured against a stated reference (e.g., ground-truth rule re-simulation); enough detail (seeds, code availability) to reproduce.
  - *what_triggers_block:* The central benchmark or damage observable is not defined precisely enough to reproduce, or the "simulation-limited" claim is asserted without any ground-truth-simulation comparison.
  - *what_triggers_warn:* Protocol parameters scattered or partially implicit; single-seed or single-configuration results where the domain expects ensemble statements; reproducibility affordances present but incomplete.

- **dimension_id: D2**
  - *what_to_look_for:* Correct statements about Wolfram's four classes and their heuristic status; correct handling of Li–Packard categories and any folding into coarser classes; correct count and use of the 88 elementary equivalence classes (orbits under reflection + complementation); standard damage-spreading/Hamming-distance definitions consistent with the Lyapunov-for-CA literature; correct size and construction of the radius-2 rule space; a bibliography that actually covers damage spreading, CA rule identification/inverse problems, and classification-scheme literature.
  - *what_triggers_block:* A factual domain error that a central claim rests on (wrong orbit structure, misdefined damage spreading, misstated class membership used as ground truth), or misrepresentation of a cited prior result.
  - *what_triggers_warn:* Claims correct but positioned against a materially incomplete literature (13 refs plausibly omits whole relevant lineages); imprecise terminology that could mislead but does not invalidate results; borderline class assignments stated without caveat.

- **dimension_id: D3**
  - *what_to_look_for:* A clean inferential chain from single-diagram reconstruction to damage-response prediction; explicit scoping to the finite protocol (measure on ICs, finite ring, finite horizon); consistency between abstract/title claims and what the experiments show; honest treatment of failure cases (non-identifiable rules, chaotic rules where damage saturates).
  - *what_triggers_block:* Title/abstract claim contradicted or unsupported by the body (e.g., "simulation-limited" claimed while reconstruction demonstrably fails on a class of rules without acknowledgement), or a circular benchmark definition.
  - *what_triggers_warn:* Overreach in isolated sentences (finite-protocol results phrased as rule-general truths); caveats present but buried; minor inconsistencies between sections.

- **dimension_id: D4**
  - *what_to_look_for:* Definitions of CA concepts self-contained for Chaos's mixed readership; ML benchmark machinery (training/evaluation splits, baselines) explained without assuming ML-venue background; the interdisciplinary payoff (what each community learns) stated and supported.
  - *what_triggers_block:* The paper is unreadable for one of its two claimed audiences to the point that its interdisciplinary claim collapses, or an interdisciplinary claim is factually wrong for one of the fields.
  - *what_triggers_warn:* Jargon from either side used without definition; the "benchmark methodology" payoff asserted but not argued; adjacent-field reader must consult external sources for load-bearing definitions.

- **dimension_id: D5**
  - *what_to_look_for:* Logical section flow (intro → definitions → benchmark → results → by-products → discussion); figures/tables legible and actually referenced; venue-appropriate length and style; consistent notation.
  - *what_triggers_block:* Structure so disorganised that the argument cannot be followed, or figures essential to claims missing/unintelligible.
  - *what_triggers_warn:* Notation drift, overlong or under-signposted sections, figure/caption mismatches, non-standard REVTeX usage that a copy-edit would not fix trivially.

## Dimension Scores

### D1 — methodology_rigor: **pass**

The protocol is fully and precisely specified (Bernoulli(1/2) ICs, ring 127, horizon ⌊w/(2r)⌋−1 with the no-wrap argument, main.tex lines 146–153; exact target formulas, lines 708–716), the "simulation-limited" claim is measured against an explicit independent-replicate reference and further against a 16×-larger simulation (lines 178–194, 277–280), and seeds/streams/splits are documented with a disclosed deviation (Appendix A, lines 667–691). Nothing in the domain-facing design meets my warn triggers.

### D2 — domain_accuracy: **warn**

The domain facts the paper states are, to my checking, correct (88 orbits, line 138–140; 2^32 radius-2 space, lines 140–143; rule-90 collapse on power-of-two rings, lines 147–149; undecidability and measure dependence, lines 86–91; damage-cone normalisation, lines 160–163), but my committed warn trigger fires: 13 references omit three whole lineages the paper's central claims sit inside — CA identification/inverse problems (Richards–Meyer–Packard 1990; Adamatzky 1994; Billings & Yang 2000), the damage-spreading/Lyapunov-for-CA lineage (Bagnoli–Rechtman–Ruffo 1992; Baetens & De Baets 2010), and structure-detection/classification prior art (Wolfram 1984; Hanson–Crutchfield; Shalizi et al. 2006; Zenil 2010) — plus the uncited "documented borderline rule 106" claim (line 591).

### D3 — argumentative_coherence: **warn**

The main inferential chain (reconstruction → re-simulation → replicate-level agreement) is clean and honestly scoped, but my committed warn trigger fires on isolated overreach and minor cross-section inconsistency: "a single space–time diagram identifies the local rule almost surely" (line 622) is not what 97.5% at radius two supports; "can be solved by system identification whenever the observation encodes the generator" (lines 625–627) generalizes beyond the one system class studied (hedged, but stated as the central lesson); Fig. 1's caption says 80 held-out rules (line 447) where the text and Table III say 160 (line 337) without the subsetting being explained; and the Discussion's "independently validated artefacts" (line 662) is stronger than Sec. IV G's own verdict on the radius-two landscape (detector "barely better than chance", lines 594–596).

### D4 — cross_disciplinary_relevance: **pass**

CA concepts (orbits, damage spreading, protocol tuple) are defined self-contained for the ML-side reader (lines 86–96, 136–167), the benchmark machinery (superiority/equivalence/inconclusive verdicts, stacking) is defined in-line for the dynamics reader (lines 245–259), and the interdisciplinary payoff is explicitly argued rather than gestured at (lines 619–630). No warn trigger fires; a few statistical terms (TOST, cross-fitting) could use one clause more each, noted under Minor Issues.

### D5 — writing_and_structure: **pass**

The section flow (benchmark → estimators → results → failure surface → cost → by-products → discussion) is logical, all tables and figures are referenced and interpreted, and REVTeX/Chaos conventions are followed. Density of the abstract and the leaking of internal registration jargon ("[registered, rev. 8]") are copy-edit-level, not structural.

## Failure Condition Checks

Evaluated from my own dimension scores (D1 pass, D2 warn, D3 warn, D4 pass, D5 pass) per the contract expressions:

- **F1** (severity 90) — "any mandatory dimension scores 'block'": **fired: false** (no blocks).
- **F2** (severity 70) — "two or more mandatory dimensions score 'warn' or worse": **fired: true** (D2 warn, D3 warn) → action: editorial_decision = major_revision.
- **F3** (severity 60) — "any high-priority dimension scores 'block'": **fired: false** (D4 pass).
- **F0** (severity 10) — "every mandatory dimension scores 'pass'": **fired: false**.

Highest-severity fired condition: **F2 → major_revision**.

## Review Body

# Peer Review Report

## Manuscript Information
- **Title**: Rule reconstruction from a single space–time diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata
- **Manuscript ID**: n/a (simulated panel)
- **Review Date**: 2026-07-05
- **Review Round**: Round 3 (revised draft)

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 2 (Domain)

### Reviewer Identity
Cellular-automata theorist in the Wolfram/Li–Packard lineage; damage spreading and Lyapunov exponents for CA, rule equivalence classes, undecidability of classification; CA identifiability and inverse-problem literature.

### Review Focus
(1) Domain accuracy: Wolfram classes, Li–Packard folding, the 88 elementary orbits, damage-spreading definitions, the radius-2 rule space. (2) Literature coverage and positioning, given a 13-reference bibliography. (3) Protocol-tuple caveats: measure dependence, finite ring, horizon, boundary conditions. ML-evaluation statistics are Reviewer 1's remit; journal fit is the EIC's.

---

## Overall Assessment

### Recommendation
- [ ] Accept
- [ ] Minor Revision
- [x] **Major Revision** — Substantial revisions needed, re-review required after revision
- [ ] Reject

### Confidence Score
**5** — Completely within my area of expertise.

### Summary Assessment

The paper benchmarks estimators of finite-horizon damage-response statistics of cellular automata from a single space–time diagram, over the 88 elementary orbits and 800 sampled radius-2 rules, and shows that under a matched observation model, exact rule reconstruction followed by re-simulation predicts all four statistics at the accuracy of an independent Monte-Carlo replicate — then maps where that route collapses (noise, masking, extreme IC densities). The domain content is technically excellent: the protocol tuple is exactly the right object given undecidability and measure dependence, the damage-response formalism is correct, the reliability-benchmark separation is a genuine contribution, and the by-products are described with unusual restraint. The critical weakness is positioning: the bibliography (13 entries) omits the CA identification/inverse-problem literature that the title claim lives inside (Richards–Meyer–Packard 1990; Adamatzky 1994; Billings & Yang 2000), credits damage spreading only through the group's own 2022/2024 papers rather than its Kauffman/Derrida/Bagnoli lineage, and misses direct prior art for both by-products (Shalizi et al. 2006; Zenil 2010; Boccara et al. 1991). The Introduction's "first result" framing must be rewritten against this prior art; a few scope-language slips ("almost surely", "whenever") need repair. Because the fix requires repositioning the contribution, not merely appending citations, I recommend Major Revision.

---

## Strengths

### S1: The problem formalization is exactly right, and the domain facts check out
The protocol-tuple framing (lines 86–96) — undecidability via Culik–Yu, measure dependence via Gilman, statistics-not-invariants — is the correct response to the classification literature's known pathologies, and it is carried through consistently. Every checkable domain fact is correct: 88 orbit representatives under reflection+complementation (lines 138–140), the 2^32 radius-2 space with order-four orbit deduplication (lines 140–143, 697–698), the non-power-of-two ring guarding against additive-rule collapse (lines 147–149; rule 90's nilpotency on 2^k rings is a real and frequently missed trap), and the no-wrap horizon ⌊w/(2r)⌋−1 (lines 150–151).

### S2: The three-way reliability separation is a methodological contribution to damage-spreading practice
Sec. II C (lines 169–203) distinguishing the ICC attenuation ceiling, independent-replicate agreement (2·ICC−1), and a large-simulation reference — and verifying the mechanistic estimator rises to the ICC ceiling against the 16× reference (lines 277–280) — is careful in a way the damage-spreading literature usually is not. Monte-Carlo-limited target caches are endemic in this field; this section deserves to be cited independently of the paper's main claim.

### S3: The identifiability phase diagram is the honest scope statement most papers omit
Sec. IV E (lines 434–538) maps the failure surface of the paper's own preferred method, including the cost of the known-radius assumption (~0.12 median R², lines 512–514), the exact polarity invariance of read-then-simulate, and the MAP-vs-sampled rule-reader contrast ("a single mostly-right table is a badly wrong dynamical system", lines 520–522 — a genuinely instructive observation about deterministic tables having no noise model).

### S4: The by-products are stated at the strength their validation supports
Sec. IV G (lines 562–598) refuses to promote the 7.8% damage-signature band to a "glider census", validates the signature on ECA against the literature class-IV set with explicit sensitivity/precision/borderline handling (rule 106 flagged as the false positive), reports the independent detector's own unreliability (sensitivity 0.5, missing rule 54's light-speed ether front), and gives the phenotype-map comparison an honest "inconclusive" verdict (lines 570–579).

### S5: Registration and disclosure discipline
Appendix A (lines 667–691) labels every analysis registered/post-hoc/exploratory, refuses to lean on "pre-registered" for an unauditable private repository, and discloses the panel-position seeding bug and its repair. This is above the field's bar.

---

## Weaknesses

### W1: The CA identification / inverse-problem literature is absent, and the paper's central mechanism lives inside it
**Problem**: The paper's core operation — "from one diagram we tabulate every observed neighbourhood→next-cell transition and rebuild the 2^(2r+1)-bit rule table" (lines 207–210) — is the founding move of the CA identification literature, none of which is cited. Richards, Meyer & Packard, "Extracting cellular automaton rules directly from experimental data", *Physica D* 45:189–202 (1990), posed exactly this inverse problem (including for noisy experimental data); Adamatzky, *Identification of Cellular Automata* (Taylor & Francis, 1994) is a book-length treatment of the exact-tabulation approach and its probabilistic extensions; Billings & Yang's IEEE Trans. SMC series (e.g., "Extracting Boolean rules from CA patterns", 2000; and their neighbourhood-detection work, which directly anticipates the paper's known-radius relaxation experiment at lines 512–514) developed identification under noise and unknown neighbourhoods. The Introduction presents "the identification problem is essentially solved by a single diagram" as the paper's first organizing result (lines 109–115) without engaging any of this.
**Why it matters**: This is a D2 failure mode ("prior work correctly represented"): the reader cannot tell what is new. Exact single-diagram tabulation under a matched observation model is close to folklore in the identification literature; what is actually new here — the reliability-calibrated "simulation-limited" benchmark, the amortization framing, the estimator race across the degradation frontier — must be positioned against that prior art or the contribution claim overreaches by omission.
**Suggestion**: Add the above references (verified: [Richards et al. 1990](https://www.sciencedirect.com/science/article/abs/pii/016727899090182O), [Adamatzky 1994](https://www.taylorfrancis.com/books/mono/10.1201/9781315274355/identification-cellular-automata-andrew-adamatzky), [Billings & Yang 2000](https://eprints.whiterose.ac.uk/id/eprint/796/1/billingssa7.pdf)); rewrite the second half of the Introduction to state explicitly that single-diagram identification is established and that the contribution is the benchmark-theoretic consequence. Sun, Rosin & Martin (IEEE Trans. SMC-B 41(3), 2011, fast rule identification and neighbourhood selection) and, for the learned rule-reader, Gilpin, "Cellular automata as convolutional neural networks", *Phys. Rev. E* 100:032402 (2019) and Mordvintsev et al., "Growing Neural Cellular Automata" (Distill, 2020) complete the lineage.
**Severity**: **Critical** (norm grounding: contract dimension D2 requires prior work be correctly represented; the named prior works are verified to exist and address the same inverse problem).

### W2: Damage spreading is credited only to the group's own 2022/2024 papers
**Problem**: Damage-response statistics are introduced citing only Vispoel et al. 2022 and 2024 (lines 92–94). The lineage those papers themselves build on is absent: Kauffman's original damage construction for Boolean networks (*J. Theor. Biol.* 22:437, 1969), Derrida & Pomeau's annealed treatment (*Europhys. Lett.* 1:45, 1986), and above all Bagnoli, Rechtman & Ruffo, "Damage spreading and Lyapunov exponents in cellular automata", *Phys. Lett. A* 172:34–38 (1992), which defines the maximal Lyapunov exponent of a CA via Boolean derivatives and connects damage spreading to a directed-percolation-type transition — i.e., the direct ancestor of all four target statistics. Shereshevsky (*J. Nonlinear Sci.* 2:1, 1992) and Tisseur (*Nonlinearity* 13:1547, 2000) give the rigorous Lyapunov side; Baetens & De Baets, *Chaos* 20:033112 (2010) — the second author's own foundational paper, in this very journal — established the Lyapunov-exponent phenomenology of CA that this benchmark quantifies.
**Why it matters**: Secondhand citation (crediting a lineage only through recent group papers) misassigns priority and denies the Chaos reader the entry points they will expect; the "survival" target is essentially the finite-size sign of Bagnoli et al.'s exponent, and that connection is currently invisible.
**Suggestion**: Cite the lineage at lines 92–96 and connect each target statistic to its ancestor (survival ↔ positive Lyapunov/DP-transition; spreading rate ↔ damage-front velocity). Verified: [Bagnoli et al. 1992](https://arxiv.org/pdf/cond-mat/9811159).
**Severity**: **Major**.

### W3: Classification and structure-detection prior art is missing where the by-products need it
**Problem**: (a) Wolfram's classification is cited only via the 2002 NKS book (line 75); the original source is Wolfram, "Universality and complexity in cellular automata", *Physica D* 10:1–35 (1984). (b) The five-statistic baseline includes a zlib compression ratio (line 226) with no citation to Zenil, "Compression-based investigation of the dynamical properties of cellular automata and other systems", *Complex Systems* 19(1) (2010), which built a CA classification on exactly that statistic. (c) The "interpretable phenotype map" by-product (lines 565–579) has direct prior art in computational mechanics: Hanson & Crutchfield's particle filters and especially Shalizi, Haslinger, Rouquier, Klinkner & Moore, "Automatic filters for the detection of coherent structure in spatiotemporal systems", *Phys. Rev. E* 73:036104 (2006), whose local statistical complexity fields are precisely spatially resolved phenotype maps for CA. (d) The glider-detector validation (lines 588–598) should engage Boccara, Nasser & Roger, "Particlelike structures and their interactions...", *Phys. Rev. A* 44:866 (1991), the canonical ECA particle census, and the Martínez–Adamatzky–McIntosh literature on rule 54's ether and gliders, which bears directly on the "ether front advances at light speed" claim (line 592) and on why localized-seed detection misses rule 54.
**Why it matters**: The by-products section explicitly offers these artefacts to the "behaviour-first (phenotype) analysis" program (lines 659–663); without the prior art, the paper appears to originate techniques (compression features, local phenotype fields, particle detection) that the field has had for 15–35 years, and forgoes the comparisons that would make the by-products credible.
**Suggestion**: Add the citations above (verified: [Shalizi et al. 2006](https://link.aps.org/doi/10.1103/PhysRevE.73.036104)); in Sec. IV G, one sentence comparing the damage-signature landscape to Li & Packard's rule-space structure analysis (already in the bibliography but cited only in passing at line 660) would also position Fig. 3 as the radius-2 analogue of their ECA map, which is what it is.
**Severity**: **Major**.

### W4: Scope-language slips and internal inconsistencies
**Problem**: (i) "a single space–time diagram identifies the local rule almost surely" (line 622) — "almost surely" is a measure-one statement; the paper's own number is 97.5% at radius two under a finite protocol. (ii) "can be solved by system identification whenever the observation encodes the generator" (lines 625–627) — one system class was studied; "whenever" is asserted, not shown. (iii) Discussion calls both by-products "independently validated artefacts" (line 662) while Sec. IV G's own verdict is that the radius-two landscape's independent detector agrees "at barely better than chance" (lines 594–596). (iv) Fig. 1's caption says 80 held-out rules (line 447); the text and Table III say 160 (line 337) — the subsetting is never explained. (v) "the documented borderline rule 106" (line 591) carries no citation to whatever documents it.
**Why it matters**: In a paper whose distinguishing virtue is calibrated language, these residual overstatements are exactly what a hostile reader will quote; (iv) and (v) are verifiability gaps.
**Suggestion**: "with high probability under the protocol" for (i); "for observation models that encode the generator, as demonstrated here for binary CA" for (ii); "validated on ECA, with stated limits at radius two" for (iii); state the 80-rule subsampling in Sec. IV E's text for (iv); cite the borderline-classification source (e.g., the scheme-comparison discussion in Vispoel et al. 2022, or the specific scheme that flags 106) for (v).
**Severity**: **Minor**.

### W5: Protocol-tuple robustness is scoped but never probed
**Problem**: All claims are (correctly) bounded to the tuple (Bernoulli(1/2), ring 127, radius-aware horizon), but the paper offers no evidence about behaviour under any other (w, T): the ECA-embeds-in-radius-2 "continuity control" (line 143) is asserted and never shown, and it is not obviously well-posed — a native ECA runs at horizon T=62 with rate normalisation 2r=2, while its radius-2 embedding runs at T=30 with normalisation 2r=4, so the target vectors are not numerically comparable across the embedding. The radius-2 landscape prevalence (7.8%) is likewise tied to uniform table sampling, which concentrates table densities near 1/2 and thus oversamples the chaotic bulk relative to, e.g., λ-stratified sampling (Langton 1990, already cited).
**Why it matters**: A Chaos reader will want to know whether "simulation-limited" is an artefact of one lattice/horizon and whether the landscape's band geometry is a property of the space or of the sampling measure; damage-spreading quantities are known to be strongly size- and measure-dependent (which the paper itself insists on, lines 94–96, 649–652).
**Suggestion**: Either report the embedding comparison explicitly (same physical horizon, renormalised rate) plus one ring-size sanity sweep (e.g., w ∈ {63, 127, 255} on a rule subset), or state plainly that no cross-(w,T) evidence is offered and that the continuity control was qualitative. For the landscape, one sentence on measure sensitivity (or a λ-stratified sub-sample) would suffice.
**Severity**: **Minor** (the paper's explicit scoping is legitimate; this is a robustness expectation, grounded in the size/measure dependence the paper itself documents at Fig. 1(d), not an unbounded demand).

---

## Detailed Comments

### Title & Abstract
Title is accurate and properly hedged ("finite-horizon"). The abstract is very dense but every claim in it is delivered in the body with matching numbers; "known neighbourhood radius" is properly foregrounded as an assumption. Consider whether "simulation-limited" needs a five-word gloss at first use for readers who will not parse 2·ICC−1 in an abstract.

### Introduction (emphasis)
The genotype/phenotype framing (lines 75–84) and the undecidability/measure-dependence motivation (lines 86–91) are correct and well-cited as far as they go (Culik–Yu 1988 and Gilman 1987 are exactly the right anchors). The shortcut-learning connection (Geirhos et al.) is apt. The structural problem is what is *not* there: the paragraph beginning "But under the observation model..." (lines 101–107) presents infer-then-simulate as an alternative the authors are introducing, when it is the established CA identification programme (W1). The fix is one honest paragraph: identification of binary CA from diagrams is a solved problem under matched assumptions (Richards et al. 1990; Adamatzky 1994; Billings & Yang 2000); the open question this paper answers is what that fact does to amortization benchmarks and where identification fails. That paragraph would *strengthen* the paper: the benchmark-methodology lesson (lines 619–630) lands harder when identification is stipulated as prior art rather than re-derived.

### Benchmark definitions (Sec. II — emphasis)
Domain-accurate throughout. The 88-orbit claim (lines 138–140) should carry a citation at first use (Li & Packard 1990, already in the bibliography, or Wuensche & Lesser 1992). The observation-model list (lines 150–153) is admirably explicit; "synchronous in the observed time direction" is an odd phrase — say "rows are consecutive synchronous updates". The horizon construction and the light-speed normalisation (Appendix B, lines 708–716) are correct (extent/(2rT)=1 is indeed the full-cone light-cone bound at any radius). The three-benchmark reliability section (II C) is the best part of the paper's methodology and should be advertised as a contribution in its own right. One domain note: survival's connection to the sign of the CA Lyapunov exponent (Bagnoli et al. 1992) belongs here (W2).

### Estimators (Sec. III)
The completion-prior treatment (lines 210–222, 344–350) is exactly the right level of care — coverage numbers, three completion policies, posterior-averaged variant. The known-radius assumption is honestly flagged and later priced (lines 512–514); connect it to Billings & Yang's neighbourhood-detection work (W1). The five statistics are individually well-chosen and correctly attributed where attributed (Wuensche's input-entropy variance, line 227) — but the compression feature needs Zenil (W3).

### Results (Sec. IV A–D)
The headline result and its two-ceiling verification (lines 264–280) are convincing; the coverage arithmetic is internally consistent (156/160 = 97.5%, exactly the exact-recovery rate). The refusal to extract a CNN-vs-statistics ranking from the underpowered ECA panel (lines 362–366) is good practice. The probe-task distinction (identity vs truth-table-bit, accessibility vs use, lines 410–432) is conceptually clean and the retirement of the anti-shortcut claim is honest.

### Identifiability and the frontier (Sec. IV E–F)
The best domain content in the paper. The observation that the deterministic table "has no noise model — one corrupted transition flips an entry" (lines 471–472) is the right mechanistic explanation for the sharp boundary, and the Bayesian-posterior repair is the natural one (it is also, unacknowledged, the probabilistic-identification move of Adamatzky 1994 and Billings & Yang — W1 again). The 80-vs-160 rule inconsistency (W4.iv) lives here. The compute section's one-sided Pareto conclusion (lines 552–560) is fair.

### By-products (Sec. IV G — emphasis)
The restraint here is commendable (see S4) and I want to protect it: the honest "inconclusive" phenotype-map verdict and the refusal to call the 7.8% band "glider-supporting" are how this section survives review. What it lacks is lineage: local phenotype fields (Shalizi et al. 2006; Hanson–Crutchfield) and particle censuses (Boccara et al. 1991; Martínez et al. on rule 54) are the instruments this section is implicitly rebuilding, and the multi-observable detector proposed as "the obvious upgrade" (lines 759–760) is essentially what the computational-mechanics filters already are. The rule-106 borderline claim needs its source (W4.v). The landscape's measure dependence deserves a sentence (W5).

### Discussion (emphasis)
The central lesson (lines 619–630) is correct, useful, and — modulo the "whenever" (W4.ii) — properly argued for the system class studied. The scoping of the neural claims to "this architecture at this training budget" (lines 632–639) is exemplary. The practical guidance paragraph (lines 652–659) is the paper's most quotable content and is supported by the frontier figures. "Independently validated artefacts" (line 662) overstates the radius-two case (W4.iii), and the citation cluster at line 663 (kleinberg2002, mitchell1993) is attached to a sentence about validation strength where Kleinberg's clustering impossibility theorem has no visible bearing — either explain the relevance or move/remove the citations.

### Conclusion
No separate conclusion section (Discussion serves); acceptable for Chaos.

### References
Thirteen entries; all that I checked are real and correctly attributed, and the entries used are used accurately (Culik–Yu for undecidability, Gilman for measure dependence, Wuensche for input entropy — all correct). The problem is coverage, not correctness: see W1–W3. Also: the bibliography's own header promises DOIs "where one exists", but several entries with DOIs lack them (Geirhos 2020: 10.1038/s42256-020-00257-z; Israeli–Goldenfeld 2006; Gilman 1987); Wolfram 1984 (*Physica D* 10:1–35) should join wolfram2002 as the primary classification source.

---

## Questions for Authors

1. **Novelty relative to the identification literature**: Given Richards–Meyer–Packard (1990), Adamatzky (1994), and Billings & Yang (2000), what precisely do you claim as new in "the identification problem is essentially solved by a single diagram" (lines 109–111)? My reading is that your contribution is the reliability-calibrated benchmark and its consequence for amortization benchmarks, not identification itself — do you agree, and will you reframe the Introduction accordingly?
2. **The ECA embedding as continuity control** (line 143): native ECA and its radius-2 embedding run at different horizons (T=62 vs T=30) and rate normalisations (2r=2 vs 4) under your protocol. What exactly was compared, and in what sense was continuity confirmed?
3. **Rule 106**: which source documents it as borderline class-IV (line 591), and how do the landscape verdicts change if the ECA reference set follows a scheme that folds complex into chaotic (Li–Packard) versus one that includes additional borderline rules?
4. **Landscape measure sensitivity**: uniform table sampling concentrates λ near 1/2. Is the 7.8% damage-signature prevalence (and the band geometry of Fig. 3) stable under λ-stratified sampling (Langton 1990), or is it a property of the sampling measure?

---

## Minor Issues

### Language / Grammar
- Line 622: "almost surely" → "with high probability under the protocol" (see W4.i).
- Line 151: "synchronous in the observed time direction" — rephrase.
- Lines 624–625: stray spacing in "and--- we believe---generalizable" (em-dash spacing).

### Citation Format
- Line 138–140: add a citation for the 88 equivalence classes at first use (Li & Packard 1990 is already in refs.bib).
- Line 663: kleinberg2002/mitchell1993 attached to a sentence they do not visibly support — clarify or relocate.
- refs.bib: add missing DOIs (Geirhos 2020, Israeli–Goldenfeld 2006, Gilman 1987); the file's header promises them.
- Wolfram classification: cite the 1984 *Physica D* original alongside NKS 2002.

### Figures and Tables
- Fig. 1 caption vs Table III: 80 vs 160 held-out rules — state the subsampling in the text (W4.iv).
- Fig. 2 caption: "Registered numbers-free as rev.~9" — internal revision-numbering jargon; Appendix A explains the three labels but not the "rev. N" scheme. Define once or strip.
- Table I: the "radius-2 complex" row's "≈0.98" ICC entry is the only non-exact number in the table — a footnote on how it was approximated would help.

### Layout
- Lines 19–21: TODO comments in the author block (ORCIDs, corresponding email) must be resolved before submission.

---

## Dimension Scores

| Dimension | Score (0–100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 72 | Adequate (upper) | The reliability-calibrated benchmark, frontier mapping, and amortization framing are novel; single-diagram identification per se is anticipated by the uncited identification literature (W1), which caps this score until repositioned. |
| Methodological Rigor (25%) | 85 | Strong | Domain-facing methodology (protocol, targets, reliability design, registration discipline) is excellent; detailed ML-statistics assessment deferred to Reviewer 1. |
| Evidence Sufficiency (25%) | 68 | Adequate | Experimental evidence for the in-scope claims is strong and two-ceiling-verified; positioning claims (novelty, by-product lineage) are under-sourced at 13 references. |
| Argument Coherence (15%) | 82 | Strong | Clean chain, honest failure cases; isolated overreach ("almost surely", "whenever") and the 80/160 inconsistency (W4). |
| Writing Quality (15%) | 84 | Strong | Precise, dense, well-signposted; registration jargon and TODO remnants are copy-edit level. |
| **Literature Integration (optional, R2 focus)** | **50** | Significant gaps | The 13 references used are real, apt, and correctly deployed, but three whole lineages central to the claims are missing (W1–W3); positioning is therefore incomplete rather than wrong. |
| Significance & Impact (optional) | — | — | R3 focus; not scored. |
| **Weighted Average** | **77.6** | — | Formula: 72×.20 + 85×.25 + 68×.25 + 82×.15 + 84×.15. The rubric mapping alone would read 65–79 = "Minor Revision"; per the sprint contract, the failure conditions are the sole authority for the editorial decision, and F2 (two mandatory warns: D2, D3) fires → major_revision. The rubric average is reported as calibration reference only. |

---

## Editorial Decision

**Major Revision** — contract failure condition F2 fired (mandatory dimensions D2 and D3 at warn; highest severity fired = 70 → editorial_decision = major_revision), consistent with my recommendation: the science is sound and carefully scoped, but the contribution must be repositioned against the CA identification and damage-spreading/Lyapunov literatures before acceptance.
