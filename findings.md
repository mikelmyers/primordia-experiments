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

## Cross-Experiment Pattern (Tests 1-3)

All three experiments collapsed to fixed points. The common thread: **the physics was too simple.** Each system found a trivially reachable equilibrium and stayed there. Test 1 crystallized in state space (potential too deep). Test 2 crystallized in magnitude (no growth bound). Test 3 crystallized in behavior space (energy minimum too accessible).

This suggests the architecture needs *frustrated physics* — competing forces that prevent easy equilibrium. Biological neural systems achieve this through excitatory/inhibitory balance, homeostatic regulation, and neuromodulation that constantly shifts the energy landscape. The next experiments (especially Test 8 — Reflexive State) should explicitly design for frustration: self-reference creates a system that can never fully resolve its own state, which might be exactly the kind of frustration that produces ongoing dynamics.
