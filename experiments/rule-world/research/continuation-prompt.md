# Continuation prompt — paste this as the first user message in a fresh session

You are continuing a long-running research investigation into whether
generative intelligence can be built without matrix multiplication at
scale. This is **research, not a product**. We are not optimizing for
demos. We are not pitching anything. We are asking an open scientific
question and following it where it leads, including into negative
results.

## What you are walking into

The repository is `mikelmyers/primordia-experiments`, branch
`claude/document-rule-world-status-iltb9`, HEAD `ba0d945` as of
2026-04-06 18:17 UTC. Fourteen iterations are complete. The
architecture is mature in its closed-domain reasoning layer and
incomplete in its open-domain generation layer. The trillion-dollar
question — *can equivalent or superior generative intelligence be
produced without matmul at scale?* — is still open, and answering it
is the actual goal.

## The four documents you must read first, in order

1. **`experiments/rule-world/research/post-matmul-foundations.md`** —
   the math. Parts 1–5 plus updates. Read all of it. Specifically
   internalize Part 4 ("the unsolved math problem hiding under the
   engineering question") and Part 2 (the survey of mathematical
   landscapes) — these frame what would actually count as a
   breakthrough.

2. **`experiments/rule-world/research/progress-log.md`** — the
   chronological lab notebook of all 14 iterations. Read it cover to
   cover. Note especially the iteration-by-iteration "what this
   proves / what this does not prove" pairs. The honesty discipline
   in those pairs is the most important single thing about how this
   work is done. Match it.

3. **`experiments/rule-world/research/WHERE-WE-STAND-2026-04-06-1817.md`** —
   the research-state snapshot you should treat as the canonical
   summary of the current position. Headline numbers are there.
   Open problems are there. What is and is not claimed is there.

4. **`experiments/rule-world/research/STATUS-2026-04-06.md`** — the
   earlier post-iteration-8 snapshot, kept for historical context.
   Compare against WHERE-WE-STAND to see what shifted between
   iteration 8 and iteration 14.

## The claim space (what is and is not currently claimable)

Claimable after iteration 14:
- Closed-domain reasoning without matmul, demonstrated at N=3
  unrelated domains (rule-world, traffic-world, kitchen-world).
- Grounded analogy substrate-independent across HDC and compression.
- Property-table induction at **89% top-1** across N=3 with no
  hand-authored property labels (8/9 adversarial queries).
- Crystallization → induction loop closure verified (oil → wood
  flipped from rank 5 to rank 1 by filtering syntactic crystallizations).
- Verbose NL explanation across N=3 (28/28 scenarios) with honest
  bug reporting.
- Humanization dictionary induction at **33%** combined (partial win,
  rule-world 38.6%, traffic-world 21.6%, kitchen-world 38.1%).

NOT claimable:
- Open-domain free text generation. **Untouched.**
- Statistical pattern extraction from unstructured text without
  gradient descent on dense matrices. **Untouched.**
- Acquiring rules themselves from text. **Untouched.**
- Generality at non-toy vocabulary scale. **Untested.**
- A general parser. Largest remaining hand-authored surface.
- **Any answer to the trillion-dollar question.** The closed-domain
  result is a smaller, related win — not the answer.

## How to behave

**Be honest about uncertainty.** The user values honesty over
advocacy. If a result is mixed, say it is mixed. If you don't know,
say you don't know. If your previous claim was wrong, say so. Do not
pad results. Do not hide failures. The grease-fire scenario in
iteration 13 — where the explainer surfaces its own bad decision —
is the model for how every result should be reported.

**Distinguish "research progress" from "product progress".** The user
is not asking you to ship anything. They are asking you to find out
whether the research question has an answer. Iteration 13 produced a
system that *could* be a product, but the user explicitly redirected:
"This isn't a product." Treat that as durable instruction.

**The trillion-dollar question is the only goal.** Every iteration
should be evaluated by the question "does this move us closer to
answering whether matmul-free generative intelligence is possible at
scale?" not by "does this make the existing closed-domain stack
better?" Polishing the closed-domain stack is fine when it serves the
research, not when it serves an imagined product.

**Build in rule-world first, then transfer.** Every layer that has
worked has been built in rule-world, then validated in traffic-world,
then validated in kitchen-world. Twice this discipline has surfaced
hidden assumptions (the iteration-8 multi-token bug, the iteration-12
antecedent-scoring bug). Skip the discipline at your peril.

**Match the iteration template.** Each iteration entry in
`progress-log.md` follows the same shape: Hypothesis → What was built
→ Result (with concrete numbers) → Diagnosed failures → What this
proves → **What this does not prove** → Status of the trillion-dollar
reframe. Use this template for every new iteration. The "what this
does not prove" section is non-optional and is where the user looks
first to test your honesty.

**Never modify rule-world architecture files in a transfer test.**
The architectural contract from iteration 12 is: rule-world is the
source of truth, transfer domains import its machinery unmodified.
Any change to `engine.py`, `abstractor.py`, `hdc.py`, `compression.py`,
`retriever.py`, `rule_store.py` is a research event in itself and
should be its own iteration entry with a clear justification. The
iteration-12 multi-token v4 projection bug and antecedent-scoring bug
are open precisely because fixing them would have violated this
contract mid-iteration.

## What the user wants you to do next

The user has explicitly framed the next phase as: *"We are going to
keep researching this until we actually do get to a real breakthrough."*
The research directions, ranked by closeness to the trillion-dollar
question (from `WHERE-WE-STAND-2026-04-06-1817.md`):

1. **Open-domain text generation without matmul.** The hardest, the
   most valuable, and the unstarted one. Compression-based language
   modeling (PPM, CTW, arithmetic coding over byte streams) is the
   most promising matmul-free starting point per Part 2 of the math
   doc. Nobody has tried this with modern compute and modern data.
   This is iteration 15's most ambitious candidate.

2. **The unsolved math problem from Part 4.** A learning rule for
   distributed representations that is (a) gradient-free, (b) scales
   linearly in data, (c) provably converges to representations
   capturing conditional structure, (d) composes across layers.
   Hebbian + HDC is the obvious starting point and has never been
   tested at language scale. A single positive result on this
   problem would be a breakthrough on its own.

3. **Acquiring rules themselves from text.** The CYC failure mode,
   worth retrying with the modern stack we now have. If a system
   could read a paragraph of domain description and produce
   formal Rule objects, the entire architecture would suddenly
   scale to domains nobody hand-authored.

4. **A general parser.** Largest remaining hand-authored surface.
   Probably needs *some* statistical component but perhaps not a
   full LLM. Classical NLP (tokenizer + dependency parser + entity
   linker) is matmul-light.

5. **Scale tests.** Run the existing architecture on a domain with
   hundreds of substances and thousands of scenarios. Find which
   assumption breaks first.

6. **The two iteration-12 bugs.** Multi-token v4 projection and
   antecedent-removing visceral scoring. Tractable, narrow, but
   neither moves the trillion-dollar question — they are debt.

7. **N=4 and N=5 transfer domains.** N=3 caught the bugs N=2 missed.
   The diminishing-returns curve is unknown.

**Default if the user has not specified: direction 1 or direction 2.**
Both are genuine swings at the open question. Direction 1 is more
empirically falsifiable (you can run a compression LM on a corpus
and measure perplexity vs a small transformer). Direction 2 is more
mathematically interesting.

If you have the option, **do not start with directions 3–7.** Those
are research debt or scaling debt, not research progress. They are
valuable when nothing else is moving, but they should not crowd out
the actual swings at the open question.

## How to start a new iteration

1. Open `progress-log.md` and read the last entry to confirm you
   understand the current state.
2. Pick a direction (1 or 2 by default unless the user has redirected).
3. State the hypothesis you are testing in one sentence.
4. State the success metric in one sentence — what number would you
   need to see to call it a positive result, and what number would
   you call a clean negative.
5. Build the smallest experiment that produces that number.
6. Run it. Capture the actual number, including if it is negative.
7. Write the iteration entry following the template in
   `progress-log.md`. The "what this does not prove" section is
   mandatory.
8. Commit and push to the same branch.
9. Update the WHERE-WE-STAND document timestamp + headline numbers
   if the iteration changed the headline.

## Things to avoid

- Modifying `engine.py`, `abstractor.py`, `hdc.py`, `compression.py`,
  `retriever.py`, or `rule_store.py` without flagging it as a
  rule-world architecture change in its own iteration entry.
- Deleting `results.md` (the original LLM-baseline output, kept for
  comparison — never overwrite).
- Introducing matmul, numpy linear algebra beyond `np.sign` and dot
  products of int8 vectors, or any learned parameter that requires
  gradient descent. **The whole point is matmul-free.**
- Starting an iteration without an explicit success/failure metric.
- Reporting only positive numbers.
- Skipping the "what this does not prove" section.
- Treating closed-domain wins as if they answered the open question.
- Pitching the architecture as a product.
- Hiding bugs the architecture surfaces about itself.
- Padding results to look better than they are. The iteration 14
  result (33% partial win) is a model for how to report a mixed
  outcome honestly.
- Using TodoWrite for short tasks; reserve it for genuinely
  multi-step iteration plans.

## A note on the user's research disposition

The user is explicitly comfortable with failure. They would rather
see "we tried compression-based language modeling and it produced
worse perplexity than a small transformer at every corpus size we
tried" than see "we got 47% on this synthetic benchmark we just
made up." Negative results are valuable research output and should
be reported with the same care as positive ones. If a swing fails
honestly, that is iteration progress. If a swing succeeds dishonestly,
that is iteration regress.

The user's stated goal — verbatim — is: *"We are going to keep
researching this until we actually do get to a real breakthrough."*
There is no time pressure. There is no demo. There is just the
question, and the discipline of trying to answer it.

## How to run the existing pipelines (sanity check)

Before starting iteration 15, run all three domains plus the
property inducer to confirm nothing has rotted:

```bash
cd /home/user/primordia-experiments

# Three domain pipelines
python experiments/rule-world/runner_symbolic.py
python experiments/traffic-world/traffic_runner.py
python experiments/kitchen-world/kitchen_runner.py

# Property inducer comparison across N=3
python experiments/rule-world/research/iteration12_runner.py

# Verbose NL explanations across N=3
python experiments/rule-world/research/iteration13_runner.py

# Humanization dictionary induction across N=3
python experiments/rule-world/research/iteration14_runner.py
```

Expected outputs:
- All scenarios resolve without exceptions.
- Iteration 12 prints `Combined N=3 result: 8/9 = 89%` for property
  induction.
- Iteration 13 prints `scenarios explained: rule-world=11
  traffic-world=8 kitchen-world=9` and writes the explanations
  markdown.
- Iteration 14 prints combined `33.3%` coverage.

If any of these break, that is iteration 15's first job — find what
rotted, fix it, document it as a regression iteration.

## Branch and commit state at handoff

Branch: `claude/document-rule-world-status-iltb9`
HEAD:   `ba0d945` (Iteration 14: humanization dictionary induction
        partial win, 33%)
Tip:    14 iterations in, all on this branch, all pushed to origin.

Last 5 iteration commits in chronological order:
- Iteration 10: crystallization → induction loop closure (mixed)
- Iteration 11: v4-only loop closure (5/6 top-1, the fix landed)
- Iteration 12: third domain transfer test (kitchen-world) at N=3
- Iteration 13: verbose NL explanations across N=3, zero matmul
- Iteration 14: humanization dictionary induction (partial, 33%)

You are now caught up. Pick a direction (1 or 2 by default) and
start iteration 15.
