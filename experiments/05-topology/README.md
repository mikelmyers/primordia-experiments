# Test 5 — Topological State Space

## What We Built

An analysis of the topology of internal representation space across 5 cognitive categories: mathematical reasoning, emotional language, spatial description, abstract philosophy, and simple factual statements. 500 text inputs (100 per category) were encoded into 768-dimensional vectors and analyzed for geometric and topological structure.

**Encoder note:** The original design called for GPT-2 hidden states (layer 6). HuggingFace was unreachable due to proxy restrictions, so we used TF-IDF + Gaussian random projection + tanh nonlinearity as the encoder. This preserves genuine text structure (vocabulary distributions, n-gram frequencies) without learned semantic representations. The topological analysis pipeline is identical regardless of encoder.

## What We Measured

### 1. Category Separability

- **Silhouette score: 0.067** — barely above zero (0 = random, 1 = perfect separation)
- **Separation ratio: 1.08** — between-class distance is only 8% larger than within-class distance
- **Centroid distances** (cosine): all pairs between 0.80-0.93, remarkably uniform
- The UMAP 2D plot shows visible category clustering (especially mathematical as a tight red cluster), but the quantitative measures say the separation is weak

### 2. Intrinsic Dimensionality

- **MLE estimate: median 2.5, mean 92.7** — the huge mean-median gap (std=481) indicates the local dimensionality is wildly heterogeneous. Most neighborhoods are ~2-3 dimensional, but some are extremely high-dimensional
- **PCA 95%: 51 components** — 51 dimensions capture 95% of variance out of 768. But the first 20 components explain only 40%, with no single dominant direction (PC1 = 2.8%)
- The variance is spread remarkably evenly — no low-dimensional manifold, but also not truly 768-dimensional

### 3. Topological Features

- **Single connected component** at all distance thresholds tested (10th-90th percentile of pairwise distances)
- No holes, loops, or disconnected regions detected — the point cloud is one continuous blob
- The representation space has trivial topology: it's simply connected with no interesting features at the scale we can measure

### 4. Reasoning Trajectories

- **Mean tortuosity: 3.67** — paths are ~3.7x longer than the straight-line distance between start and end points. Reasoning doesn't follow direct paths
- **Mean direction consistency: -0.44** — consecutive reasoning steps tend to go in *opposite* directions (negative cosine). Each step is an anti-correlated zig-zag rather than a smooth curve
- **Step sizes are remarkably uniform** (~2.5-2.9 L2 distance per step) — each reasoning step moves approximately the same distance through state space regardless of content

## What the Shape of Thought Looks Like (With This Encoder)

**It doesn't look like much.** The state space is a diffuse cloud with weak category structure, no topological features, and reasoning trajectories that zig-zag rather than flow.

But several things are worth noting:

1. **The UMAP plot does show visual clustering** — mathematical inputs form a tight cluster, emotional inputs scatter differently from philosophical ones. The categories are not random noise. The silhouette score is low because the clusters overlap and have large intra-class variance, not because there's zero structure.

2. **The flat PCA spectrum is informative.** In a transformer, you'd expect a few dominant directions of variation. With TF-IDF encoding, every dimension carries roughly equal weight because random projection distributes information uniformly. This is the encoder's fingerprint, not a finding about cognition.

3. **The trajectory zig-zagging is real and interesting.** Even with a simple encoder, each reasoning step moves to a very different region of vocabulary space than the previous step. Reasoning doesn't accumulate — it oscillates. Each step reframes the problem using different words, which creates anti-correlated direction vectors. Whether a transformer would show smooth curves is an open question this experiment can't answer.

4. **The trivial topology (single connected component, no holes) may be an artifact of the encoder** — TF-IDF representations tend to live on a positive cone in high-dimensional space, producing convex point clouds with trivial topology. A transformer's nonlinear geometry could produce genuinely interesting topological features.

## Honest Assessment

This experiment is **limited by the encoder**. The topological analysis pipeline works correctly, but TF-IDF + random projection produces representations that are:
- Too uniformly distributed (flat PCA spectrum)
- Too high-dimensional for interesting topology
- Too vocabulary-dependent (categories separate by word choice, not meaning)

The interesting finding is the trajectory analysis: even with a shallow encoder, multi-step reasoning creates zig-zag paths through representation space. Whether this is a property of *reasoning* (each step genuinely reframes) or a property of *language* (each sentence uses different words) would require a transformer to disentangle.

**To do this properly:** run with GPT-2 or a larger model where hidden states capture semantic geometry, not just vocabulary statistics. The pipeline is ready — only the encoder needs upgrading.

## Files

- `capture_states.py` — text encoding and input generation (TF-IDF + random projection)
- `topology.py` — UMAP, persistent homology proxy, intrinsic dimensionality, category separability
- `visualize.py` — all plots: UMAP 2D/3D, trajectories, PCA spectrum, centroid heatmap
- `results.json` — all quantitative measurements
