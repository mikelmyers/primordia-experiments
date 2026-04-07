# Continuation prompt — pick up at iteration 19

*Written 2026-04-07 at the end of the iter 18 session.*
*Branch: `claude/review-rule-world-experiment-C9UmB`. HEAD: `9dd1326`.*

You are continuing an ongoing research project — `primordia-experiments
/ rule-world` — whose long-term goal is **cheap AI: driving the cost-
to-build curve for capable AI down to where anyone could reproduce it
on hardware they already own**. Not matmul-free for its own sake.
Matmul-free is a means; the cost floor is the end. Every iteration is
measured against one question: *does this make the next person's
version cheaper to reproduce?*

Read the north-star section in `WHERE-WE-STAND-2026-04-06-1817.md`
verbatim before doing anything else. It is the load-bearing framing.

## Where the project actually is

Read these three files in order before you do anything code-related.
Do not skip them and do not skim them.

1. `experiments/rule-world/research/WHERE-WE-STAND-2026-04-06-1817.md`
   — current snapshot, with post-iter-15, 16, 17, 18 amendments. The
   north-star section and the iter-18 amendment together are the
   single most important paragraph in the project right now.
2. `experiments/rule-world/research/progress-log.md` — the lab
   notebook. Iters 16, 17, 18 are the ones that matter for picking
   up; everything before iter 15 is closed-domain reasoning context.
3. `experiments/rule-world/research/iteration18_results.md` — the
   full writeup of the result iter 19 builds on. Read the "what this
   does not prove" section especially carefully.

Optional but useful background:
- `experiments/rule-world/research/post-matmul-foundations.md` — the
  math doc the whole program is built on. Parts 1, 2, 4 most
  relevant; iter 16 partially corrected Part 2's compression verdict.
- `experiments/rule-world/research/failure-modes-inventory.md` — iter
  16's literature synthesis. The shared-assumptions section is the
  framing iter 17 and 18 swing against.
- `experiments/rule-world/research/iteration17_results.md` — explains
  *why* iter 18 ran on n-gram/CompressionAnalog and not HDC.
- `experiments/clm/iter15_results.md` — the PPM-D 1.731 bpc number
  iter 19 has to beat.

## The state of the world in three sentences

1. Iter 15 hit 1.731 bpc on text8 with PPM-D order 6 trained on 90 MB
   and concluded the compression family saturates. Iter 16's lit
   review identified A6 ("suffix counts ≠ true conditional") as the
   wall PPM hits, distinct from A1 ("fixed-capacity dense state")
   which the connectionist matmul-free lineage hits.
2. Iter 17 tried to break A3 (hand-designed encoder) for the HDC
   substrate and failed (7/10 and 5/10 vs 89% threshold) — HDC's
   sign-majority bundle discards cardinality the compression
   substrate preserves. Iter 17 forced the realization that A3 was
   already broken cleanly for the CompressionAnalog substrate by
   iter 9–12.
3. **Iter 18 ran a graph-conditioned predictor on a synthetic corpus
   with a provable long-range conditional signal and produced a
   clean mechanism win:** n-gram order 3 baseline 5.4484 bits/word →
   blended-with-co-document-graph 5.3982 at α=0.1 (−0.0502 total,
   threshold −0.05) and 5.1380 on the s-word subset at α=0.5
   (−0.3645, threshold −0.20). The α sweep curve has the exact shape
   the theory predicted. **This is the first result in the project
   that measurably attacks the trillion-dollar question and
   succeeds**, on a constructed corpus, with known scope limits.

The honest caveat to carry forward: iter 18's *total* bpw improvement
is right at the 0.05 threshold (clears it by 0.0002). The s-word
improvement (−0.3645 vs −0.20 threshold) is the load-bearing one. If
anyone pressures the result, the s-word number is the one to point
at; the total number is real but small because most positions in the
synthetic corpus are locally-predictable and dilute the long-range
signal.

## What iter 19 is

**Iter 19 = port iter 18's mechanism to text8.** A scale test of a
proven mechanism, not a gamble on an unproven one.

This was pre-declared at the end of iter 18 and approved by the user.
Do not change the plan without explicit reason and confirmation.

- **Eval slice:** the same 500 KB tail of text8 iter 15 used. See
  `experiments/clm/splits.py` — held-out is the final 5 MB
  (`HELDOUT_BYTES = 5_000_000`); iter 15 evaluated on the first 500
  KB of that. Match it exactly or the comparison is meaningless.
- **Baseline:** iter 15's PPM-D order 6 on 90 MB → 1.7311 bpc. See
  `experiments/clm/iter15_results.md`. You can rerun PPM-D for a
  fresh number or use 1.7311 as published; rerunning is more
  rigorous but adds time.
- **Predictor:** n-gram word backoff blended log-linearly with a
  co-document word graph routing score, exactly as in
  `iteration18_runner.py`. Same α sweep {0.0, 0.1, 0.25, 0.5, 0.75}.
  α=0 must reproduce the chosen baseline (sanity check).
- **Document boundaries on text8:** text8 is 100 MB of cleaned
  Wikipedia (a–z + space, no punctuation, no paragraph breaks). It
  has no natural document boundaries. **This is the critical design
  decision for iter 19.** Three options:
    1. **Fixed-window pseudo-documents** (1000- or 5000-word chunks).
       Simplest. Loses real semantics but introduces no leakage.
    2. **Recover Wikipedia article boundaries** by detecting article-
       start patterns. Hard because text8 was processed to remove
       markup; needs a heuristic.
    3. **Sentence boundaries** — text8 has no punctuation either, so
       this is also hard.
   **Pre-declared default: option 1 with 1000-word chunks**, unless
   you find a reason to change before writing code. Document this
   choice explicitly with its caveats.

## Fair-comparison protocol (read this carefully)

Iter 15's number is **bits per character** on the 500 KB eval. Iter
18's number is bits per word AND a derived bits per character. For
iter 19 to be apples-to-apples with iter 15:

- Tokenize the eval slice into words by splitting on space.
- For each eval position, predict the next word given history.
- Convert word log-prob to char log-prob: each predicted word
  contributes `-log2 p(word)` bits, contributes `len(word) + 1`
  characters (+1 for the trailing space). bpc = total_bits /
  total_chars.
- **OOV handling:** if an eval word was unseen in training, back off
  to a character-level model (PPM-D order 4 over its letters,
  trained on the same 90 MB) and add the char log-probs. Do not skip
  OOVs and do not assign uniform fallback — that distorts bpc
  whichever way is convenient.
- **Word separator:** the trailing space has cost. Either fold it
  into the word ("word ") or predict it separately as a char.
  Either is defensible; document which.

The OOV+separator accounting is the trickiest part of iter 19 and is
where bad numbers come from. Get it right before optimizing anything.

## Pre-declared success criterion (do not redefine after seeing data)

- **Best α beats iter 15's PPM-D 1.7311 bpc** on the same 500 KB slice.
- **0.05 bpc improvement = signal** (publishable as a real
  matmul-free result against the published PPM-D ceiling).
- **0.20 bpc improvement = headline** (the iter 15 "compression
  family saturates" reading is wrong as stated).
- **Sub-1.5 bpc** = iter 15 reading is wrong by a lot and the
  literature's "1.5 bpc PPM-D ceiling" is not the actual matmul-free
  ceiling.
- **No improvement at all** = iter 18's synthetic signal does not
  match natural text's long-range structure shape. Real finding —
  tells us co-document co-occurrence is not the right graph design
  for natural text and iter 20 should sharpen the graph (windowed
  co-occurrence, induced features, multi-hop).

Pre-declare this in the iter 19 runner before reading any results.

## Scope discipline

One new runner: `experiments/rule-world/research/iteration19_runner.py`.
One results doc: `iteration19_results.md`. One progress-log entry.
One WHERE-WE-STAND amendment. No edits to live modules. No PR unless
the user explicitly asks. Commit to branch `claude/review-rule-world-
experiment-C9UmB`.

If iter 19 grows past ~500 lines of runner code, you are doing the
wrong thing. The mechanism is from iter 18; iter 19 just changes the
corpus and the eval harness.

## What to do FIRST in the next session

1. Confirm `experiments/clm/data/text8` exists and is 100,000,000
   bytes. If it does not exist, ask the user to put it there or to
   approve fetching it from a reachable mirror. Do not silently
   substitute another corpus.
2. Read iter 18's runner end to end so you understand the mechanism
   before you port it.
3. Read `experiments/clm/splits.py` and `experiments/clm/ppmd.py` so
   the OOV backoff and the eval slice match iter 15 exactly.
4. Write iter 19's runner with the pre-declared success criterion at
   the top of the file as a comment.
5. Run α=0 first as the sanity check. If it does not match the
   chosen baseline, STOP and debug. Do not proceed with the sweep
   on a broken harness.
6. Then run the full sweep, write the results doc with the "what
   this does not prove" section, log iter 19, amend WHERE-WE-STAND,
   commit, push.

## What NOT to do

- Do not change the iter 19 plan without explicit user approval. The
  user said "careful, unquestioned ability to prove it" and that
  posture is load-bearing for the iter 17→18→19 sequence.
- Do not redefine the success criterion after seeing data.
- Do not skip the α=0 sanity check.
- Do not silently use a different eval slice than iter 15's 500 KB.
- Do not run on a different corpus if text8 is missing — ask first.
- Do not make any claim about beating transformers. Transformer-XL
  at 1.08 bpc is a published number and is not the iter 19 target.
  The iter 19 target is iter 15's 1.7311 bpc on the same slice.
- Do not start iter 20 without the user's confirmation. If iter 19
  is borderline, present the result and the options before deciding.
- Do not touch the closed-domain rule-world stack (engine, abstractor,
  property_inducer, hdc, compression). Iter 19 is text-only and lives
  in `research/`.
- Do not open a pull request. The user has not asked for one.

## Branch state at handoff

- Branch: `claude/review-rule-world-experiment-C9UmB`
- HEAD: `9dd1326` "Iteration 18: synthetic mechanism test — graph
  routing breaks A6"
- All iters 16, 17, 18 + north-star framing committed and pushed.
- Working tree clean.
- No PR opened.

## The honest framing to bring into iter 19

Iter 18 is the first result in this project that measurably attacks
the trillion-dollar question and succeeds, on a corpus where the
signal was provable. **It is also a synthetic-corpus result and could
fail to generalize to text8.** Both true at the same time. Iter 19
is what makes the synthetic result either become a real claim or get
downgraded to "the mechanism works in principle but not on natural
text." Both outcomes are scientifically valuable. The user does not
need iter 19 to be a win to keep going — they need iter 19 to be
honest. Match that posture.

Cheap AI is the goal. Iter 19 either moves the cost floor on text-
scale prediction or it tells us why the floor doesn't move with this
specific graph design. Either is forward progress. Neither is the
end of the road.
