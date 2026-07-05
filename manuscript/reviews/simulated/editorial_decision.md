# Editorial Decision

> **SIMULATED REVIEW MATERIAL.** Editorial synthesis of the 5-reviewer ARS
> panel (academic-paper-reviewer v1.10.0, full mode, sprint contract
> `reviewer/reviewer_full/v1`), 2026-07-05. Not a real editorial decision.
> Every synthesis point below traces to a specific panel report
> (`r0_eic.md`, `r1_methodology.md`, `r2_domain.md`, `r3_perspective.md`,
> `r4_devils_advocate.md`); auxiliary audits (`citation_check.md`,
> `rebuttal_audit.md`, `project_audit.md`) are cited as such and were not
> visible to the panel.

## Manuscript Information
- **Title**: Rule reconstruction from a single space–time diagram yields
  simulation-limited prediction of the finite-horizon damage response of
  cellular automata
- **State reviewed**: `manuscript/main.tex`, branch `rev9-frontier`, HEAD
  d4c6efb (round-3-ready draft incl. the identifiability-frontier section)
- **Decision date**: 2026-07-05 · **Review round**: internal pre-round-3

---

## Decision

### MAJOR REVISION

Contract derivation (synthesizer three-step protocol, panel N=5):

| Dimension (mandatory\*) | EIC | R1 Meth | R2 Domain | R3 Persp | DA |
|---|---|---|---|---|---|
| D1 methodology_rigor\* | pass | warn | pass | pass | warn |
| D2 domain_accuracy\* | pass | warn | warn | warn | warn |
| D3 argumentative_coherence\* | pass | pass | warn | pass | **block** |
| D4 cross_disciplinary_relevance (high) | warn | pass | pass | warn | warn |
| D5 writing_and_structure | warn | pass | pass | pass | pass |

- **F1** (sev 90, any: mandatory block) — **FIRED** (DA D3 block) → `reject_or_major_revision`
- **F2** (sev 70, majority: ≥2 mandatory warns) — not fired (3 of 5 reviewers meet the predicate; threshold for N=5 is 4)
- **F3** (sev 60, any: high-priority block) — not fired
- **F0** (sev 10, all mandatory pass) — not fired (only the EIC's scores satisfy it)

Highest-severity fired condition F1 → `reject_or_major_revision`, resolved to
**Major Revision**: the underlying measurements are sound (R1 traced 46
numbers to artifacts, 44 exact; DA: "the core measurements … I probed and
could not break"), the blocking issue is a localized conclusions-level
contradiction, and every listed item is feasible in one revision cycle. The
iron rule that a Devil's-Advocate CRITICAL bars Accept is honoured.

## Reviewer Summary

| Reviewer | Identity | Recommendation | Confidence | Rubric avg |
|---|---|---|---|---|
| EIC | *Chaos* editor, nonlinear dynamics | Minor Revision | 4/5 | 81.6 |
| R1 | ML-evaluation statistician (repo access) | Major Revision (borderline minor) | 5/5 | 83.0 |
| R2 | CA theorist (Wolfram/Li–Packard lineage) | Major Revision | 5/5 | 77.6 |
| R3 | System-identification / SINDy researcher | Minor Revision | 4/5 | 79.3 |
| DA | Devil's Advocate | Major Revision | 4/5 | 71.0 |

Mean rubric score 78.5 (ordinally the minor-revision band); per the sprint
contract, the failure conditions — not the rubric — govern the decision.

## Consensus Analysis

### Points of Agreement

**[CONSENSUS-5] The paper never cites the literatures its claims live in.**
Each reviewer found a different missing body from their own seat: EIC W1
(ML-for-dynamics positioning, "the general lesson is never connected to the
literature it addresses", Major); R2 W1–W3 (inverse-CA prior art —
Richards/Meyer/Packard 1990, Adamatzky 1994, Billings & Yang 2000 — plus the
damage-spreading lineage from Kauffman/Derrida–Pomeau/Bagnoli to Baetens & De
Baets 2010, and by-product prior art incl. Shalizi 2006; **Critical**); R3 W1
(SINDy/Schmidt–Lipson/SBI/McGreivy–Hakim; Major); R1 D2-warn (adjacent); DA
M4 ("the general lesson targets an uncited antagonist" — the criticized
benchmark practice is the one load-bearing premise with no citation). This is
the dominant revision item. R2's sharpest form: the paper's core operation
(tabulate transitions → rebuild the table) is the founding move of the CA
identification literature, so "the identification problem is essentially
solved by a single diagram" must be repositioned as stipulated prior art —
which *strengthens* the actual novelty (the reliability-calibrated
simulation-limited benchmark and the degradation frontier).

**[CONSENSUS-5] The measurement/registration discipline is exemplary and the
ICC vs 2·ICC−1 distinction is an exportable contribution.** EIC S1–S2, R1
S1–S2 (verified in git and artifacts, including the 0.9871 vs 2·0.9936−1 =
0.9872 self-validation), R2 S2, R3 S3, DA Observations ("better than the
large majority of ML-for-science papers"). The revision must preserve this.

**[CONSENSUS-4] The identifiability frontier (§IV.E/Fig. 2–3) is the paper's
most valuable, transferable artifact** (EIC S3, R2 S3, R3 S1–S2; R1 S5
adjacent), with the DA concurring on value while disputing the fairness of
one comparison inside it (see Disagreement 3).

**[CONSENSUS-3] The abstract needs a rewrite** — DA C1 (contradiction with
§IV.E, Critical), EIC W2 (≈370 words vs the ≤250 limit; missing *Chaos*
non-technical lead paragraph; Major), DA m8 (jargon density); R2 W4 flags
abstract-level scope slips ("identifies … almost surely"). R1 and R3 silent.

### Points of Disagreement

**Disagreement 1 — Does the abstract contradict the paper's own results? (D3)**
- **EIC view**: coherence exemplary; "every abstract number traces to a table" (r0 S1, D3 pass).
- **DA view**: D3 **block** — the abstract assigns the degraded regime to
  "direct amortization has a rationale" (main.tex:55–59) while §IV.E shows
  read-then-simulate repairs owning most of it (posterior 0.85 vs 0.24 at 40%
  masking; 0.59 vs −0.77 at 50%; 0.77 vs 0.08 at density 0.1) and the noise
  dead zone belonging to *learned system identification*, not the frozen CNN.
- **Type**: existence disagreement. **Resolution**: DA upheld. The
  synthesizer independently verified the cited lines: the abstract's final
  clause is the rev-8 framing, never updated for the rev-9 results it now
  contradicts. The EIC evaluated number-traceability (true) but missed the
  regime-attribution clause. Per the one-outlier rule ("if the rationale is
  valid and others missed it, escalate"), the block stands. Note the DA's own
  qualifier: localized, "fixable in a paragraph".

**Disagreement 2 — Severity of the missing inverse-CA literature.**
- **R2 view**: Critical (novelty framing rests on uncited direct prior art).
- **EIC/R3 view**: Major (positioning gap, no new experiments needed).
- **Type**: severity disagreement. **Resolution**: Required revision at
  Critical priority, but not rejection-grade: the named prior works are
  verified to exist (R2 and R3 confirmed Richards 1990 and Adamatzky 1994
  independently, from different fields), yet the paper's distinct
  contributions (three-benchmark calibration, frontier, honest verdicts)
  survive repositioning intact — R2's own report says the novelty "survives
  and lands harder once repositioned".

**Disagreement 3 — Is the central result a tautology, and is the frontier fair?**
- **DA view** (Strongest Counter-Argument; M1/M5/M6): benchmark attainment is
  a corollary of the setup on simulation-defined targets; the frontier gives
  read-then-simulate two purpose-built repairs while the direct CNN stays
  frozen and clean-trained; the matched-regime negative rests on one
  author-handicapped network whose constraint rationale the paper retires.
- **R1/R3 view**: D3 pass — "simulation-limited" is operationally defined,
  falsification-tested against the 16× reference, and honestly scoped (R1);
  "the general lesson is real, timely, and cleanly demonstrated" (R3 S1).
- **Type**: perspective difference on framing + existence disagreement on two
  controls. **Resolution**: split the difference on evidence. (a) The
  tautology charge is defused *if* the Introduction states the
  corollary structure up front (targets are simulation-defined, so
  amortization can only ever win on cost/robustness — currently surfaced only
  at §IV.F); this is the DA's own residual demand and becomes S-1. (b) The
  two missing controls (degradation-augmented CNN; same-budget unconstrained
  CNN) were raised independently by DA (M1, M6) and R3 (Question 1), are
  cheap (~22 min/seed per the paper's own Appendix B), and gate the paper's
  degraded-regime guidance — they become R-6 (run them, or scope the guidance
  to adaptation-naive amortizers explicitly).

**Disagreement 4 — Overall recommendation (3 Major / 2 Minor).**
Resolved to Major Revision by the contract (F1) and the conservative
principle for splits; R1's "borderline-minor, driven by the contract, not by
any conclusion-invalidating flaw" is noted for calibration — this is a
near-boundary Major.

## Decision Rationale

The panel is unanimous that the measurements are trustworthy and unusually
well-bookkept, and unanimous that the paper fails to cite the literatures on
which its novelty framing, its terminology ("amortization"), and its closing
lesson depend. Two findings force Major over Minor. First, the Devil's
Advocate's verified CRITICAL: the abstract's degraded-regime attribution is
contradicted by the paper's own §IV.E results, and an abstract-level reader
would carry away the wrong recommendation — under the panel's standards a
manuscript that would mislead readers cannot pass without re-verification.
Second, the methodology reviewer's artifact audit found one §IV.E number
(frozen CNN −1.1 at 20% noise) unsupported by the canonical released artifact
(−0.93) and traced it to a provenance chain the repository itself documents
as discarded — conclusion-preserving, but integrity-relevant for a paper
whose selling point is auditability, and it must be corrected at the source.
Around these sit consistent Major items from independent seats: the
literature repositioning (all five reviewers), the registration-taxonomy gap
for rev-9 (DA M3, R1 W4, R3 W4), the unexplained stacking base (DA M2), the
undisclosed reduced Monte-Carlo budgets and single-seed reader (R1 W2), and
two cheap fairness controls that gate the degraded-regime guidance (DA
M1/M6, R3 Q1). No reviewer identified a conclusion-invalidating flaw; the
revision is demanding but bounded, so rejection would be inappropriate and
Minor Revision would understate the required re-verification.

## Required Revisions (Must Fix)

| # | Item | Source | Severity | Where | Effort |
|---|---|---|---|---|---|
| R-1 | Rewrite the abstract (≤250 words): align the degraded-regime clause with §IV.E (posterior owns intermediate band; sampled reader owns the noise dead zone; frozen CNN does not), add the *Chaos* lead paragraph, one plain sentence per result; fix the one contradicted Discussion sentence | DA C1; EIC W2; DA m8 | **Critical** | Abstract; Discussion | 1 day |
| R-2 | Correct "frozen CNN to −1.1" → the canonical artifact value (−0.93); re-derive the RESULTS.md F2-table cnn/stack column (6 cells) from `frontier_grid/summary.json`; extend the programmatic numbers audit to prose and tables | R1 W1 | **Critical** (integrity) | §IV.E; RESULTS.md | 0.5 day |
| R-3 | Literature repositioning: (a) inverse-CA prior art (Richards/Meyer/Packard 1990; Adamatzky 1994; Billings & Yang 2000) and reframe "identification is essentially solved" as anticipated prior art; (b) damage-spreading lineage (Kauffman 1969; Derrida & Pomeau 1986; Bagnoli/Rechtman/Ruffo 1992; Baetens & De Baets, *Chaos* 2010); (c) ML-for-dynamics / SBI / weak-baselines (Brunton 2016; Schmidt & Lipson 2009; Cranmer 2020; McGreivy & Hakim 2024); (d) by-products (Shalizi 2006; Zenil 2010; Boccara 1991; Wolfram 1984) | R2 W1–W3; R3 W1/W3; EIC W1; DA M4 | **Critical** (R2) / Major | Intro; Discussion; refs | 2–3 days |
| R-4 | Registration bookkeeping: add the rev-9 frontier items to Appendix A's taxonomy; enumerate the three registered hypotheses referenced by ordinal; disclose the reduced MC budgets (n_pairs 48/64 vs 256) in the figure captions; disclose the single-seed rule-reader; report the registered posterior-interval calibration | DA M3; R1 W2/W4; R3 W4 | Major | App. A; §IV.E captions | 1 day |
| R-5 | Define the stacking base model and reconcile base-vs-headline R² (0.56/0.14 vs Table III); if protocol-induced, state the increment under the headline protocol | DA M2 | Major | §IV.C; App. B | 0.5–1 day |
| R-6 | Run the two fairness controls — (i) the same CNN retrained with the reader's degradation augmentation, (ii) a same-budget unconstrained CNN — or explicitly scope every degraded-regime recommendation to adaptation-naive amortizers | DA M1/M6; R3 Q1 | Major | §III(iii); §IV.E | 1–2 days (gated: training runs need approval) |
| R-7 | Fix internal inconsistencies: "2/88" vs {54,106,110} (3/88); 80 vs 160 held-out rules between Fig. 1–2 captions and Table III; "[+0.00,+0.20] excluding 0" (print decimals); silently truncated CI 1.0056→1.00 | R1 W3; DA m1/m2; R2 W4 | Major (bundle) | §IV.G; captions | 0.5 day |

**Acceptance criteria**: R-1/R-2 verified by re-reading abstract & §IV.E
against `frontier_grid/summary.json`; R-3 by a positioning paragraph naming
the prior-art relationship explicitly; R-4 by Appendix A listing every label
§IV.E uses; R-5 by a reader being able to reconcile the two tables; R-6 by
new grid columns or scoped claim language; R-7 by grep.

## Suggested Revisions (Should Fix)

| # | Item | Source | Priority |
|---|---|---|---|
| S-1 | State the simulation-defined-target corollary in the Introduction (amortization can only win on cost/robustness) | DA M5 | P2 |
| S-2 | One Discussion paragraph mapping each frontier axis to its continuous-state / stochastic analogue, marking measured vs conjectured | R3 W2 | P2 |
| S-3 | Restructure §IV.E (subsections or a results box) + a practitioner decision table for the three-step guidance | EIC W3; R3 W5 | P2 |
| S-4 | Regenerate figures from corrected `make_figures.py` (retire "complex" label and "no advantage" title); remove orphaned `map_benchmark.pdf` | EIC W5; project_audit P1 | P2 |
| S-5 | AIP production matter: Author Declarations, Acknowledgments, Data Availability with a concrete DOI'd-archive pointer; resolve ORCID/email TODOs; external timestamp for the registration history; pin scikit-learn | EIC W4; R1 W5/D5 | P2 |
| S-6 | Citation metadata: `rollier2024cnn` year → 2025 + pages 49–70; add the five verified missing DOIs | citation_check E1/E2 (auxiliary audit) | P3 |
| S-7 | Round-3 letter: attach the anonymized registration archive proactively; fix the anonymity rationale; fold the rev-9 addendum into the per-concern replies | rebuttal_audit R1–R3 (auxiliary audit) | P2 |
| S-8 | Optional robustness: denoise-then-invert baseline for the 3–7% noise band; two-stage survival head for the CNN's cone-fill instability | DA Alternatives 1/3 | P3 |

## Revision Roadmap

**Priority 1 — correctness & integrity (2–3 days)**: R-1, R-2, R-7.
**Priority 2 — positioning & bookkeeping (3–4 days)**: R-3, R-4, R-5, S-1, S-2.
**Priority 3 — experiments (1–2 days compute + analysis; training gated)**: R-6, then S-8 if desired.
**Priority 4 — structure & production (1–2 days)**: S-3, S-4, S-5, S-6, S-7.
**Total estimate**: 1.5–2 weeks — comfortably within a round-3 window.

## Response Letter Instructions
Respond item-by-item (R→A→C format per `revision_response_template.md`);
mark changes; include a cross-reference table. R-2's correction should be
disclosed plainly (the repository's own provenance standard demands it).

## Closing
The panel encourages a careful revision: no reviewer doubts the measurements,
three independently call parts of the apparatus exemplary, and the required
work is concentrated in framing, positioning, and two cheap controls. The
revised manuscript would undergo verification review (re-review mode) against
this roadmap.

## Panel integrity note
All 5 reviewer outputs usable (panel cardinality 5/5); reviewers ran in
isolated contexts, blind to each other, to the real referee history, and to
the auxiliary audits. Phase-1 (contract paraphrase + scoring plan) preceded
manuscript access by enforced ordering within each context — an adaptation of
the physically-separated two-call protocol, disclosed in
`phase0_field_analysis.md`. A mid-review API-quota interruption paused all
five reviewers; each was resumed with context intact. The synthesizer applied
the contract expressions mechanically (matrix above) and independently
verified the DA's CRITICAL and M2/M3 claims against `main.tex` before
upholding them.
