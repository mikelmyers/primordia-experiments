# Iteration 17 — A3 attack summary (structural + behavioral)

*Date: 2026-04-07*
*Branch: `claude/review-rule-world-experiment-C9UmB`*

Iteration 16's failure-modes inventory identified **A3** — "encoder is
fixed / hand-designed, not learned from data" — as the assumption
rule-world shares with HTM and Spaun, the two prior matmul-free
systems most architecturally similar to ours that both failed to
scale to language. Iter 17 tests whether A3 can be cleanly broken for
the HDC substrate on the existing N=3 adversarial set, using two
learned-encoder variants.

Iter 9–12 had already shown that induced features + `CompressionAnalog`
reach 89% (10/10 on the iter 12 query set) — so A3 was arguably
already broken for the compression substrate. The unmeasured cell was
**induced features + HDC**, and the iter 17 plan defined two clean
variants:

- **17a (structural).** Induce features from all rules, all actions,
  and all parsed scenario observations (the iter 9 corpus), feed the
  result into the live HDC role-weighted analog path.
- **17b (behavioral).** Induce features from only rules whose
  antecedents are actually satisfied during the scenario suite, only
  actions whose preconditions actually hold, and the union of all
  derived facts. Same HDC path.

Both variants reuse the existing `property_inducer`, `hdc`, and
`compression` modules end to end. No edits to any live module. HDC
codebook seed=42 (same as live v4).

## Headline numbers

| variant                     | induced + HDC | induced + compress |
|---|---|---|
| **17a structural**          | **7/10**      | 10/10              |
| **17b behavioral**          | **5/10**      | 8/10               |

*(Induced+compress column is the iter 12 baseline reproduced with
identical inputs, re-run here so HDC and compression are apples-to-
apples on each corpus.)*

### Per-domain breakdown

| domain            | 17a HDC | 17a comp | 17b HDC | 17b comp |
|---|---|---|---|---|
| rule-world        | 3/4     | 4/4      | 3/4     | 3/4      |
| traffic-world     | 1/3     | 3/3      | 0/3     | 2/3      |
| kitchen-world     | 3/3     | 3/3      | 2/3     | 3/3      |
| **combined N=3**  | **7/10**| **10/10**| **5/10**| **8/10** |

## What the numbers say

**Finding 1: HDC is strictly weaker than CompressionAnalog on the
same induced feature table.** Identical inputs, identical query set —
HDC hits 7/10 where CompressionAnalog hits 10/10. The failure modes
are exactly the ones the iter 16 inventory warned about:

- Iter 17a rule-world: `oil` → `food` at sim 0.6296, `food` at sim
  0.6296, `medicine` at 0.6296. Three-way tie on sign-majority
  bundles. The authored target `wood` lands at rank 5.
- Iter 17a traffic-world: `horse_carriage` → `robotaxi` at 0.6904,
  `robotaxi` → `horse_carriage` at 0.6904 (same reason).
- Iter 17b rule-world: `oil` → `food` at sim **1.0**, tied with
  `medicine` at 1.0, because the firing-trace-restricted bundles for
  these three substances become structurally identical under sign
  majority.

The root cause is that HDC's `bundle` operator collapses frequency
into a sign vector. CompressionAnalog's similarity is frequency-
weighted and preserves exactly the cardinality HDC discards. On small
feature vocabularies (40–85 features, 5–10 substances) the sign
collapse produces ties that count-based similarity disambiguates.

This is a substrate-level observation, not a tuning problem. A
richer HDC encoder that preserved cardinality — integer bundles
without sign, or role-bound multi-token features, or a proper
count-hypervector (CDHV) — would plausibly close the gap. But that
is a new substrate, not a break of A3.

**Finding 2: Behavioral restriction makes things worse at this
corpus size, for both substrates.** Iter 17b degrades both columns
(HDC 7→5, compress 10→8). The cause is straightforward: restricting
the induction corpus to fired rules strips vocabulary. traffic-world
`truck` appears in zero fired rules because no scenario fires one,
so `fire_engine → truck` becomes unreachable — not ambiguous, but
structurally absent from the feature space. The "learn from
behavior not syntax" intuition is the right one for large corpora;
on a 14-rule domain with 8 scenarios it simply removes the only
signal the inducer had.

This is a corpus-size effect, not a refutation of behavioral
learning as a strategy. It means the behavioral variant is not
testable at N=3 and has to wait for scale.

## What iter 17 proved

1. **A3 is broken for the compression substrate** on this adversarial
   set (iter 12's 89% result is reproduced and extended to 100% with
   the iter 14 v4 crystallizations folded in). This is the iter 17
   confirmation that the iter 9–12 result holds.
2. **A3 is not cleanly broken for the HDC substrate** at this corpus
   size. The hand-designed table's advantage is real and repeatable.
   HDC's sign-majority bundle discards cardinality information the
   induced features depend on.
3. **Behavioral learning from firing traces is untestable at N=3.**
   The corpora are too small for firing restriction to add signal;
   it only strips it.

## What iter 17 does *not* prove

- It does not prove HDC cannot learn from induced features. It proves
  that on this corpus, with this bundling operator, at this vocabulary
  size, HDC underperforms frequency-based compression. A richer HDC
  substrate (count-preserving bundles, role-bound features) is not
  ruled out — it is untested.
- It does not prove behavioral learning is a dead end. It proves that
  at toy scale, firing-trace restriction removes signal. Whether
  behavioral learning helps at text-scale corpora is the actual
  question and it is still open.
- It does not prove rule-world will succeed on open-domain text. Iter
  17 is still a closed-domain experiment. The trillion-dollar
  question is untouched.
- It does not prove iter 18 (A6 attack on text8) will succeed. Iter
  17 only clarifies *which substrate* the A6 attack should run on.

## The decision this result forces

Going into iter 17 the plan was: break A3 for HDC first, then attack
A6 (graph-conditioned predictor on text8) using the learned HDC
encoder, so the text8 result would be interpretable as "the graph
substrate is doing the work" rather than "we hand-tuned the encoder
until it worked."

Iter 17 says A3 is not cleanly breakable for HDC at this scale. But
it also says A3 *was already cleanly broken* for CompressionAnalog
by iter 9–12, and that result reproduces and extends here. So the
interpretability concern that motivated the "break A3 first" plan
is satisfied — on the compression substrate.

**Updated iter 18 scope: graph-conditioned CompressionAnalog on
text8, not graph-conditioned HDC.** This swaps which substrate
carries the A6 attack:

- The predictor is induced-feature CompressionAnalog with the same
  machinery as iter 12 / iter 17, but the "context" it conditions on
  is a growing property graph over the text stream, not the suffix
  string PPM-D used in iter 15.
- The encoder is the induced feature table — already a broken-A3
  result, so any text8 win is interpretable as graph routing, not
  hand-tuning.
- The bpc comparison is head-to-head against iter 15's PPM-D 1.731
  on the same 500 KB text8 eval slice.

HDC remains a parallel research thread, but its open problem is now
"count-preserving bundle operator" rather than "learned encoder" —
a substrate change, not an encoder change. That is a different
iteration shape and is deferred.

## Files touched

- `experiments/rule-world/research/iteration17a_runner.py` (new)
- `experiments/rule-world/research/iteration17a_results.md` (new)
- `experiments/rule-world/research/iteration17b_runner.py` (new)
- `experiments/rule-world/research/iteration17b_results.md` (new)
- `experiments/rule-world/research/iteration17_results.md` (new, this file)

No edits to `hdc.py`, `abstractor.py`, `property_inducer.py`,
`compression.py`, or `engine.py`. Iter 17 is a measurement iteration;
the live stack is unchanged.
