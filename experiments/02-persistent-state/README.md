# Test 2 — Persistent Non-Resetting State

## What We Built

An entity with a 128-dimensional internal state vector that never resets. Every interaction permanently alters the state via:

```
S(t+1) = α·S(t) + β·encode(input) + γ·tanh(S(t))
```

- α = 0.95 (decay — most state preserved)
- β = 0.1 (input influence — small but permanent)  
- γ = 0.3 (self-influence — state acts on itself)
- 1000 interactions with temporally structured input mix (questions, statements, emotional, contradictions, abstract)
- Probe input ("What is the nature of consciousness?") measured at t=10, 100, 500, 999

## What Happened

**The entity became a monument.** The state norm grew rapidly from 0 to ~68 in the first ~100 interactions, then saturated. After saturation, the entity became nearly inert — new inputs produce state changes of ~0.095, negligible against a state norm of 68.

Key numbers:
- **State norm**: 0 → 68.2 (saturated by t=100, stable thereafter)
- **Sensitivity**: 0.41 (t=10) → 0.094 (t=999) — a 4.4x decrease
- **Response consistency**: cosine sim = 1.000 between t=100, t=500, t=999 — the entity responds identically regardless of 900 additional interactions
- **Effective dimensionality**: 1 (PC1 = 99.0% of variance)
- **Drift from origin**: monotonically increasing until saturation, then flat

The sensitivity plot is the most revealing: there's a dramatic collapse in the first ~50 interactions, after which all inputs regardless of category produce essentially identical state changes.

## Why This Happened

The update rule has a mathematical fixed point. Once ||S|| is large:
- α·S dominates (0.95 × 68 ≈ 64.6)
- γ·tanh(S) saturates at ±0.3 per dimension (total contribution ~2.4)
- β·encode(input) contributes ~0.1 (unit vector scaled by β)

So the state is determined almost entirely by its own history. New inputs are negligible perturbations on top of an enormous accumulated vector. The entity doesn't develop habits — it develops rigor mortis.

## What This Means

1. **Persistence without saturation control is death.** The α=0.95 decay is too slow to prevent runaway accumulation. By t=100, the entity is already too massive to be meaningfully influenced. This is the state-space equivalent of Test 1's crystallization.

2. **The self-influence term (γ·tanh) creates a fixed attractor.** Once the state is large, tanh saturates and becomes a constant offset. The self-influence stops being dynamic and becomes structural — it sets the shape of the attractor but doesn't create ongoing dynamics.

3. **The "habits" finding is actually about rigidity, not learning.** The entity doesn't respond less to familiar inputs specifically — it responds less to *all* inputs equally. This isn't habituation (which would be category-specific). It's just mass.

4. **For persistent state to be interesting, growth must be bounded.** Either through normalization (keep ||S|| fixed), through stronger decay (lower α), or through a fundamentally different update rule where state magnitude doesn't monotonically increase.

## What Would Be Different

For genuine habit formation (category-specific sensitivity changes):
- Normalize S to fixed magnitude after each update
- Use a gating mechanism where state history modulates input gain per-category
- Or use a completely different formulation where persistence is about *structure* not *magnitude*

## Files

- `persistent_entity.py` — entity, encoder, update rule
- `simulate.py` — 1000 interactions with structured input sequence
- `visualize.py` — drift, sensitivity, trajectory, consistency, dimension analysis
- `results.json` — all measurements
- `drift.png` — state magnitude over time (shows saturation)
- `sensitivity.png` — response magnitude collapse
- `trajectory.png` — PCA state trajectory (essentially 1D)
- `consistency.png` — probe response similarity across time
- `dimensions.png` — per-dimension analysis and autocorrelation
