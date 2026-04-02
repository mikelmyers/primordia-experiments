# Test 4 — Sparse Spiking Dynamics

## What We Built

A leaky integrate-and-fire spiking neural network with 1000 neurons, implemented from scratch:

```
dV/dt = -V/τ + I_input + I_recurrent
Fire when V > 1.0, then V = 0, refractory for 2ms
```

- **1000 neurons**: 800 excitatory, 200 inhibitory (Dale's law)
- **Sparse connectivity**: 5% random (49,742 connections out of ~1M possible)
- **Excitatory weights**: exponential(0.1), positive
- **Inhibitory weights**: exponential(0.4), negative (4x stronger — balance)
- **No learning**: fixed weights throughout
- **Input**: 3 patterns (A, B, C), each activating a different 10% subset, 20 presentations each in random order, 50ms per presentation with 100ms gaps

## What Happened

**This is the first experiment that worked as intended.** The network produced coherent, sparse, pattern-specific responses.

Key numbers:
- **Mean firing fraction**: 0.14% (well under 5% target)
- **98.6% of timesteps** had fewer than 5% of neurons active
- **97.3% of timesteps** had zero spikes (between pattern presentations)
- **Pattern separation**: cosine similarity between pattern centroids ≈ 0.001 (near-perfect separation)
- **Within-pattern variance**: 0.0 (identical response to same pattern every time)
- **Stability**: completely stable — no explosion, no death
- **60 bursts** detected, each exactly 50ms (matching pattern duration)
- **Dominant frequency**: 6.6 Hz (matching the pattern presentation rate)
- **Total spikes**: 132,480 across 9.2 seconds of simulation
- **Spikes per neuron per second**: 14.4

## What This Means

### The Sparsity Result

0.14% mean firing fraction means that at any given moment, roughly 1-2 neurons out of 1000 are active. During pattern presentations, this rises to about 10% (the input subset), but between presentations it drops to zero. This is **extreme sparsity** — far beyond the 5% target.

The biological comparison: cortical neurons fire at roughly 0.1-5 Hz on average. Our network at 14.4 spikes/neuron/second is on the high end during active periods but achieves it through intense bursting followed by complete silence, rather than sustained low-rate activity.

### The Pattern Separation Result

This is the strongest result across all experiments so far. Three input patterns activating different 10% subsets produce population responses with near-zero cosine similarity (0.001). The PCA plot shows three completely separated clusters. Within-pattern variance is zero — the same pattern always produces the exact same response.

**Why it's almost too perfect**: Zero within-pattern variance means the network is acting as a purely feedforward input-to-output map with no internal dynamics influencing the response. The recurrent connections exist but don't create any variability or internal processing. Each pattern presentation produces a stereotyped burst in exactly the input neurons, with minimal spread through the network.

### The Efficiency Argument

132,480 spikes to process 60 pattern presentations. That's ~2,208 spikes per pattern. With 1000 neurons, this means each pattern activates about 100 neurons (the input set) for 50ms at roughly 1 spike per ms. The other 900 neurons contribute essentially nothing.

**This is efficient but trivial.** The sparsity comes from the input structure (only 10% activated), not from the network learning to be sparse. The network isn't compressing or encoding — it's relaying.

### What's Missing

The network is stable and sparse but not *doing* anything interesting. There's no:
- Recurrent amplification (spikes in input neurons don't propagate)
- Pattern completion (partial input doesn't activate the full pattern)
- Temporal integration (no memory of previous patterns)
- Competitive dynamics (patterns don't interact or interfere)

The excitatory/inhibitory balance is working too well — the inhibition is strong enough to prevent any recurrent activity, which keeps things stable but kills any emergent dynamics.

### For the GPU Replacement Argument

The sparsity numbers support the efficiency claim: you don't need every unit active to get coherent responses. But this implementation shows sparsity through triviality — only the directly stimulated neurons participate. The real challenge is getting sparsity with *processing* — where a small number of active neurons are doing real computation, not just relaying input.

To make this argument properly, the network needs: (a) patterns that require recurrent processing to separate (overlapping inputs), (b) tasks that require temporal integration, and (c) evidence that sparse activity carries more information per spike than dense activity.

## Files

- `snn.py` — neuron model, network construction, spike analysis
- `simulate.py` — pattern presentation and full measurement suite
- `visualize.py` — raster plot, population rate, pattern separation, power spectrum
- `results.json` — all quantitative measurements
- `raster.png` — every spike in the network (blue=exc, red=inh)
- `population_rate.png` — firing rate and sparsity over time
- `pattern_responses.png` — PCA separation, cosine similarity matrix
- `power_spectrum.png` — frequency analysis of population activity
