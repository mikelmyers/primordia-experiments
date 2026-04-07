# Continuation prompt — paste this as the first user message in a fresh session

You are continuing a long-running research investigation into whether
generative intelligence can be built without matrix multiplication at
scale. This is **research, not a product**. We are not optimizing for
demos. We are not pitching anything. We are asking an open scientific
question and following it where it leads, including into negative
results.

## What you are walking into

Repository: `mikelmyers/primordia-experiments`.
Branch: `claude/review-continuation-prompt-9afno`.
HEAD: `807d5a1` (Iteration 15 landed and pushed).
Iterations complete and committed: 1 through 15.
Iteration 16 is **in progress and not yet committed** — the literature
review was run, the findings are summarized below, but the write-up
files have not been created. Your first job is to finalize iteration
16 to disk, then move to iteration 17.

## The four documents you must read first, in order

1. **`experiments/rule-world/research/post-matmul-foundations.md`** —
   the math. Parts 1–5 plus updates. Specifically internalize Part 2
   (the landscape) and Part 4 (the unsolved math problem).

2. **`experiments/rule-world/research/progress-log.md`** — the
   chronological lab notebook through iteration 15. Iteration 15 is
   the first real swing at the open-domain side of the trillion-dollar
   question. Read it carefully, especially its "what this does not
   prove" section. Iteration 16 entry does not exist yet; you will
   write it.

3. **`experiments/rule-world/research/WHERE-WE-STAND-2026-04-06-1817.md`** —
   the research-state snapshot. It has been amended with a
   post-iteration-15 headline. Iteration 16 amendment is not there
   yet; you will add it after finalizing iteration 16.

4. **`experiments/clm/iter15_results.md` and `iter15_results.json`** —
   the PPM-D vs nanoGPT bpc table on text8. This is our anchor
   empirical data point for the open-domain question.

## The claim space as of iteration 15

Claimable:
- Closed-domain reasoning without matmul across N=3 unrelated domains
  (rule-world, traffic-world, kitchen-world).
- Property induction at 89% top-1, humanization induction at 33%.
- Verbose NL explanation across 28/28 scenarios.
- **First open-domain data point (iteration 15):** PPM-D order 6 on
  text8 at 90 MB reaches **1.731 bpc** on a 500 KB held-out slice.
  A compute-matched CPU nanoGPT baseline (420 s wallclock, 814K params)
  plateaus at ~2.52 bpc at every training size — compute-bound, not
  data-bound. The gap to the published Transformer-XL ceiling
  (~1.08 bpc) is 1.60×, just past the pre-declared 1.5× live-signal
  threshold.

Not claimable:
- Open-domain free text generation. Still untouched.
- Any answer to the trillion-dollar question.
- A well-funded transformer baseline we ran ourselves (we only have
  published ceiling numbers to cite).

## What iteration 16 found (do NOT lose this)

Iteration 16 was not a code iteration. It was a structured
literature review of every serious prior attempt at matmul-free /
gradient-free generative substrates. Coverage: HDC/VSA for language,
classical and modern Hopfield, Numenta HTM, compression LMs (PPM/CTW/
cmix/NNCP), reservoir computing, spiking NNs (incl. SpikeGPT — which
is backprop-trained and not matmul-free), thermodynamic computing
(Extropic/Normal — no published LM results), feedback alignment
(Bartunov 2018 — the canonical scale-up negative result), predictive
coding (μPC 2025 — vision only), equilibrium propagation (ImageNet-32,
no text), Hinton's forward-forward (MNIST/IMDb only), tensor networks
for language (PTB/WikiText-2, bond-dimension wall), Eliasmith's Spaun
(HRR chain-length noise wall).

**The payoff of the review — the shared-assumptions section — is the
main output.** Six assumptions recur across the walls. The three
strongest form a single wall in three vocabularies:

- **A1:** "A single fixed-capacity vector must carry the context."
  (HDC bundling, HRR binding, Hopfield attractors, MPS bond dimension,
  ESN spectral horizon — all the same wall.)
- **A4:** "Scaling means denser." (Every substrate's scale-up knob
  increases the density of a dense-matmul-equivalent operation.)
- **A6:** "Long-range dependencies must live in the substrate's
  state." (All RNN-family substrates + HDC + TN.)

These three together are the wall every matmul-free LM attempt has
hit. The transformer's actual innovation, viewed from this inventory,
is not "matmul" or "attention" — it is **"stop compressing context
into a state vector at all; keep the raw context around and look it
up against it."** Transformers do this with KV cache + softmax.
Databases do it with indices + lookups.

**The critical research observation:** our existing property-graph +
symbolic-engine architecture (rule-world, traffic-world, kitchen-world)
already makes the same architectural move — *without matmul*, by
replacing softmax-over-keys with index-lookup-over-graph-nodes. We
already drop A1. We already drop A6. The PPM-D experiment in
iteration 15 is the negative control: it keeps A1 (a dense parametric
context model) and plateaus exactly where the theory predicts it
should.

Two other shared assumptions also stand out as droppable:
- **A2:** locality of the learning rule (biological constraint, not
  logical — we aren't trying to be biologically plausible).
- **A5:** biological/physical plausibility as a design constraint
  (inherited by most of the field — not inherited by our stack).

A3 (generation = sampling from a parametric distribution fit by loss
minimization) is the subtlest. Symbolic engines can generate by
**construction** (graph traversal + rewriting) rather than by
sampling. This is the conceptual bridge to iteration 17+.

## Iteration 16 — what you must write to disk

**Do not re-run the literature review.** The findings are durable;
copy them from the iteration-16 section in the chat history of the
session that was interrupted. If the full findings are unavailable,
re-run a focused subagent search with the same prompt structure:
target 10–12 entries with {name, citation, what built, best scale,
best metric, failure mode, underlying assumption, do-we-share-it,
confidence}, and the shared-assumptions section at the end.

Files to create:

1. `experiments/rule-world/research/failure-modes-inventory.md` — the
   full inventory. Keep entries faithful to the subagent's findings,
   clean the formatting, add a preamble explaining the iteration and
   the method. The shared-assumptions synthesis section is the main
   payoff and must be present.

2. `experiments/rule-world/research/progress-log.md` — append an
   iteration 16 entry following the template (Hypothesis → What was
   built → Result → What this proves → **What this does not prove**
   → Status of the trillion-dollar reframe). Iteration 16 is a
   **literature-synthesis iteration**, not a code iteration. The
   hypothesis: "structured inventory of prior failure modes will
   localize shared assumptions that, if broken, would open new
   ground." The result: the six shared assumptions, with the finding
   that our existing stack already drops A1/A4/A6 and the PPM-D
   experiment is the negative control. The "what this does not
   prove" section is mandatory and should explicitly include: (a)
   the inventory is not exhaustive, (b) "never tested at scale" is
   not the same as "would work at scale," (c) shared-assumption
   analysis can be wrong even when the inventory is right, (d) the
   synthesis may be confirmation-biased toward our existing stack.

3. `experiments/rule-world/research/WHERE-WE-STAND-2026-04-06-1817.md`
   — add a post-iteration-16 amendment at the top, under the
   post-iteration-15 amendment, with the six shared assumptions and
   the architectural observation that our stack already drops three
   of them.

4. Commit + push with a clear iteration-16 commit message.

## How to behave (unchanged from earlier continuation prompts)

- Be honest about uncertainty. Negative results are valuable output.
- "What this does not prove" is mandatory on every iteration entry.
- Do not pitch the architecture as a product.
- Do not modify `engine.py`, `abstractor.py`, `hdc.py`,
  `compression.py`, `retriever.py`, `rule_store.py` without flagging
  the change as a rule-world architecture event in its own iteration.
- Rule-world is the source of truth. Transfer domains validate.
- Match the iteration template.
- The trillion-dollar question is the only goal. Polishing the
  closed-domain stack is fine when it serves the research, not when
  it serves an imagined product.

## What the user wants you to do next (iteration 17 candidates)

After finalizing iteration 16 to disk, propose iteration 17. The
shared-assumptions finding reorders the direction ranking from the
earlier continuation prompt. In priority order:

1. **Extend the property-graph substrate toward open-domain generation
   by construction, not by sampling.** This is the A1/A3/A6 swing.
   Concretely: can the rule-world engine generate a novel paragraph
   about a grounded topic by graph traversal + token substitution +
   HDC analogy, with no parametric distribution and no softmax? The
   iteration-11 v4 pipeline already does this for single-action
   outputs. The next step is multi-sentence coherent text about a
   closed domain — not ChatGPT-scale, but a real demonstration that
   "generation by construction" is possible for structured knowledge.
   If this works, scaling up is the subsequent question. If it
   doesn't, we learn where graph-based generation hits its own wall.

2. **CTW as the compression-family door-closer.** Cheap (~1 day),
   independent second data point for the compression family.
   Expected within 0.1 bpc of PPM-D. Useful confirmation, not a swing.

3. **A well-funded transformer baseline** so the "1.60× gap" becomes
   measurement-quality instead of estimate-quality. Requires GPU or
   overnight CPU.

4. **Scale tests of the closed-domain reasoner** on a domain with
   hundreds of substances and thousands of scenarios. Finds where
   the property-graph architecture actually breaks before we try to
   extend it to open-domain.

5. **The Part 4 learning-rule problem (Hebbian/HDC at language
   scale).** Still the "strongest single candidate" per the math doc,
   but shares A1 with HDC language modeling and is therefore subject
   to the bundle-saturation wall the inventory documents. Worth
   trying only if direction 1 saturates.

**Default if the user has not specified: direction 1.** It is the
one direction that (a) builds on what already works in the stack,
(b) drops the assumptions the inventory flagged as breakable, and
(c) produces a result — positive or negative — that directly
informs the trillion-dollar question.

## Branch and commit state at handoff

Branch: `claude/review-continuation-prompt-9afno`
HEAD: `807d5a1` (Iteration 15: CLM vs nanoGPT on text8, mixed-but-real result)
Untracked / uncommitted at handoff: **iteration 16 files have not
been written yet**. The subagent returned its findings in the prior
session's chat history. Your first action should be to finalize
iteration 16 to disk, then commit and push, then propose iteration 17.

## Things to avoid

- Re-running the literature review if the prior findings are
  available. The review was ~30 tool calls and produced durable
  output. Copy it, do not redo it.
- Starting iteration 17 before iteration 16 is committed and pushed.
- Treating the shared-assumptions finding as a proof that our
  architecture will work at open-domain scale. It is a hypothesis
  about why prior attempts failed, not a guarantee that dropping
  those assumptions succeeds.
- Introducing matmul, dense linear algebra, or gradient descent.
- Using TodoWrite for short tasks; reserve it for multi-step
  iteration plans.

You are now caught up. Finalize iteration 16 to disk, commit and
push, then propose iteration 17 based on the shared-assumptions
analysis. Default to direction 1 (generation by construction on the
existing property-graph substrate) unless the user redirects.
