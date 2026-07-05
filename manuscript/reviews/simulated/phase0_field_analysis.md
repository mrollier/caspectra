# Field Analysis Report — ARS simulated review panel (Phase 0)

> **SIMULATED REVIEW MATERIAL.** Generated 2026-07-05 by the
> academic-research-skills `academic-paper-reviewer` skill (v1.10.0, full mode)
> run locally as an internal pre-round-3 stress test. Not a real referee
> document. Real referee reports live in `manuscript/reviews/chaos_*.md`.

## Paper Basic Information
- **Title**: Rule reconstruction from a single space–time diagram yields
  simulation-limited prediction of the finite-horizon damage response of
  cellular automata
- **Manuscript state**: `manuscript/main.tex` @ branch `rev9-frontier`
  (HEAD d4c6efb), 9 pp two-column REVTeX, incl. the held-for-round-3
  identifiability-frontier section
- **Full text length**: ≈ 8,500 words (774 lines LaTeX source)
- **Number of references**: 13 BibTeX entries
- **Venue**: *Chaos: An Interdisciplinary Journal of Nonlinear Science* (AIP);
  manuscript has passed two real referee rounds (reject→resubmit framing round,
  then "major revision")

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Nonlinear dynamics / complex systems (cellular automata) |
| Secondary Disciplines | Machine-learning evaluation & benchmark methodology; system identification / inverse problems; Bayesian inference |
| Research Paradigm | Quantitative, computational (simulation benchmark with pre-registered decision rules) |
| Methodology Type | Statistical modeling / machine learning benchmark; large-scale simulation study |
| Target Journal Tier | Q1–Q2 (Chaos is a leading specialized nonlinear-science journal) |
| Paper Maturity | Pre-submission (round-3-ready revised draft; polished, compiled, figures final) |

## Recommended Target Journals (Top 3)
1. *Chaos* (AIP) — current target; CA + ML-for-dynamics is squarely in scope.
2. *Physical Review E* — damage spreading / CA classification has a long PRE lineage.
3. *Journal of Cellular Automata / Complex Systems* — specialized fallback.

## Reviewer Configuration Cards

### Card #1 — EIC
**Role**: Editor-in-Chief perspective
**Identity**: Senior editor at *Chaos* (AIP), 20+ years in nonlinear dynamics
and complex systems, has handled the recent wave of machine-learning-for-
dynamical-systems submissions and is wary of both ML hype and reflexive ML
dismissal.
**Review focus**: (1) journal fit and interest to the Chaos readership; (2)
originality and significance of the "system identification is the baseline to
beat" lesson; (3) whether the paper's claims and framing match what the
abstract promises. **Will particularly care about**: whether a benchmark paper
(as opposed to a new-phenomenon paper) carries its weight for this venue.
**Possible blind spots**: fine-grained statistics of ML evaluation (covered by R1).

### Card #2 — Peer Reviewer 1 (Methodology)
**Role**: Methodology reviewer
**Identity**: Statistician / ML-evaluation methodologist who reviews for
NeurIPS Datasets & Benchmarks and champions registered reports; expert in
bootstrap inference, reliability theory (ICC), equivalence testing (TOST), and
reproducibility auditing.
**Review focus**: (1) are the "decision rules committed in advance" actually
followed — and is the registration-status labelling honest; (2) statistical
correctness of the 2·ICC−1 simulation-limited benchmark vs the ICC ceiling, the
bootstrap CIs, and the per-cell verdict rules; (3) reproducibility affordances
— **this reviewer additionally receives the code repository as supplementary
material** (RESULTS.md, EVALUATION_CRITERIA.md, caspectra/, tests/, runs/
summaries, README) and spot-checks that manuscript numbers trace to measured
records. **Will particularly care about**: whether any pre-registered threshold
was quietly relaxed. **Possible blind spots**: CA domain literature (covered by R2).

### Card #3 — Peer Reviewer 2 (Domain)
**Role**: Domain reviewer
**Identity**: Cellular-automata theorist in the Wolfram/Li–Packard lineage;
works on damage spreading and Lyapunov exponents for CA, rule equivalence
classes, and the undecidability of classification; knows the identifiability
and inverse-CA literature.
**Review focus**: (1) domain accuracy — are Wolfram classes, Li–Packard
folding, the 88 orbits, and damage-spreading definitions represented correctly;
(2) literature coverage and positioning (13 references is thin — what key work
is missing); (3) whether the protocol-tuple caveats (measure dependence,
finite-size, horizon) are handled with the care the CA literature demands.
**Will particularly care about**: conflation of behaviour classes with rule
identity, and boundary-condition/finite-size artefacts. **Possible blind
spots**: ML benchmark methodology (covered by R1).

### Card #4 — Peer Reviewer 3 (Perspective)
**Role**: Cross-disciplinary reviewer
**Identity**: System-identification / inverse-problems researcher (SINDy,
symbolic regression, physics-informed ML) who studies when governing equations
can be recovered from data and what to do when they cannot.
**Review focus**: (1) does the "when the observation encodes the generator,
system identification is the baseline to beat" lesson generalize as claimed —
is it substantiated for readers outside CA; (2) accessibility of framing and
definitions to adjacent-field readers; (3) practical impact of the
read-the-rule-then-simulate recipe and the identifiability frontier for the
broader ML-for-dynamics community. **Will particularly care about**: whether
the paper connects to the model-discovery literature it is implicitly speaking
to. **Possible blind spots**: CA-specific correctness (covered by R2).

### Card #5 — Devil's Advocate
**Role**: Devil's Advocate
**Identity**: Adversarial senior reviewer whose job is to construct the
strongest case against the paper.
**Review focus**: (1) is "simulation-limited prediction" a disguised
tautology — deterministic finite system, fully observed, known radius: of
course the rule is readable, so what is actually learned; (2) does the
three-tier framing ("interpretable methods dominate") cherry-pick the regime
where it holds; (3) are the frontier hypotheses' split verdicts (weakly
confirmed / refuted) spun favourably; (4) alternative explanations for the
CNN's failure (capacity, training budget) that would undermine the moral; (5)
the "so what?" test for the Chaos readership. Uses the dedicated DA report
format (strongest counter-argument, CRITICAL/MAJOR/MINOR issues, ignored
alternatives, stakeholder blind spots).

## Review Strategy Recommendations
- Built-in tension to exploit: R1 will credit the pre-registration discipline
  while the DA attacks the value of what was registered — the synthesizer must
  arbitrate "rigorous" vs "rigorously establishing the obvious".
- R2 and R3 approach literature from opposite sides (CA canon vs model-discovery
  canon); overlapping "missing references" comments are expected but must name
  different bodies of work.
- All reviewers are blind to the real referee history (`manuscript/reviews/`,
  `response_to_referees.md`) so the panel surfaces *new* issues; the review
  history is handled separately by the rebuttal audit.

## Orchestration adaptation note (transparency)
The v3.6.2 sprint-contract protocol prescribes a physically separate
paper-blind Phase 1 call per reviewer. This run adapts it to single-context
subagents with **enforced ordering**: each reviewer must emit its Contract
Paraphrase + Scoring Plan (from `shared/contracts/reviewer/full.json` +
metadata only) *before* opening the manuscript, and the report preserves that
section order for audit. Panel size 5 per `reviewer_full`.
