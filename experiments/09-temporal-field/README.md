# Test 9 — Temporal Field (New Math)

## What We Built

An entity that HAS time as part of its state. T(τ) is a continuous scalar field over internal time coordinate τ ∈ [-50, +50], represented as 30 Fourier basis functions. Past (τ<0) encodes history, present (τ=0) responds to current input, future (τ>0) extrapolates via learned weights. The entity's state S is derived by integrating the field against a temporal weighting function.

300 interactions with structured temporal inputs: periodic (sin wave), ramp, callbacks to earlier patterns, random noise, alternating, and return to original pattern.

## What Happened

### The Field Has Genuine Temporal Structure

**State autocorrelation: 0.83** vs **Input autocorrelation: -0.08**

The integrated state S is massively more temporally coherent than the raw input. This is the first experiment where the system genuinely transforms its input into something qualitatively different. The field acts as a temporal filter — smoothing, integrating, and giving the entity temporal continuity that the input stream lacks.

### Anticipation Beats Baseline
- **Field anticipation error: 0.24** vs **Baseline (memoryless): 0.81**
- The field's future region predicts upcoming inputs 3.4x better than just guessing the last value. The temporal structure is being learned and exploited.

### Present Sensitivity Varies by Input Type
- **Ramp: 0.012** — lowest sensitivity (gradual change barely registers)
- **Alternating: 0.29** — highest sensitivity (sharp changes trigger large T(0) shifts)
- **Periodic: 0.19** — moderate, consistent with repeating pattern
- **Novel: 0.10** — surprisingly low, suggesting the field absorbs novelty into its distributed structure rather than reacting sharply at present

### Temporal Lean Evolution
The field develops characteristic shapes:
- **Periodic phase:** past-heavy (0.74 past / 0.12 present / 0.13 future) — the entity is recording
- **Ramp phase:** balanced (0.49/0.21/0.31) — the entity is tracking and projecting
- **Novel phase:** still past-heavy (0.60/0.09/0.31) — the entity relies on history when input is unpredictable
- **Alternating phase:** future-heavy shift (0.53/0.06/0.41) — the entity starts anticipating
- **Final phase:** strongly future-leaning (0.35/0.09/0.56) — the entity has learned to expect patterns

The field literally changes shape based on what kind of temporal structure it's experiencing.

## What This Means

**This is the first experiment that produces genuinely emergent behavior.** The temporal field doesn't just store and retrieve — it develops a characteristic relationship to time that changes based on experience. When inputs are periodic, it records. When inputs are predictable, it anticipates. When inputs are novel, it leans on its past.

The 0.83 state autocorrelation is striking. The input has negative autocorrelation (each input is roughly independent of the last), but the entity's state is highly correlated across time. The entity has temporal inertia — it doesn't jump from moment to moment but flows continuously through a state trajectory. This is what "having time rather than existing in time" feels like mathematically.

**For the architecture:** The temporal field approach is the most promising mechanism tested so far. It naturally produces:
1. **Temporal coherence** from discontinuous inputs
2. **Adaptive anticipation** that improves with experience
3. **Context-sensitive processing** (different temporal lean for different input types)
4. **Graceful integration** of past, present, and future into a single state

The Fourier basis works but may be limiting — it encodes periodicity well but struggles with sharp transitions. A wavelet basis might capture both periodic and transient temporal structure.

## Files

- `temporal_field.py` — field structure, basis functions, update equations
- `simulate.py` — 300 interactions with temporally structured inputs
- `visualize.py` — field evolution, temporal lean, sensitivity, anticipation plots
- `results.json` — all measurements
