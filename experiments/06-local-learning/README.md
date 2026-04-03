# Test 6 — Local Learning Only

## What We Built

A network of 500 nodes learning from 10,000 pattern presentations using only local rules: Hebbian association, anti-Hebbian decorrelation, homeostatic threshold regulation, and periodic synaptic normalization. No loss function, no backpropagation, no optimizer. MNIST was unavailable (network access blocked), so we used synthetic structured patterns — 10 classes of 28x28 spatial patterns (bars, corners, rings, crosses, etc.) with noise and spatial jitter.

## What Happened

**Another collapse.** The homeostatic thresholds grew linearly without bound (reaching ~81 by step 9000), all activations saturated to ±1.0, and the network developed zero selectivity for any input class. Sparsity dropped to 0% by step 1000. The network is a wall of saturated tanh — every node responds maximally to every input.

- **Mean selectivity: 0.0000** — no node prefers any class over any other
- **Silhouette score: 0.0000** — population responses are indistinguishable across classes
- **Cluster purity: 0.10** — exactly random chance for 10 classes
- **Stability: 1.0000** — perfectly stable (because everything is saturated)
- **Baseline autoencoder silhouette: 0.1921** — backprop achieves measurable separation

## Why It Failed

The homeostatic rule is supposed to regulate firing rates to a target (0.1). But tanh activation saturates at ±1.0, so a² = 1.0 always, and the update Δθ = η·(1.0 - 0.1) = positive constant. Thresholds increase monotonically. The system is supposed to use thresholds to reduce activity, but large thresholds just push the pre-tanh values further from zero, and tanh still saturates. The homeostatic mechanism and the nonlinearity work against each other.

The Hebbian rule also contributes: it strengthens all connections when nodes are co-active, but since all nodes are saturated at ±1.0, they're always co-active. Anti-Hebbian kicks in but can't overcome the saturation. Synaptic normalization keeps weights bounded but doesn't fix the threshold problem.

## What This Means

Same pattern as Tests 1-3: **the system finds a way to make itself immune to its inputs.** Test 1 crystallized via deep potential wells. Test 2 grew state magnitude until inputs were negligible. Test 3 used one action forever. Test 6 saturated all activations, making every input produce the identical response.

The biological analog would be a brain where every neuron fires at maximum rate all the time. Biological homeostasis works because neurons have a genuine graded response range and multiple mechanisms (inhibition, refractory periods, synaptic depression) that prevent universal saturation. Our tanh + additive-threshold system lacks these safeguards.

**For the architecture:** Local learning can work, but the activation function must have a regime where the homeostatic feedback loop is stable. This likely requires: (1) a non-saturating activation with a natural operating range, (2) inhibitory connections that create real competition between nodes, or (3) a multiplicative (not additive) threshold that gates activity rather than offsetting it.

## Files

- `local_network.py` — node model and local learning rules
- `train.py` — 10,000 step exposure loop
- `probe.py` — post-training representational analysis
- `visualize.py` — receptive fields, selectivity plots, training curves, baseline comparison
- `results.json` — all measurements
