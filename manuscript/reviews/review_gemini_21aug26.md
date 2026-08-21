# Peer Review Report

**Title:** Rule reconstruction from a single spacetime diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata  
**Authors:** Michiel Rollier and Jan M. Baetens  
**Reviewer Profile:** Machine Learning, Dynamical Systems, and Cellular Automata (CA)

## 1. General Assessment: A Bitter Pill the ML Community Needs to Swallow

Let me begin by stating that I read dozens of manuscripts a month where deep learning is carelessly thrown at dynamical systems, partial differential equations (PDEs), and physics simulations. Invariably, these papers declare victory over some arbitrary baseline while fundamentally ignoring the mechanistic realities of the system. This manuscript is a desperately needed, highly rigorous, and intellectually sobering slap in the face to that entire subfield [cite: 2].

The authors have formalized a truth that should be self-evident to anyone with a background in complex systems: if an observation contains enough information to perfectly reconstruct the generating mechanism, then extracting that mechanism and running a simulation will trivially dominate any amortized neural network [cite: 1, 2]. By proving this on a finite-horizon damage response task for elementary and radius-two Cellular Automata, the authors expose deep learning's tendency toward shortcut learning and memorization [cite: 1]. 

However, my enthusiasm for the scientific rigor of this paper is severely tempered by my frustration with its pedagogical presentation. As an educator, I am appalled that a paper dissecting the "phenotype" of visual spacetime diagrams and damage cones fails to include a single diagram of the actual phenomena [cite: 1, 2]. It is scientifically airtight, but pedantically and structurally impenetrable. 

## 2. The "So What?": Scientific Significance and Impact

The most commendable aspect of this manuscript is its meta-scientific contribution. The authors ask the "So what?" question directly of the simulation-based inference community [cite: 1]. 

*   **Exposing the Illusion of Skill:** The ML community loves the $R^2$ metric. The authors brilliantly demonstrate how deceptive this is. A Convolutional Neural Network (CNN) achieves an $R^2$ of 0.98 on the elementary CA spreading rate, which an ML reviewer would typically rubber-stamp as "state-of-the-art" [cite: 1]. By introducing the $\rho$ metric—which measures error in units of the target's own Monte-Carlo noise—the authors reveal that this 0.98 score is actually $\rho=20$, or twenty times the noise floor [cite: 1, 2]. The mechanistic model sits at $\rho \approx 1.41$ [cite: 2]. This single analytical framing is a masterclass in proper baseline calibration.
*   **Mode Assignment vs. Regression:** The paper demonstrates that the learned models are essentially acting as classifiers, correctly identifying "dies out" versus "spreads," but failing completely to resolve intermediate rules (scoring worse than the band mean) [cite: 1, 2]. This completely undermines the utility of direct amortization for dynamical behavior forecasting.
*   **The Identifiability Frontier:** By mapping where the exact mechanistic reconstruction breaks down (e.g., beyond 5% bit-flip noise, 25% masking, or extreme initial-condition densities), the authors provide a rigorous map of when ML actually becomes useful [cite: 1, 2]. It is a rare paper that accurately maps the boundaries of its own baseline.

## 3. Methodological Scrutiny: The Good, the Bad, and the Missing

The methodological hygiene here is exemplary. The pre-registration of decision rules, margins, and the handling of the 57 force-held "signature-complex" rules prevents data snooping [cite: 1, 2]. The stacking and retrieval diagnostics (showing the CNN operates essentially as a nearest-neighbor lookup in its bottleneck) are elegant and devastating [cite: 1, 2].

However, I have significant critical reservations regarding the limits of the models tested:

1.  **The "Missing" Probabilistic Decoder:** The authors themselves admit to a major omission: they did not build the correctly specified probabilistic decoder for noisy diagrams (marginalizing the latent clean diagram via Gibbs sampling or Expectation-Maximization) [cite: 1, 2]. Instead, they rely on an entrywise pseudo-posterior that becomes wildly overconfident (nominal 68% intervals covering only 13% at 20% noise) [cite: 1, 2]. If you are going to critique ML for cutting corners, you cannot cut corners on your own mechanistic repair strategy. The noise-regime conclusions are therefore bounded *only* to the specific estimators tested, weakening the universality of the "frontier."
2.  **Architectural Scope of the Neural Baseline:** The authors test a 31,524-parameter constrained CNN and an unconstrained ResNet18 (11 million parameters) [cite: 1, 2]. While the ResNet18 failed to change the verdict [cite: 1, 2], I remain unconvinced that this definitively closes the book on deep learning for this task. What about modern sequence models, transformers, or graph neural networks that might better capture the permutations and causal light-cones of CA evolution? The authors correctly state they do not claim deep networks *cannot* close the gap [cite: 1, 2], but ML reviewers will undoubtedly attack the choice of a standard CNN as a "weak" neural baseline.
3.  **The Asymptotic Cop-Out:** The authors are careful to state their results are bounded by the specific protocol (ring of 127, 127 steps) because the asymptotic classification of Wolfram classes is formally undecidable [cite: 1]. While mathematically true, this limits the paper's reach. Are these finite-horizon proxy metrics actually useful for anything beyond proving ML models fail at them?

## 4. Pedagogical and Presentational Failures (Major Revisions Required)

I cannot overstate how frustrating this manuscript is to read. The authors have produced an accompanying "plain-language summary" [cite: 2], which is an implicit admission that the main text is a dense, jargon-laden slog.

1.  **A Complete Lack of Visual Intuition:** You are analyzing the phenotypic behavior of cellular automata. You are measuring "damage survival," "spreading rate," "damage fraction," and "cone fill" [cite: 1, 2]. **How is it possible that there is not a single image of a spacetime diagram or a damage cone in the entire manuscript?** You are demanding the reader visualize a 127x127 Boolean grid, a perturbed twin run, and the resulting intersection cone entirely in their head. This is pedagogical malpractice. You *must* include a figure showing:
    *   A clean spacetime diagram.
    *   A twin run with a single perturbed cell.
    *   The resulting difference diagram highlighting the damage cone, with visual annotations for extent, fraction, and fill.
2.  **Dense, Unbreathable Prose:** Sentences run on for lines at a time. The table captions are practically mini-essays (see Table IV and Figure 3) [cite: 1]. The text feels written for an audience of five people who have spent thirty years studying CA system identification. If you want the modern ML community to read this and change their habits, you must write for them. Integrate the clear, punchy takeaways from your plain-language summary directly into the abstract and introduction of the main paper [cite: 2].
3.  **Figure 3 (The Landscape):** It is a scatter plot that relies on a threshold criterion that you admit is "substantially a coordinate effect" [cite: 1, 2]. It is interesting, but without visualizing the actual gliders or structures in that 7.8% region, it is just abstract data points [cite: 1, 2].

## 5. Conclusion and Recommendation

This is a scientifically excellent paper buried in a terrible presentation. The meta-scientific point is too important to be lost in dense prose. 

**Recommendation:** Accept with Major Revisions.

**Required Actions for the Authors:**
1.  **Add Visualizations:** Introduce a minimum of two figures explicitly illustrating the CA spacetime diagrams, the twin-run perturbation protocol, and the geometries of the damage metrics. 
2.  **De-jargon the Text:** Migrate the clarity of the plain-language summary into the main manuscript. Break up the monolithic paragraphs. 
3.  **Clarify the Neural Limits:** Explicitly address why a CNN/ResNet was the chosen boundary for the neural baseline and discuss whether attention-based mechanisms might bypass the shortcut learning observed.
4.  **Acknowledge the Missing Decoder Prominently:** Move the admission about the unbuilt probabilistic decoder (marginalizing the latent clean diagram) from the discussion directly into the results section where the noise frontier is presented [cite: 1]. Readers must know immediately that the mechanistic baseline in the noise regime is handicapped by this approximation.
