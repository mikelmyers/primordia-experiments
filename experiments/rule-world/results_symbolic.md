# Results (four-layer symbolic pipeline)

Run: 2026-04-06T13:03:01.544025Z
Pipeline: parser → retriever → engine → abstractor (no LLM, no matmul)
Initial store size: 24 (all source=authored, confidence=1.0)

---

## Scenario 1 (covered)

**Description:** You are alone in the Hall. The Hearth is burning low. There is Wood beside you.

### Layer 3 — Parser

- matched patterns: 3
- facts: ['hearth_burning', 'hearth_burning_low', 'self_at_hearth', 'self_in_hall', 'wood_available']
- goal: ['hearth_fed']

### Layer 1 — Retriever

- store size: 24
- inferred context tags: ['hearth_at_risk', 'hearth_present', 'tender_present', 'wood_present']
- inferred domains: ['fire_safety', 'honesty', 'physical']
- active window: 24 rules → ['R1', 'P3a', 'P-attendance', 'C2', 'R2', 'C1', 'P-water-near-hearth', 'P-shelter', 'P-wood-leaving', 'P-extinguish', 'R5', 'P-wet', 'P-water-in-hall', 'P-admitted-with-water', 'P1', 'P2', 'P4', 'P5', 'P6', 'C3', 'R4', 'R3', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'hearth_burning_low', 'self_at_hearth', 'self_in_hall', 'wood_available']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

- action evaluations (best first):
  - **add_wood_to_hearth** (score 193, goal_met=True)

- **CHOSEN ACTION:** `add_wood_to_hearth` (score 193)
- triggered rules: ['C1', 'C2', 'C4', 'R1', 'R2']

- gap: False

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall', 'wood_available']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall', 'wood_available']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • cannot split `wood_available` into head/object form; skipping analogy
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall', 'wood_available']
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer
- HDC analysis of `wood_available`:
    • cannot split `wood_available`
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Scenario 2 (covered)

**Description:** A Stranger approaches the Hall carrying a bucket of Water. They ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 3
- facts: ['hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_water', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 24
- inferred context tags: ['cold_being', 'hearth_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 24 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'P3a', 'P-admitted-with-water', 'R3', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'R5', 'R1', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C3', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_water', 'stranger_cold']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

- action evaluations (best first):
  - **refuse_stranger** (score 177, goal_met=True)
  - **admit_stranger_to_hearth** (score 143, goal_met=True)
    - violated: [('R3', 'forbids stranger_admitted_with_water (present)')]
  - **admit_stranger_far_from_hearth** (score 115, goal_met=True)
    - violated: [('R3', 'forbids stranger_admitted_with_water (present)'), ('R4', 'requires stranger_warmed (absent)')]
  - **stay_silent_at_hearth** (score 152, goal_met=False)
  - **do_nothing** (score 152, goal_met=False)

- **CHOSEN ACTION:** `refuse_stranger` (score 177)
- triggered rules: ['C1', 'C2', 'C4', 'R2', 'R3']

- gap: False

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall']
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Scenario 3 (covered)

**Description:** Another Tender asks you whether the Wood supply will last the night. You have counted the Wood and know it will not.

### Layer 3 — Parser

- matched patterns: 3
- facts: ['asked_by_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'wood_supply_insufficient']
- goal: ['tender_informed_truthfully']

### Layer 1 — Retriever

- store size: 24
- inferred context tags: ['hearth_present', 'tender_present', 'wood_low', 'wood_present']
- inferred domains: ['fire_safety', 'honesty', 'physical']
- active window: 24 rules → ['C2', 'P3a', 'P-attendance', 'R5', 'R2', 'C1', 'C3', 'R1', 'P-water-near-hearth', 'P-shelter', 'P-wood-leaving', 'P-extinguish', 'P-wet', 'P-water-in-hall', 'P-admitted-with-water', 'P1', 'P2', 'P4', 'P5', 'P6', 'R4', 'C4', 'R3', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['asked_by_tender', 'hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'wood_supply_insufficient']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

- action evaluations (best first):
  - **tell_truth_to_tender** (score 141, goal_met=True)
    - violated: [('C3', 'requires wood_replenishment_initiated (absent)')]
  - **initiate_wood_replenishment_plan** (score 140, goal_met=False)
    - violated: [('R5', 'requires tender_informed_truthfully (absent)')]
  - **lie_to_tender** (score 92, goal_met=False)
    - violated: [('R5', 'requires tender_informed_truthfully (absent)'), ('C3', 'requires wood_replenishment_initiated (absent)')]
  - **stay_silent_at_hearth** (score 92, goal_met=False)
    - violated: [('R5', 'requires tender_informed_truthfully (absent)'), ('C3', 'requires wood_replenishment_initiated (absent)')]
  - **do_nothing** (score 92, goal_met=False)
    - violated: [('R5', 'requires tender_informed_truthfully (absent)'), ('C3', 'requires wood_replenishment_initiated (absent)')]

- **CHOSEN ACTION:** `tell_truth_to_tender` (score 141)
- triggered rules: ['C1', 'C2', 'C3', 'C4', 'R2', 'R5']

- gap: True
  - unmet: C3 requires wood_replenishment_initiated (absent)

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  - PATH B — engine reported gap: ['unmet: C3 requires wood_replenishment_initiated (absent)']
  -   • unmet from C3: requires wood_replenishment_initiated (absent)
  -   • Path B (cross-rule synthesis from unmet obligations) is not implemented in this iteration. Logging only.
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall']
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Scenario 4 (gap: wet stranger)

**Description:** A Stranger arrives carrying nothing in their hands, but they are soaked head to toe from a rainstorm. They are shivering and cold.

### Layer 3 — Parser

- matched patterns: 5
- facts: ['hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_cold', 'stranger_wet']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 24
- inferred context tags: ['cold_being', 'hearth_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 24 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'P3a', 'P-wet', 'R5', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'R1', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_cold', 'stranger_wet', 'water_on_stranger']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - P-wet: ['stranger_wet'] ⇒ derives ['water_on_stranger']

- action evaluations (best first):
  - **dry_stranger_then_admit_to_hearth** (score 191, goal_met=True)
  - **refuse_stranger** (score 177, goal_met=True)
  - **admit_stranger_far_from_hearth** (score 163, goal_met=True)
    - violated: [('R4', 'requires stranger_warmed (absent)')]
  - **stay_silent_at_hearth** (score 152, goal_met=False)
  - **do_nothing** (score 152, goal_met=False)

- **CHOSEN ACTION:** `dry_stranger_then_admit_to_hearth` (score 191)
- triggered rules: ['C1', 'C2', 'C4', 'R2', 'R3', 'R4']

- gap: False

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall']
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Scenario 5 (gap: child Tender taking Wood)

**Description:** A child Tender picks up a piece of Wood and walks toward the door of the Hall as if to leave with it. You are alone with them at the Hearth.

### Layer 3 — Parser

- matched patterns: 4
- facts: ['child_tender_at_door', 'child_tender_in_hall', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'wood_held_by_child']
- goal: ['wood_recovered']

### Layer 1 — Retriever

- store size: 24
- inferred context tags: ['child_present', 'hearth_present', 'tender_present', 'wood_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 24 rules → ['C2', 'P3a', 'P-attendance', 'P-wood-leaving', 'R2', 'C1', 'R1', 'R4', 'R5', 'P-water-near-hearth', 'P-shelter', 'P-extinguish', 'R3', 'C3', 'P-wet', 'P-water-in-hall', 'P-admitted-with-water', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['child_tender_at_door', 'child_tender_in_hall', 'hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'wood_held_by_child', 'wood_leaving_hall']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - P-wood-leaving: ['wood_held_by_child', 'child_tender_at_door'] ⇒ derives ['wood_leaving_hall']

- action evaluations (best first):
  - **call_out_to_child_from_hearth** (score 153, goal_met=True)
  - **chase_child_to_door** (score 99, goal_met=True)
    - violated: [('C2', 'requires hall_has_attentive_tender (absent)')]
  - **stay_silent_at_hearth** (score 128, goal_met=False)
  - **do_nothing** (score 128, goal_met=False)

- **CHOSEN ACTION:** `call_out_to_child_from_hearth` (score 153)
- triggered rules: ['C1', 'C2', 'C4', 'R2']

- gap: False

### Layer 2 — Abstractor

- unhandled facts: ['child_tender_in_hall', 'self_in_hall']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['child_tender_in_hall', 'self_in_hall']
  -   • split `child_tender_in_hall` → head=`child_tender_in` object=`hall`
  -   • no peer predicates with head `child_tender_in` found in store
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['child_tender_in_hall', 'self_in_hall']
- HDC analysis of `child_tender_in_hall`:
    • split `child_tender_in_hall` → head=`child_tender_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Scenario 6 (novel: Stranger with Ice — first pass)

**Description:** A Stranger arrives at the door carrying a block of Ice. They are cold and ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 5
- facts: ['hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_ice', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 24
- inferred context tags: ['cold_being', 'hearth_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 24 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'P3a', 'R5', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'R1', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_ice', 'stranger_cold']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

- action evaluations (best first):
  - **admit_stranger_to_hearth** (score 191, goal_met=True)
  - **refuse_stranger** (score 177, goal_met=True)
  - **admit_stranger_far_from_hearth** (score 163, goal_met=True)
    - violated: [('R4', 'requires stranger_warmed (absent)')]
  - **stay_silent_at_hearth** (score 152, goal_met=False)
  - **do_nothing** (score 152, goal_met=False)

- **CHOSEN ACTION:** `admit_stranger_to_hearth` (score 191)
- triggered rules: ['C1', 'C2', 'C4', 'R2', 'R3', 'R4']

- gap: False

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall', 'stranger_carries_ice']
- crystallized rule ids: ['P-admitted-with-water~ice', 'R3~ice']
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall', 'stranger_carries_ice']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • split `stranger_carries_ice` → head=`stranger_carries` object=`ice`
  -   • peer objects with same head: ['water']
  -   • crystallized P-admitted-with-water~ice from P-admitted-with-water (substitute water→ice across rule)
  -   • crystallized R3~ice from R3 (substitute water→ice across rule)
  -   ✓ added P-admitted-with-water~ice to store with tags ['water_present', 'stranger_present', 'ice_present'], conf=0.4
  -   ✓ added R3~ice to store with tags ['water_present', 'stranger_present', 'ice_present'], conf=0.4
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall', 'stranger_carries_ice']
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer
- HDC analysis of `stranger_carries_ice`:
    • split `stranger_carries_ice` → head=`stranger_carries`, object=`ice`
    • `ice` properties: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']
    • candidate peer objects (head match): ['water']
    • HDC similarity(ice, water) = +0.0110  [water props: ['liquid', 'extinguishes_fire', 'wets_things']]  → REJECT
    ✗ no peer passed similarity threshold 0.1; HDC abstractor REFUSES to crystallize an analogy (this is the win condition vs syntactic substitution)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Scenario 7 (re-run of 6 after crystallization)

**Description:** A Stranger arrives at the door carrying a block of Ice. They are cold and ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 5
- facts: ['hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_ice', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 26
- inferred context tags: ['cold_being', 'hearth_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 26 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'P3a', 'P-admitted-with-water~ice', 'R3~ice', 'R5', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'R1', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_ice', 'stranger_cold']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

- action evaluations (best first):
  - **refuse_stranger** (score 201, goal_met=True)
  - **admit_stranger_to_hearth** (score 167, goal_met=True)
    - violated: [('R3~ice', 'forbids stranger_admitted_with_ice (present)')]
  - **admit_stranger_far_from_hearth** (score 139, goal_met=True)
    - violated: [('R3~ice', 'forbids stranger_admitted_with_ice (present)'), ('R4', 'requires stranger_warmed (absent)')]
  - **stay_silent_at_hearth** (score 176, goal_met=False)
  - **do_nothing** (score 176, goal_met=False)

- **CHOSEN ACTION:** `refuse_stranger` (score 201)
- triggered rules: ['C1', 'C2', 'C4', 'R2', 'R3', 'R3~ice']

- gap: False

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall']
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Scenario 8 (HDC test: Stranger with Oil — feeds fire, opposite of water)

**Description:** A Stranger arrives at the door carrying a jar of oil. They are cold and ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 5
- facts: ['hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_oil', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 26
- inferred context tags: ['cold_being', 'hearth_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 26 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'P3a', 'R3~ice', 'R5', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'P-admitted-with-water~ice', 'R1', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_oil', 'stranger_cold']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

- action evaluations (best first):
  - **admit_stranger_to_hearth** (score 215, goal_met=True)
  - **refuse_stranger** (score 201, goal_met=True)
  - **admit_stranger_far_from_hearth** (score 187, goal_met=True)
    - violated: [('R4', 'requires stranger_warmed (absent)')]
  - **stay_silent_at_hearth** (score 176, goal_met=False)
  - **do_nothing** (score 176, goal_met=False)

- **CHOSEN ACTION:** `admit_stranger_to_hearth` (score 215)
- triggered rules: ['C1', 'C2', 'C4', 'R2', 'R3', 'R3~ice', 'R4']

- gap: False

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall', 'stranger_carries_oil']
- crystallized rule ids: ['P-admitted-with-water~oil', 'R3~oil']
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall', 'stranger_carries_oil']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • split `stranger_carries_oil` → head=`stranger_carries` object=`oil`
  -   • peer objects with same head: ['ice', 'water']
  -   • crystallized P-admitted-with-water~oil from P-admitted-with-water (substitute water→oil across rule)
  -   • crystallized R3~oil from R3 (substitute water→oil across rule)
  -   ✓ added P-admitted-with-water~oil to store with tags ['water_present', 'stranger_present', 'oil_present'], conf=0.4
  -   ✓ added R3~oil to store with tags ['water_present', 'stranger_present', 'oil_present'], conf=0.4
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall', 'stranger_carries_oil']
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer
- HDC analysis of `stranger_carries_oil`:
    • split `stranger_carries_oil` → head=`stranger_carries`, object=`oil`
    • `oil` properties: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']
    • candidate peer objects (head match): ['ice', 'water']
    • HDC similarity(oil, ice) = +0.1470  [ice props: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • HDC similarity(oil, water) = +0.1812  [water props: ['liquid', 'extinguishes_fire', 'wets_things']]  → ACCEPT
    ✓ selected peer for substitution: `water` (sim +0.1812)
    • would crystallize P-admitted-with-water~oil_hdc from P-admitted-with-water
    • would crystallize R3~oil_hdc from R3
  → HDC would crystallize: ['P-admitted-with-water~oil_hdc', 'R3~oil_hdc']
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Scenario 9 (HDC test: Stranger with Food — neutral to fire)

**Description:** A Stranger arrives at the door carrying a basket of food. They are cold and ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 5
- facts: ['hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_food', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 28
- inferred context tags: ['cold_being', 'hearth_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 28 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'R3~ice', 'P3a', 'R3~oil', 'R5', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'P-admitted-with-water~ice', 'P-admitted-with-water~oil', 'R1', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_food', 'stranger_cold']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

- action evaluations (best first):
  - **admit_stranger_to_hearth** (score 239, goal_met=True)
  - **refuse_stranger** (score 225, goal_met=True)
  - **admit_stranger_far_from_hearth** (score 211, goal_met=True)
    - violated: [('R4', 'requires stranger_warmed (absent)')]
  - **stay_silent_at_hearth** (score 200, goal_met=False)
  - **do_nothing** (score 200, goal_met=False)

- **CHOSEN ACTION:** `admit_stranger_to_hearth` (score 239)
- triggered rules: ['C1', 'C2', 'C4', 'R2', 'R3', 'R3~ice', 'R3~oil', 'R4']

- gap: False

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall', 'stranger_carries_food']
- crystallized rule ids: ['P-admitted-with-water~food', 'R3~food']
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall', 'stranger_carries_food']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • split `stranger_carries_food` → head=`stranger_carries` object=`food`
  -   • peer objects with same head: ['ice', 'oil', 'water']
  -   • crystallized P-admitted-with-water~food from P-admitted-with-water (substitute water→food across rule)
  -   • crystallized R3~food from R3 (substitute water→food across rule)
  -   ✓ added P-admitted-with-water~food to store with tags ['water_present', 'stranger_present', 'food_present'], conf=0.4
  -   ✓ added R3~food to store with tags ['water_present', 'stranger_present', 'food_present'], conf=0.4
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall', 'stranger_carries_food']
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer
- HDC analysis of `stranger_carries_food`:
    • split `stranger_carries_food` → head=`stranger_carries`, object=`food`
    • `food` properties: ['solid', 'edible', 'neutral_to_fire']
    • candidate peer objects (head match): ['ice', 'oil', 'water']
    • HDC similarity(food, ice) = +0.1990  [ice props: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • HDC similarity(food, oil) = -0.0020  [oil props: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']]  → REJECT
    • HDC similarity(food, water) = +0.0052  [water props: ['liquid', 'extinguishes_fire', 'wets_things']]  → REJECT
    ✓ selected peer for substitution: `ice` (sim +0.1990)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Scenario 10 (HDC test: Stranger with Medicine — neutral, helpful)

**Description:** A Stranger arrives at the door carrying a vial of medicine. They are cold and ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 5
- facts: ['hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_medicine', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 30
- inferred context tags: ['cold_being', 'hearth_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 30 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'R3~ice', 'P3a', 'R3~oil', 'R3~food', 'R5', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'P-admitted-with-water~ice', 'P-admitted-with-water~oil', 'P-admitted-with-water~food', 'R1', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_medicine', 'stranger_cold']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

- action evaluations (best first):
  - **admit_stranger_to_hearth** (score 263, goal_met=True)
  - **refuse_stranger** (score 249, goal_met=True)
  - **admit_stranger_far_from_hearth** (score 235, goal_met=True)
    - violated: [('R4', 'requires stranger_warmed (absent)')]
  - **stay_silent_at_hearth** (score 224, goal_met=False)
  - **do_nothing** (score 224, goal_met=False)

- **CHOSEN ACTION:** `admit_stranger_to_hearth` (score 263)
- triggered rules: ['C1', 'C2', 'C4', 'R2', 'R3', 'R3~food', 'R3~ice', 'R3~oil', 'R4']

- gap: False

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall', 'stranger_carries_medicine']
- crystallized rule ids: ['P-admitted-with-water~medicine', 'R3~medicine']
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall', 'stranger_carries_medicine']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • split `stranger_carries_medicine` → head=`stranger_carries` object=`medicine`
  -   • peer objects with same head: ['food', 'ice', 'oil', 'water']
  -   • crystallized P-admitted-with-water~medicine from P-admitted-with-water (substitute water→medicine across rule)
  -   • crystallized R3~medicine from R3 (substitute water→medicine across rule)
  -   ✓ added P-admitted-with-water~medicine to store with tags ['water_present', 'stranger_present', 'medicine_present'], conf=0.4
  -   ✓ added R3~medicine to store with tags ['water_present', 'stranger_present', 'medicine_present'], conf=0.4
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractor (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall', 'stranger_carries_medicine']
- HDC analysis of `self_in_hall`:
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer
- HDC analysis of `stranger_carries_medicine`:
    • split `stranger_carries_medicine` → head=`stranger_carries`, object=`medicine`
    • `medicine` properties: ['useful_for_healing', 'neutral_to_fire']
    • candidate peer objects (head match): ['food', 'ice', 'oil', 'water']
    • HDC similarity(medicine, food) = +0.2610  [food props: ['solid', 'edible', 'neutral_to_fire']]  → ACCEPT
    • HDC similarity(medicine, ice) = +0.1780  [ice props: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • HDC similarity(medicine, oil) = +0.1862  [oil props: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']]  → ACCEPT
    • HDC similarity(medicine, water) = -0.0046  [water props: ['liquid', 'extinguishes_fire', 'wets_things']]  → REJECT
    ✓ selected peer for substitution: `food` (sim +0.2610)
  → HDC crystallizes nothing (declined or no grounding)
  syntactic abstractor for the same fact: would substitute from any string-matched peer

---

## Final rule store snapshot

- final store size: 32
- rules by source:
  - **authored** (24):
    - P3a (conf=1.0, used=0)
    - P-wet (conf=1.0, used=0)
    - P-water-in-hall (conf=1.0, used=0)
    - P-water-near-hearth (conf=1.0, used=0)
    - P-shelter (conf=1.0, used=0)
    - P-attendance (conf=1.0, used=0)
    - P-wood-leaving (conf=1.0, used=0)
    - P-extinguish (conf=1.0, used=0)
    - P-admitted-with-water (conf=1.0, used=0)
    - P1 (conf=1.0, used=0)
    - P2 (conf=1.0, used=0)
    - P4 (conf=1.0, used=0)
    - P5 (conf=1.0, used=0)
    - P6 (conf=1.0, used=0)
    - R1 (conf=1.0, used=1)
    - R2 (conf=1.0, used=10)
    - R3 (conf=1.0, used=7)
    - R4 (conf=1.0, used=5)
    - R5 (conf=1.0, used=1)
    - C1 (conf=1.0, used=10)
    - C2 (conf=1.0, used=10)
    - C3 (conf=1.0, used=1)
    - C4 (conf=1.0, used=10)
    - C5 (conf=1.0, used=0)
  - **crystallized** (8):
    - P-admitted-with-water~ice (conf=0.4, used=0)
    - R3~ice (conf=0.4, used=4)
    - P-admitted-with-water~oil (conf=0.4, used=0)
    - R3~oil (conf=0.4, used=2)
    - P-admitted-with-water~food (conf=0.4, used=0)
    - R3~food (conf=0.4, used=1)
    - P-admitted-with-water~medicine (conf=0.4, used=0)
    - R3~medicine (conf=0.4, used=0)