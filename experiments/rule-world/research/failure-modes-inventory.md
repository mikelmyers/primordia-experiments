# Rule-World Iteration 16 — Failure-Modes Inventory of Prior Matmul-Free / Scaling-Friendly Generative Substrates

*Date: 2026-04-07*
*Status: literature synthesis, not survey — failure modes only*
*Purpose: identify which walls prior matmul-free LM substrates hit, name the assumption each wall rests on, and check whether the rule-world stack (property-graph context + HDC bipolar 10k retrieval + PPM counters + STRIPS planner, zero matmul) inherits that assumption.*

A note on rigor up front: several entries below cite numbers from memory of the published literature. Where I am not confident in a specific figure I flag it explicitly with "approx." or "unverified." The reader should treat any unflagged number as a claim I am reasonably confident is in the cited paper but should still spot-check before quoting.

---

## 1. HDC / VSA sequence prediction — Joshi et al.

- **Paper**: Joshi, Halseth, Kanerva. "Language Geometry using Random Indexing." QI 2016 (also arXiv:1412.7026 lineage). Companion: Kleyko et al., "A Survey on Hyperdimensional Computing aka VSA, Part I & II," ACM CSUR 2022 (arXiv:2111.06077, 2112.15424).
- **What they built**: A 10,000-dim random-indexing model that bound n-gram letter contexts into a single bundled hypervector per language and classified 21 European languages from short text samples. Near-perfect language ID with no gradient training.
- **Where it hit the wall**: Works for *classification* of bundled bag-of-trigrams; never extended to actual next-token language modeling at competitive bpc. Bundling capacity in a D=10k bipolar vector saturates around O(D / log D) ~ a few hundred items before crosstalk dominates (Frady, Kleyko, Sommer 2018, "A theory of sequence indexing and working memory in RNNs," Neural Computation). No HDC LM has reported a bpc on enwik8/text8 in the published literature that I can locate.
- **Underlying assumption (A1)**: Context state is a single fixed-dimension distributed vector whose information capacity is bounded by D.
- **Do we share it?**: **No for context, partially yes for retrieval.** Rule-world holds context in an unbounded property graph; HDC vectors are used only as content-addressable keys into that graph, not as the state itself. The bundling-saturation wall does not apply to graph nodes; it still applies to any single HDC slot we try to overload.

## 2. Holographic Reduced Representations — Plate

- **Paper**: Plate, "Holographic Reduced Representations," IEEE TNN 1995; book 2003.
- **What they built**: Circular-convolution binding of role-filler pairs into fixed-D real vectors, with cleanup memory via nearest-neighbor lookup. Demonstrated analogy and simple frame representation.
- **Where it hit the wall**: Decoding accuracy degrades as O(1/sqrt(D)) per additional bound pair; depth of nested structure limited to ~3–4 before cleanup memory cannot disambiguate (Plate 2003 ch. 6). Never produced a generative LM.
- **Underlying assumption (A1, A2)**: A1 fixed-D state; A2 compositional structure must round-trip through a noisy binding operator whose SNR falls with depth.
- **Do we share it?**: **A1 no, A2 partially.** We bind via graph edges, not convolution; depth is unbounded in the graph. We do still rely on HDC cleanup for retrieval, so any path that routes information *through* the HDC layer inherits the SNR-vs-depth tradeoff.

## 3. Sparse Distributed Memory — Kanerva

- **Paper**: Kanerva, *Sparse Distributed Memory*, MIT Press 1988.
- **What they built**: Address-decoder memory over {0,1}^N with Hamming-radius activation; stores ~0.15 N patterns reliably.
- **Where it hit the wall**: Capacity ceiling 0.15 N (Kanerva 1988 ch. 7); writing is constructive but no learning rule discovers *which* features to store. No generative sequence work at scale.
- **Underlying assumption (A1, A3)**: A1 fixed-D; A3 features are given, not discovered.
- **Do we share it?**: **A1 no. A3 yes, partially** — rule-world's HDC features come from a hand-chosen encoding pipeline, not learned. This is a real shared wall.

## 4. Hopfield networks (classical) — Amit

- **Paper**: Amit, Gutfreund, Sompolinsky 1985; Amit, *Modeling Brain Function*, CUP 1989.
- **What they built**: Hebbian-trained recurrent binary network storing patterns as fixed points.
- **Where it hit the wall**: Capacity 0.138 N patterns before catastrophic retrieval failure (Amit-Gutfreund-Sompolinsky 1985). Sequence storage variants (temporal asymmetry) drop capacity further. Never used as an LM.
- **Underlying assumption (A1)**: Memory is a single N-neuron attractor basin; capacity scales linearly in N with a small constant.
- **Do we share it?**: **No.** Graph storage is not attractor-based.

## 5. Modern Hopfield — Ramsauer et al. (honesty check on matmul)

- **Paper**: Ramsauer et al., "Hopfield Networks Is All You Need," ICLR 2021 (arXiv:2008.02217).
- **What they built**: Continuous-state Hopfield with exponential-energy update rule; one update step is mathematically identical to softmax attention.
- **Where it hit the wall**: It does not hit a wall — but the leave-off summary's question is correct: **the update rule X^T softmax(beta X q) is exactly a matmul against the stored-pattern matrix.** Modern Hopfield achieves exponential capacity (~exp(N/2) per Ramsauer Theorem 3) precisely by smuggling dense matmul back in. So as a matmul-free candidate it disqualifies itself.
- **Underlying assumption (A4)**: Exponential capacity requires a dense inner-product over all stored patterns at query time.
- **Do we share it?**: **No** — but this is the most important negative result in the inventory: nobody has shown sub-quadratic, matmul-free associative recall with exp-capacity. Rule-world's graph index is sub-linear via hashing but its *capacity guarantees* are weaker than modern Hopfield's.

## 6. HTM / Sparse Distributed Representations — Numenta

- **Paper**: Hawkins, Ahmad, "Why Neurons Have Thousands of Synapses, A Theory of Sequence Memory in Neocortex," Frontiers in Neural Circuits 2016. Cui, Ahmad, Hawkins, "Continuous Online Sequence Learning with an Unsupervised Neural Network Model," Neural Computation 2016.
- **What they built**: Hierarchical Temporal Memory: SDR encoder + sequence memory with Hebbian segment growth, online and unsupervised.
- **Where it hit the wall**: Across ~20 years of Numenta publications, HTM has never produced a published bpc on enwik8/text8. Best public benchmarks are NAB (anomaly detection) and synthetic sequence prediction. The 2016 sequence memory paper reports prediction accuracy on artificial grammars and NYC taxi data, not language. Repeated community attempts to push HTM to character-level LM saturated above 2.5 bpc (unverified — based on community reports, not a paper I can cite).
- **Underlying assumption (A3, A5)**: A3 fixed encoder is sufficient; A5 local Hebbian segment growth is sufficient to discover long-range conditional structure.
- **Do we share it?**: **A3 yes (we have a fixed HDC encoder); A5 partially** — our PPM counters are also a local statistical rule, though over an unbounded context tree rather than a fixed-cell grid. This is the closest prior art to rule-world and its 20-year failure to produce a competitive bpc is the single most concerning data point in the inventory.

## 7. Compression-based LMs — PPM, CTW, DMC

- **Paper**: Cleary & Witten, "Data Compression Using Adaptive Coding and Partial String Matching," IEEE T-Comm 1984; Willems, Shtarkov, Tjalkens, "The Context-Tree Weighting Method," IEEE T-IT 1995. Mahoney's PAQ family (2002–2012) for the modern ceiling.
- **Where it hit the wall**: PPM-D plateaus around 1.7 bpc on enwik8; CTW similar; PAQ8 reaches ~1.2 bpc but only by *mixing* hundreds of models including neural ones (Mahoney's "Data Compression Explained," 2013). Pure context-counting methods never broke 1.5. Iteration 15 of this very project re-confirmed ~1.5–1.7 bpc on text8 — consistent with the published ceiling.
- **Underlying assumption (A6)**: Conditional probability estimation from suffix counts converges to the true distribution as context length grows, in finite data.
- **Do we share it?**: **Yes, in the PPM component** — and iteration 15 already showed this is binding. The graph + HDC layers are precisely the parts that might escape A6, but only if they contribute information the suffix counter cannot.

## 8. Reservoir computing / Echo State Networks for language

- **Paper**: Jaeger & Haas, "Harnessing Nonlinearity," Science 2004. For language specifically: Tong, Bickett, Christiansen, Cottrell, "Learning grammatical structure with Echo State Networks," Neural Networks 2007.
- **What they built**: Fixed random recurrent reservoir + linear readout trained by ridge regression. Tong et al. trained on Elman-style artificial grammars.
- **Where it hit the wall**: Largest reservoir-LM attempts I can find are in the 10^3–10^4 unit range on synthetic or small natural-language tasks; never approached enwik8 numbers. Memory capacity of an ESN is bounded by the number of reservoir units (Jaeger 2001 tech report) and is linear, not exponential, in N. No published character-LM bpc on standard benchmarks that I am aware of.
- **Underlying assumption (A1, A7)**: A1 fixed-D state; A7 random projection preserves enough task-relevant structure that a *linear* readout suffices.
- **Do we share it?**: **A1 no; A7 partially** — our HDC random binding is also untrained, but the readout is a graph walk, not a linear map. This is a meaningful difference.

## 9. Spiking neural networks for language

- **Paper**: Plank et al., "A Long Short-Term Memory for Spiking Neural Networks (LSNN)," NeurIPS 2018 (Bellec et al., arXiv:1803.09574). For LM specifically: Lotfi Rezaabad & Vishwanath, "Long Short-Term Memory Spiking Networks and Their Applications," ICONS 2020.
- **What they built**: LIF-neuron networks with adaptive thresholds trained via surrogate gradients (BPTT through a smoothed spike). Reported language tasks at small scale (PTB-level, with neural trickery).
- **Where it hit the wall**: Every SNN that reaches competitive LM numbers does so via surrogate-gradient BPTT, which is matmul-heavy; pure event-driven STDP-trained SNNs have not produced a published competitive bpc. The wall is *training rule*, not substrate.
- **Underlying assumption (A5, A8)**: A5 a local biologically-plausible rule (STDP) is sufficient; A8 spike-time coding carries enough bits per event.
- **Do we share it?**: **A5 yes** — we are also betting on a non-gradient local rule. SNN failure to find such a rule for language at scale is negative evidence for our own bet, and should be acknowledged.

## 10. Thermodynamic / probabilistic computing — Extropic, Normal Computing

- **Paper**: Coles et al. (Normal Computing), "Thermodynamic Computing System for AI Applications," arXiv:2312.04836 (2023). Extropic has issued white papers and a 2024 litepaper but, to my knowledge, no peer-reviewed LM result as of the cutoff.
- **What they built**: Analog stochastic hardware that samples from Gaussian / Boltzmann distributions natively; demonstrated linear-algebra primitives (matrix inversion, Gaussian sampling) on small prototypes.
- **Where it hit the wall**: As of my knowledge, **no thermodynamic-computing system has demonstrated a language model of any size on real text.** Demonstrations are linear-algebra microbenchmarks. The claim "thermodynamic LM" is currently aspirational.
- **Underlying assumption (A9)**: Sampling is the bottleneck; once sampling is cheap, useful generative models will follow.
- **Do we share it?**: **No.** Rule-world is deterministic at inference; sampling cost is not our bottleneck.

## 11. Gradient-free deep learning rules

A grouped entry — five rules, one wall.

- **Papers**:
  - Feedback Alignment: Lillicrap et al., "Random synaptic feedback weights support error backpropagation," Nature Comm 2016 (arXiv:1411.0247).
  - Direct Feedback Alignment: Nokland, NeurIPS 2016 (arXiv:1609.01596).
  - Predictive Coding: Whittington & Bogacz, Neural Computation 2017; Millidge et al., "Predictive Coding Approximates Backprop Along Arbitrary Computation Graphs," Neural Computation 2022 (arXiv:2006.04182).
  - Equilibrium Propagation: Scellier & Bengio, Frontiers in Computational Neuroscience 2017 (arXiv:1602.05179).
  - Forward-Forward: Hinton, "The Forward-Forward Algorithm," arXiv:2212.13345 (2022).
- **What they built**: Five distinct local-or-semi-local learning rules intended to replace backprop.
- **Where it hit the wall**:
  - FA: degrades on convolutional networks deeper than ~6 layers; fails on ImageNet (Bartunov et al. NeurIPS 2018, arXiv:1807.04587).
  - DFA: Launay et al. arXiv:2006.12878 actually scales DFA to Transformers but loses several points on WMT and ~5 perplexity on PTB-class LM vs backprop.
  - Predictive coding: matches backprop on MNIST/CIFAR; no reported competitive LM bpc.
  - EqProp: works on small MLPs; scaling to convnets requires the "holomorphic" trick (Laborieux 2021); no LM result.
  - Forward-Forward: Hinton 2022 reports MNIST and small CIFAR; no LM.
- **Underlying assumption (A5, A10)**: A5 a local rule suffices; A10 the rule must still parameterize a *dense weight matrix per layer* and learn it.
- **Do we share it?**: **A5 yes, A10 no** — we have no weight matrices to learn. The gradient-free literature's failure suggests A10 may be the actual wall: it is not enough to replace backprop if you keep the dense parameters. Rule-world drops A10 entirely, which is the single most distinctive thing about it.

## 12. Tensor-network LMs — MPS / MERA

- **Paper**: Stoudenmire & Schwab, "Supervised Learning with Tensor Networks," NeurIPS 2016 (arXiv:1605.05775). For LM specifically: Pestun & Vlassopoulos, "Tensor network language model," arXiv:1710.10248 (2017); Miller, Rabusseau, Terilla, "Tensor Networks for Probabilistic Sequence Modeling," AISTATS 2021 (arXiv:2003.01039).
- **What they built**: Matrix Product State / Born-machine LMs whose parameters are a chain of small tensors; sampling and likelihood are exact.
- **Where it hit the wall**: Bond dimension chi must grow exponentially with the entanglement (mutual-information) of the sequence. Miller et al. 2021 report competitive results on small-vocab synthetic tasks but bond dim required for natural language is empirically prohibitive; no published competitive bpc on enwik8. Contraction is also a sequence of matmuls — so even when it works, it isn't matmul-free.
- **Underlying assumption (A1, A11)**: A1 fixed-bond-dim state; A11 mutual information across long-range dependencies in language is low enough to compress into a 1D MPS.
- **Do we share it?**: **A1 no; A11 unclear** — we are betting that the *graph* can route long-range information that an MPS cannot. This is testable.

## 13. Spaun / Semantic Pointer Architecture — Eliasmith

- **Paper**: Eliasmith et al., "A Large-Scale Model of the Functioning Brain," Science 2012; Eliasmith, *How to Build a Brain*, OUP 2013.
- **What they built**: 2.5M-spiking-neuron model that performs eight cognitive tasks via Semantic Pointers (HRR-style 512-D vectors) routed through a basal-ganglia action-selection circuit. Closest existing system to "HDC + symbolic controller."
- **Where it hit the wall**: Spaun is hand-engineered task-by-task; it does not learn from a corpus and is not a language model. SPA's vector dimension (~512) and the binding noise floor mean that the working set is a few dozen items. No bpc number exists.
- **Underlying assumption (A1, A3)**: A1 fixed-D; A3 task-specific encoder.
- **Do we share it?**: **A1 no; A3 yes.** Spaun is the most architecturally similar prior art to rule-world. Its failure to generalize is informative: the missing piece is *learning the encoder from data*, which Spaun never tried and rule-world also has not solved.

## 14. (Optional) Neural Turing Machines / DNC — external memory

- **Paper**: Graves et al., "Neural Turing Machines," arXiv:1410.5401 (2014); "Hybrid computing using a neural network with dynamic external memory" (DNC), Nature 2016.
- **What they built**: Differentiable controller + external memory matrix with content- and location-based addressing.
- **Where it hit the wall**: Controller is matmul-heavy. Memory addressing is differentiable softmax — quadratic. DNC reaches small algorithmic tasks but no competitive LM bpc; eclipsed by Transformers immediately. Relevant to us only because it confirms that *external content-addressable memory* + small controller is a viable architecture in principle.
- **Underlying assumption (A4, A10)**: Differentiable everything; dense controller.
- **Do we share it?**: **No.** But the existence of DNC is positive evidence for the "graph-as-context" structural choice — what failed was the differentiable controller, not the external memory idea.

---

## Shared Assumptions

Distinct assumptions appearing in 2+ entries:

- **A1 — Fixed-capacity dense state vector for context.** Appears in: HDC bundling (1), HRR (2), SDM (3), classical Hopfield (4), ESN (8), MPS (12), Spaun (13). **Seven entries.** This is by far the dominant shared assumption.
- **A3 — Encoder is fixed / hand-designed, not learned from data.** Appears in: SDM (3), HTM (6), Spaun (13). Three entries.
- **A4 — Exponential capacity / good associative recall requires a dense inner product over all stored patterns.** Appears in: modern Hopfield (5), DNC (14). Two entries — but notably, no published method has refuted this.
- **A5 — A local biologically-plausible rule suffices to learn conditional structure.** Appears in: HTM (6), SNNs (9), gradient-free deep learning (11). Three entries — and uniformly negative results at LM scale.
- **A6 — Suffix-count statistics asymptotically capture the conditional distribution.** Appears in: PPM/CTW (7) and implicitly in HTM sequence memory (6). Two entries.
- **A10 — A local rule must still parameterize and learn dense per-layer weights.** Appears in: all of (11). One grouped entry but five papers' worth.

### Test of the prior claim

The leave-off summary asserts: *"every prior matmul-free LM compressed context into a fixed-capacity dense state vector and hit saturation."*

Reading the inventory honestly, this claim is **strongly but not universally supported**.

- **Supported by**: HDC bundling (1), HRR (2), SDM (3), Hopfield (4), ESN (8), MPS (12), Spaun (13). Seven of the most-cited matmul-free or near-matmul-free generative substrates do exactly this and do hit a capacity-related wall.
- **Partially supported by**: HTM (6) — uses SDRs (sparse but still fixed-cell-count); the wall is more about the local learning rule than capacity per se.
- **Refuted by / orthogonal**: PPM/CTW (7) does *not* use a fixed-D state vector — it uses an unbounded suffix tree — and it still hits a wall (~1.5 bpc). So A1 is not the *only* possible wall; A6 (suffix statistics ≠ true conditional) is a separate, independent wall that rule-world also faces. Compression-based LMs disprove the strong form of the prior claim: there exists at least one matmul-free LM family that does not compress to fixed-D and still saturates.

So the corrected statement is: *"Almost every matmul-free LM hits a wall; in most cases that wall is fixed-D state capacity (A1), but in the compression family the wall is the asymptotic insufficiency of suffix statistics (A6). These are two distinct walls, not one."* Iteration 15's PPM-D result is a data point on the second wall, not the first.

### What rule-world drops vs inherits

**Already dropped:**
- A1 (fixed-D context state): the property graph is unbounded.
- A4 (dense inner-product recall): hash-indexed graph lookup is sub-linear.
- A10 (dense per-layer weights to learn): no weights anywhere.
- A9 (sampling-bottleneck assumption): inference is deterministic.

**Still inherited:**
- A3 (fixed, hand-designed encoder): our HDC encoder is not learned. **Shared with HTM and Spaun, both of which failed.**
- A5 (local rule suffices to learn conditional structure): PPM counters are local. **Shared with HTM, SNN-LMs, and the gradient-free family, all of which failed at LM scale.**
- A6 (suffix counts converge to true distribution): directly inherited via the PPM component, and iteration 15 just confirmed this binds at ~1.5–1.7 bpc.
- A2 (binding SNR degrades with depth): inherited *only* on paths that route through HDC retrieval, not on graph-only paths.

### Most "breakable" assumptions

These look most like path-dependent historical accidents rather than mathematical necessities, ranked by my subjective confidence that they can fall:

1. **A1 (fixed-D state).** Already broken by the existence of compression-based LMs and by rule-world's graph context. The literature treats it as universal because the dominant lineage is connectionist; it isn't mathematically forced. Highest confidence breakable.
2. **A10 (must parameterize dense per-layer weights and learn them).** The entire gradient-free literature implicitly assumes this — they replaced backprop but kept the weights. Rule-world is the natural test of dropping it.
3. **A3 (fixed, hand-designed encoder).** Breakable in principle (online HDC encoder learning has been sketched by Frady et al., Kleyko et al.), and the most strategically important one for rule-world to break next, because A3 is the assumption we share with the two prior systems most architecturally similar to ours (HTM, Spaun) — both of which failed to scale.

The single most consequential finding of this inventory: **the wall iteration 15 hit (A6, suffix-statistic insufficiency) is independent of the wall the connectionist matmul-free literature mostly hit (A1, fixed-D capacity).** Rule-world has dropped A1 architecturally but is still bound by A6 in its predictor and by A3 + A5 in its learning story. Iteration 17 should attack A3 (learn the HDC encoder online from graph structure) before attacking anything else, because A3 is the assumption that connects rule-world to the two closest prior systems in the inventory and is the assumption whose break would most clearly differentiate the stack from HTM/Spaun.

---

### What this iteration does not prove

- It does not prove rule-world will succeed where HTM and Spaun failed. The shared A3/A5 assumptions are real and the prior failures are negative evidence on our own bet. The inventory only sharpens *which* specific bet is the live one.
- It does not exhaustively cover the literature. Twelve grouped entries is depth-not-breadth by design; entire neighbors (Boltzmann machines, RBMs, energy-based models more generally, neural ODEs, state-space models like Mamba) are out of scope and could shift conclusions.
- The unverified claims flagged inline (HTM character-LM ~2.5 bpc community number, Joshi 2016 venue attribution, current Extropic publication state) should be spot-checked before any of this is quoted externally.
- "Breakable" is a subjective ranking of where path-dependence is most plausible, not a proof any of these assumptions actually fall.
- Most importantly: the inventory identifies *where to swing*, not whether the swing connects. Iteration 17 is still a real research bet whose outcome is unknown.

*Caveats on this inventory: The HTM character-LM bpc number (~2.5) is from community recollection, not a published paper I can cite — flag for verification. The Extropic claim of "no peer-reviewed LM result" is true to my knowledge cutoff but the field is moving; verify before publishing. The Joshi 2016 attribution to a specific venue should be double-checked; the random-indexing language-ID line of work has multiple overlapping publications.*

