# Primordia Experiments — Findings Log

## Test 1 — Single Attractor Dynamics

**What we expected:** Multiple attractor basins with spontaneous transitions between them. A system that settles into stable modes without being told to, with those modes being interesting and varied.

**What actually happened:** The system crystallized into a single deep attractor within ~10 time units. All 64 dimensions independently snapped to one of the two double-well equilibria (±1.414) and stayed there permanently. Effective dimensionality collapsed to 2. Zero basin transitions. The recurrent coupling (W at scale 0.05) was negligible against the potential gradient, and each dimension behaved as an independent bistable switch.

**What felt different vs what was just different numbers:** The speed of crystallization was striking. The system didn't gradually settle — it slammed into place. Looking at the phase portrait, there's a single sharp curve from start to end with the entire rest of the simulation compressed into a single dense point. It feels like a system that found death, not stability. The difference between "stable" and "dead" is whether there's any remaining sensitivity to perturbation, and this system has essentially none (noise at 0.02 can't cross barriers of ~1.0).

**Which direction this points for the architecture:** The potential energy landscape matters enormously. A separable per-dimension potential (each dimension independent) produces trivially boring dynamics regardless of the recurrent structure. For cognitive-like dynamics, we need either: (a) coupling strong enough to compete with the potential, creating a tug-of-war between local stability and global influence, or (b) a non-separable potential where the energy depends on relationships between dimensions, not just individual dimension values. The latter is more interesting architecturally — it means the "physics" of the system is inherently relational. This connects to the persistent state question in Test 2: if state persistence requires a potential landscape, that landscape must be shallow enough to allow ongoing dynamics, not deep enough to freeze everything.

---

## Test 2 — Persistent Non-Resetting State

**What we expected:** An entity that develops habits — inputs that once caused large state changes gradually causing smaller ones. Category-specific sensitivity changes. Something like character emerging from accumulated experience. State trajectory forming distinct regions in UMAP, corresponding to different "modes of being."

**What actually happened:** The entity became a monument. State norm exploded from 0 to ~68 in the first ~100 interactions, then saturated completely. After saturation, sensitivity dropped 4.4x and became uniform across all input categories. Response consistency between t=100 and t=999 was perfect (cosine similarity = 1.000). The entity didn't develop habits — it developed rigor mortis. Effective dimensionality collapsed to 1 (PC1 = 99.0%). The trajectory is a single curve from origin to a fixed point, with the remaining 900 interactions producing imperceptible movement.

**What felt different vs what was just different numbers:** The sensitivity plot is striking. There's a brief window (~50 interactions) where the entity is genuinely responsive — each input creates visible state changes, different categories push in different directions. Then the window slams shut. It's like watching something alive become a statue. The mathematical reason is clear (||S|| grows until inputs are negligible), but the visual impression is of a system that had a brief childhood and then froze into permanent adulthood. The probe responses at t=100, t=500, and t=999 being identical to 4 decimal places despite 900 intervening interactions is eerie — it means nothing that happened to the entity after t=100 matters at all.

**Which direction this points for the architecture:** Persistence without bounded magnitude is death — the same finding as Test 1, expressed differently. Test 1 crystallized because the potential was too deep. Test 2 crystallized because the state grew too large. In both cases, the system found a way to make itself immune to influence. For persistent state to be interesting, the state must be normalized or bounded, and the update rule must maintain sensitivity even as experience accumulates. The biological analogy: neurons don't get larger with experience — they change their *patterns* of connectivity. Persistence should be structural, not magnitudinal.

---

## Test 3 — Energy Minimization as Motivation

**What we expected:** An entity that develops preferred actions (proto-habits), recovers from perturbations with decreasing recovery time (learning), and shows recurring behavioral sequences that look like motivated behavior. Energy trending downward with periodic spikes. Different actions dominating in different contexts.

**What actually happened:** The entity became a homing pigeon. `seek_familiar` was chosen 93.6% of the time. Only 3 of 10 actions were ever used. The entity found its energy minimum almost immediately and spent its entire 5000-step existence doing one thing: returning home after each perturbation. Recovery was 100% reliable at ~15 steps but showed zero adaptation — the 24th recovery was identical to the 1st. The "proto-habits" were just seek_familiar repeated. The entity doesn't want something — it's a ball on a smooth hill.

**What felt different vs what was just different numbers:** The energy curve is the most telling. Between perturbations, it's a flat line at 0.156. After perturbations, it's a clean exponential decay back to 0.156. There's no texture, no variation, no personality. Compare this to what you'd expect from a motivated entity — variable baseline energy, different recovery strategies, occasional exploration. This entity has the behavioral complexity of a thermostat. The 7 unused actions are damning — the energy landscape is so simple that 70% of the action space is irrelevant. The novelty_cost term, intended to create a preference for the familiar, instead created a system that is terrified of the unfamiliar and does nothing else.

**Which direction this points for the architecture:** Three experiments, three collapses to trivial fixed points. The pattern is now clear: **simple energy landscapes produce simple behavior, regardless of the sophistication of the action space or update rule.** For energy minimization to produce motivation-like behavior, the energy function needs internal tension — competing terms that can't be simultaneously minimized. Curiosity (energy increases when state is static) must compete with comfort (energy increases when state changes too fast). Boredom must compete with overwhelm. The entity needs to be frustrated, not satisfied. A system at its global energy minimum has no reason to do anything. A system that can never reach its minimum has reason to do everything.

---

---

## Test 4 — Sparse Spiking Dynamics

**What we expected:** Coherent population-level responses from less than 5% active neurons at any moment. Different input patterns producing distinguishable activity. Temporal structure — oscillations, bursts. The efficiency argument: intelligence from sparsity, not from flooding every unit.

**What actually happened:** The first experiment that worked as designed. Mean firing fraction 0.14% — far under the 5% target. Pattern separation was essentially perfect: cosine similarity between pattern centroids was ~0.001 (near zero overlap). Within-pattern variance was exactly 0.0 — the same pattern produced the identical response every single time across all 20 presentations. The network was completely stable. 60 bursts detected, each exactly 50ms, matching the input duration. 132,480 total spikes across 9.2 seconds.

**What felt different vs what was just different numbers:** This experiment felt alive in a way the first three didn't. The raster plot shows clear structure — discrete bursts of activity in specific neuron subsets, silence between them. It looks like a brain scan. But looking closer, the aliveness is an illusion. The zero within-pattern variance is the tell. A real neural system has trial-to-trial variability — noise, history effects, internal state fluctuations. This network has none of that. Each pattern presentation is a photocopy of the last. The "coherent population response" is just 100 input neurons firing and 900 neurons sitting silent. The recurrent connections exist but accomplish nothing — the inhibitory balance is so effective that activity never propagates beyond the directly stimulated subset. It's sparse, but it's sparse in the way an empty room is quiet. There's no compression, no processing, no computation happening in the sparsity.

**Which direction this points for the architecture:** The sparsity numbers validate the premise — you don't need every unit active to get organized responses. But this is sparsity by exclusion, not sparsity by selection. The interesting version would be: overlapping input patterns that the network must *actively separate* using recurrent dynamics, with only a sparse subset of neurons carrying the discriminative signal. That requires the recurrent connections to do real work, which requires the E/I balance to be tuned to the edge of instability — not so stable that nothing propagates, not so unstable that activity explodes. The edge of chaos, not the middle of order. This connects back to the frustrated physics theme: the network needs to be in tension between amplification (excitation wants to spread activity) and suppression (inhibition wants to kill it), with sparsity emerging as the resolution of that tension, not as the absence of activity.

---

## Cross-Experiment Pattern (Tests 1-4)

Tests 1-3 collapsed to trivial fixed points. Test 4 succeeded at its target metrics but revealed a deeper problem: **the system works by doing nothing.** The sparsity is achieved by most neurons never participating, not by a small number of neurons doing sophisticated processing.

The common thread across all four: **the systems find the path of least resistance and take it.** Test 1: lock into potential wells. Test 2: grow until inputs are negligible. Test 3: repeat seek_familiar forever. Test 4: let input neurons fire and suppress everything else.

This suggests the architecture needs *frustrated physics* — competing forces that prevent easy equilibrium. Biological neural systems achieve this through excitatory/inhibitory balance tuned to criticality, homeostatic regulation, and neuromodulation that constantly shifts the energy landscape. The next experiments (especially Test 8 — Reflexive State) should explicitly design for frustration: self-reference creates a system that can never fully resolve its own state, which might be exactly the kind of frustration that produces ongoing dynamics.

**The emerging design principle:** Don't optimize for a target. Design a physics where the target state is unreachable but the system's attempts to reach it produce interesting behavior. Intelligence might not be a solution — it might be the process of failing to find one.

---

## Test 5 — Topological State Space

**What we expected:** Distinct cognitive categories occupying different regions of state space with interesting topological features — holes, loops, disconnected components. Reasoning trajectories following smooth curves. Evidence that cognition has geometry.

**What actually happened:** This experiment was constrained by encoder availability (HuggingFace blocked by proxy — used TF-IDF + random projection instead of GPT-2 hidden states). The results are partially informative and partially encoder-limited.

Category separability was weak: silhouette score 0.067, separation ratio 1.08. The UMAP plot shows visible clusters (mathematical inputs form a tight group) but quantitative separation is marginal. Intrinsic dimensionality was wildly heterogeneous — MLE median of 2.5 but mean of 92.7, meaning most local neighborhoods are low-dimensional but some are not. PCA required 51 components for 95% variance, with no dominant directions (PC1 = 2.8%). Topology was trivial: one connected component at all thresholds, no holes or loops.

The most interesting finding was the trajectory analysis. Reasoning trajectories have tortuosity of 3.67 (paths 3.7x longer than straight-line) and direction consistency of -0.44 (consecutive steps go in *opposite* directions). Each reasoning step zig-zags rather than flowing smoothly. Step sizes are remarkably uniform (~2.7 L2) regardless of content.

**What felt different vs what was just different numbers:** The zig-zagging trajectories are genuinely surprising. We expected reasoning to trace curves through state space — a smooth path from question to answer. Instead, each step leaps to a different region and the next step leaps back. Whether this is a property of reasoning (each step reframes the problem) or of language (each sentence uses different vocabulary) is unknowable with this encoder. But the uniformity of step sizes is striking: every step moves approximately the same distance, as if reasoning has a characteristic "stride length" regardless of whether you're solving algebra or pondering consciousness.

The flat PCA spectrum is the encoder's fingerprint, not a cognitive finding. TF-IDF + random projection distributes information uniformly by construction. A transformer would almost certainly show dominant directions of variation corresponding to semantic axes.

**Which direction this points for the architecture:** The pipeline works — UMAP, persistent homology, dimensionality estimation, trajectory analysis are all functional and ready for richer representations. The key takeaway: **representation geometry depends entirely on the encoder.** A TF-IDF encoder produces diffuse, topologically trivial clouds because it encodes vocabulary, not meaning. For the architecture, this means the choice of representation is not neutral — it determines what geometric structure is even *possible*. If we want cognition with interesting topology (holes = concepts the system can't represent, disconnected components = incommensurable modes of thought), we need representations that are shaped by something like a transformer's nonlinear geometry. The geometry isn't in the data — it's in the encoding.

The trajectory finding connects to the frustrated physics theme: reasoning may inherently be oscillatory rather than convergent. Each step doesn't get "closer" to an answer — it reframes the problem space. This is consistent with the idea that intelligence is the process of failing to converge, not the convergence itself.

---

## Test 6 — Local Learning Only

**What we expected:** A network that develops selectivity for input patterns without supervision. Individual nodes developing receptive fields. Hebbian + homeostatic rules producing global structure from local rules.

**What actually happened:** Another collapse. Homeostatic thresholds grew linearly without bound (~81 by step 9000). All activations saturated to ±1.0. Zero selectivity (0.0000), zero discriminability (silhouette 0.0000), cluster purity at random chance (0.10). The baseline backprop autoencoder achieved silhouette 0.19 — infinitely better than the local network.

**What felt different vs what was just different numbers:** This is the cleanest failure. The training curves tell the whole story: thresholds go up linearly, weights stay bounded (normalization works), but activations are permanently saturated from step ~500 onward. The network is alive for about 500 steps, then it's a wall of ones. The receptive fields of the "most selective" nodes are pure noise — they look like TV static because every node responds identically to every input.

**Which direction this points for the architecture:** Four of the first six experiments (1, 2, 3, 6) collapsed to trivial fixed states. The common failure mode: the system finds a way to saturate, freeze, or make itself immune to inputs. Tanh + additive homeostasis is fundamentally broken — biological homeostasis works because neurons have genuine graded responses and multiple regulatory mechanisms. For local learning to work, we need non-saturating activations, inhibitory competition between nodes, and multiplicative gating rather than additive thresholds.

---

## Test 7 — Competitive Global Broadcast

**What we expected:** Hard competition feeling qualitatively different from soft integration. A system that functions like one thing at a time vs a committee.

**What actually happened:** The most nuanced results in the series. Hard competition (τ=0.1) genuinely behaves differently: higher coherence (0.31-0.44 vs 0.29-0.32 for soft), much lower switching (0.025 vs 0.80 for medium in conflict), but dramatically higher workspace variance (0.06-0.11 vs 0.004-0.007 for soft). Medium competition (τ=1.0) was the worst performer in conflict — frantically switching 80% of timesteps. But conflict resolution accuracy flipped: hard got 34%, medium got 74%. The hold_time mechanism makes hard competition stubborn.

**What felt different vs what was just different numbers:** This is the first experiment where the modes feel genuinely different, not just numerically different. Hard mode feels decisive — one module takes over and stamps its character on the workspace. Soft mode feels muddy — everything blended into a low-variance average. Medium mode during conflict feels anxious — switching every other timestep, never committing. These are qualitative descriptions of mathematical behaviors, and they're not forced — they arise naturally from the dynamics.

**Which direction this points for the architecture:** Hard competition produces something that feels more like "one thing at a time" (consciousness-like) but at the cost of flexibility. The hold_time parameter is critical and should be dynamic, not fixed. The system needs a mechanism to decide when to persist with a winner and when to allow re-competition. This is attention regulation — not just attention, but attention about attention. Meta-cognitive control of competition.

---

## Test 8 — Reflexive State (New Math)

**What we expected:** A system where self-reference R = Φ(R) produces genuinely self-including states without infinite regress. The fixed-point iteration converging to a self-consistent self-model. Self-reference improving self-knowledge.

**What actually happened:** The fixed-point never converged — 0% convergence rate, mean final delta 0.162 (162x above tolerance). The self-model M oscillates permanently. The reflexive entity is twice as volatile as the control (state changes 2.9 vs 1.5) but no more accurate in self-modeling (cosine 0.54 vs 0.55). Self-referential and external inputs are processed nearly identically (accuracy gap = 0.004). Self-reference creates instability, not insight.

**What felt different vs what was just different numbers:** The non-convergence is the finding, and it's philosophically resonant. The system genuinely cannot resolve what it is — every attempt to model itself changes what's being modeled, which changes the model, ad infinitum. This isn't a bug; it's the mathematics of self-reference asserting itself. Gödel would recognize it. The system oscillates because self-reference is inherently irresolvable — you can't fully know yourself because the knowing is part of the self. But the oscillation doesn't produce interesting structure; it's just amplified noise. Self-reference without structural hierarchy is just feedback.

**Which direction this points for the architecture:** Self-reference needs levels. A flat self-model (M directly models S) is just a mirror — and mirrors create infinite regress, not self-knowledge. What's needed is self-reference across levels of abstraction: a self-model that operates on a compressed, categorically different representation of the content state. The map must be a different kind of thing than the territory. This connects to the GWT finding in Test 7: the metacognitive module should model the workspace competition, not the workspace content. Self-reference about process, not about state.

---

## Test 9 — Temporal Field (New Math)

**What we expected:** An entity that doesn't just store the past and predict the future — one that IS its temporal extension. Past, present, and anticipated future coexisting as a single field.

**What actually happened:** **The best experiment in the series.** State autocorrelation 0.83 from inputs with autocorrelation -0.08 — a 10x coherence gain. Anticipation error 0.24 vs baseline 0.81 — 3.4x better prediction. The field develops characteristic temporal lean shapes: past-heavy during recording phases, future-heavy during predictable phases. Present sensitivity varies meaningfully by input type: low for gradual ramps (0.012), high for sharp alternation (0.29). The field literally changes shape based on what kind of temporal structure it encounters.

**What felt different vs what was just different numbers:** This experiment felt alive. Not in the illusory way Test 4 felt alive (clean raster plots hiding empty processing), but genuinely — the entity develops a relationship to time. It becomes past-heavy when accumulating experience, then shifts to future-heavy when patterns become predictable. The 0.83 autocorrelation means the entity has temporal continuity: it doesn't jump from moment to moment but flows. For an entity that's just a set of Fourier coefficients, it has a surprisingly coherent inner life.

The most striking finding: the entity responds MORE to pattern callbacks (returning to a previously seen pattern) than to novel inputs. It recognizes temporal structure it's seen before — not in a lookup table way, but as a resonance in the field. The past field literally vibrates when a familiar pattern returns.

**Which direction this points for the architecture:** The temporal field is the most architecturally promising component so far. It solves the persistence problem (Tests 1-2) by encoding history in a continuous field rather than an accumulating state vector. It solves the frustration problem (Tests 1-3) because the field is always shifting — the normalization prevents saturation and the field evolution creates ongoing dynamics. And it provides anticipation for free — the future region naturally encodes learned temporal expectations. A cognitive architecture should have a temporal field as a core primitive, not memory as an add-on.

---

## Test 10 — Unity Primitive (New Math)

**What we expected:** Whether a system mathematically constrained to remain one thing while expressing multiple modes behaves differently from a system built from parts. Whether unity-as-primitive produces something that parts-first cannot.

**What actually happened:** The math works perfectly — projection identity errors at machine epsilon (1.6e-14), perfect orthogonality, perfect idempotency. Pre-destruction, unity is preserved to 15 decimal places. But mode selectivity is poor (23%, barely above 20% random) because the projections are random subspaces not aligned with input structure. When the affect mode is destroyed at t=500, unity error jumps to 0.46 and never fully recovers (settles at ~0.25). The system does NOT reconstitute the lost mode. Perception takes over 100% of affect-type inputs.

**What felt different vs what was just different numbers:** The destruction experiment is the most philosophically revealing result in the series. Destroying a mode in the unity-first system is qualitatively different from destroying a module in a parts-first system. In parts-first, you lose a function but other modules can partially compensate because representations overlap. In unity-first, you lose a dimension — and orthogonality guarantees no compensation is possible. The system doesn't gracefully degrade; it develops a permanent blind spot. It's not like losing the ability to feel emotion; it's like losing the part of reality that emotion was tracking.

This reveals that orthogonality — the mathematically elegant constraint — is exactly wrong. Biological brains have overlapping, redundant representations because overlap provides robustness. Orthogonality provides clean separation but zero fault tolerance. The "unity" we enforced is actually more fragile than parts.

**Which direction this points for the architecture:** Unity-first is an interesting primitive but orthogonal projection is the wrong differentiation mechanism. What we need is non-orthogonal differentiation — modes that overlap, interfere, and can compensate. Not P_i · P_j = 0, but P_i · P_j = small-but-nonzero. This would sacrifice clean reconstruction (Σ D_k(U) ≠ U exactly) but gain robustness and the kind of graceful degradation that biological systems exhibit. The tension between mathematical elegance and functional robustness is itself a finding.

---

## Cross-Experiment Synthesis (All 10 Tests)

### The Collapse Pattern (Tests 1, 2, 3, 4, 6)
Five experiments collapsed to trivial fixed states. The mechanism varied — potential wells (T1), magnitude growth (T2), action monotony (T3), activation saturation (T6), exclusion-based sparsity (T4) — but the pattern is identical: **the system finds the path of least resistance and takes it.** Simple dynamics with simple energy landscapes produce simple behavior, full stop.

### The Partial Successes (Tests 5, 7, 8)
Three experiments produced interesting but limited results. Test 5 showed zig-zag trajectories (limited by encoder). Test 7 showed qualitative differences between competition modes. Test 8 showed that self-reference creates irresolvable oscillation. These are genuine findings, but they don't yet produce architecturally useful components.

### The Breakthrough (Test 9)
The temporal field produced genuinely emergent behavior: temporal coherence from incoherent input, learned anticipation, and context-sensitive temporal lean. This is the one component that should move forward into architectural integration.

### The Philosophical Finding (Test 10)
Mathematical unity is more fragile than pragmatic parts. Orthogonality trades robustness for elegance. Real unity might require overlapping, interfering, partially redundant representations — the kind of messy, non-orthogonal structure that biological systems exhibit.

### Emerging Design Principles

1. **Frustrated physics is necessary.** Systems that can reach equilibrium do. Intelligence requires unreachable equilibria.
2. **Temporal fields over state vectors.** Persistent state saturates or crystallizes. Continuous fields with normalization maintain ongoing dynamics.
3. **Hard competition with dynamic hold.** One-at-a-time processing produces coherent behavior but needs adaptive persistence.
4. **Self-reference needs levels.** Flat self-models oscillate. Self-reference across abstraction levels might converge.
5. **Non-orthogonal differentiation.** Clean separation is fragile. Overlapping modes provide robustness.
6. **Non-saturating dynamics.** Every system that could saturate did. The activation function determines the fate of the architecture.

### The Single Most Important Finding
**Intelligence might not be a solution — it might be the process of failing to find one.** The systems that "worked" (T9's temporal field) are the ones that never settle. The systems that "failed" (T1-3, T6) are the ones that found equilibrium and died there. The architecture should be designed so that equilibrium is unreachable but the attempt to reach it produces structured, adaptive behavior.
