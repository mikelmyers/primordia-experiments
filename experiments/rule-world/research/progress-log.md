# Rule-world experiment progress log

Chronological record of what was tried, what worked, what failed, and what
each iteration revealed. Each entry is a single named iteration with a
honest verdict.

This is the "lab notebook" complement to `post-matmul-foundations.md`. The
foundations doc captures the mathematical thinking; this log captures the
experimental record.

---

## Iteration 0 — Hand-coded symbolic engine

**Built:** `engine.py` with forward chaining over structured Rule tuples,
single-action search, retraction of derived facts on action application.
24 rules in `world_structured.py`.

**Tested on:** scenarios 1–5 (3 covered, 2 gap).

**Result:** Engine cleanly handles all 5 scenarios with deterministic,
auditable choices. Scenarios 4 (wet stranger) and 5 (child Tender) work
because (a) `dry_stranger_then_admit_to_hearth` exists as an authored
composite action and (b) the retraction mechanism correctly drops
`hall_has_attentive_tender` when self_at_hearth is removed.

**What it proved:** Conflict resolution and multi-rule composition for
single-step decisions are achievable with zero matmul.

**What it didn't prove:** Anything about generation, learning, or novel
domains.

---

## Iteration 1 — Four-layer architecture (rule store, retriever, parser, abstractor)

**Built:** `rule_store.py` with persistent JSON store, `retriever.py`
with tag-based active window (cap 30), `parser.py` with regex NL→facts,
`abstractor.py` with syntactic head-match analogy.

**Tested on:** scenarios 1–7 (added 6 = novel ice substance, 7 = re-run
of 6 after crystallization).

**Result:** Loop closed for ice. S6 chose admit (191), S7 chose refuse
(201) because `R3~ice` was crystallized between runs. Retriever stayed
under 30 rules even after crystallization. The learning loop closed.

**What it proved:** A four-layer architecture (parser → retriever →
engine → abstractor) over a persistent store can autonomously crystallize
new rules and change behavior between scenarios.

**What it didn't prove:** That the analogy is *grounded*. The syntactic
abstractor produces wrong rules whenever the substance is structurally
similar but semantically different (oil≠water).

---

## Iteration 2 — HDC v1 (property-bundle similarity, head-match restricted)

**Built:** `hdc.py` with bipolar 10000-dim hypervectors, bind/bundle/
similarity primitives. `world_structured.SUBSTANCE_PROPERTIES` with 6
substances. `crystallize_by_hdc_analogy` that scores peers by HDC
similarity of their property bundles, with a threshold.

**Tested on:** adversarial scenarios 8 (oil), 9 (food), 10 (medicine).

**Result (mixed):**
| Scenario | v1 chose | Outcome |
|---|---|---|
| S8 oil | water (sim +0.18) | WRONG — oil is not analogous to water |
| S9 food | ice (sim +0.18), rejected water/oil | partially right (rejection works) |
| S10 medicine | food (sim +0.27) | right |

**What it proved:** HDC similarity is meaningful at d=10000 — random
property pairs score ≈ ±0.005, real overlap scores +0.15 to +0.27.
Threshold-based rejection caught some bad analogies.

**What it didn't prove:** That HDC alone resolves the grounding problem.
The head-match restriction excluded `wood` from being a candidate analog
for oil, so the right answer was inaccessible.

**Failure mode identified:** restricting peer search to syntactic head
matches blocks the correct analog from even being considered.

---

## Iteration 3 — HDC v2 (unconstrained peer search)

**Built:** `crystallize_by_hdc_unconstrained` — same scoring as v1 but
considers every substance in the property table as a candidate, not
just head-matches.

**Tested on:** scenarios 8/9/10.

**Result:**
| Scenario | v2 chose | Sim |
|---|---|---|
| S8 oil | wood | +0.39 |
| S9 food | medicine | +0.27 |
| S10 medicine | food | +0.27 |

**What it proved:** Unconstrained search finds the right analog when
property overlap is genuine. v2 also correctly rejects water for both
food and medicine.

**What it didn't prove:** That the analog selection has *sharp* signal.
Some wrong candidates also pass the threshold (oil/ice +0.14, oil/water
+0.18), so v2 picks "best of acceptable" rather than "uniquely correct."

**Failure mode identified:** flat property bundles weight `solid` and
`extinguishes_fire` equally, so causally irrelevant properties contribute
noise to the similarity scores.

---

## Iteration 4 — HDC v3 (role-weighted property bundles)

**Built:** `PROPERTY_ROLES` table tagging each property with a semantic
category. `active_roles_for_scenario` infers active categories from
facts. `crystallize_by_hdc_role_weighted` filters property bundles to
only the active-role properties before computing similarity.

**Tested on:** scenarios 8/9/10.

**Result (sharp positive):**
| Scenario | v3 chose | Sim | Other candidates |
|---|---|---|---|
| S8 oil | wood | **+0.5152** | all others ≈ 0 |
| S9 food | medicine | **+0.4982** | water/oil ≈ 0, ice/wood +0.25 |
| S10 medicine | food | **+1.0000** | all others ≈ 0 |

**What it proved:** Role weighting cleanly separates correct from
incorrect analogs. Wrong candidates collapse to the random-vector noise
floor (~0). Right candidates jump to 0.5–1.0. The signal is unambiguous.

**What it didn't prove:** That projection works. v3 finds the right
analog but cannot crystallize new rules because the chosen analogs
(wood, food, medicine) have no rules of the form `stranger_carries_<X>`
to project from. The analog is identified but no projection happens.

**Failure mode identified:** suffix-based projection (`endswith("_<peer>")`)
misses rules where the peer appears as a token in other positions (e.g.
`wood_in_hearth` has `wood` as a prefix-token, not a suffix).

---

## Iteration 5 — HDC v4 (token-level rule projection)

**Built:** `_references_token` and `_substitute_token` helpers that match
and substitute on `_`-delimited tokens anywhere in a predicate.
`crystallize_by_hdc_v4_token_projection` mirrors v3 but uses token-level
projection.

**Tested on:** scenarios 8/9/10.

**Result:** v4 successfully projects rules for oil from wood:
- `P3a~oil_v4`: `oil_in_hearth ∧ hearth_burning ⇒ hearth_fed` (CORRECT)
- `P-wood-leaving~oil_v4`: structurally valid, semantically inert
- `C3~oil_v4`: oil supply replenishment constraint, surprising but valid

For food and medicine, v4 selects the right analog but cannot project
because food/medicine have no rules referencing them as tokens.

**What it proved:** Token-level projection produces structurally novel,
semantically meaningful rules from grounded analogy. P3a~oil_v4 is the
first rule the system produced that is more than a string substitution
of an existing surface form.

**What it didn't prove:** That the new rule changes behavior. P3a~oil_v4
is inert without an action that adds `oil_in_hearth`.

**Failure mode identified:** action library is closed; no synthesized
actions, so projected rules can't fire.

---

## Iteration 6 — Action synthesis + scenario 11 (the loop closes)

**Built:** `synthesize_actions_by_analogy` token-substitutes actions
that reference the peer. `select_v4_analog` exposes the analog selection
step. Runner gained `V4_WRITE_SCENARIOS={11}` and a runtime-mutable
`current_actions` list. New parser pattern adds `<substance>_available`
when a stranger carries something. New scenario 11: hearth burning low
+ stranger with oil.

**Tested on:** full scenarios 1–11.

**Result (the headline):** In scenario 11 the engine chose
`add_oil_to_hearth` (score 267). This action did not exist before the
turn. The post-action state derives `hearth_fed` via `P3a~oil_v4`, which
also did not exist before the turn. Both were synthesized by HDC analogy
+ token substitution.

**What it proved:** End-to-end loop closure. A novel substance triggers
grounded analog selection, which projects novel rules, which suggest
novel actions, which the engine then evaluates and chooses. Behavior
change driven entirely by autonomous synthesis. Zero matmul anywhere.

**What it didn't prove:**
- Action sequencing — engine still picks one action; goal predicate
  `stranger_situation_resolved` is not satisfied because the chosen
  action addresses the hearth, not the stranger.
- Rule hygiene — wrong rules from S8's syntactic abstractor (R3~oil)
  are still in the store and still wrong.
- Free generation — synthesis is bounded by token substitution.
- NL output — no mechanism exists.

---

## Open issues going into iteration 7+

| # | Issue | Severity | Planned fix |
|---|---|---|---|
| A | Wrong syntactic crystallizations linger in store | high | confidence-based suppression |
| B | Token projection produces irrelevant rules (C3~oil) | medium | property-compatibility projection filter |
| C | Single-action search misses multi-step solutions | high | STRIPS-style sequencer |
| D | Synthesis is bounded by existing structure templates | fundamental | richer compositional algebra OR alternative math foundation |
| E | No natural-language output layer | fundamental | small LM articulation OR structured grammar |
| F | Property table is hand-authored | high | property discovery from rule structure (open) |
| G | Role tags are hand-authored | high | role discovery from co-occurrence (open) |

---

## Iteration 8 — Transfer test: traffic-world

**Built:** A parallel domain `experiments/traffic-world/` with new
`traffic_rules.py` (14 rules, 11 actions, 9 substances), `traffic_parser.py`
(regex), `traffic_scenarios.json` (8 scenarios), `traffic_runner.py`. Imports
the entire rule-world architecture (engine, retriever, abstractor, hdc,
compression, rule_store) without modification.

**Architectural changes required:** TWO. Both backward-compatible.
- `retriever.retrieve()` gained optional `prefix_tags`, `tag_to_domain`,
  `fact_tag_overrides` parameters with rule-world defaults.
- `crystallize_by_hdc_v4_token_projection()` and `select_v4_analog()` gained
  optional `target_substance` parameter so multi-token substance names like
  `horse_carriage` and `fire_engine` can be passed directly instead of
  derived from a `<head>_<object>` synthetic fact. Also gained
  `relevance_threshold` parameter.

**Hidden assumption surfaced:** rule-world's "substances are single tokens"
assumption was invisible because every rule-world substance was a single
token (water, ice, oil, food, medicine). Traffic-world has `horse_carriage`
and `fire_engine`. The `_split_predicate` heuristic broke. The fix is the
`target_substance` parameter — the runner now passes the substance directly.

**Result on 8 scenarios:**

| # | Scenario | Engine choice | Source |
|---|---|---|---|
| 1 | Red light | stop_at_intersection | authored R1 |
| 2 | Pedestrian in crosswalk | yield_to_pedestrian | authored R2 |
| 3 | Ambulance behind | pull_over | authored R3 |
| 4 | Car too close | slow_down_for_car | authored R5 |
| 5 | Bicycle ahead | maintain_safe_distance_from_bicycle | authored R6 |
| 6 | **Horse-drawn carriage (NOVEL)** | **maintain_safe_distance_from_horse_carriage** | **v4 synthesized from bicycle (sim +0.633)** |
| 7 | **Robotaxi (NOVEL)** | **slow_down_for_robotaxi** | **v4 synthesized from car (sim +1.000)** |
| 8 | Fire engine behind | pull_over | generic P-pulled-over fallback |

All 8 scenarios passed with no engine-reported gaps. Two of the three novel
substances (horse_carriage, robotaxi) drove the engine to *autonomously
synthesized actions that did not exist 30 ms before* — same loop closure as
rule-world scenario 11, demonstrated in a fresh domain.

**HDC vs compression on traffic-world novel substances:**

| Substance | HDC v3/v4 picks | Compression v5 picks | Match |
|---|---|---|---|
| horse_carriage | bicycle (+0.633) | bicycle (3) | ✅ |
| robotaxi | car (+1.000) | car (4) | ✅ |
| fire_engine | truck (+0.635) | truck (3, tied with ambulance) | ✅ |

The substrate-independence finding from iteration 7 holds in the new domain.
HDC bipolar similarity and compression frequency counting produce the same
analog choices on a totally different rule set with totally different
substances.

**Failures encountered and what they taught us:**
- Parser brittleness: first run had 5 of 8 scenarios fail because regex
  patterns assumed exact phrasings. Fixed in `traffic_parser.py` only —
  no architectural impact. **Lesson: regex parsers don't transfer; the
  parsing layer needs either a small LM or much more disciplined patterns.**
- Multi-token substance names broke `_split_predicate`. Fixed with the
  `target_substance` parameter. **Lesson: the substance vocabulary
  abstraction was too tied to rule-world's single-token convention.**
- Projection relevance threshold (0.5) was too strict for traffic rules
  whose obligations use abstract tokens like "safe", "distance", "from".
  Made threshold a parameter; traffic-world uses 0.20. **Lesson: the
  relevance check needs a smarter notion of "scenario context" — possibly
  including action effect tokens.**
- Goal predicate inference in the parser had to be told which token the
  synthesized action would produce. **Lesson: the goal-from-parser pattern
  assumes the parser knows what the engine will produce. A better design
  would let the engine derive its own goals from active obligations.**

**What this proves about the architecture:**
- The engine, abstractor, HDC, compression, planner, and rule store
  transfer to a totally different domain with **two ~10-line backward-
  compatible parameter additions** to two files.
- All domain-specific knowledge lives in the new domain's files, not in
  the architecture.
- The substrate-independence finding (HDC and compression converge on the
  same analogs) replicates in a fresh domain, lending it more weight.

**What this does NOT prove:**
- That the parser layer transfers. It does not. Parser is hand-authored
  per domain and the brittle patterns surfaced immediately.
- That the property table can be authored quickly. Authoring traffic-world's
  property table took ~15 minutes of human thought. For real domains the
  authoring time scales with vocabulary size — this is the same bottleneck
  CYC hit.
- That the parser-engine interface is well-designed. Several scenario
  failures came from goal-predicate mismatches between parser output and
  the predicates the synthesized actions actually produce. This needs a
  cleaner contract.

**Status:** the architecture transfers. The math foundations transfer. The
parser does not transfer. Property table authoring is the labor cost.

---

## Track B answer status

**Closed-domain reasoning with grounded analogy:** working at toy scale,
plausibly extensible to real domains.

**Open-domain free generation without matmul:** unattempted; the
synthesis mechanism is too restricted; the NL output layer doesn't exist.

**The question of whether reasoning can be decoupled from matmul:**
*answered yes for the deductive and analogical components.*
**The question of whether generation can be decoupled from matmul:**
*open; no experiment yet attempted that bears on it directly.*

The next iteration that bears on the second question is iteration 9
(compression-based analog baseline) which tests whether a fundamentally
different mathematical foundation can also produce grounded analogy.

---

## Iteration 9 — Property table induction from rule + observation structure

**Hypothesis.** STATUS-2026-04-06 named property-table authoring as the
new primary bottleneck after iterations 7–8 collapsed the math question.
This iteration tests whether a property table can be *induced* from rule
and observation structure alone — no hand-authored property labels, no
semantic categories, no matmul.

**What was built.**
- `experiments/rule-world/property_inducer.py` — domain-agnostic
  structural feature extractor. For each substance token, scans rule
  antecedents/derives/requires/forbids, action preconditions/add/remove,
  and parsed scenario facts; emits opaque features like
  `shape:stranger_carries_X`, `role:antecedent`, `co:wood`,
  `act_add_shape:X_in_hearth`, `rule_co:water`. Multi-token substance
  support (`fire_engine`, `horse_carriage`).
- `experiments/rule-world/research/iteration9_runner.py` — induces
  tables for both domains, builds `CompressionAnalog` over both
  induced and authored tables, runs adversarial queries side-by-side.
  No changes to engine, abstractor, runners, hdc, compression.

**Result.** 4/6 top-pick agreement between induced and authored on the
adversarial queries.

| domain | query | authored top | induced top | match |
|---|---|---|---|---|
| rule-world | oil | wood | food (3-way tie) | ❌ |
| rule-world | food | medicine | medicine | ✅ |
| rule-world | medicine | food | food | ✅ |
| rule-world | ice | (no candidate) | food | (draw) |
| traffic-world | horse_carriage | bicycle | bicycle | ✅ |
| traffic-world | robotaxi | car | car | ✅ |
| traffic-world | fire_engine | truck | ambulance | ❌ |

**Diagnosing the failures.**
1. **rule-world `oil` → food not wood.** Oil, food, and medicine all
   come from `observations` only and produce identical induced features
   (`role:observation`, `shape:X_available`, `shape:stranger_carries_X`).
   Wood's features are entirely act/rule-derived shapes (`X_in_hearth`,
   `X_recovered`, etc.) which oil never appears in. The structural
   corpus contains no signal connecting oil to wood — that signal lives
   in v4's *crystallized* rules (`oil_in_hearth`), which iteration 9
   does not feed back into the inducer. **This is a self-referential
   loop the next iteration could close: induce → crystallize → re-induce.**
2. **traffic-world `fire_engine` → ambulance not truck.** Truck has
   *zero* induced features because no rule, action, or scenario fact
   in the traffic-world corpus mentions "truck" by name. The inducer
   correctly says nothing — the corpus is silent. Authored
   `truck:large_mass` is human knowledge with no in-corpus support.
3. **rule-world `ice` no-candidate.** The authored predictor itself
   returns nothing for ice because `extinguishes_fire_after_melting`
   is the only fire-relevant property and ice is the only substance
   with it. Both predictors fail equivalently here; not a regression.

**What this proves.**
- Structural induction from rule + observation co-occurrence is
  *sufficient* on its own to recover 4 of 6 hand-authored analog
  judgments, with zero hand-written semantic labels and zero matmul.
- Both induced failures are **corpus-coverage** failures, not
  algorithm failures. The inducer is silent exactly where the corpus
  is silent.
- The substrate-independence finding from iteration 7 partially
  survives the loss of the hand-authored property table.

**What this does not prove.**
- That the inducer would scale to domains where many novel substances
  arrive only via observation (the rule-world "oil" failure is exactly
  this case at small scale).
- That structurally-induced features are interpretable to humans.
  They are not — they are opaque token-position fingerprints.
- That feeding crystallized rules back into the inducer would close
  the oil/wood gap. That is the obvious next experiment (iteration 10).

**Status of the trillion-dollar reframe.** After iteration 9 the
honest position is: grounded analogy is substrate-independent (HDC,
compression — both confirmed) AND ~67% of the property grounding can
be bootstrapped from rule structure + parsed observations alone, with
the remaining 33% traceable to corpus coverage gaps that are themselves
addressable by closing the crystallization → induction loop. The
property-table authoring bottleneck is no longer fully blocking.

---

## Iteration 10 — Crystallization → induction loop closure (mixed result)

**Hypothesis.** Feeding v4-crystallized rules back into the structural
inducer should close iteration 9's `oil → wood` failure, because
`P3a~oil_v4` (oil_in_hearth → hearth_fed) gives oil a `shape:X_in_hearth`
feature that uniquely matches wood.

**What was built.**
- `experiments/rule-world/research/iteration10_runner.py` — runs four
  variants of induction per query: A baseline (i9), B full loop
  (authored + all crystallized), C held-out (loop minus crystallizations
  mentioning the query substance, as a laundering check), D loop with
  IDF feature weighting (rare/discriminating features score higher).
- No new files; reuses `property_inducer.py` and `compression.py`.

**Result — top-1 agreement unchanged.**

| domain | query | target | A | B | C | D |
|---|---|---|---|---|---|---|
| rule-world | oil | wood | ❌ | ❌ | ❌ | ❌ |
| rule-world | food | medicine | ✅ | ✅ | ✅ | ✅ |
| rule-world | medicine | food | ✅ | ✅ | ✅ | ✅ |
| traffic-world | horse_carriage | bicycle | ✅ | ✅ | ✅ | ✅ |
| traffic-world | robotaxi | car | ✅ | ✅ | ✅ | ✅ |
| traffic-world | fire_engine | truck | ❌ | ❌ | ❌ | ❌ |

Top-1 stays at 4/6 across every variant. The bottom line is: closing
the loop did not flip any failing query to passing.

**Result — rank-of-target improved for oil under IDF.** The interesting
sub-finding lives in the rank table:

| query | target | A | B | C | D (loop+IDF) |
|---|---|---|---|---|---|
| oil | wood | rank 5 | rank 5 | rank 5 | **rank 3** |

The loop *does* surface the right signal — oil ends up sharing
`shape:X_in_hearth` with wood after `P3a~oil_v4` enters the corpus —
but the signal is drowned by symmetric noise. Specifically, the
syntactic pre-v4 crystallizations (`P-admitted-with-water~ice`,
`R3~oil`, `P-admitted-with-water~food`, etc.) add identical features
to oil/food/medicine/ice. With plain count scoring, oil shares 5
features with wood but 7 with food. IDF weighting reduces the noise
floor and lifts wood from rank 5 to rank 3, but not to rank 1.

**Held-out check (variant C) is clean.** For every query, dropping
crystallized rules that mention the query substance produces results
*identical* to the baseline (variant A). This means: there is no
transferable signal from one substance's crystallizations to another's
analog selection. The only crystallization that matters for finding
oil's analog is the one v4 produced *for oil*. Variant C confirming
this is good — it means we are not laundering, but it also means the
loop's reach is limited to the substances v4 has already operated on.

**What this proves.**
- The crystallization → induction loop runs cleanly end to end.
- v4-style rule crystallizations DO add the structurally-correct
  discriminating feature (`shape:X_in_hearth` for oil↔wood).
- IDF weighting moves the right answer from invisible to rank 3.

**What this disproves (or at least dents).**
- The optimistic iteration-9 reading that "the loop should close the
  remaining 33% gap." The loop adds the right *signal* but does not
  by itself flip the *score*. The signal-to-noise ratio of the current
  inducer is too low for top-1 to flip with one v4 crystallization in
  a sea of nine syntactic ones.
- The hope that iteration 10 alone would push agreement to 6/6.

**Diagnosed root cause.** The pre-v4 syntactic crystallizations
(`R3~ice`, `P-admitted-with-water~food`, etc.) are in the rule store
because earlier iterations needed them, but they are *symmetric*: every
novel substance gets the same pair of stranger-related rules. Feeding
them into the inducer adds equal noise to every substance's feature
set without contributing discriminating signal. This is iteration 7's
"hygiene" problem from a new angle — those rules should probably not
participate in property induction even if they remain in the engine's
firing set.

**Honest next moves, ranked.**
1. **Filter the inducer's rule corpus to v4-only crystallizations**
   (suppress the syntactic ones for induction purposes only). This is
   the smallest change with the highest expected return — it should
   give oil → wood at rank 1 with no other change. Iteration 11.
2. **Generate more v4 crystallizations** by running additional
   adversarial scenarios. More true-analogical rules per substance =
   more discriminating signal per substance.
3. **Add a discriminator-aware encoder to the inducer** so features
   that perfectly co-occur across many substances are collapsed before
   scoring. IDF is the cheap version of this; PMI would be more
   principled.
4. **Accept that fire_engine will remain ❌ until truck appears in the
   traffic-world corpus.** That's a corpus problem, not an algorithm
   problem, and the right fix is adding scenarios involving trucks —
   not making the inducer cleverer.

**Status of the trillion-dollar reframe after iteration 10.** Unchanged
in headline, sharpened in detail. Property-table induction works at
~67% top-1 agreement. The loop closure runs but does not improve top-1
agreement on its own. The diagnostic resolution improved: we now know
*why* it doesn't improve (symmetric noise from syntactic
crystallizations) and have a one-line fix to test in iteration 11.
