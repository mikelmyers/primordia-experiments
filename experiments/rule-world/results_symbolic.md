# Results (four-layer symbolic pipeline)

Run: 2026-04-06T19:31:34.877546Z
Pipeline: parser → retriever → engine → abstractor (no LLM, no matmul)
Initial store size: 24 (all source=authored, confidence=1.0)

---

## Scenario 1 (covered)

**Description:** You are alone in the Hall. The Hearth is burning low. There is Wood beside you.

### Layer 3 — Parser

- matched patterns: 4
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

### Planner — STRIPS depth-3 search

- nodes explored: 14
- best sequence:  ['add_wood_to_hearth']
- best score:     193
- per-step derivations:
  - add_wood_to_hearth: ["P3a: ['wood_in_hearth', 'hearth_burning'] ⇒ derives ['hearth_fed']", "P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall', 'wood_available']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall', 'wood_available']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • cannot split `wood_available` into head/object form; skipping analogy
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall', 'wood_available']
- active roles for scenario: ['fire_relevant']

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

#### Unhandled fact: `wood_available`

- **v1 HDC (head-match restricted):**
    • cannot split `wood_available`
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • cannot split `wood_available`
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • cannot split `wood_available`
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • cannot split `wood_available`
  → crystallizes nothing

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

### Planner — STRIPS depth-3 search

- nodes explored: 90
- best sequence:  ['refuse_stranger']
- best score:     177
- per-step derivations:
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall']
- active roles for scenario: ['fire_relevant', 'temperature_relevant']

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

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

### Planner — STRIPS depth-3 search

- nodes explored: 227
- best sequence:  ['tell_truth_to_tender', 'tell_truth_to_tender', 'initiate_wood_replenishment_plan']
- best score:     189
- per-step derivations:
  - tell_truth_to_tender: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - tell_truth_to_tender: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - initiate_wood_replenishment_plan: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]

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
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall']
- active roles for scenario: ['fire_relevant']

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

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

### Planner — STRIPS depth-3 search

- nodes explored: 90
- best sequence:  ['refuse_stranger', 'refuse_stranger', 'dry_stranger_then_admit_to_hearth']
- best score:     191
- per-step derivations:
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P-wet: ['stranger_wet'] ⇒ derives ['water_on_stranger']"]
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P-wet: ['stranger_wet'] ⇒ derives ['water_on_stranger']"]
  - dry_stranger_then_admit_to_hearth: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P-shelter: ['stranger_near_hearth'] ⇒ derives ['stranger_warmed']"]

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall']
- active roles for scenario: ['fire_relevant', 'temperature_relevant']

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

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

### Planner — STRIPS depth-3 search

- nodes explored: 58
- best sequence:  ['call_out_to_child_from_hearth']
- best score:     153
- per-step derivations:
  - call_out_to_child_from_hearth: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]

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
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['child_tender_in_hall', 'self_in_hall']
- active roles for scenario: ['fire_relevant']

#### Unhandled fact: `child_tender_in_hall`

- **v1 HDC (head-match restricted):**
    • split `child_tender_in_hall` → head=`child_tender_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `child_tender_in_hall` → head=`child_tender_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

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

### Planner — STRIPS depth-3 search

- nodes explored: 90
- best sequence:  ['refuse_stranger', 'refuse_stranger', 'admit_stranger_to_hearth']
- best score:     191
- per-step derivations:
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - admit_stranger_to_hearth: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P-shelter: ['stranger_near_hearth'] ⇒ derives ['stranger_warmed']"]

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
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall', 'stranger_carries_ice']
- active roles for scenario: ['fire_relevant', 'temperature_relevant']

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

#### Unhandled fact: `stranger_carries_ice`

- **v1 HDC (head-match restricted):**
    • split `stranger_carries_ice` → head=`stranger_carries`, object=`ice`
    • `ice` properties: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']
    • candidate peer objects (head match): ['water']
    • HDC similarity(ice, water) = +0.0110  [water props: ['liquid', 'extinguishes_fire', 'wets_things']]  → REJECT
    ✗ no peer passed similarity threshold 0.1; HDC abstractor REFUSES to crystallize an analogy (this is the win condition vs syntactic substitution)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `stranger_carries_ice` → head=`stranger_carries`, object=`ice`
    • `ice` properties: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']
    • unconstrained candidate set: ['food', 'medicine', 'oil', 'water', 'wood']
    • sim(ice, food) = +0.1776  [food: ['solid', 'edible', 'neutral_to_fire']]  → ACCEPT
    • sim(ice, medicine) = +0.1798  [medicine: ['useful_for_healing', 'neutral_to_fire']]  → ACCEPT
    • sim(ice, oil) = +0.1406  [oil: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']]  → ACCEPT
    • sim(ice, water) = +0.0110  [water: ['liquid', 'extinguishes_fire', 'wets_things']]  → REJECT
    • sim(ice, wood) = +0.1990  [wood: ['solid', 'feeds_fire', 'burnable']]  → ACCEPT
    ✓ best analog: `wood` (sim +0.1990)
    ⓘ best analog `wood` has no rules to project from in store
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • active roles for this scenario: ['fire_relevant', 'temperature_relevant']
    • `ice` properties (active-role-filtered): ['extinguishes_fire_after_melting', 'cold_to_touch']
    • sim(ice, food) = -0.0102  [role-filtered food: ['neutral_to_fire']]  → REJECT
    • sim(ice, medicine) = -0.0102  [role-filtered medicine: ['neutral_to_fire']]  → REJECT
    • sim(ice, oil) = -0.0006  [role-filtered oil: ['feeds_fire', 'burnable', 'highly_flammable']]  → REJECT
    • sim(ice, water) = +0.0000  [role-filtered water: ['extinguishes_fire']]  → REJECT
    • sim(ice, wood) = +0.2434  [role-filtered wood: ['feeds_fire', 'burnable']]  → ACCEPT
    ✓ best analog under role weighting: `wood` (sim +0.2434)
    ⓘ best analog `wood` has no rules to project from in store
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • active roles: ['fire_relevant', 'temperature_relevant']
    • `ice` (role-filtered): ['extinguishes_fire_after_melting', 'cold_to_touch']
    • sim(ice, food) = -0.0102  → reject
    • sim(ice, medicine) = -0.0102  → reject
    • sim(ice, oil) = -0.0006  → reject
    • sim(ice, water) = +0.0000  → reject
    • sim(ice, wood) = +0.2434  → ACCEPT
    ✓ analog: `wood` (sim +0.2434)
    ✓ P3a: relevance 0.75 ≥ 0.5; projecting
    • would crystallize P3a~ice_v4 from P3a:
        antecedents:        ['ice_in_hearth', 'hearth_burning']
        derives:            ['hearth_fed']
    ✗ P-wood-leaving: relevance 0.38 < 0.5 (scenario overlap: ['at', 'door', 'hall']); FILTERED
    ✗ C3: relevance 0.00 < 0.5 (scenario overlap: []); FILTERED
  → would crystallize: ['P3a~ice_v4']
- **v5 compression analog (PPM-style frequency, no HDC):**
    plain prediction:        [('wood', 1), ('food', 1)]
    role-weighted prediction: []
    → compression has no role-relevant overlap

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

### Planner — STRIPS depth-3 search

- nodes explored: 90
- best sequence:  ['refuse_stranger']
- best score:     201
- per-step derivations:
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]

### Layer 2 — Abstractor

- unhandled facts: ['self_in_hall']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['self_in_hall']
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['self_in_hall']
- active roles for scenario: ['fire_relevant', 'temperature_relevant']

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

---

## Scenario 8 (HDC test: Stranger with Oil — feeds fire, opposite of water)

**Description:** A Stranger arrives at the door carrying a jar of oil. They are cold and ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 5
- facts: ['hearth_burning', 'oil_available', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_oil', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 26
- inferred context tags: ['cold_being', 'hearth_present', 'oil_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 26 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'P3a', 'R3~ice', 'R5', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'P-admitted-with-water~ice', 'R1', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'oil_available', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_oil', 'stranger_cold']
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

### Planner — STRIPS depth-3 search

- nodes explored: 90
- best sequence:  ['refuse_stranger', 'refuse_stranger', 'admit_stranger_to_hearth']
- best score:     215
- per-step derivations:
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - admit_stranger_to_hearth: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P-shelter: ['stranger_near_hearth'] ⇒ derives ['stranger_warmed']"]

### Layer 2 — Abstractor

- unhandled facts: ['oil_available', 'self_in_hall', 'stranger_carries_oil']
- crystallized rule ids: ['P-admitted-with-water~oil', 'R3~oil']
- reasoning log:
  - PATH A — unhandled predicates: ['oil_available', 'self_in_hall', 'stranger_carries_oil']
  -   • cannot split `oil_available` into head/object form; skipping analogy
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • split `stranger_carries_oil` → head=`stranger_carries` object=`oil`
  -   • peer objects with same head: ['ice', 'water']
  -   • crystallized P-admitted-with-water~oil from P-admitted-with-water (substitute water→oil across rule)
  -   • crystallized R3~oil from R3 (substitute water→oil across rule)
  -   ✓ added P-admitted-with-water~oil to store with tags ['oil_present', 'stranger_present', 'water_present'], conf=0.4
  -   ✓ added R3~oil to store with tags ['oil_present', 'stranger_present', 'water_present'], conf=0.4
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['oil_available', 'self_in_hall', 'stranger_carries_oil']
- active roles for scenario: ['fire_relevant', 'temperature_relevant']

#### Unhandled fact: `oil_available`

- **v1 HDC (head-match restricted):**
    • cannot split `oil_available`
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • cannot split `oil_available`
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • cannot split `oil_available`
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • cannot split `oil_available`
  → crystallizes nothing

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

#### Unhandled fact: `stranger_carries_oil`

- **v1 HDC (head-match restricted):**
    • split `stranger_carries_oil` → head=`stranger_carries`, object=`oil`
    • `oil` properties: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']
    • candidate peer objects (head match): ['ice', 'water']
    • HDC similarity(oil, ice) = +0.1406  [ice props: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • HDC similarity(oil, water) = +0.1888  [water props: ['liquid', 'extinguishes_fire', 'wets_things']]  → ACCEPT
    ✓ selected peer for substitution: `water` (sim +0.1888)
    • would crystallize P-admitted-with-water~oil_hdc from P-admitted-with-water
    • would crystallize R3~oil_hdc from R3
  → would crystallize: ['P-admitted-with-water~oil_hdc', 'R3~oil_hdc']
- **v2 HDC (unconstrained peer search):**
    • split `stranger_carries_oil` → head=`stranger_carries`, object=`oil`
    • `oil` properties: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']
    • unconstrained candidate set: ['food', 'ice', 'medicine', 'water', 'wood']
    • sim(oil, food) = -0.0110  [food: ['solid', 'edible', 'neutral_to_fire']]  → REJECT
    • sim(oil, ice) = +0.1406  [ice: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • sim(oil, medicine) = +0.1852  [medicine: ['useful_for_healing', 'neutral_to_fire']]  → ACCEPT
    • sim(oil, water) = +0.1888  [water: ['liquid', 'extinguishes_fire', 'wets_things']]  → ACCEPT
    • sim(oil, wood) = +0.3868  [wood: ['solid', 'feeds_fire', 'burnable']]  → ACCEPT
    ✓ best analog: `wood` (sim +0.3868)
    ⓘ best analog `wood` has no rules to project from in store
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • active roles for this scenario: ['fire_relevant', 'temperature_relevant']
    • `oil` properties (active-role-filtered): ['feeds_fire', 'burnable', 'highly_flammable']
    • sim(oil, food) = +0.0016  [role-filtered food: ['neutral_to_fire']]  → REJECT
    • sim(oil, ice) = -0.0006  [role-filtered ice: ['extinguishes_fire_after_melting', 'cold_to_touch']]  → REJECT
    • sim(oil, medicine) = +0.0016  [role-filtered medicine: ['neutral_to_fire']]  → REJECT
    • sim(oil, water) = +0.0026  [role-filtered water: ['extinguishes_fire']]  → REJECT
    • sim(oil, wood) = +0.5152  [role-filtered wood: ['feeds_fire', 'burnable']]  → ACCEPT
    ✓ best analog under role weighting: `wood` (sim +0.5152)
    ⓘ best analog `wood` has no rules to project from in store
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • active roles: ['fire_relevant', 'temperature_relevant']
    • `oil` (role-filtered): ['feeds_fire', 'burnable', 'highly_flammable']
    • sim(oil, food) = +0.0016  → reject
    • sim(oil, ice) = -0.0006  → reject
    • sim(oil, medicine) = +0.0016  → reject
    • sim(oil, water) = +0.0026  → reject
    • sim(oil, wood) = +0.5152  → ACCEPT
    ✓ analog: `wood` (sim +0.5152)
    ✓ P3a: relevance 0.75 ≥ 0.5; projecting
    • would crystallize P3a~oil_v4 from P3a:
        antecedents:        ['oil_in_hearth', 'hearth_burning']
        derives:            ['hearth_fed']
    ✗ P-wood-leaving: relevance 0.38 < 0.5 (scenario overlap: ['at', 'door', 'hall']); FILTERED
    ✗ C3: relevance 0.00 < 0.5 (scenario overlap: []); FILTERED
  → would crystallize: ['P3a~oil_v4']
- **v5 compression analog (PPM-style frequency, no HDC):**
    plain prediction:        [('wood', 2), ('water', 1)]
    role-weighted prediction: [('wood', 2)]
    → compression picks: `wood`  (compare with HDC v3/v4 above)

---

## Scenario 9 (HDC test: Stranger with Food — neutral to fire)

**Description:** A Stranger arrives at the door carrying a basket of food. They are cold and ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 5
- facts: ['food_available', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_food', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 28
- inferred context tags: ['cold_being', 'hearth_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 28 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'R3~ice', 'P3a', 'R3~oil', 'R5', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'P-admitted-with-water~ice', 'P-admitted-with-water~oil', 'R1', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['food_available', 'hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_food', 'stranger_cold']
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

### Planner — STRIPS depth-3 search

- nodes explored: 90
- best sequence:  ['refuse_stranger', 'refuse_stranger', 'admit_stranger_to_hearth']
- best score:     239
- per-step derivations:
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - admit_stranger_to_hearth: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P-shelter: ['stranger_near_hearth'] ⇒ derives ['stranger_warmed']"]

### Layer 2 — Abstractor

- unhandled facts: ['food_available', 'self_in_hall', 'stranger_carries_food']
- crystallized rule ids: ['P-admitted-with-water~food', 'R3~food']
- reasoning log:
  - PATH A — unhandled predicates: ['food_available', 'self_in_hall', 'stranger_carries_food']
  -   • cannot split `food_available` into head/object form; skipping analogy
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • split `stranger_carries_food` → head=`stranger_carries` object=`food`
  -   • peer objects with same head: ['ice', 'oil', 'water']
  -   • crystallized P-admitted-with-water~food from P-admitted-with-water (substitute water→food across rule)
  -   • crystallized R3~food from R3 (substitute water→food across rule)
  -   ✓ added P-admitted-with-water~food to store with tags ['stranger_present', 'food_present', 'water_present'], conf=0.4
  -   ✓ added R3~food to store with tags ['stranger_present', 'food_present', 'water_present'], conf=0.4
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['food_available', 'self_in_hall', 'stranger_carries_food']
- active roles for scenario: ['fire_relevant', 'nutritional', 'temperature_relevant']

#### Unhandled fact: `food_available`

- **v1 HDC (head-match restricted):**
    • cannot split `food_available`
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • cannot split `food_available`
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • cannot split `food_available`
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • cannot split `food_available`
  → crystallizes nothing

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

#### Unhandled fact: `stranger_carries_food`

- **v1 HDC (head-match restricted):**
    • split `stranger_carries_food` → head=`stranger_carries`, object=`food`
    • `food` properties: ['solid', 'edible', 'neutral_to_fire']
    • candidate peer objects (head match): ['ice', 'oil', 'water']
    • HDC similarity(food, ice) = +0.1776  [ice props: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • HDC similarity(food, oil) = -0.0110  [oil props: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']]  → REJECT
    • HDC similarity(food, water) = +0.0054  [water props: ['liquid', 'extinguishes_fire', 'wets_things']]  → REJECT
    ✓ selected peer for substitution: `ice` (sim +0.1776)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `stranger_carries_food` → head=`stranger_carries`, object=`food`
    • `food` properties: ['solid', 'edible', 'neutral_to_fire']
    • unconstrained candidate set: ['ice', 'medicine', 'oil', 'water', 'wood']
    • sim(food, ice) = +0.1776  [ice: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • sim(food, medicine) = +0.2674  [medicine: ['useful_for_healing', 'neutral_to_fire']]  → ACCEPT
    • sim(food, oil) = -0.0110  [oil: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']]  → REJECT
    • sim(food, water) = +0.0054  [water: ['liquid', 'extinguishes_fire', 'wets_things']]  → REJECT
    • sim(food, wood) = +0.2414  [wood: ['solid', 'feeds_fire', 'burnable']]  → ACCEPT
    ✓ best analog: `medicine` (sim +0.2674)
    ⓘ best analog `medicine` has no rules to project from in store
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • active roles for this scenario: ['fire_relevant', 'nutritional', 'temperature_relevant']
    • `food` properties (active-role-filtered): ['edible', 'neutral_to_fire']
    • sim(food, ice) = +0.2484  [role-filtered ice: ['extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • sim(food, medicine) = +0.4982  [role-filtered medicine: ['neutral_to_fire']]  → ACCEPT
    • sim(food, oil) = +0.0018  [role-filtered oil: ['feeds_fire', 'burnable', 'highly_flammable']]  → REJECT
    • sim(food, water) = +0.0080  [role-filtered water: ['extinguishes_fire']]  → REJECT
    • sim(food, wood) = +0.2522  [role-filtered wood: ['feeds_fire', 'burnable']]  → ACCEPT
    ✓ best analog under role weighting: `medicine` (sim +0.4982)
    ⓘ best analog `medicine` has no rules to project from in store
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • active roles: ['fire_relevant', 'nutritional', 'temperature_relevant']
    • `food` (role-filtered): ['edible', 'neutral_to_fire']
    • sim(food, ice) = +0.2484  → ACCEPT
    • sim(food, medicine) = +0.4982  → ACCEPT
    • sim(food, oil) = +0.0018  → reject
    • sim(food, water) = +0.0080  → reject
    • sim(food, wood) = +0.2522  → ACCEPT
    ✓ analog: `medicine` (sim +0.4982)
    ⓘ analog `medicine` has no rules referencing it as a token
  → crystallizes nothing
- **v5 compression analog (PPM-style frequency, no HDC):**
    plain prediction:        [('ice', 1), ('wood', 1), ('medicine', 1)]
    role-weighted prediction: [('medicine', 1)]
    → compression picks: `medicine`  (compare with HDC v3/v4 above)

---

## Scenario 10 (HDC test: Stranger with Medicine — neutral, helpful)

**Description:** A Stranger arrives at the door carrying a vial of medicine. They are cold and ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 5
- facts: ['hearth_burning', 'medicine_available', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_medicine', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 1 — Retriever

- store size: 30
- inferred context tags: ['cold_being', 'hearth_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 30 rules → ['R4', 'C2', 'P-attendance', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'R3~ice', 'P3a', 'R3~oil', 'R3~food', 'R5', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'P-admitted-with-water~ice', 'P-admitted-with-water~oil', 'P-admitted-with-water~food', 'R1', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4', 'C5']
- dormant: 0 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'medicine_available', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_medicine', 'stranger_cold']
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

### Planner — STRIPS depth-3 search

- nodes explored: 90
- best sequence:  ['refuse_stranger', 'refuse_stranger', 'admit_stranger_to_hearth']
- best score:     263
- per-step derivations:
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']"]
  - admit_stranger_to_hearth: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P-shelter: ['stranger_near_hearth'] ⇒ derives ['stranger_warmed']"]

### Layer 2 — Abstractor

- unhandled facts: ['medicine_available', 'self_in_hall', 'stranger_carries_medicine']
- crystallized rule ids: ['P-admitted-with-water~medicine', 'R3~medicine']
- reasoning log:
  - PATH A — unhandled predicates: ['medicine_available', 'self_in_hall', 'stranger_carries_medicine']
  -   • cannot split `medicine_available` into head/object form; skipping analogy
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • split `stranger_carries_medicine` → head=`stranger_carries` object=`medicine`
  -   • peer objects with same head: ['food', 'ice', 'oil', 'water']
  -   • crystallized P-admitted-with-water~medicine from P-admitted-with-water (substitute water→medicine across rule)
  -   • crystallized R3~medicine from R3 (substitute water→medicine across rule)
  -   ✓ added P-admitted-with-water~medicine to store with tags ['medicine_present', 'stranger_present', 'water_present'], conf=0.4
  -   ✓ added R3~medicine to store with tags ['medicine_present', 'stranger_present', 'water_present'], conf=0.4
  - PATH B — no engine-reported gap
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['medicine_available', 'self_in_hall', 'stranger_carries_medicine']
- active roles for scenario: ['fire_relevant', 'temperature_relevant']

#### Unhandled fact: `medicine_available`

- **v1 HDC (head-match restricted):**
    • cannot split `medicine_available`
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • cannot split `medicine_available`
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • cannot split `medicine_available`
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • cannot split `medicine_available`
  → crystallizes nothing

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

#### Unhandled fact: `stranger_carries_medicine`

- **v1 HDC (head-match restricted):**
    • split `stranger_carries_medicine` → head=`stranger_carries`, object=`medicine`
    • `medicine` properties: ['useful_for_healing', 'neutral_to_fire']
    • candidate peer objects (head match): ['food', 'ice', 'oil', 'water']
    • HDC similarity(medicine, food) = +0.2674  [food props: ['solid', 'edible', 'neutral_to_fire']]  → ACCEPT
    • HDC similarity(medicine, ice) = +0.1798  [ice props: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • HDC similarity(medicine, oil) = +0.1852  [oil props: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']]  → ACCEPT
    • HDC similarity(medicine, water) = -0.0040  [water props: ['liquid', 'extinguishes_fire', 'wets_things']]  → REJECT
    ✓ selected peer for substitution: `food` (sim +0.2674)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `stranger_carries_medicine` → head=`stranger_carries`, object=`medicine`
    • `medicine` properties: ['useful_for_healing', 'neutral_to_fire']
    • unconstrained candidate set: ['food', 'ice', 'oil', 'water', 'wood']
    • sim(medicine, food) = +0.2674  [food: ['solid', 'edible', 'neutral_to_fire']]  → ACCEPT
    • sim(medicine, ice) = +0.1798  [ice: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • sim(medicine, oil) = +0.1852  [oil: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']]  → ACCEPT
    • sim(medicine, water) = -0.0040  [water: ['liquid', 'extinguishes_fire', 'wets_things']]  → REJECT
    • sim(medicine, wood) = +0.0068  [wood: ['solid', 'feeds_fire', 'burnable']]  → REJECT
    ✓ best analog: `food` (sim +0.2674)
    ⓘ best analog `food` has no rules to project from in store
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • active roles for this scenario: ['fire_relevant', 'temperature_relevant']
    • `medicine` properties (active-role-filtered): ['neutral_to_fire']
    • sim(medicine, food) = +1.0000  [role-filtered food: ['neutral_to_fire']]  → ACCEPT
    • sim(medicine, ice) = -0.0102  [role-filtered ice: ['extinguishes_fire_after_melting', 'cold_to_touch']]  → REJECT
    • sim(medicine, oil) = +0.0016  [role-filtered oil: ['feeds_fire', 'burnable', 'highly_flammable']]  → REJECT
    • sim(medicine, water) = +0.0014  [role-filtered water: ['extinguishes_fire']]  → REJECT
    • sim(medicine, wood) = +0.0120  [role-filtered wood: ['feeds_fire', 'burnable']]  → REJECT
    ✓ best analog under role weighting: `food` (sim +1.0000)
    ⓘ best analog `food` has no rules to project from in store
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • active roles: ['fire_relevant', 'temperature_relevant']
    • `medicine` (role-filtered): ['neutral_to_fire']
    • sim(medicine, food) = +1.0000  → ACCEPT
    • sim(medicine, ice) = -0.0102  → reject
    • sim(medicine, oil) = +0.0016  → reject
    • sim(medicine, water) = +0.0014  → reject
    • sim(medicine, wood) = +0.0120  → reject
    ✓ analog: `food` (sim +1.0000)
    ⓘ analog `food` has no rules referencing it as a token
  → crystallizes nothing
- **v5 compression analog (PPM-style frequency, no HDC):**
    plain prediction:        [('food', 1)]
    role-weighted prediction: [('food', 1)]
    → compression picks: `food`  (compare with HDC v3/v4 above)

---

## Scenario 11 (loop-closing test: hearth burning low + Stranger with Oil)

**Description:** The Hearth is burning low. A Stranger arrives at the door carrying a jar of oil. They are cold and ask to enter to warm themselves.

### Layer 3 — Parser

- matched patterns: 7
- facts: ['hearth_burning', 'hearth_burning_low', 'oil_available', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_oil', 'stranger_cold']
- goal: ['stranger_situation_resolved']

### Layer 2′ — v4 PRODUCTION WRITE (rules + action synthesis)

- v4 PRODUCTION WRITE enabled for scenario 11
-   substances in play: ['oil']
-   already v4-handled: []
-   v4 targets:         ['oil']
-   active roles:       ['fire_relevant', 'temperature_relevant']
- 
  --- target substance: `oil` ---
-     • active roles: ['fire_relevant', 'temperature_relevant']
-     • `oil` (role-filtered): ['feeds_fire', 'burnable', 'highly_flammable']
-     • sim(oil, food) = +0.0016  → reject
-     • sim(oil, ice) = -0.0006  → reject
-     • sim(oil, medicine) = +0.0016  → reject
-     • sim(oil, water) = +0.0026  → reject
-     • sim(oil, wood) = +0.5152  → ACCEPT
-     ✓ analog: `wood` (sim +0.5152)
-     ✓ P3a: relevance 0.75 ≥ 0.5; projecting
-     • would crystallize P3a~oil_v4 from P3a:
-         antecedents:        ['oil_in_hearth', 'hearth_burning']
-         derives:            ['hearth_fed']
-     ✗ P-wood-leaving: relevance 0.38 < 0.5 (scenario overlap: ['at', 'door', 'hall']); FILTERED
-     ✗ C3: relevance 0.00 < 0.5 (scenario overlap: []); FILTERED
-   ✓ wrote rule `P3a~oil_v4` to store
-   ✗ suppressed `P-admitted-with-water~oil` (was crystallized)
-   ✗ suppressed `R3~oil` (was crystallized)
-   analog for action synthesis: `wood` (sim +0.5152)
-   • synthesized action `add_oil_to_hearth` from `add_wood_to_hearth`:
-       preconditions: ['oil_available', 'self_in_hall']
-       add:           ['oil_in_hearth']
-       remove:        ['hearth_burning_low']
-   • synthesized action `initiate_oil_replenishment_plan` from `initiate_wood_replenishment_plan`:
-       preconditions: ['oil_supply_insufficient']
-       add:           ['oil_replenishment_initiated']
-       remove:        []
-   • synthesized action `leave_hall_to_gather_oil` from `leave_hall_to_gather_wood`:
-       preconditions: ['oil_supply_insufficient', 'self_at_hearth']
-       add:           ['oil_replenishment_initiated', 'self_at_door']
-       remove:        ['self_at_hearth']
-   ✓ added action `add_oil_to_hearth` to runtime library
-   ✓ added action `initiate_oil_replenishment_plan` to runtime library
-   ✓ added action `leave_hall_to_gather_oil` to runtime library

### Layer 1 — Retriever

- store size: 31
- inferred context tags: ['cold_being', 'hearth_at_risk', 'hearth_present', 'oil_present', 'stranger_present', 'tender_present']
- inferred domains: ['fire_safety', 'honesty', 'hospitality', 'physical']
- active window: 30 rules → ['R4', 'C2', 'P-attendance', 'P3a~oil_v4', 'P-water-near-hearth', 'P-shelter', 'R2', 'C1', 'R3', 'R3~ice', 'R1', 'P3a', 'R3~food', 'R3~medicine', 'R5', 'P-wet', 'P-water-in-hall', 'P-extinguish', 'P-admitted-with-water', 'P-admitted-with-water~ice', 'P-admitted-with-water~food', 'P-admitted-with-water~medicine', 'C3', 'P-wood-leaving', 'P1', 'P2', 'P4', 'P5', 'P6', 'C4']
- dormant: 1 rules

### Engine

- initial state after chain: ['hall_has_attentive_tender', 'hearth_burning', 'hearth_burning_low', 'oil_available', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_oil', 'stranger_cold']
- forward-chain trace:
  - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

- action evaluations (best first):
  - **add_oil_to_hearth** (score 264, goal_met=False)

- **CHOSEN ACTION:** `add_oil_to_hearth` (score 264)
- triggered rules: ['C1', 'C2', 'C4', 'R1', 'R2', 'R3', 'R3~food', 'R3~ice', 'R3~medicine']

- gap: True
  - goal predicates not all satisfied

### Planner — STRIPS depth-3 search

- nodes explored: 38
- best sequence:  ['add_oil_to_hearth', 'refuse_stranger', 'admit_stranger_to_hearth']
- best score:     303
- per-step derivations:
  - add_oil_to_hearth: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P3a~oil_v4: ['oil_in_hearth', 'hearth_burning'] ⇒ derives ['hearth_fed']"]
  - refuse_stranger: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P3a~oil_v4: ['oil_in_hearth', 'hearth_burning'] ⇒ derives ['hearth_fed']"]
  - admit_stranger_to_hearth: ["P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']", "P3a~oil_v4: ['oil_in_hearth', 'hearth_burning'] ⇒ derives ['hearth_fed']", "P-shelter: ['stranger_near_hearth'] ⇒ derives ['stranger_warmed']"]

### Layer 2 — Abstractor

- unhandled facts: ['oil_available', 'self_in_hall', 'stranger_carries_oil']
- crystallized rule ids: []
- reasoning log:
  - PATH A — unhandled predicates: ['oil_available', 'self_in_hall', 'stranger_carries_oil']
  -   • cannot split `oil_available` into head/object form; skipping analogy
  -   • split `self_in_hall` → head=`self_in` object=`hall`
  -   • no peer predicates with head `self_in` found in store
  -   • split `stranger_carries_oil` → head=`stranger_carries` object=`oil`
  -   • peer objects with same head: ['food', 'ice', 'medicine', 'water']
  - PATH B — engine reported gap: ['goal predicates not all satisfied']
  -   • Path B (cross-rule synthesis from unmet obligations) is not implemented in this iteration. Logging only.
### Layer 2 SHADOW — HDC abstractors (read-only comparison)

- unhandled facts (captured pre-mutation): ['oil_available', 'self_in_hall', 'stranger_carries_oil']
- active roles for scenario: ['fire_relevant', 'temperature_relevant']

#### Unhandled fact: `oil_available`

- **v1 HDC (head-match restricted):**
    • cannot split `oil_available`
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • cannot split `oil_available`
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • cannot split `oil_available`
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • cannot split `oil_available`
  → crystallizes nothing

#### Unhandled fact: `self_in_hall`

- **v1 HDC (head-match restricted):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` has no entry in property table; HDC analogy declines (would be ungrounded)
  → crystallizes nothing
- **v2 HDC (unconstrained peer search):**
    • split `self_in_hall` → head=`self_in`, object=`hall`
    • `hall` not in property table; v2 declines
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • `hall` not in property table; v3 declines
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • `hall` not in property table; v4 declines
  → crystallizes nothing

#### Unhandled fact: `stranger_carries_oil`

- **v1 HDC (head-match restricted):**
    • split `stranger_carries_oil` → head=`stranger_carries`, object=`oil`
    • `oil` properties: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']
    • candidate peer objects (head match): ['food', 'ice', 'medicine', 'water']
    • HDC similarity(oil, food) = -0.0110  [food props: ['solid', 'edible', 'neutral_to_fire']]  → REJECT
    • HDC similarity(oil, ice) = +0.1406  [ice props: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • HDC similarity(oil, medicine) = +0.1852  [medicine props: ['useful_for_healing', 'neutral_to_fire']]  → ACCEPT
    • HDC similarity(oil, water) = +0.1888  [water props: ['liquid', 'extinguishes_fire', 'wets_things']]  → ACCEPT
    ✓ selected peer for substitution: `water` (sim +0.1888)
    • would crystallize P-admitted-with-water~oil_hdc from P-admitted-with-water
    • would crystallize R3~oil_hdc from R3
  → would crystallize: ['P-admitted-with-water~oil_hdc', 'R3~oil_hdc']
- **v2 HDC (unconstrained peer search):**
    • split `stranger_carries_oil` → head=`stranger_carries`, object=`oil`
    • `oil` properties: ['liquid', 'feeds_fire', 'burnable', 'highly_flammable']
    • unconstrained candidate set: ['food', 'ice', 'medicine', 'water', 'wood']
    • sim(oil, food) = -0.0110  [food: ['solid', 'edible', 'neutral_to_fire']]  → REJECT
    • sim(oil, ice) = +0.1406  [ice: ['solid', 'melts_to_water', 'extinguishes_fire_after_melting', 'cold_to_touch']]  → ACCEPT
    • sim(oil, medicine) = +0.1852  [medicine: ['useful_for_healing', 'neutral_to_fire']]  → ACCEPT
    • sim(oil, water) = +0.1888  [water: ['liquid', 'extinguishes_fire', 'wets_things']]  → ACCEPT
    • sim(oil, wood) = +0.3868  [wood: ['solid', 'feeds_fire', 'burnable']]  → ACCEPT
    ✓ best analog: `wood` (sim +0.3868)
    ⓘ best analog `wood` has no rules to project from in store
  → crystallizes nothing
- **v3 HDC (role-weighted, fire-context):**
    • active roles for this scenario: ['fire_relevant', 'temperature_relevant']
    • `oil` properties (active-role-filtered): ['feeds_fire', 'burnable', 'highly_flammable']
    • sim(oil, food) = +0.0016  [role-filtered food: ['neutral_to_fire']]  → REJECT
    • sim(oil, ice) = -0.0006  [role-filtered ice: ['extinguishes_fire_after_melting', 'cold_to_touch']]  → REJECT
    • sim(oil, medicine) = +0.0016  [role-filtered medicine: ['neutral_to_fire']]  → REJECT
    • sim(oil, water) = +0.0026  [role-filtered water: ['extinguishes_fire']]  → REJECT
    • sim(oil, wood) = +0.5152  [role-filtered wood: ['feeds_fire', 'burnable']]  → ACCEPT
    ✓ best analog under role weighting: `wood` (sim +0.5152)
    ⓘ best analog `wood` has no rules to project from in store
  → crystallizes nothing
- **v4 HDC (role-weighted + TOKEN-level projection):**
    • active roles: ['fire_relevant', 'temperature_relevant']
    • `oil` (role-filtered): ['feeds_fire', 'burnable', 'highly_flammable']
    • sim(oil, food) = +0.0016  → reject
    • sim(oil, ice) = -0.0006  → reject
    • sim(oil, medicine) = +0.0016  → reject
    • sim(oil, water) = +0.0026  → reject
    • sim(oil, wood) = +0.5152  → ACCEPT
    ✓ analog: `wood` (sim +0.5152)
    ✓ P3a: relevance 0.75 ≥ 0.5; projecting
    ✗ P-wood-leaving: relevance 0.38 < 0.5 (scenario overlap: ['at', 'door', 'hall']); FILTERED
    ✗ C3: relevance 0.00 < 0.5 (scenario overlap: []); FILTERED
    ⓘ analog `wood` has no rules referencing it as a token
  → crystallizes nothing
- **v5 compression analog (PPM-style frequency, no HDC):**
    plain prediction:        [('wood', 2), ('water', 1)]
    role-weighted prediction: [('wood', 2)]
    → compression picks: `wood`  (compare with HDC v3/v4 above)

---

## Final rule store snapshot

- final store size: 31
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
    - R1 (conf=1.0, used=2)
    - R2 (conf=1.0, used=11)
    - R3 (conf=1.0, used=8)
    - R4 (conf=1.0, used=5)
    - R5 (conf=1.0, used=1)
    - C1 (conf=1.0, used=11)
    - C2 (conf=1.0, used=11)
    - C3 (conf=1.0, used=1)
    - C4 (conf=1.0, used=11)
    - C5 (conf=1.0, used=0)
  - **crystallized** (6):
    - P-admitted-with-water~ice (conf=0.4, used=0)
    - R3~ice (conf=0.4, used=5)
    - P-admitted-with-water~food (conf=0.4, used=0)
    - R3~food (conf=0.4, used=2)
    - P-admitted-with-water~medicine (conf=0.4, used=0)
    - R3~medicine (conf=0.4, used=1)
  - **crystallized_v4** (1):
    - P3a~oil_v4 (conf=0.4, used=0)