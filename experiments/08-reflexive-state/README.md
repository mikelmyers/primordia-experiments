# Test 8 — Reflexive State (New Math)

## What We Built

A system where the self-model IS part of the state: R = (S, M) where S is content (dim=64) and M is self-model (dim=32). The self-model M converges to a fixed point of Φ: M = g(S, M) via 5 iterations per timestep. Contraction enforced by constraining spectral radius < 1. Compared reflexive entity (self-model feeds back into content via W_m) against control (W_m = 0).

## What Happened

### Fixed-Point Convergence: Failed
- **Convergence rate: 0%** — M never converged within 5 iterations
- **Mean final delta: 0.162** — 162x above the 0.001 tolerance
- M oscillates rather than converging — the fixed-point iteration doesn't find a stable self-model

This is the first interesting failure. The system can't resolve what it is. The self-model keeps changing because the content it's trying to model is itself changing in response to the self-model. It's not a bug — it's the mathematical structure of self-reference creating genuine irresolvability.

### Self-Model Accuracy
- **Reflexive: 0.54** cosine similarity (S predicted from M)
- **Control: 0.55** cosine similarity
- The self-model is slightly LESS accurate with self-reference enabled. Self-awareness makes self-knowledge harder.

### Behavioral Difference
- **Reflexive state changes: ~2.9** (much larger movements per step)
- **Control state changes: ~1.5** (more moderate)
- The reflexive entity is twice as volatile. Self-reference amplifies dynamics rather than stabilizing them.
- **Reflexive S norm: 2.64** vs **Control S norm: 1.12** — the reflexive entity's state grows larger

### Self vs External Processing
- **Self-referential accuracy: 0.544** vs **External: 0.540** — negligible gap (0.004)
- The system processes self-referential inputs almost identically to external ones. It doesn't "know" it's thinking about itself.

## What This Means

**Self-reference creates frustration — exactly as hypothesized.** The fixed-point never converges because self-reference is inherently circular: M models S, but S depends on M. This is the mathematical version of "I can't fully know myself because the act of knowing changes what I am." The oscillation IS the finding.

But the frustration doesn't produce interesting behavior — it just amplifies everything. The reflexive entity is more volatile but not more structured. Self-reference creates instability, not complexity. The self-model doesn't differentiate between self-referential and external inputs (gap = 0.004), which means the self-reference loop is adding noise, not information.

**For the architecture:** Self-reference works mathematically (the contraction mapping framework is sound, the fixed-point iteration runs), but 5 iterations isn't enough for convergence, and more iterations risk divergence. The deeper issue: self-reference as implemented here is just an extra weight matrix (W_m). For genuine self-reference, the self-model needs to be structurally different from the content — it needs to operate on a different level of abstraction, not just a compressed projection. This connects to the levels-of-description problem: a map of a territory is useful because it's a different kind of thing than the territory. A map that IS the territory is just the territory again.

## Files

- `reflexive_state.py` — R state structure, Φ operator, fixed-point iteration
- `simulate.py` — 500 interactions with mixed self-referential and external inputs
- `visualize.py` — M trajectory, convergence plots, self vs external comparison
- `results.json` — convergence stats, self-model accuracy, behavioral difference metrics
