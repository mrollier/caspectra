# Referee report

**Manuscript:** *Rule reconstruction from a single spacetime diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata*
**Authors:** M. Rollier, J. M. Baetens
**Date of report:** 20 August 2026

---

## 1. Summary and overall recommendation

The paper argues that a benchmark of the form "predict a perturbation-defined dynamical statistic from one spacetime diagram" is, under a fully-observed noiseless deterministic observation model, solved by system identification: read the rule table off the diagram, re-run the perturbation experiment, done. The authors confirm this at scale (100% ECA, 97.5% radius-two exact recovery), show that the resulting predictions sit at the independent-replicate reliability benchmark, show that two direct learned estimators fall short, and then map an *identifiability frontier* along four degradation axes, with a probabilistic decoder and a corruption-trained network taking over in successive bands.

The writing is disciplined, the registration and audit practices are unusually honest, and the reporting of null and inconclusive results is exemplary. I want to say that first, because most of what follows is critical.

My central concern is one of **contribution shape**. The matched-regime result is close to analytic: conditional on exact reconstruction and an independent simulation stream, agreement with a noisy cached target is *identically* the replicate-agreement benchmark. Sections IV A, and the mechanistic columns of Tables I–III, therefore measure a quantity whose value is fixed by construction. The genuinely empirical content of the matched regime is a single number — the exact-reconstruction rate — and that number is prior art the authors themselves stipulate. Meanwhile the part of the paper that is not a tautology, the frontier (Secs. IV E–IV F), rests on an 80-rule subsample, single training seeds for two of the key estimators, one architecture, one training budget, single-axis corruptions, and a training protocol whose run-to-run variance the authors measure at a factor of two. The balance of page count is inverted relative to the balance of evidence.

I think the paper is publishable, but not in its current shape. My recommendation is **major revision**, with two things I would want to see: (i) a restructuring that states the matched-regime result as the near-identity it is and reallocates space to the frontier, and (ii) at least one experiment that makes the thesis non-trivial — the obvious candidate, discussed in §5.1, is a **stochastic generator**, which the authors currently exclude in one sentence and which their own pseudo-posterior decoder is already the correct estimator for.

---

## 2. Goal-level criticism

### 2.1 The thesis is true but is it news, and to whom?

"When the observation encodes the generator, system identification is the baseline to beat" is, for anyone working on CA, close to a definition. For the ML-for-dynamics audience it is the McGreivy–Hakim complaint (ref. 18) which the paper cites approvingly. The paper's own framing concedes both points. So the contribution reduces to: a controlled, closed-world instance of a known critique, in a system chosen precisely because the encoding is maximal.

The honest referee question is then: **does the closed-world instance transfer?** The paper answers "the frontier is what transfers", and the Discussion supplies a table of named analogues (measurement noise ↔ equation-discovery noise, masking ↔ missing sensors, IC density ↔ persistency of excitation). But every one of those analogues is asserted, and the paper marks most of them "transfer conjectured". A reader is being asked to accept a generality claim on the strength of an analogy list.

Two ways out, either of which would strengthen the paper materially:

- **Name a real benchmark this invalidates.** Pick one published "predict Lyapunov exponent / chaos / stability from a trajectory" benchmark, construct the identification baseline for it, and report the gap. If the gap is large, the paper acquires teeth. If no such benchmark exists in a form where the encoding is complete, say so plainly — the contribution then becomes pedagogical, which is fine, but should be labelled.
- **Break the encoding by construction, not by corruption.** See §5.1.

### 2.2 The delta relative to ref. 8 needs stating explicitly

Ref. 8 (Rollier, Daly, Baetens 2025) already establishes that a CNN recovers ECA rule identity from a single clean diagram at 99.9%. The present paper's premise — the diagram contains the rule, and learned models will read it — is therefore the authors' own prior result. The Introduction cites this in passing at the end of a sentence. Readers and referees will ask how much daylight there is. I would put a short explicit paragraph in the Introduction: *ref. 8 showed the rule is readable by a network; this paper shows the consequence for a perturbation-defined benchmark, and calibrates it.* Say it in your own voice rather than leaving it to be inferred.

### 2.3 The sampling measure on radius-two rules

Radius-two rules are drawn uniformly over the 2³² encodings. This is a defensible *statistical* measure and the authors state it clearly (Appendix B). But it is a poor *dynamical* measure: a uniformly random Boolean function of five inputs is overwhelmingly "chaotic-looking", and the region anyone cares about is of vanishing measure. Every radius-two prevalence in the paper, including the 7.8% in Fig. 3, is a statement about a distribution that is dynamically uninteresting.

This is not fatal, but it deserves more than a methods-appendix note, because it interacts with the enrichment problem (§3.6): you force-hold the 57 signature-complex rules precisely *because* the uniform measure barely produces them. A λ-stratified sample (Langton parameter strata, essentially free to draw) would let you report results as a function of table density and would make the radius-two panel far more informative than one enriched draw.

---

## 3. Mathematical and statistical concerns

### 3.1 The matched-regime "result" is an identity, and should be labelled as one

Let the cached target be $Y_1 = \theta + \varepsilon_1$ and let the mechanistic estimator, conditional on exact table recovery, return $\hat{Y} = \theta + \varepsilon_2$ with $\varepsilon_2$ drawn from an independent stream at the same $n_{\text{pairs}}$. Then $\hat{Y}$ and $Y_1$ are *exchangeable*, and $R^2(\hat{Y}, Y_1)$ is the replicate-agreement benchmark exactly — not approximately, not up to a margin. There is nothing to test.

The paper knows this ("run at the target's Monte-Carlo budget it attains the independent-replicate benchmark by construction", Sec. I) and then proceeds to run a pre-registered paired TOST against margins $\max(0.01, 1-\mathrm{ICC}_t)$, reporting six of eight comparisons as formally equivalent and two as resolution-limited. What that analysis actually tests is *implementation correctness* — that the streams are independent, that reconstruction is exact where claimed, that the scoring is unbiased. That is a valuable audit, but it is a checksum, not a finding, and presenting it with equivalence margins and bootstrap intervals invites the reader to believe an empirical question was answered.

**Recommendation.** State the identity in one displayed line. Report the exact-reconstruction rate and the residual attributable to the 2.5% of radius-two failures. Move the TOST apparatus to Appendix A as a correctness audit. This alone recovers roughly a column.

The genuinely non-trivial matched-regime numbers are the ones you almost bury: **97.5% of radius-two rules recovered, 0.990 per-diagram exact-reconstruction rate**, and the four tables missing one entry each. What happens on the 2.5%? Are those failures dynamically benign (unexercised entry that never fires) or catastrophic (wrong entry in the reachable set)? A short analysis of the failure cases is worth more than the equivalence tests.

### 3.2 ICC is a property of the panel, and your panel and your ICC come from different distributions

$\mathrm{ICC} = \sigma_a^2/(\sigma_a^2+\sigma_e^2)$ depends on the between-rule variance $\sigma_a^2$, which is a property of the *rule panel*, not of the target or the estimator. Table I's caption says the reliability columns come from a **250-rule universe sample** and are "applied panel-wide", while the $R^2$ columns are computed on the **enriched 160-rule panel** (35.6% signature-complex versus 7.1% in the universe). These have different $\sigma_a^2$. You are comparing an $R^2$ computed under one distribution to a ceiling computed under another.

The post-stratification in rows 3–4 of Table I fixes the estimator scores but not the benchmark columns, which stay fixed at 0.985/0.993 across all four radius-two rows. That cannot be right: the random subpanel and the enriched panel do not have the same reliability ceiling.

**Required:** recompute the replicate benchmark and ICC *within each panel decomposition*, or drop the reliability columns from the decomposed rows.

### 3.3 The Gaussian identity is disavowed and then used as a decision margin

Sec. II C says survival and cone fill are "markedly heteroscedastic across rules", that you therefore "do not lean on the Gaussian identity", and that ICC(1) is "used descriptively". Sec. IV A then adopts $1-\mathrm{ICC}_t$ as a **pre-registered equivalence margin**. You cannot have it both ways. Under heteroscedastic $\sigma_e^2(\text{rule})$, ICC(1) from a one-way random-effects decomposition is not the attenuation ceiling for any particular rule, and $1-\mathrm{ICC}$ is not a principled margin.

There is a deeper problem with the margin choice regardless of heteroscedasticity: an equivalence margin should encode a *substantively negligible* difference. Setting it to $1-\mathrm{ICC}$ means that the more reliable the target, the harder it is to declare equivalence, even though the practical stakes are unchanged. That is backwards.

### 3.4 A better metric: report everything in units of the target's own Monte-Carlo error

This is my main constructive suggestion on the statistics, and it dissolves §3.2, §3.3 and part of §3.9 at once.

You have $K=20$ replicates per rule. Estimate $\hat\sigma_e(\text{rule}, \text{target})$ directly, per rule, and report

$$\rho \;=\; \frac{\mathrm{RMSE}(\hat{Y}, Y_1)}{\hat\sigma_e}$$

Then:

- The simulation-limited benchmark is **exactly $\rho = \sqrt{2}$**, per rule, per target, with no variance decomposition and no Gaussian identity required.
- The latent ceiling is **exactly $\rho = 1$**.
- $\rho$ is invariant to panel composition, so enrichment and post-stratification stop mattering for the benchmark.
- Heteroscedasticity is handled pointwise instead of being averaged away.
- $\rho$ has an interpretation a practitioner can act on ("this estimator is 1.4 replicate-noise units off") that $R^2$ does not.

$R^2$ can stay as a secondary column for comparability with the literature. But $\rho$ should be the primary quantity, and I suspect it will make the frontier figures far more legible than the current $R^2$ curves that dive to $-5.6$.

### 3.5 Three of your four targets are algebraically dependent

This one needs checking before publication. From Appendix B:

- fraction $= \mathbb{E}[\bar d \mid \text{surv}] = \mathbb{E}[N/w]$
- rate $= \mathbb{E}[\mathrm{ext}(d)/(2rT)]$
- fill $= \mathbb{E}[N/\mathrm{ext}(d)]$

so that, up to Jensen,

$$\text{fill} \;\approx\; \frac{w}{2rT}\cdot\frac{\text{fraction}}{\text{rate}} \;=\; 1.058\,\frac{\text{fraction}}{\text{rate}} \quad (r=2),\qquad 1.024\,\frac{\text{fraction}}{\text{rate}} \quad (r=1).$$

If the ratio-of-expectations approximation is tight — and with 256 pairs it may well be — you do not have four targets, you have roughly two and a half. This has consequences throughout:

- The four-target median in Table I is a median over partly redundant coordinates.
- The per-target $R^2$ columns in Tables II–III are not four independent pieces of evidence.
- It explains, mechanically, why cone fill has the lowest ICC (0.980 vs 0.998) and why the CNN does worst on it ($0.337 \pm 0.109$): a ratio estimator inherits the noise of both its parts.
- It explains why cone fill and spreading rate look like they trace a curve in Fig. 3.

**Required:** report the empirical scatter of fill against $1.058\cdot\text{fraction}/\text{rate}$ across your panel. If $R^2 > 0.95$, either drop cone fill or state explicitly that it is a derived coordinate.

### 3.6 Figure 3's two axes may be coordinate artifacts

Following on: Fig. 3 plots cone fill against spreading rate, and reads a "band between the ordered arm and the chaotic bulk". But by the relation above, at fixed damage count $N$ the two coordinates trace a hyperbola $\text{fill} \propto 1/\text{rate}$. The visible ordered arm (low rate, high fill) and chaotic bulk (high rate, moderate fill) are precisely what a family of iso-$N$ hyperbolae with $N$ increasing along the family looks like.

**Required:** overlay iso-$N$ contours on Fig. 3, or re-plot in decorrelated coordinates — e.g. spreading rate against $N/(2rT)$ (normalised damage count), which is not mechanically tied to extent. If the red band survives decorrelation as a genuine cluster, the figure becomes a real result; if it does not, it is a parametrisation.

### 3.7 Cone fill is degenerate at the sparse end

$\mathrm{ext}(d)=1$ for a single surviving damaged cell, so fill $=1$. The axis label in Fig. 3 reads "low = gliders, high = solid", but a rule whose damage collapses to one cell scores at the *top* of the axis, indistinguishable from a solid cone. Rules 204 and 184 sitting at (0, 1.0) in Fig. 3 are exactly this degenerate case. Either regularise (e.g. $N/\max(\mathrm{ext}, c)$ for some floor, or report $N$ and $\mathrm{ext}$ separately) or restrict the fill statistic to trials with $\mathrm{ext} > 1$ and report the exclusion rate.

### 3.8 The spreading rate cannot reach 1

$\mathrm{ext}(d) = \max_i p_i - \min_i p_i + 1$, so the light-cone maximum is $\mathrm{ext} = 2rT+1$ and hence $\text{rate}_{\max} = 1 + 1/(2rT) = 1.0083$ at $r=2$, $1.0081$ at $r=1$. Sec. II B says "so 1 is light speed at any radius" and Fig. 3's axis label says "1 = light speed". This is false as defined. Use $\mathrm{ext}(d)-1$ in the numerator, or $2rT+1$ in the denominator. Trivial to fix, but a referee will catch it and it costs credibility on a paper that asks to be judged strictly on its metrology.

### 3.9 The ECA and radius-two protocols have different horizons

$T = \lfloor w/(2r)\rfloor - 1$ gives $T = 62$ for ECA and $T = 30$ for radius two. These are different experiments. Survival at $T=62$ and survival at $T=30$ are not comparable quantities, yet the paper compares them freely — most consequentially in Sec. IV H, where the radius-two prevalence of 7.8% (at $T=30$) is set against 3/88 ECA orbits (at $T=62$) and read as "a radius-two analogue of Li and Packard".

Damage survival is monotone decreasing in horizon; a longer horizon kills more marginal rules. The cross-space prevalence comparison is confounded. Either match horizons (run ECA at $T=30$ as a control) or drop the comparison.

### 3.10 The pseudo-posterior's independence assumption is violated even at zero noise

The A3 log-odds

$$\ell_k = \log\frac{p_0}{1-p_0} + (2\,\text{ones}_k - \text{total}_k)\log\frac{1-\varepsilon}{\varepsilon}$$

treat the $\text{total}_k$ transitions at entry $k$ as independent Bernoulli trials. They are not, and the dependence is structural, not a noise artifact:

- Every cell $s_{t,i}$ appears as the *output* of one transition and as an *input* of $2r+1$ others.
- Overlapping neighbourhoods within a row share $2r$ of $2r+1$ bits.
- Under bit-flip noise a single corrupted cell corrupts $2r+1$ input bins *and* one output bin, in a correlated way.

The paper acknowledges only the last of these ("input-side corruption is deliberately not modelled; it is absorbed into the effective $\varepsilon$"). But absorption into $\varepsilon$ addresses *bias*, not *count inflation*. With $\sim$16,000 transitions over 32 entries, $\text{total}_k \approx 500$, and your own worked example produces $\ell \approx 77$. That is a posterior with certainty $1 - 10^{-33}$ from data with an effective sample size perhaps an order of magnitude smaller than the nominal count. The calibration collapse you measure on the noise axis (coverage 0.58 at 2%, 0.13 at 20%) is exactly what an unmodelled effective-sample-size inflation produces.

**Two fixes, in increasing order of effort:**

1. **Effective sample size.** Divide counts by an overlap factor estimated from the neighbourhood-sharing structure, or fit an overdispersion parameter. Cheap, and would likely fix the calibration numbers without changing the point estimates much.
2. **Marginalise the latent clean diagram.** You name this as "the natural untested repair" and then run the whole noise axis without it. This is a factor graph with known structure: latent clean diagram $\mathbf{s}$, observed $\tilde{\mathbf{s}}$ with iid flips, deterministic CA factors linking rows given the table $\mathbf{b}$. Gibbs sampling alternating $(\mathbf{s} \mid \tilde{\mathbf{s}}, \mathbf{b})$ and $(\mathbf{b} \mid \mathbf{s})$, or EM, is a standard construction on a $127\times127$ binary lattice and is not expensive.

The second point is a **threat to the paper's headline frontier result**, and I want to be blunt about it. The "noise dead zone" and the "posterior-to-network crossover at 3–7.5%" are claims about *the estimators you happened to build*. The correct read-then-simulate estimator under bit-flip noise is the one that models the flips, and you did not build it. Your rev-10 controls already reversed one rev-9 conclusion by adapting the direct network; a correctly specified likelihood may well reverse the other by adapting the mechanistic route. Sec. IV F(i) says as much in a single hedged sentence ("the noise-band verdicts below therefore bound the estimators evaluated, not the read-then-simulate family") — this should be in the abstract, or the experiment should be run.

### 3.11 The $\varepsilon$ self-consistency estimator is biased

$D = \sum_k \min(\text{ones}_k, \text{total}_k - \text{ones}_k)/\sum_k \text{total}_k$ estimates the minority fraction. For entries with $\text{total}_k = 1$ the contribution is identically zero; for small counts it is downward-biased in general. These are exactly the sparsely-exercised entries where the posterior matters. Report the bias against known $\varepsilon$ on the grid — you have supplied-$\varepsilon$ runs, so the comparison is already available, and Sec. IV F(i) claims they "match throughout" without showing the estimator's calibration. Show $\hat\varepsilon$ against $\varepsilon$ directly.

Related: on the *masking* axis $D \approx 0$, so $\hat\varepsilon$ pins to the grid floor of 0.005. That is presumably harmless, but the same statistic drives radius selection (A4), where $D$ at the wrong radius is inflated by *aliasing*, not by noise. Using one statistic for two different jobs deserves a sentence.

### 3.12 The radius-selection rule is unmotivated

A4 selects the smallest $r$ whose $D$ is within 0.005 of the minimum. $D$ is non-increasing in $r$ under nesting (a larger neighbourhood can always explain at least as much), so this is a model-selection problem with a magic-number tolerance and no complexity penalty — and the tolerance happens to equal the floor of the $\varepsilon$ grid, which looks like coincidence rather than design.

**Replace with something principled.** The entrywise Beta–Bernoulli model you already have supplies a marginal likelihood, and the parameter count $2^{2r+1}$ gives you a description-length penalty for free. A proper MDL/marginal-likelihood criterion would both justify the choice and probably reduce the reported $\sim$0.12 median-$R^2$ cost of radius selection.

### 3.13 Incremental $R^2$ is not interpretable when the base $R^2$ is negative

Table IV's caption notes that "percentile intervals of an increment may exceed 1 when a bootstrap draw's base $R^2$ is negative", and Sec. IV E reports mechanistic medians of $-0.77$ and $-5.6$. Once a base is negative, ratios and increments of $R^2$ stop having a scale. The clipping of frontier bootstrap draws to $[-1,1]$ "for the median CI" (Appendix B, item 3) is a further undisclosed-in-effect estimator modification that biases the interval.

Reporting in $\rho = \mathrm{RMSE}/\hat\sigma_e$ units (§3.4) removes this entirely: $\rho$ is bounded below by 0, has no sign pathology, and needs no clipping.

### 3.14 $R^2$ on a bimodal target rewards mode assignment

ECA survival has Monte-Carlo SD 0.022 at $n_\text{pairs}=256$ and ICC 0.994, implying a between-rule SD around 0.28 — consistent with a strongly bimodal distribution (most rules near 0 or near 1). For such a target, $R^2$ is dominated by whether the estimator puts each rule in the right mode; the interesting question — resolution *within* the intermediate band — is invisible.

The CNN's 0.700 on ECA survival probably means "gets ordered/chaotic right, is useless in between", and the mechanistic 0.985 means "is right". Those are different claims from what $R^2$ appears to say. **Add a stratified report**: $R^2$ or $\rho$ restricted to rules with survival in, say, $[0.1, 0.9]$, alongside a classification metric for the mode. This would make Sec. IV C's complementarity finding (+0.32 incremental $R^2$ on survival) far more informative — is the network resolving the middle, or just calling the mode?

### 3.15 Power, and asymmetric evaluation of the estimator families

Several issues compound:

- **The ECA panel has 18 held-out orbits.** A cluster bootstrap with 18 units and $10^4$ resamples does not manufacture information; percentile coverage at $n=18$ is poor. Most ECA verdicts are "inconclusive" for this reason alone, and the paper says so, but the panel then still supplies half of the headline table.
- **The CNN gets one split with five seeds; the deterministic methods get leave-one-orbit-out and 20 repeated outer splits.** ECA CNN training is $\approx$10 min/seed; leave-one-orbit-out over 88 orbits is $\approx$15 hours on one machine. That is affordable and should be run.
- **The enrichment penalises the learned estimators specifically, and post-stratification does not fix it.** Force-holding all 57 signature-complex rules means the CNN is *trained* on a distribution that contains no complex rules and *tested* on one that is 35.6% complex. That is a covariate-shift experiment, not a held-out-rule experiment. The mechanistic estimator is shift-invariant by construction, so the enrichment is a one-sided handicap. Post-stratification reweights the *evaluation*; it cannot undo the *training* distortion. The right control is a CNN trained on a stratified split (no force-holding) and evaluated on random held-out rules. Without it, the headline gap between families is overstated by an unknown amount.

### 3.16 The frontier figures need their own ceilings drawn

Fig. 1 sweeps at $n_\text{pairs}=64$, Fig. 2 at 48, against production targets at 256. The replicate-agreement benchmark on those panels is therefore substantially below 1 and strongly target-dependent. Taking your Table III ICCs and scaling $\sigma_e^2 \propto 1/n$:

| radius-2 target | $2\,\mathrm{ICC}-1$ at $n=256$ | at $n=64$ | at $n=48$ |
|---|---|---|---|
| damage survival | 0.974 | 0.900 | 0.869 |
| damage fraction | 0.997 | 0.984 | 0.979 |
| spreading rate  | 0.997 | 0.984 | 0.979 |
| cone fill       | 0.959 | 0.849 | 0.804 |

So the clean-cell ceiling in Fig. 2 sits near 0.80–0.98 depending on target, not at 1.0. Table V then quotes frontier numbers ("0.55 vs det 0.38 at 2%") next to matched-regime numbers (0.99) as if they were on the same scale. **Draw the panel-specific benchmark as a horizontal reference on every frontier figure**, and state in Table V's caption that its numbers are on the reduced-budget scale. Also clarify whether the frontier targets were recomputed at reduced budget or scored against the 256-pair cache — the text is ambiguous and the two give different ceilings.

### 3.17 Seed variance of a factor of two is a training-protocol artifact, not a finding

Sec. IV F(iii) reports the degradation-trained CNN at 0.51–0.62 (seed 0), 0.49–0.56 (seed 2), and 0.24–0.33 (seed 1), attributes the spread to "final-epoch selection" with validation medians swinging by $\pm 0.2$ between late epochs, and then propagates "expect $\sim 2\times$ run-to-run variance at this budget" into Table V as practitioner guidance.

The protocol is 60 epochs, AdamW, **no early stopping**, final-epoch weights. Under heavy augmentation with an oscillating validation curve, this is a known failure mode with a standard fix: validation-based checkpoint selection, or EMA/SWA weight averaging. Reporting the resulting instability as a property of the estimator family, when it is a property of taking the last epoch, is not defensible — particularly in a paper whose thesis is that baselines must be constructed carefully before conclusions are drawn about them. The same standard you apply to the mechanistic estimator (build the strong version) should apply here.

**Rerun with checkpoint selection.** If the spread persists, it is a finding. If it collapses, Table V's central caveat disappears and the frontier guidance becomes much cleaner.

### 3.18 Registration through revision 12

I want to be fair here: labelling every analysis registered / post-hoc confirmatory / exploratory is more honest than most of the literature, and the paper deserves credit. But a registration amended twelve times, held in a private repository, with the labels assigned by the authors, and with revisions 9–11 written *in response to referees who had already seen the earlier numbers*, is not pre-registration in the sense the word normally carries. "Registered numbers-free before measurement" cannot be verified from outside, and referee exposure to prior results contaminates the numbers-free claim in a way no protocol can fix.

I would **not** ask you to drop the practice. I would ask you to stop letting it do rhetorical work in the main text. The `[registered, rev. N]` tags appear roughly thirty times in Secs. II–IV; they are a significant readability tax and they signal an authority the private repo cannot back. Move the whole apparatus to Appendix A (where it already lives, well written), keep at most a single sentence in the main text pointing to it, and let the numbers stand on their own.

### 3.19 The cost analysis is implementation-bound

283 ms per diagram for the mechanistic estimator at 256 pairs on one CPU core. A $127\times127$ radius-two CA with 256 twin runs is roughly $2 \times 256 \times 30 \times 127 \approx 2\times10^6$ cell updates. In bit-packed form a 127-cell ring fits in two `uint64` words and 64 independent runs can be evolved in parallel per word with a handful of bitwise operations. An optimised implementation is plausibly two orders of magnitude faster, which would move the break-even from $\approx 4700$ queries to $\approx 50$ and eliminate the network's cost argument entirely.

This *strengthens* your conclusion, so there is no reason not to say it. But as written, Sec. IV G presents an implementation timing as an algorithmic property. Either implement the bit-parallel version (a day's work, and it would let you raise $n_\text{pairs}$ on the frontier panels too) or state clearly that 283 ms is a first-party Python figure and the algorithmic floor is far lower.

### 3.20 Smaller mathematical points

- **Default-0 completion and ties-to-0 majority** are both biased toward quiescence, which biases reconstructed survival downward. You compare default-0 / default-1 / empirical completions on *clean* data (differences in the fourth decimal) but not under degradation, where coverage is low and the prior actually binds. Run the comparison on the masking and density axes.
- **"identifies the table from as few as 4 rows"** (Fig. 1a) should say *median*. The mechanism is coupon collection on the $t=0$ row: under Bernoulli(1/2) ICs the 5-cell window is uniform over 32 entries, and coupon collection needs $32 H_{32} \approx 130$ draws against 127 available per row. So two rows suffice typically and ordered rules that freeze immediately never get there. Stating the mechanism turns Fig. 1(a) from an empirical curve into a one-line calculation — and lets you cut the panel (see §6).
- **"survival is a finite-horizon proxy for the sign of the maximal Lyapunov exponent"**: the Bagnoli–Rechtman–Ruffo construction (ref. 14) defines the exponent from the *defect multiplication rate*, which is closer to your fraction/rate than to survival probability. Survival is a proxy for *positivity of the damage measure*, which is related but not the same object. Tighten the wording.
- **"never distinguishable in the unfavourable direction"** appears twice as a headline phrase. It rests on two underpowered tests out of eight, both failing in the favourable direction. With $n=18$ on one of them, this is a post-hoc reading of noise. Soften.
- **$2^{2^3} = 256$** renders as "22 3 = 256" in the PDF; check the LaTeX.

---

## 4. What is genuinely good and should be kept

So that the report is not read as uniformly negative:

- **Sec. II C's three-benchmark distinction** is the paper's real conceptual contribution and is correct. The $2\,\mathrm{ICC}-1$ versus $\mathrm{ICC}$ distinction is exactly the kind of thing the amortisation literature gets wrong, and stating it cleanly is worth doing. (See §3.4 for a reformulation I think is strictly better, but the idea is right.)
- **Sec. IV D, retiring the anti-shortcut claim.** Reporting that your own architectural intervention failed, with probes that quantify the failure, is the correct scientific move and I hope it survives revision. (I would add one sentence noting it was foreseeable: a $2\times2$ window at $(t,i),(t,i{+}1),(t{+}1,i),(t{+}1,i{+}1)$ already contains two of three ECA input bits and an output bit; two such windows compose in layer 2.)
- **Table VI (Appendix D)**, the prior-work-by-assumptions table. This is the clearest statement of the paper's novelty boundary anywhere in the manuscript and should arguably be promoted into the main text.
- **The distinction between "the network carries survival information" and "a practitioner can buy it"** (Sec. IV C, +0.32 within-panel diagnostic versus +0.001 deployment stack). This is exactly the kind of honesty that is usually missing, and it is the most interesting empirical result in the paper.
- **Sec. IV F(iii)'s fairness controls**, which reverse one of your own registered conclusions. Keep.

---

## 5. Suggested new directions

### 5.1 Run the benchmark on a *stochastic* generator — this is the experiment the paper is missing

The Discussion dismisses this in three lines: "a stochastic generator changes the problem in kind — single-diagram identification no longer reduces to transition tabulation, and the replicate benchmark becomes the operative ceiling — so nothing here licenses conclusions for that case."

That is precisely the argument for doing it. In the deterministic case your thesis is a near-identity (§3.1). In the probabilistic case it becomes a real question:

- The generator is a table of probabilities $\pi_k = \Pr[s_{t+1,i}=1 \mid k]$ rather than bits.
- Single-diagram identification gives a *noisy* estimate of $\pi$, so read-then-simulate is no longer optimal by construction — it has genuine estimation error that trades off against a direct estimator's.
- **Your A3 pseudo-posterior is already the right estimator for this case.** It is a Beta–Bernoulli posterior over $\pi_k$; you built it as a noise model and it is natively a stochastic-rule model. The $\varepsilon$ machinery drops out entirely.
- The independence-approximation problem (§3.10) is *much* milder, because in the stochastic case the outputs really are conditionally independent given the inputs — only the input-side window overlap remains.
- The frontier acquires a natural extra axis: stochasticity level, interpolating continuously from the deterministic case (your current paper) to the fully-noisy case where identification must lose.

Domany–Kinzel is the obvious family: two parameters, well-studied phase diagram, embeds deterministic ECA exactly at the corners, and the damage-spreading literature on it is extensive. The cost is a modest extension of code you already have.

I would go further: **this could be the paper.** "Here is exactly where along the determinism axis the identification baseline stops dominating" is a result. "Under a deterministic generator the identification baseline dominates" is a corollary of Richards–Meyer–Packard 1990.

### 5.2 Build the correctly specified noisy-observation decoder

See §3.10. Gibbs or EM over latent clean diagrams. This is the single most likely thing to change a headline conclusion, and leaving it as future work in a paper whose thesis is "construct the strong baseline before you conclude" is an uncomfortable position to be in.

### 5.3 Two missing baselines that would sharpen the shortcut-learning story

- **Retrieval / kNN.** With 640 training rules $\times$ 64 diagrams, a nearest-neighbour lookup in the five-statistic space (or in the CNN bottleneck) that returns the *cached target of the nearest training rule* costs nothing. Its performance tells you how much of the CNN's $R^2$ is "recognising which training rule this resembles" versus genuine generalisation to unseen tables. Given the shortcut-learning framing, this is the diagnostic the paper wants and does not have.
- **Identify-then-look-up.** Reconstruct the table, then return the *cached* target if the rule is in the training set, and simulate only otherwise. On held-out rules this is identical to the mechanistic estimator, but running it on *training* rules cleanly separates the identification component from the simulation-budget component of the cost hierarchy, which the paper currently conflates.

### 5.4 Joint corruption axes

Table V's caption concedes that "each axis was swept singly: joint corruptions (noisy and masked, say) were not tested, and the per-axis recommendations are not established to compose." A $3\times3$ grid over (noise, masking) at your existing budgets is a small extension and would either validate the guidance or show it does not compose — either outcome is more useful than the disclaimer.

### 5.5 A cleaner presentation of the central claim

Consider a single figure that carries the paper: $\rho = \mathrm{RMSE}/\sigma_e$ on the $y$-axis (log scale, with horizontal lines at $\rho=1$ and $\rho=\sqrt2$), simulation budget on the $x$-axis, one curve per estimator family, with the mechanistic family shown as the budget-indexed family it is. The direct estimators appear as horizontal lines. That figure states the paper's thesis, the benchmark distinction of Sec. II C, and the cost analysis of Sec. IV G all at once, and would let you delete a substantial amount of prose.

---

## 6. What to cut

The manuscript is dense to the point of being hard to read; several sections carry very little per column. My suggestions, roughly in order of confidence:

| Target | Action | Recovered |
|---|---|---|
| Sec. IV A equivalence apparatus | Move TOST to Appendix A as a correctness audit; keep the reconstruction rates and a one-line identity | ~0.8 col |
| Sec. IV G, annealed zero-budget member | **Delete.** A mean-field approximation for asymptotic damage density, scored against finite-horizon conditional statistics on a 127-ring, returns $R^2=-2.15$. That is a straw comparison — it establishes that an inapplicable approximation is inapplicable. If you want to keep it, calibrate it first (isotonic recalibration on training rules would likely recover a lot, and *that* would be interesting) | ~0.5 col |
| Sec. IV H, localised-seed glider detector | **Delete.** Balanced accuracy 0.39 and precision 0.05 on radius two; sensitivity 0.5 on ECA. An instrument that performs at or below chance establishes nothing, and the paper already says so. One sentence in the Discussion suffices | ~0.4 col |
| Sec. IV H, composed-system maps | Move to the repository. The result is explicitly inconclusive ($\Delta=+0.047$, CI $[-0.002,+0.102]$) and the section spends a paragraph plus an appendix on a null | ~0.4 col |
| Fig. 1(a), observation-length axis | Replace with the coupon-collector calculation (§3.20). Two rows suffice by construction | 1 panel |
| Fig. 2, label-polarity panel | Replace with one sentence: the read-then-simulate family is exactly invariant; the CNN is not. Four flat lines do not need a panel | 1 panel |
| Constrained CNN | Demote to appendix and promote `resnet18` to the direct baseline of record. You retired the anti-shortcut claim; the architecture's only remaining role is historical, and carrying it through Tables I–IV and Fig. 2 costs a column of exposition across the paper | ~0.5 col |
| Table I, four-target medians | Delete the median-over-targets column entirely. A median of four values is the mean of the middle two; you warn against this summarisation and then use it as the headline table | table |
| `[registered, rev. N]` inline tags | Move to Appendix A (§3.18) | ~0.3 col |

Total: roughly two columns, which is close to what the stochastic-generator experiment (§5.1) or the correctly-specified noise decoder (§5.2) would need.

Two things I would **not** cut, in case the length pressure tempts you: Sec. IV C's deployment-stack negative result, and Sec. IV F(iii)'s fairness controls.

---

## 7. Presentation

- **Figure axis labels are broken** in the compiled PDF: Figs. 1 and 2 render the $y$-label as "m e dia n h eld-o ut R 2". Check the font/rotation setup.
- **Fig. 2** repeats an eight-entry legend in all four panels. Use one shared legend outside the axes; you will recover most of the plot area, which those curves badly need.
- **Fig. 3** stars are unlabelled in the legend; the rule numbers 204/184 overlap at the top left.
- **The abstract is a single 250-word paragraph** with five distinct claims, three parenthetical qualifications, and two nested clauses of statistical caveat. It is accurate and nearly unreadable. Split it, and lead with the frontier rather than the identity.
- **Sec. IV F is 2.5 columns of continuous prose** covering four estimators, three registered hypotheses, two fairness controls, a panel replication and a seed replication. It needs subheadings or a summary table at the top.
- **"pseudo-posterior"** is introduced mid-paragraph in Sec. IV F(i) after the object has already been called "an approximate Bayesian rule decoder", "a rule-posterior simulator" and "the Bayesian posterior" in three preceding places. Fix the naming once and use it consistently, including in Fig. 2's legend (`f1_eps_known` / `f1_eps_estimated` are not names a reader can follow).

---

## 8. Summary of required changes

**Must fix before publication:**

1. State the matched-regime result as the identity it is; move the equivalence apparatus to an audit appendix (§3.1).
2. Recompute reliability benchmarks within each panel decomposition (§3.2).
3. Resolve the ICC-disavowed-then-used-as-margin inconsistency (§3.3).
4. Report and address the algebraic dependence among fraction, rate and fill (§3.5).
5. Decorrelate or annotate Fig. 3's axes (§3.6).
6. Fix the spreading-rate normalisation (§3.8).
7. Draw panel-specific benchmarks on the frontier figures and clarify their scoring budget (§3.16).
8. Rerun the degradation-trained control with checkpoint selection before reporting factor-2 seed variance as practitioner guidance (§3.17).
9. Add the CNN trained without force-holding, or downgrade the family-gap claim (§3.15).
10. Match ECA and radius-two horizons before comparing prevalences (§3.9).

**Strongly recommended:**

11. Report primary results in $\mathrm{RMSE}/\sigma_e$ units (§3.4).
12. Build the correctly-specified noisy-observation decoder, or state its absence prominently in the abstract (§3.10, §5.2).
13. Add a stochastic-generator arm (§5.1).
14. Add the retrieval baseline (§5.3).
15. Cut per §6.

---

*I have read the manuscript closely and my criticism is proportional to how seriously I take it. The three-benchmark distinction, the retired anti-shortcut claim, and the deployment-versus-diagnostic stacking result are all things I would like to see in print. My hesitation is that the paper currently spends most of its space proving something that follows from its own construction, while the part that would justify the framing — the frontier — is the part carrying single seeds, one panel, and an estimator family that was never given its strongest member.*
