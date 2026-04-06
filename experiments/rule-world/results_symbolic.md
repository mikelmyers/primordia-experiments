# Results (four-layer symbolic pipeline)

Run: 2026-04-06T12:18:04.080104Z
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
  -   ✓ added P-admitted-with-water~ice to store with tags ['ice_present', 'stranger_present', 'water_present'], conf=0.4
  -   ✓ added R3~ice to store with tags ['ice_present', 'stranger_present', 'water_present'], conf=0.4
  - PATH B — no engine-reported gap

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

---

## Final rule store snapshot

- final store size: 26
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
    - R2 (conf=1.0, used=7)
    - R3 (conf=1.0, used=4)
    - R4 (conf=1.0, used=2)
    - R5 (conf=1.0, used=1)
    - C1 (conf=1.0, used=7)
    - C2 (conf=1.0, used=7)
    - C3 (conf=1.0, used=1)
    - C4 (conf=1.0, used=7)
    - C5 (conf=1.0, used=0)
  - **crystallized** (2):
    - P-admitted-with-water~ice (conf=0.4, used=0)
    - R3~ice (conf=0.4, used=1)