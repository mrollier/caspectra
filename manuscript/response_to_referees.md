# Response to the referee

We thank the referee for an unusually detailed and constructive report. The
central criticism — that the original manuscript's sweeping conclusion outran a
narrow experiment — was correct, and acting on it produced a materially stronger
and, we believe, more interesting paper. The single most consequential change is
that we added the *mechanistic estimator the referee asked for* (concern 5: "a
transparent mechanistic baseline that infers the rule table and then simulates
it"). It does not merely contextualise the deep model — it **reaches the
reliability ceiling and dominates both the deep network and the cheap
statistics**, which reorganises the paper around a three-tier result and an
interpretable positive finding rather than a bare negative. Every new decision
rule was pre-registered numbers-free before measurement (repository revision 7).

Point-by-point below; "R1–R7" name the new pre-registered analyses.

---

## 1. The anti-shortcut architecture is not shown to block rule recovery

**Agreed, and we now measure it rather than assert it.** New probes (R5) recover
rule identity from the CNN's 64-dimensional bottleneck at balanced accuracy 0.88
(ECA) / 0.95 (radius-two), and truth-table entries of *unseen* rules at 0.78 /
0.61 — far above the five statistics and chance. The raw diagram yields the rule
*exactly* (100% ECA, 97.5% radius-two) via the mechanistic inverter (R4). We
therefore **drop the claim that the architecture prevents rule recovery**;
"anti-shortcut" now names only an architectural intent, and the *readability* of
the rule is presented as the mechanism behind the null (new Sec. "Why: the rule
is readable"). This strengthens rather than weakens the paper: the deep model has
nothing to add precisely because the rule — and hence any smooth function of
it — is already fully present.

## 2. Failed superiority ≠ equivalence; baseline treated as deterministic

**Agreed; fully reworked (R1).** We now report **per target** (never a 4-target
median alone), with the **held-out rule as the unit of resampling** (cluster
bootstrap, 10⁴ resamples), and classify each method pair by a pre-registered rule:
superiority (median ΔR² ≥ 0.10, 95% CI excludes 0), practical equivalence (TOST,
90% CI within ±0.05), or inconclusive. On radius-two (N=160, powered) the
mechanistic estimator is *superior* to both others on most targets; the deep net
and the cheap baseline *trade* (net marginally ahead on survival, baseline clearly
ahead on cone fill), neither dominating. We also disclose honestly that the ECA
held-out set (N=18) is underpowered for tight per-target intervals and report it
at the median level there. The baseline is no longer treated as noiseless — the
bootstrap resamples rules for every method identically.

## 3. Monte-Carlo noise does not by itself bound R²

**Agreed; replaced with a proper reliability analysis (R3).** We draw K=20
independent target replicates per rule and fit a one-way random-effects model to
obtain, per target, ICC(1) = the achievable-R² ceiling. On ECA these are
0.994/0.999/0.9995/0.999 (survival is the noisiest, std 0.022); on radius-two
0.987/0.998/0.998/0.980. Every R² is now read against its per-target ceiling, and
the old "0.006–0.014 upper-bounds R²" sentence is removed. This also sharpens the
result: the mechanistic estimator sits *at* the ceiling, so the gap to the deep
model is a real, quantified shortfall, not a comparison against an unreachable 1.

## 4. Under-specified experimental design

**Addressed.** Methods now state the rule counts and sampling, the identity-keyed
target streams and their independence from the training diagrams, the
leave-rules-out split and that tuning never touches held-out rules, the full
encoder (kernels, bottleneck, norm, head, map variant), training length and seed
protocol, the baseline features and both regressors, and the exact definitions of
the four statistics (cone extent, fill, survival, fraction) and the map contrast.
The complete code, cached targets and sampled panels are released on publication;
we have kept the article self-contained on every quantity it reports.

## 5. Selectively strong baseline, selectively weak network

**This is where the referee's suggestion most improved the paper.** We built the
recommended mechanistic *infer-the-rule-and-simulate* estimator (R4) and the
cross-fitted *stacking* test (R2). Two consequences:

- The mechanistic estimator reaches the reliability ceiling and **dominates**
  both the cheap features and the CNN on every task — an interpretable method,
  not a tuned network, is the right tool. This is now the paper's headline.
- The stacking test answers "does the representation add information beyond five
  numbers?" directly and *honestly*: the CNN **does** add a real, significant
  increment on damage survival (+0.32) — the least texture-like statistic, exactly
  where the referee (concern 7) predicted learning might help — but nothing on the
  texture-dominated statistics, and the five statistics add nothing beyond the
  CNN. We report this nuance prominently; the headline is no longer "deep learning
  adds nothing" but "an interpretable estimator dominates, and the net's one real
  edge is small."

We respectfully **push back** on the request for an exhaustive
architecture/optimiser sweep (larger/multiscale/temporal/recurrent nets): no
finite sweep can establish "no network ever wins," so we make a *bounded* claim
instead. The stacking test bounds the incremental value of *any* estimator built
on the same single-diagram information; the mechanistic estimator shows the
ceiling is reachable interpretably; and we now argue from *measured* rule
recoverability (R5) rather than from parameter count, which the referee rightly
noted is not a capacity proxy. We state explicitly that a learned representation
may yet win on targets or regimes that depend on non-local or rare structure.

## 6. "Dynamical invariants" is misleading

**Agreed; renamed throughout.** The title and text now say **"finite-horizon
damage-response statistics,"** and the paper states plainly that they are
finite-size, finite-horizon and IC-measure-dependent, indexed by the protocol
tuple.

## 7. One observation regime, treated as structural

**Softened and scoped.** The Discussion now confines the "structural" reading to
the tested protocol, notes the short horizons explicitly, and cites the
protocol-sensitivity of the induced taxonomy. Crucially, the survival increment
from the stacking test is presented as a concrete hint of where a learned
representation *could* help (rare-event, less-texture-like targets), and
identifying such a target/regime is named as the natural next step. We do not
claim universality.

## 8. Complex/glider classification is circular

**Agreed; independently validated and re-worded (R6).** We added a localized-seed
/ periodic-localization glider detector — a *different observable* from the
twin-run damage signature. On ECA the damage criterion selects exactly
{54,106,110}; {54,110} are the literature's canonical class-IV rules (independent
ground truth), and the detector agrees on 92% of applicable rules (FP 6%, FN 2%,
the one miss being rule 54, whose ether front advances at light speed — disclosed,
not tuned away). On radius-two, where no literature ground truth exists, the two
observables agree only 47%, so we now report the prevalence strictly as **"the
fraction (≈7.8%, Wilson CI [6.9,8.8]%) satisfying the pre-registered
damage-signature criterion,"** *not* as validated glider prevalence — exactly the
conservative wording the referee requested. We state that single-observable glider
detection is itself unreliable in the large space.

## 9. The spatial-map experiment is not fair or grounded

**Agreed; rebuilt (R7).** We compute a location-resolved ground truth by **local
perturbation in the composed system** (not the assumed pure-rule invariant, and
honestly reflecting mixed interface dynamics), and score each map by spatial
correlation to it. The hand-crafted window is now **selected on a validation split
of rule pairs** (the per-pair best window is reported only as an oracle
sensitivity). Against this fair, independent test the learned map shows **no
statistically significant** localisation advantage (Spearman 0.67 vs 0.61, Δ+0.05,
95% CI [−0.002,+0.10]) — a tie. We note for the record that the earlier
best-window choice handicapped the *CNN* (our preferred method), so it could not
have inflated the negative; the validation-selected comparison removes the concern
regardless.

## 10. Pre-registration is unverifiable while the repository is private

**Acknowledged.** We have softened the wording to "criteria committed to a
timestamped repository in advance and released on publication," and we disclose
the one deviation from the original pre-registration (the target-stream RNG fix)
explicitly in the appendix, with its measured effect. An immutable, DOI-bearing
archive of the pre-registration, code, sampled rules and cached targets will
accompany the published article; we did not want to compromise anonymity/priority
by making it public during review.

## 11. Presentation and citation quality

**Fixed.** The wide result tables are now full-width and no longer clip; figure
captions are expanded to stand alone; the incorrect/placeholder citation for the
prior CNN paper is corrected to the real reference (Rollier, Daly & Baetens, 2024,
Springer *Emergence, Complexity and Computation*; arXiv:2409.02740) and no
"TODO" markers remain in the bibliography. Author/affiliation placeholders remain
only pending the non-anonymised submission.

---

## Summary of new, pre-registered evidence added
R1 per-target paired inference + TOST; R2 cross-fit stacking / incremental value;
R3 reliability-adjusted ceilings; R4 mechanistic rule-inference estimator; R5
rule-recoverability probes; R6 independent glider validation; R7 nuCA
local-perturbation map ground truth. Together they convert the original bare
negative into a mechanistic, interpretable, and appropriately bounded result.
