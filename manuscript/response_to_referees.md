# Simulated peer review and responses

An adversarial review anticipated for a benchmark-forward submission (target:
*Machine Learning: Science and Technology*, or *Chaos*). Each point lists the
referee's likely objection, our response, and the concrete manuscript change it
triggers. Written against the first full draft; used to harden it before the
error bars land.

---

## Referee 1 — machine-learning / benchmarking

**1.1 "Your CNN simply isn't tuned; a better network would win."**
*Response.* The comparison is deliberately asymmetric in the deep model's
favour: the amortiser is a multi-layer CNN with a 64-d representation and
$\sim10^5$ parameters trained for 60 epochs to convergence, while the baseline is
a regressor on *five* scalar statistics. We report five seeds (mean ± std), so
the result is not a single-run accident. Our claim is not that a CNN *cannot*
match the baseline but that it does not *exceed* it by the pre-registered margin
— and a negative of that form only strengthens if the network is made larger,
because the bar it fails to clear is set by five cheap numbers. We add capacity
and training details and this framing explicitly.
*Change.* Methods: state parameter count / capacity asymmetry; Discussion: add
the "a stronger network would still have to beat five numbers" sentence.

**1.2 "Simple-baselines-beat-deep-nets is already known (shortcut learning)."**
*Response.* The general phenomenon is known; what is not on record is a
*pre-registered, quantitative* demonstration for CA dynamical-invariant
estimation, together with the mechanism (rule readability + texture correlation
of the invariants) and two constructive consequences (a training-free spatial-map
method; a data-driven complexity landscape). Pre-registration is what converts
"the baseline happened to win" into "the deep model provides no advantage" — the
distinction the shortcut-learning literature repeatedly asks for.
*Change.* Intro/Discussion: sharpen the novelty statement to "pre-registered,
mechanistic, with a constructive alternative."

**1.3 "The map comparison is rigged: you pick the hand-crafted window per period."**
*Response.* We give the *baseline* its best window and the CNN still ties or
loses — i.e. we handicap our own preferred method, not the baseline. The two maps
are compared at identical column resolution with the identical contrast metric on
identical diagrams; the hand-crafted regressor is trained on full uniform
diagrams and applied locally, exactly mirroring the CNN's train-global/apply-local
recipe (so it is if anything *disadvantaged* by the train/test window-size shift).
Window flexibility is a real property of the cheap method, not a thumb on the
scale.
*Change.* Methods (maps): add the "best window = strongest baseline; matched
resolution/metric; hand-crafted is disadvantaged by the window shift" clarifications.

**1.4 "Only one invariant family (damage spreading)."**
*Response.* Scope is stated. We argue the mechanism is general to any
texture-correlated invariant and pre-registered that expectation; we flag
genuinely non-local invariants as the place a learned representation might still
help. Broadening to the Lyapunov spectrum is a natural, and separately reported,
extension.
*Change.* Discussion: keep the scope paragraph; add one sentence on which
invariant *classes* would escape the argument.

**1.5 "Reproducibility on a single Apple-silicon machine."**
*Response.* Fixed seeds, released code + cached data + pre-registered criteria;
the identity-keyed targets make the ground truth machine-independent up to
floating point. Error bars are over five training seeds.
*Change.* Already in the appendix; add the URL/license on release.

---

## Referee 2 — cellular automata / nonlinear dynamics

**2.1 "Your invariants depend on the observation protocol, so the whole thing is
protocol-specific."** *Response.* Agreed — and stated as a feature, not a bug.
"The behaviour class of a rule" is not well-defined (undecidability;
measure-dependence), so we index every claim by an explicit protocol tuple. The
benchmark result (deep ≯ simple) is what we claim *for that protocol*; we do not
over-generalise.
*Change.* Intro already frames this; add a half-sentence in Results that the
comparison is protocol-conditional by construction.

**2.2 "The 'complex' signature is operational and risks circularity."**
*Response.* The signature only *selects a held-out subpopulation*; the reported
quantity is prediction accuracy ($R^2$) and signed bias of the four continuous
invariants for that subpopulation — not a classification score, so there is no
circularity. The thresholds were fixed a priori by calibrating on the embedded
famous complex ECAs (54, 110, 106), which the signature recovers exactly on the
88 ECA orbits; results are robust to small threshold perturbations.
*Change.* Methods: add the two sentences distinguishing "selects a subpopulation"
from "classifies," and the a-priori calibration + robustness note.

**2.3 "3000 of $4\times10^9$ rules — is the 7.8% density trustworthy?"**
*Response.* It is a uniform-sampling estimate with a Wilson 95% CI [6.9, 8.8]%;
we report it as such and it is consistent with an independent 800-rule sample
(7.1%). We claim a density estimate, not an exact count.
*Change.* Results (landscape): already gives the CI; add "uniform-sampling
estimate" wording.

**2.4 "cone fill is poorly predicted by everything."** *Response.* Disclosed;
the median clears the bar without it, and its weakness is shared by the CNN and
the baseline (so it does not affect the comparison). It reflects the genuine
difficulty of the glider/chaos texture discriminator.
*Change.* Results: add the "weakness is shared, so comparison-neutral" note.

**2.5 "Is the training-free map actually new/useful?"** *Response.* Modest but
useful: an interpretable, GPU-free, per-patch dynamical-invariant map for
non-uniform CA, resolving to ~16 cells. We present it as a constructive corollary
of the negative, not as the headline.
*Change.* Discussion: keep as corollary; add one concrete use (localising the
interface behaviour in a composed CA).

---

## Referee 3 — editor / significance

**3.1 "Is a negative result significant enough to publish?"** *Response.* The
result is a pre-registered correction to an implicit, optimistic assumption
(that deep amortisation of dynamical invariants is a capability worth building),
delivered with a mechanism and a cheaper working alternative — precisely the kind
of rigorous benchmark the venue solicits. It also contributes a reusable
protocol-tuple methodology and a rule-space complexity map.
*Change.* Abstract/Intro: lead with the pre-registration and the constructive
outputs so the contribution is not read as "merely" negative.

**3.2 "The earlier 'repair' framing oversells the network."** *Response.* We
explicitly correct it: populating the intermediate regime, not the network,
removes the placement bias — any competent regressor does it. This honesty is
part of the paper's point.
*Change.* Results (complex): already stated; keep prominent.

---

## Net revisions applied to the manuscript
- Methods: capacity asymmetry; map-fairness clarifications; complex-signature
  non-circularity + a-priori calibration.
- Results: comparison is protocol-conditional; cone-fill weakness is
  comparison-neutral; landscape wording.
- Discussion: sharpened novelty (pre-registered + mechanistic + constructive);
  "a stronger net still must beat five numbers"; invariant classes that could
  escape the argument; one concrete map use.
