# Results (symbolic forward-chaining engine)

Run: 2026-04-06T11:55:57.947766Z
Engine: pure forward chaining over structured rule tuples (no LLM, no matmul)
Rules loaded: 24 | Actions in library: 13

No scenario-specific code anywhere in engine.py, world_structured.py, or this file.
Every answer is derived at runtime from the rule set + action library.

---

## Scenario 1 (covered)

**Initial facts:** ['hearth_burning', 'hearth_burning_low', 'self_at_hearth', 'self_in_hall', 'wood_available']

**Goal predicates:** ['hearth_fed']

**Initial forward-chain derivations:**

- P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

**State after initial chain:** ['hall_has_attentive_tender', 'hearth_burning', 'hearth_burning_low', 'self_at_hearth', 'self_in_hall', 'wood_available']

**All action evaluations (best first):**

  - **add_wood_to_hearth** (score 193, goal_met=True)
    - fulfilled: [('R1', 'requires hearth_fed'), ('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P3a: ['wood_in_hearth', 'hearth_burning'] ⇒ derives ['hearth_fed']
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

**CHOSEN ACTION:** `add_wood_to_hearth`

**Triggered rules at decision time:** ['C1', 'C2', 'C4', 'R1', 'R2']

**Score:** 193

**Gap encountered:** no

---

## Scenario 2 (covered)

**Initial facts:** ['hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_water']

**Goal predicates:** ['stranger_situation_resolved']

**Initial forward-chain derivations:**

- P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

**State after initial chain:** ['hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_carries_water']

**All action evaluations (best first):**

  - **refuse_stranger** (score 177, goal_met=True)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('R3', 'forbids stranger_admitted_with_water'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **admit_stranger_to_hearth** (score 129, goal_met=True)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - violated: [('R3', 'forbids stranger_admitted_with_water (present)')]
    - post-action derivations:
      - P-shelter: ['stranger_near_hearth'] ⇒ derives ['stranger_warmed']
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
      - P-admitted-with-water: ['stranger_in_hall', 'stranger_carries_water'] ⇒ derives ['stranger_admitted_with_water']
  - **admit_stranger_far_from_hearth** (score 129, goal_met=True)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - violated: [('R3', 'forbids stranger_admitted_with_water (present)')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
      - P-admitted-with-water: ['stranger_in_hall', 'stranger_carries_water'] ⇒ derives ['stranger_admitted_with_water']
  - **stay_silent_at_hearth** (score 152, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('R3', 'forbids stranger_admitted_with_water'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **do_nothing** (score 152, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('R3', 'forbids stranger_admitted_with_water'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

**CHOSEN ACTION:** `refuse_stranger`

**Triggered rules at decision time:** ['C1', 'C2', 'C4', 'R2', 'R3']

**Score:** 177

**Gap encountered:** no

---

## Scenario 3 (covered)

**Initial facts:** ['asked_by_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'wood_supply_insufficient']

**Goal predicates:** ['tender_informed_truthfully']

**Initial forward-chain derivations:**

- P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

**State after initial chain:** ['asked_by_tender', 'hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'wood_supply_insufficient']

**All action evaluations (best first):**

  - **tell_truth_to_tender** (score 141, goal_met=True)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('R5', 'requires tender_informed_truthfully'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - violated: [('C3', 'requires wood_replenishment_initiated (absent)')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **initiate_wood_replenishment_plan** (score 140, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C3', 'requires wood_replenishment_initiated'), ('C4', 'forbids being_harmed')]
    - violated: [('R5', 'requires tender_informed_truthfully (absent)')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **lie_to_tender** (score 92, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - violated: [('R5', 'requires tender_informed_truthfully (absent)'), ('C3', 'requires wood_replenishment_initiated (absent)')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **stay_silent_at_hearth** (score 92, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - violated: [('R5', 'requires tender_informed_truthfully (absent)'), ('C3', 'requires wood_replenishment_initiated (absent)')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **do_nothing** (score 92, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - violated: [('R5', 'requires tender_informed_truthfully (absent)'), ('C3', 'requires wood_replenishment_initiated (absent)')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **leave_hall_to_gather_wood** (score 86, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C3', 'requires wood_replenishment_initiated'), ('C4', 'forbids being_harmed')]
    - violated: [('R5', 'requires tender_informed_truthfully (absent)'), ('C2', 'requires hall_has_attentive_tender (absent)')]

**CHOSEN ACTION:** `tell_truth_to_tender`

**Triggered rules at decision time:** ['C1', 'C2', 'C3', 'C4', 'R2', 'R5']

**Score:** 141

**Gap encountered:** yes

**Gap reasons (honest report — composition failures):**

- unmet: C3 requires wood_replenishment_initiated (absent)

**How the engine resolved (or failed to resolve) the gap:**

The chosen action above is whatever scored highest after disqualifying
actions that would violate visceral constraints. If unmet obligations
remain, the engine has not 'resolved' the gap — it has revealed exactly
which predicates pure forward chaining cannot bridge.

---

## Scenario 4 (gap: wet stranger)

**Initial facts:** ['hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_cold', 'stranger_wet']

**Goal predicates:** ['stranger_situation_resolved']

**Initial forward-chain derivations:**

- P-wet: ['stranger_wet'] ⇒ derives ['water_on_stranger']
- P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

**State after initial chain:** ['hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'stranger_at_door', 'stranger_cold', 'stranger_wet', 'water_on_stranger']

**All action evaluations (best first):**

  - **dry_stranger_then_admit_to_hearth** (score 191, goal_met=True)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('R3', 'forbids stranger_admitted_with_water'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed'), ('R4', 'requires stranger_warmed')]
    - post-action derivations:
      - P-shelter: ['stranger_near_hearth'] ⇒ derives ['stranger_warmed']
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **refuse_stranger** (score 177, goal_met=True)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('R3', 'forbids stranger_admitted_with_water'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P-wet: ['stranger_wet'] ⇒ derives ['water_on_stranger']
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **admit_stranger_far_from_hearth** (score 163, goal_met=True)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('R3', 'forbids stranger_admitted_with_water'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - violated: [('R4', 'requires stranger_warmed (absent)')]
    - post-action derivations:
      - P-wet: ['stranger_wet'] ⇒ derives ['water_on_stranger']
      - P-water-in-hall: ['water_on_stranger', 'stranger_in_hall'] ⇒ derives ['water_in_hall']
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **stay_silent_at_hearth** (score 152, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('R3', 'forbids stranger_admitted_with_water'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P-wet: ['stranger_wet'] ⇒ derives ['water_on_stranger']
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **do_nothing** (score 152, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('R3', 'forbids stranger_admitted_with_water'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P-wet: ['stranger_wet'] ⇒ derives ['water_on_stranger']
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']

**CHOSEN ACTION:** `dry_stranger_then_admit_to_hearth`

**Triggered rules at decision time:** ['C1', 'C2', 'C4', 'R2', 'R3', 'R4']

**Score:** 191

**Gap encountered:** no

---

## Scenario 5 (gap: child Tender taking Wood)

**Initial facts:** ['child_tender_at_door', 'child_tender_in_hall', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'wood_held_by_child']

**Goal predicates:** ['wood_recovered']

**Initial forward-chain derivations:**

- P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
- P-wood-leaving: ['wood_held_by_child', 'child_tender_at_door'] ⇒ derives ['wood_leaving_hall']

**State after initial chain:** ['child_tender_at_door', 'child_tender_in_hall', 'hall_has_attentive_tender', 'hearth_burning', 'self_at_hearth', 'self_in_hall', 'wood_held_by_child', 'wood_leaving_hall']

**All action evaluations (best first):**

  - **call_out_to_child_from_hearth** (score 153, goal_met=True)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
  - **chase_child_to_door** (score 99, goal_met=True)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C4', 'forbids being_harmed')]
    - violated: [('C2', 'requires hall_has_attentive_tender (absent)')]
  - **stay_silent_at_hearth** (score 128, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
      - P-wood-leaving: ['wood_held_by_child', 'child_tender_at_door'] ⇒ derives ['wood_leaving_hall']
  - **do_nothing** (score 128, goal_met=False)
    - fulfilled: [('R2', 'forbids water_near_hearth'), ('C1', 'forbids hearth_extinguished'), ('C2', 'requires hall_has_attentive_tender'), ('C4', 'forbids being_harmed')]
    - post-action derivations:
      - P-attendance: ['self_at_hearth'] ⇒ derives ['hall_has_attentive_tender']
      - P-wood-leaving: ['wood_held_by_child', 'child_tender_at_door'] ⇒ derives ['wood_leaving_hall']

**CHOSEN ACTION:** `call_out_to_child_from_hearth`

**Triggered rules at decision time:** ['C1', 'C2', 'C4', 'R2']

**Score:** 153

**Gap encountered:** no

---
