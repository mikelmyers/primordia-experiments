# Continuation prompt — Track B post-matmul reasoning experiment

Use this prompt to start a fresh session and pick up the experiment without
prior chat history. Paste it as the first user message after starting a new
Claude Code session in the `primordia-experiments` repo.

---

## The prompt

You are continuing Track B of a post-matmul reasoning research experiment.
Eight iterations have already been completed and pushed to branch
`claude/rule-world-experiment-LpYuc`. You have **full repo context** but no
chat history with the user.

**Before doing anything else, read these three files in order:**

1. `experiments/rule-world/research/STATUS-2026-04-06.md`
   The single comprehensive snapshot of where the experiment stands. Tells
   you what has been built, what works, what doesn't, and the current
   open questions.

2. `experiments/rule-world/research/post-matmul-foundations.md`
   The mathematical research that motivated everything. Parts 1-5 are the
   landscape survey. The "Update — v4 results and the loop closing" section
   is the most current.

3. `experiments/rule-world/research/progress-log.md`
   The chronological lab notebook of all 8 iterations with verdicts on
   what each one proved and what failed.

After reading those three files, run both pipelines to confirm they still
work:

```bash
cd /home/user/primordia-experiments
python experiments/rule-world/runner_symbolic.py
python experiments/traffic-world/traffic_runner.py
```

You should see no errors. Both produce results files (`results_symbolic.md`
and `results_traffic.md`) with all scenarios passing without engine-reported
gaps.

---

## The current state, in one paragraph

After 8 iterations we have a four-layer symbolic reasoning architecture
(parser → retriever → engine → abstractor) with grounded analogy via HDC
and a parallel compression baseline, plus a STRIPS depth-3 planner, plus
end-to-end loop closure (gap → analog → rule projection → action synthesis
→ behavior change), plus a successful transfer test to a second domain
(traffic-world). **Zero matrix multiplication anywhere.** The headline
finding from iterations 7 and 8 is that grounded analogy is
substrate-independent: HDC bipolar similarity and integer-counter PPM
frequency converge on the same analog choices in both domains. This
localizes the bottleneck to **the property table itself** (which is
hand-authored) and **the parser layer** (which does not transfer).

---

## Three options for the next iteration, ranked by my recommendation

### Option A — Property table acquisition (the hardest open question)

Build a mechanism that mines property candidates from existing rule
predicate co-occurrence. Specifically: for every substance that appears
in any rule predicate, gather the *other* tokens that co-occur with it
in those predicates and propose them as candidate properties. Use the
compression baseline's frequency tables as the property hypothesis
generator.

This attacks the deepest bottleneck. It is the same problem CYC failed
to solve in 40 years, so success is not guaranteed and even partial
progress is meaningful.

Expected scope: ~150 lines in a new `property_discovery.py`, plus
integration into the abstractor and a test scenario where the system
infers properties for a substance with no hand-authored entry.

Success criterion: the system proposes at least one correct property
for a held-out substance from the rule store alone, without that
substance having a `SUBSTANCE_PROPERTIES` entry.

### Option B — Third transfer test (more empirical confidence)

Build a third domain (kitchen safety, first aid, or wilderness survival)
under `experiments/<name>-world/` following the traffic-world template.
Use it to validate that the architecture really does transfer cleanly
and that no further hidden assumptions exist. Document any new architectural
parameters that need to be added.

This is the least ambitious but the most empirically rigorous next step.
If a third domain works with the same two backward-compatible parameter
additions from iteration 8, the architecture claim is much stronger. If
it surfaces a new hidden assumption, that assumption is the next thing to
fix.

Expected scope: ~400 lines in a new domain directory (rules + parser +
scenarios + runner), zero or near-zero changes to rule-world.

Success criterion: all scenarios pass with no architectural changes
beyond what iteration 8 added.

### Option C — Compression-based language model for output (the generation question)

The math doc Part 5 named compression-based prediction (PPM/CTW) over
rule traces as the most underexplored matmul-free path to actual
generation. We have a tiny PPM-style baseline (`compression.py`) but
it's used only for analog selection, not for generation.

Build a small CTW-style sequential predictor over the engine's output
tokens (action names + cited rule IDs + rule statements) and see if it
can produce coherent post-hoc explanations. This is the first attempt
to test whether matmul-free *generation* is possible at all, even at
trivial scale.

Expected scope: ~200 lines in a new `generation.py`, plus a scenario
or two where the engine's structured output gets fed through the
generator and the result is compared to the LLM-baseline `results.md`.

Success criterion: the generator produces at least one English-like
explanation of an engine choice that is not just a templated string.
Even partial coherence would be a meaningful result.

---

## My recommendation

**Option B first, then Option A.**

Reasoning:
- Option B is the safest and most empirically rigorous. It either
  strengthens the core claim or finds the next hidden bug. Either
  outcome is valuable.
- Option A is the most important question but is also the hardest. It
  benefits from having more empirical evidence that the architecture
  is solid before attacking the deepest open problem. If A works on
  rule-world but the architecture turns out to have hidden domain
  assumptions in iteration 9, you've spent effort on the wrong layer.
- Option C is interesting but speculative. It is the most aligned with
  the trillion-dollar question but also the most likely to produce a
  null result. Save it for after A.

Suggested order: B (a third transfer test), then A (property
acquisition), then C (compression generation).

If the user has a different priority, follow theirs. They have context
that this prompt does not.

---

## Things to avoid

1. **Do not modify the rule-world architecture files
   (`engine.py`, `rule_store.py`, `retriever.py`, `abstractor.py`,
   `hdc.py`, `compression.py`)** without a strong reason. Eight
   iterations have stabilized them. New domains should use the
   existing parameters and add their own files. If you absolutely
   must modify, keep changes backward-compatible (defaulted parameters).

2. **Do not delete `experiments/rule-world/results.md`.** That file is
   the original LLM baseline output (from iteration 0) and has been
   preserved as a reference. Modifications by linters are fine; do
   not revert them.

3. **Do not commit the `__pycache__` directories.** They are local
   build artifacts.

4. **Do not introduce matrix multiplication into the inference path.**
   The whole point of Track B is to test whether reasoning can be
   decoupled from matmul. Matmul-shaped math (tensor contraction over
   small bond dimensions) is acceptable in principle for tensor
   network experiments but should be flagged explicitly and not
   slipped in.

5. **Do not skip the progress log update.** Every iteration ends with
   an entry in `experiments/rule-world/research/progress-log.md`.
   Date, what was built, result, what it proved, what it didn't,
   failure modes identified. The log is the experiment's memory.

6. **Do not assume the user wants a PR.** No PR has been opened. The
   user has not asked for one. Push to the branch as you go.

7. **Do not rebuild what already works.** The four-layer pipeline,
   the HDC analog mechanisms, the planner, the compression baseline,
   the suppression logic, and the projection filter are all in place
   and tested. Iteration 9+ should *add* to them, not replace them.

---

## Format expectations

When you finish an iteration:
- Update `experiments/rule-world/research/progress-log.md` with a new
  iteration entry following the existing format
- Commit with a descriptive message that lists what was built, what
  the result was, and what failure modes were identified
- Push to `claude/rule-world-experiment-LpYuc`
- Report the result to the user with a clear "what worked / what didn't /
  honest verdict" section
- If you uncover a new finding worth recording in the foundations doc,
  add it to `post-matmul-foundations.md`
- If your context window is approaching the halfway mark, tell the
  user explicitly so they can decide whether to continue or hand off

When you cannot finish an iteration:
- Commit the partial work clearly labeled
- Update the progress log with the current state
- Document what you tried, what failed, and what you would try next

---

## The deeper context, briefly

The user is investigating whether the trillion-dollar compute monopoly
on AI is mathematically necessary or just a contingent engineering
outcome. They want honest, falsifiable experiments, not advocacy for any
particular architecture. They explicitly value being told when something
doesn't work, when an experiment shows the wrong result, and when the
hypothesis is partially or fully wrong.

They have already received an honest assessment that the architecture
will replace LLMs for closed-domain reasoning where the rule store can
be authored or grown by analogy, but will NOT replace LLMs for
open-domain free generation in its current form. They are not asking
for confirmation. They are asking for new experimental data.

When in doubt: do the most informative experiment, report the result
honestly even if it doesn't help the hypothesis, and document what you
learned.

---

## End of continuation prompt

Read the three docs, run both pipelines to confirm the baseline, and
then propose your next move (or execute the user's chosen move). Good
luck.
