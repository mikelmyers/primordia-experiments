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
