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
