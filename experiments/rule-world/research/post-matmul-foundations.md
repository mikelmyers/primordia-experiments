# Post-matmul foundations for generative reasoning

**A research note from the Track B experiment**
*Status: living document. Capture of mathematical thinking, not a final result.*

---

## The question

Transformer-based LLMs achieve generative intelligence through dense matrix
multiplication at massive scale. That math requires GPUs, GPUs require data
centers, and data centers require trillion-dollar capital. This creates a
monopoly on intelligence.

We are asking: **does there exist a fundamentally different mathematical
foundation that can produce equivalent or superior generative intelligence
without matrix multiplication at scale?**

This is not a question about optimizing transformers or shrinking models. It
is a question about whether the matmul–GPU–datacenter pipeline is a
mathematical necessity or a contingent engineering choice.

This document is the mathematical thinking we did before deciding what to
build next. It does not answer the question. It frames it precisely enough
that the next experiments can produce real signal.

---

## Part 1 — What generation actually requires

Strip every implementation away. A generative system is a function

$$G : \mathcal{C} \to \Delta(\mathcal{Y})$$

mapping a context space $\mathcal{C}$ to probability measures over an output
space $\mathcal{Y}$, applied recursively so that $y_t \sim G(c_t)$ and
$c_{t+1} = f(c_t, y_t)$.

That's the surface. The four irreducible requirements beneath any
implementation are:

**(1) Compression.** $\mathcal{C}$ is combinatorially huge — for natural
language, $|\mathcal{C}| \approx |V|^n$ for vocabulary $V$ and context
length $n$, which is around $50000^{4096}$. You cannot store $G$ as a
lookup table. You need a representation using $\ll |\mathcal{C}|$ bits.
**Generation is dual to compression.** This is Shannon's prediction–
compression duality, and it is mathematically airtight: the best language
model is the best compressor of language and vice versa.

**(2) Generalization / interpolation.** $G$ must produce sensible outputs
for contexts it has never seen exactly. This means $G$ must be defined by
some smoothness property under some metric on $\mathcal{C}$. The choice of
metric is the choice of inductive bias.

**(3) Composition / recursion.** The output $y_t$ must be encodable back
into the context for $t+1$. This requires that $\mathcal{C}$ and $\mathcal{Y}$
share an algebra — usually $\mathcal{Y} \subseteq \mathcal{C}$ or there is
a natural embedding.

**(4) Learnability.** $G$ must be parameterizable by some object $\theta$
such that you can update $\theta$ from $(c, y)$ pairs efficiently. This is
historical, not mathematical — a perfect $G$ with hand-set $\theta$ would
still generate. Learnability is what makes generation scale beyond what
humans can author.

### The decomposition that matters

Any function from contexts to distributions can be factored as:

$$G(c) = \mathcal{A}\big( \{ (s_i, y_i) : s_i = \kappa(c, c_i) \} \big)$$

where $\kappa$ is a **similarity structure** on contexts (kernel, metric,
graph adjacency, topology, congruence) and $\mathcal{A}$ is an **aggregation
operator** that combines outputs from contexts the similarity structure
rates as nearby. Every working generative system instantiates this template:

- k-NN regression: $\kappa$ = Euclidean metric, $\mathcal{A}$ = mean of $k$ nearest
- Gaussian processes: $\kappa$ = RBF/Matérn kernel, $\mathcal{A}$ = Bayesian posterior
- Transformers: $\kappa$ = learned dot-product attention, $\mathcal{A}$ = softmax-weighted value combination + MLP nonlinearity + autoregressive iteration
- Diffusion models: $\kappa$ = noise-conditional score field, $\mathcal{A}$ = Langevin / probability flow ODE integration

**Matrix multiplication is one mechanism for implementing all four
requirements simultaneously, but it is not a logical requirement of any of
them.**

- Compression: matmul compresses by linear projection. Other codes (Huffman, arithmetic, Lempel-Ziv, contextual prediction trees) also compress.
- Generalization: matmul generalizes by linearity. Other functions also generalize (kernel methods, nearest neighbor, decision trees with smoothing).
- Composition: matmul composes by associativity. So do groups, monoids, categories, lambda calculus.
- Learnability: matmul is learnable by gradient descent because it is differentiable. Other parameterizations are learnable by other methods (Hebbian, Bayesian, evolutionary, compression-based).

**The transformer's specific bet is that all four requirements can be met
efficiently by a single mathematical primitive (matmul) at the cost of
needing massive scale to compensate for weak inductive biases.** The bet
paid off because matmul is hardware-friendly, gradient descent is
well-understood, and "weak biases + scale" turned out to work better than
"strong biases + cleverness" for language.

The mathematical statement of the post-matmul question is:

> Find an induction method other than gradient descent on dense matrices
> that can extract the empirical regularities of an open domain at
> competitive quality and cost.

Everything else is detail.

---

## Part 2 — Survey of mathematical landscapes

Honest verdicts from the survey, kept brief.

| Framework | Generation | Reasoning | Cost | Verdict |
|---|---|---|---|---|
| **Probabilistic graphical models** | yes (ancestral sampling) | native | #P-hard general, polynomial sparse | indispensable for structured reasoning, insufficient as open-language substrate |
| **Topological data analysis** | no | limited | polynomial | analysis tool, not substrate |
| **Category theory** | indirectly | yes | theoretical | meta-language not engine |
| **Cellular automata** | yes (Turing-complete) | possible | parallel-cheap | inverse problem intractable; no learning method |
| **Tensor networks (MPS, MERA, PEPS)** | yes | limited | polynomial in bond dim | post-transformer, not post-matmul; could shrink models 10–1000× |
| **Geometric algebra** | not natively | spatial | linear-algebra-like | refines matmul for symmetric domains; doesn't replace |
| **Hyperdimensional computing / VSA** | yes (associative retrieval) | strong (analogy native) | O(d) XOR/sum | **strongest single candidate**; never tested at language scale |
| **Sparse distributed representations / HTM** | yes (sequence prediction) | limited | sparse, very cheap | same profile as HDC; 20 years of marginal results |
| **Reservoir computing** | yes (time series) | limited | training is regression | viable for subsystems, not whole stack |
| **Thermodynamic / probabilistic computing** | yes (native physical sampling) | depends on energy fn | thermodynamic minimums | **strongest hardware bet**; programming the energy fn is the bottleneck |
| **Information geometry** | indirect | analytic | conceptual | lens, not engine |
| **Causal inference / do-calculus** | yes (SCM sampling) | native | cheap if SCM known | right tool for reasoning, hard to learn structure from text |
| **Process algebra** | as descriptions | yes | model checking | wrong tool |
| **Free energy principle / active inference** | yes (predictive sampling) | yes | depends on gen model | descriptive, computationally underdetermined |
| **Compression-based prediction (PPM, CTW, arithmetic)** | yes | limited | polynomial | matmul-free; abandoned in 2017; **deeply underexplored at modern scale** |
| **Spiking neural networks / neuromorphic** | yes | possible | event-driven, sparse | hardware exists; training brittle; not yet competitive |

The two strongest single candidates with the right computational profile
(no matmul, parallelizable, hardware-friendly) and unproven scaling
behavior are **HDC** and **thermodynamic computing**. HDC is testable in
software today. Thermodynamic computing requires hardware that exists only
in early prototype.

A third deeply underexplored candidate is **compression-based language
modeling** combined with structured priors. Pre-transformer compression LMs
were respectable in the 1990s and 2000s. Nobody has revisited them with
modern hardware, modern data, modern compute budgets, or modern
compositional structure. The field collectively stopped looking in 2017.

---

## Part 3 — Promising unexplored combinations

The history of breakthroughs suggests they come from combining frameworks
that were never seriously tried together. Three combinations:

### Combination A — HDC + symbolic rule engine + property graph

HDC handles distributed similarity-based retrieval. The rule engine handles
hard logical constraints and deductive verification. The property graph
provides grounded semantics for entities, so HDC's analogies are validated
against actual property overlap rather than just structural similarity.

**What emerges that none has alone: principled analogy under hard
constraints.** Pure symbolic abstraction substitutes strings without
grounding. Pure HDC retrieves by similarity without logical guarantees.
Combined, HDC retrieves structurally similar rules, the property graph
checks whether the analogy makes semantic sense, and the engine verifies
the substituted rule is consistent with hard constraints.

This is the combination we are actively building. The current rule-world
codebase has the engine and a primitive abstractor; the HDC layer is
partial; the property table is small.

### Combination B — Tensor networks + HDC

Tensor networks compress high-dimensional functions into structured
factorizations with exponential parameter savings. HDC encodes structured
items as high-dimensional vectors. The natural pairing: an MPS-style
factorization of an HDC associative memory, where bond dimension acts as a
hidden state width and the items are HDC encodings.

**What emerges: parameter efficiency of TN with the symbolic structure of
HDC.** Generation becomes "contract the tensor train conditioned on the
context, decode the result by similarity search." Speculative — nobody has
built it. Open question: do HDC distributions factorize cleanly into tensor
train form? Intuition says yes, because HDC binding is multiplicative in
spectrum.

Caveat: tensor contraction is multiplication of small tensors. Strictly
this is "structured matmul" not "no matmul." But FLOPs could be 1000×
smaller than dense transformers — enough to change what hardware is needed.

### Combination C — Thermodynamic sampling + symbolic energy function

A symbolic system (rules + properties + graph) defines an energy function
$E(x)$ over outputs. A thermodynamic chip returns $x \sim e^{-E(x)/T}$ in
physical time, no matrix multiplication. The symbolic system never
generates; it only judges. The sampler never reasons; it only samples.

**What emerges: the only architecture in this list where the generation
step itself uses no arithmetic.** A thermodynamic chip relaxes to its
equilibrium distribution by the same process water finds its level. The
math is statistical mechanics; the implementation is solid-state physics.

Unsolved problem: compiling a symbolic rule set into an energy function a
physical chip can implement. Boolean SAT to Ising is well-studied. Soft
constraints to QUBO is well-studied. Composing these for a multi-domain
symbolic system at language scale is not yet attempted.

---

## Part 4 — Do we need new mathematics?

Honest answer: no, we do not need a new branch of mathematics. The
components exist, scattered across HDC, sparse coding, kernel methods,
categorical probability, causal inference, compression theory, and
statistical mechanics. What is missing is **theoretical glue** that lets
these components compose with quality guarantees.

The single unsolved math problem whose solution would unlock the rest:

> **Find a learning rule for distributed representations that (a) is
> gradient-free, (b) scales linearly in data, (c) provably converges to
> representations capturing the conditional structure of the training
> distribution, and (d) composes across layers.**

Existing pieces:
- Hebbian learning: satisfies (a), partially (b); fails (c) and (d) at depth
- Contrastive divergence: satisfies (a) and (c) shallow; fails (d)
- HDC encoding: satisfies (a) and (d); fails (c) — HDC representations don't *learn*, they're constructed from a fixed encoding scheme
- Compression algorithms: satisfy (a), (b), (c) for surface statistics; fail (d) for deep compositional structure

A construction of a learning rule satisfying all four would be a major
positive result and would change everything. A proof none can exist would
be a major negative result and would tell us matmul is mathematically
necessary.

This is the math problem hiding under the engineering question. It has
been neglected because the field went all-in on gradient descent in 2012
and never came back. Statistics, dynamical systems, and information theory
all hold pieces of the puzzle. Nobody is currently combining them
seriously.

---

## Part 5 — Minimum viable test

The highest-information-per-line-of-code experiment that fits on top of the
rule-world codebase: **add an HDC-based associative memory to the
abstractor and test whether it can crystallize correct rules in cases where
the current syntactic abstractor crystallizes wrong ones.**

Concretely:

1. Each rule is encoded as a 10,000-bit bipolar HDC vector. Encoding uses
   bind/bundle to compose antecedents, consequents, action, and tags.
2. Build a small property table for substances (water, ice, wood, oil,
   food, medicine) with 2–4 properties each.
3. Replace the syntactic substitution in the abstractor with HDC analogy:
   compute the HDC similarity between the new substance's property bundle
   and each existing peer's property bundle. Substitute only when
   similarity exceeds a threshold.
4. Add adversarial scenarios: stranger carrying oil (feeds fire), food
   (neutral), medicine (neutral). Compare what each abstractor crystallizes.

This was built (see `hdc.py`, `abstractor.crystallize_by_hdc_analogy`,
scenarios 8–10). Honest results from the first run:

| Scenario | HDC verdict | Honest reading |
|---|---|---|
| 8 — oil | picked water (sim +0.18), wrong | HDC failed because the right analog (wood) was excluded from the head-match peer set |
| 9 — food | picked ice (sim +0.20), wrong but rejected water/oil | HDC's threshold caught the worst syntactic substitution; still picked an irrelevant analog via shared "solid" property |
| 10 — medicine | picked food (sim +0.26), correct (both `neutral_to_fire`) | once food was in the store, HDC chained the analogy correctly |

**The mixed result confirmed two specific failure modes the next iteration
should attack:**

1. **Peer search must escape syntactic head matching.** S8's failure is
   entirely caused by restricting peer search to predicates with the same
   head. Wood was excluded by structure even though it was correct by
   property. The fix is unconstrained property-table search.

2. **Property bundles need internal structure.** HDC's flat bundle treats
   `solid` and `extinguishes_fire` equivalently. To make `food → ice` lose
   to `food → no analog`, properties must be weighted by their role in the
   active rule context.

These two fixes are the next experiments. If they work, distributed
analogy under property grounding becomes a real grounded-generation
mechanism with no matmul. If they don't, the limitation is inherent to
flat HDC bundles and the next move is full property graphs with explicit
causal structure.

---

## Bottom line

The math says the post-matmul question is **open**. The empirical record
says **nobody is testing it** with modern resources. That combination —
open question, untested by anyone — is exactly the configuration where
breakthroughs happen, and exactly the configuration where dead ends also
happen. There is no way to tell the difference except by trying.

The next experiments to run, in order:

1. Unconstrained HDC peer search (`crystallize_by_hdc_analogy_v2`)
2. Role-weighted HDC encoding (`crystallize_by_hdc_analogy_v3`)
3. Compression-based prediction over rule-world traces (PPM/CTW baseline)
4. Property-graph-grounded HDC with causal entailment chains
5. (Hardware permitting) thermodynamic sampling with symbolic energy fn

This document will be updated as each experiment produces signal.

---

## Update — v4 results and the loop closing

After v3 (role-weighted similarity) we built v4 = role-weighted analog
selection + token-level rule projection + analogous action synthesis. The
key result is **scenario 11 (the loop-closing test)**.

**Setup.** Hearth burning low. Stranger arrives carrying a jar of oil.

**Pipeline.**
1. Parser extracts `hearth_burning_low`, `stranger_carries_oil`, `oil_available`.
2. v4 in production write mode targets the substance `oil`. Role-weighted
   similarity selects `wood` as the analog (sim **+0.5152** vs all others ≈ 0).
3. v4 projects three rules from wood-referencing rules by token substitution:
   - `P3a~oil_v4`: `oil_in_hearth ∧ hearth_burning ⇒ hearth_fed`
   - `P-wood-leaving~oil_v4`: `oil_held_by_child ∧ child_at_door ⇒ oil_leaving_hall`
   - `C3~oil_v4`: `oil_supply_insufficient ⇒ requires oil_replenishment_initiated`
4. v4 synthesizes three actions by token substitution from wood-referencing
   actions:
   - `add_oil_to_hearth` (from `add_wood_to_hearth`)
   - `initiate_oil_replenishment_plan`
   - `leave_hall_to_gather_oil`
5. Engine runs against the now-extended store + action library. The only
   action that doesn't violate a visceral constraint is `add_oil_to_hearth`,
   which adds `oil_in_hearth`, removes `hearth_burning_low`, fires
   `P3a~oil_v4` to derive `hearth_fed`, and satisfies R1.
6. Engine chooses `add_oil_to_hearth` (score 267).

**What this proves.** The system produced a behavioral choice that depends
on a rule and an action *neither of which existed before this turn*. Both
were synthesized at runtime by HDC analogy + token substitution, with zero
matrix multiplication. This is the first time the system generated novel
output that flows through to behavior change.

**What it does not prove.**
- **It is not free generation.** The synthesis is bounded by token
  substitution from existing structures. No fundamentally new rule shape or
  action pattern can emerge — only renamings of existing patterns onto new
  objects. This is a real ceiling, not a bug.
- **It is not natural language generation.** There is no NL output layer.
  The engine produces structured choices; we have not yet built a path from
  those choices to fluent text without an LLM.
- **There is no retraction.** The wrong rules from S8's syntactic
  abstractor (R3~oil etc.) are still in the store. v4's correct
  crystallizations sit alongside the wrong ones. We need rule hygiene.
- **The token projection is unfiltered.** v4 projects every rule that
  contains the analog token, including ones that are structurally valid
  but semantically irrelevant (C3~oil for "oil supply" management).
- **The action library is closed.** v4 synthesizes new actions by mirroring
  existing ones. It cannot invent actions that don't have an analog source.

---

## Updated landscape after v4

The HDC + property-grounding + token-substitution stack now demonstrates:
- ✅ Grounded analog selection (v3, v4)
- ✅ Threshold-based rejection of bad analogies (v3)
- ✅ Structural rule projection (v4)
- ✅ Action synthesis by analogy (v4)
- ✅ End-to-end behavior change from autonomous synthesis (scenario 11)

The next bottlenecks, in priority order:
1. **Rule hygiene** — confidence-based suppression of contradicted rules
2. **Projection filter** — semantic check before token substitution
3. **Action sequencing** — STRIPS-style search over multi-step plans
4. **Alternative math foundation** — compression-based prediction as a
   non-HDC test of grounded analogy
5. **NL output layer** — the hardest unbuilt piece; requires either small
   LLM articulation OR a structured-to-text grammar

Items 1–3 are HDC stack improvements. Item 4 is a parallel track testing
a different mathematical foundation. Item 5 is the missing piece for any
"replace LLMs" claim.

---

## What this means for the research question

The Track B hypothesis was: *can a symbolic engine + small LLM replace
trillion-parameter generative models?*

After v4, the honest split:

- **For closed-domain reasoning where the rule store can be authored or
  grown by analogy:** the answer is increasingly "yes." The system handles
  conflict resolution, multi-rule composition, gap detection, grounded
  analogy, and now structural synthesis of novel rules and actions. With
  rule hygiene + projection filtering it would be a credible production
  reasoner for any domain where you have a property table.
- **For open-domain free generation:** the answer is still "no." The
  bottleneck is no longer reasoning — it is the synthesis mechanism's
  expressive ceiling (token substitution) and the absence of any NL
  output layer.

The next experiment that would move the answer is **(item 4)** —
compression-based prediction over the rule store, as a non-HDC test of
whether grounded analogy is achievable from a fundamentally different
mathematical foundation. If compression-based modeling can match HDC's
performance on the adversarial scenarios, that would be evidence that
grounded analogy is a *property of the right representation*, not an
artifact of HDC specifically. If it cannot, that would localize HDC as
a uniquely useful primitive.

This document should be updated again after items 1–4 land.
