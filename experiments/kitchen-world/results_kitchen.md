# Results — kitchen-world (third transfer test)

Run: 2026-04-06T17:10:39.603642Z
Engine: rule-world machinery, unmodified, on a third unrelated domain.
Authored rules: 16 | actions: 9 | substances: 9

---

## Scenario 1 (covered: oil pan unattended)

**Description:** You are cooking. The burner is on with oil in the pan. You stepped away to answer the door.

### Parser

- facts: ['burner_on', 'cook_at_stove', 'cook_unattentive', 'oil_in_pan', 'oil_near_flame']
- goal:  ['fire_risk_high_resolved']

### Retriever

- store size:    16
- context tags:  ['cook_state', 'oil_present', 'stove_active']
- domains:       ['cook_state', 'physical', 'stove']
- active window: 16 rules → ['P-oil-near-flame', 'P-burner-flame', 'R1', 'P-water-on-fire', 'P-water-grease-fire', 'P-raw-meat-contamination', 'P-knife-edge', 'P-vegetable-knife', 'R2', 'R3', 'R4', 'R5', 'C1', 'C2', 'C3', 'C4']

### Engine (single-action)

- initial state after chain: ['burner_on', 'cook_at_stove', 'cook_unattentive', 'fire_risk_high', 'flame_on', 'oil_in_pan', 'oil_near_flame']

- evaluations (best 5):
  - **turn_burner_off** (score 160, goal_met=False)
  - **move_oil_away_from_flame** (score 160, goal_met=False)

- **CHOSEN:** `turn_burner_off` (score 160)

- gap: True
  - goal predicates not all satisfied

### Planner (depth 3)

- nodes: 13
- best sequence: ['turn_burner_off']
- best score:    160

---

## Scenario 2 (covered: raw chicken on counter)

**Description:** You are in the kitchen. Raw chicken is sitting on the counter from your shopping bag.

### Parser

- facts: ['cook_at_stove', 'raw_meat_on_counter', 'raw_meat_present']
- goal:  ['raw_meat_in_fridge']

### Retriever

- store size:    16
- context tags:  ['cook_state', 'food_safety_concern', 'raw_food_present']
- domains:       ['cook_state', 'food_handling', 'physical']
- active window: 16 rules → ['R2', 'P-raw-meat-contamination', 'P-burner-flame', 'P-oil-near-flame', 'P-water-on-fire', 'P-water-grease-fire', 'P-knife-edge', 'P-vegetable-knife', 'R1', 'R3', 'R4', 'R5', 'C1', 'C2', 'C3', 'C4']

### Engine (single-action)

- initial state after chain: ['cook_at_stove', 'counter_contaminated', 'raw_meat_on_counter', 'raw_meat_present']

- evaluations (best 5):
  - **place_raw_meat_in_fridge** (score 172, goal_met=True)
  - **do_nothing** (score 93, goal_met=False)
    - violated: [('R2', 'requires raw_meat_in_fridge (absent)')]

- **CHOSEN:** `place_raw_meat_in_fridge` (score 172)

- gap: False

### Planner (depth 3)

- nodes: 10
- best sequence: ['place_raw_meat_in_fridge']
- best score:    172

---

## Scenario 3 (covered: knife at edge)

**Description:** You are cooking. There is a knife on the edge of the counter.

### Parser

- facts: ['cook_at_stove', 'knife_at_edge', 'knife_present']
- goal:  ['knife_stored_safely']

### Retriever

- store size:    16
- context tags:  ['cook_state', 'knife_present']
- domains:       ['cook_state', 'physical', 'tool_handling']
- active window: 16 rules → ['R3', 'P-knife-edge', 'P-vegetable-knife', 'P-burner-flame', 'P-oil-near-flame', 'P-water-on-fire', 'P-water-grease-fire', 'P-raw-meat-contamination', 'R1', 'R2', 'R4', 'R5', 'C1', 'C2', 'C3', 'C4']

### Engine (single-action)

- initial state after chain: ['cook_at_stove', 'fall_hazard', 'knife_at_edge', 'knife_present']

- evaluations (best 5):
  - **store_knife_safely** (score 169, goal_met=True)
  - **do_nothing** (score 96, goal_met=False)
    - violated: [('R3', 'requires knife_stored_safely (absent)')]

- **CHOSEN:** `store_knife_safely` (score 169)

- gap: False

### Planner (depth 3)

- nodes: 10
- best sequence: ['store_knife_safely']
- best score:    169

---

## Scenario 4 (covered: grease fire)

**Description:** You are cooking. The pan caught fire — a small grease fire is in the pan.

### Parser

- facts: ['cook_at_stove', 'fire_in_kitchen', 'grease_fire']
- goal:  ['fire_extinguished']

### Retriever

- store size:    16
- context tags:  ['cook_state', 'fire_present']
- domains:       ['cook_state', 'fire_response', 'physical']
- active window: 16 rules → ['R5', 'P-water-on-fire', 'P-water-grease-fire', 'P-burner-flame', 'P-oil-near-flame', 'P-raw-meat-contamination', 'P-knife-edge', 'P-vegetable-knife', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4']

### Engine (single-action)

- initial state after chain: ['cook_at_stove', 'fire_in_kitchen', 'grease_fire']

- evaluations (best 5):
  - **pour_water_on_fire** (score 105, goal_met=True)
    - VISCERAL VIOLATIONS: [('C3', 'forbids fire_spread (present)')]
    - violated: [('C3', 'forbids fire_spread (present)')]
  - **cover_grease_fire_with_lid** (score 80, goal_met=False)
    - VISCERAL VIOLATIONS: [('R5', 'requires fire_extinguished (absent)')]
    - violated: [('R5', 'requires fire_extinguished (absent)')]
  - **do_nothing** (score 80, goal_met=False)
    - VISCERAL VIOLATIONS: [('R5', 'requires fire_extinguished (absent)')]
    - violated: [('R5', 'requires fire_extinguished (absent)')]

- **CHOSEN:** `pour_water_on_fire` (score 105)

- gap: True
  - every action violates a visceral constraint
  - unmet: C3 forbids fire_spread (present)

### Planner (depth 3)

- nodes: 1
- best sequence: []
- best score:    -1000000000

---

## Scenario 5 (covered: chopping vegetables for dinner)

**Description:** You are in the kitchen. Carrots are on the counter and the knife is beside them. Dinner is in twenty minutes and the guests are hungry.

### Parser

- facts: ['cook_at_stove', 'hungry_diner', 'knife_present', 'vegetable_present']
- goal:  ['vegetable_chopped']

### Retriever

- store size:    16
- context tags:  ['cook_state', 'food_safety_concern', 'knife_present', 'mealtime', 'vegetable_present']
- domains:       ['cook_state', 'food_handling', 'food_prep', 'physical', 'tool_handling']
- active window: 16 rules → ['R4', 'P-vegetable-knife', 'P-knife-edge', 'R3', 'P-raw-meat-contamination', 'R2', 'P-burner-flame', 'P-oil-near-flame', 'P-water-on-fire', 'P-water-grease-fire', 'R1', 'R5', 'C1', 'C2', 'C3', 'C4']

### Engine (single-action)

- initial state after chain: ['cook_at_stove', 'hungry_diner', 'knife_present', 'vegetable_present']

- evaluations (best 5):
  - **chop_vegetable** (score 157, goal_met=True)
  - **do_nothing** (score 108, goal_met=False)
    - violated: [('R4', 'requires vegetable_chopped (absent)')]

- **CHOSEN:** `chop_vegetable` (score 157)

- gap: False

### Planner (depth 3)

- nodes: 15
- best sequence: ['chop_vegetable']
- best score:    157

---

## Scenario 6 (covered: water spilled on stovetop)

**Description:** You are cooking. There is spilled water on the stovetop next to the burner.

### Parser

- facts: ['cook_at_stove', 'water_spilled']
- goal:  ['counter_dry']

### Retriever

- store size:    16
- context tags:  ['cook_state', 'water_present']
- domains:       ['cook_state', 'physical', 'stove']
- active window: 16 rules → ['P-burner-flame', 'P-oil-near-flame', 'R1', 'P-water-on-fire', 'P-water-grease-fire', 'P-raw-meat-contamination', 'P-knife-edge', 'P-vegetable-knife', 'R2', 'R3', 'R4', 'R5', 'C1', 'C2', 'C3', 'C4']

### Engine (single-action)

- initial state after chain: ['cook_at_stove', 'water_spilled']

- evaluations (best 5):
  - **wipe_up_water** (score 120, goal_met=False)
  - **do_nothing** (score 120, goal_met=False)

- **CHOSEN:** `wipe_up_water` (score 120)

- gap: True
  - goal predicates not all satisfied

### Planner (depth 3)

- nodes: 10
- best sequence: []
- best score:    120

---

## Scenario 7 (novel: butter melting in pan, walked away)

**Description:** You are cooking. The burner is on with a stick of butter melting in the pan. You walked away to answer the door.

### Parser

- facts: ['burner_on', 'butter_in_pan', 'butter_near_flame', 'cook_at_stove', 'cook_unattentive']
- goal:  ['fire_risk_high_resolved']

### v4 PRODUCTION WRITE

- substances in play: ['butter']
- v4 targets:         ['butter']
- active roles:       ['fire_relevant']

#### target: `butter`
    • target_substance override: `butter`
    • active roles: ['fire_relevant']
    • `butter` (role-filtered): ['flammable_when_hot']
    • sim(butter, oil) = +1.0000  → ACCEPT
    • sim(butter, water) = +0.0060  → reject
    ✓ analog: `oil` (sim +1.0000)
    ✓ P-oil-near-flame: relevance 0.50 ≥ 0.2; projecting
    • would crystallize P-oil-near-flame~butter_v4 from P-oil-near-flame:
        antecedents:        ['butter_near_flame', 'flame_on']
        derives:            ['fire_risk_high']
  ✓ wrote P-oil-near-flame~butter_v4
  analog peer for action synthesis: `oil` (sim +1.0000)
  • synthesized action `move_butter_away_from_flame` from `move_oil_away_from_flame`:
      preconditions: ['butter_near_flame']
      add:           ['butter_safely_placed']
      remove:        ['butter_near_flame']
  ✓ added action `move_butter_away_from_flame` to runtime library

### Retriever

- store size:    17
- context tags:  ['butter_present', 'cook_state', 'stove_active']
- domains:       ['cook_state', 'physical', 'stove']
- active window: 17 rules → ['P-oil-near-flame~butter_v4', 'P-burner-flame', 'P-oil-near-flame', 'R1', 'P-water-on-fire', 'P-water-grease-fire', 'P-raw-meat-contamination', 'P-knife-edge', 'P-vegetable-knife', 'R2', 'R3', 'R4', 'R5', 'C1', 'C2', 'C3', 'C4']

### Engine (single-action)

- initial state after chain: ['burner_on', 'butter_in_pan', 'butter_near_flame', 'cook_at_stove', 'cook_unattentive', 'fire_risk_high', 'flame_on']

- evaluations (best 5):
  - **turn_burner_off** (score 160, goal_met=False)
  - **move_butter_away_from_flame** (score 160, goal_met=False)

- **CHOSEN:** `turn_burner_off` (score 160)

- gap: True
  - goal predicates not all satisfied

### Planner (depth 3)

- nodes: 13
- best sequence: ['turn_burner_off']
- best score:    160

### Compression analog baseline (v5)

- target substance:        `butter`
- plain prediction:        [('oil', 2)]
- role-weighted prediction: [('oil', 1)]

---

## Scenario 8 (novel: cracked raw eggs on counter)

**Description:** You are in the kitchen. You cracked an egg and the raw eggs are on the counter from breakfast prep.

### Parser

- facts: ['cook_at_stove', 'raw_egg_on_counter', 'raw_egg_present']
- goal:  ['raw_egg_in_fridge']

### v4 PRODUCTION WRITE

- substances in play: ['raw_egg']
- v4 targets:         ['raw_egg']
- active roles:       ['food_safety']

#### target: `raw_egg`
    • target_substance override: `raw_egg`
    • active roles: ['food_safety']
    • `raw_egg` (role-filtered): ['perishable', 'contamination_risk', 'needs_cooking']
    • sim(raw_egg, peas) = +0.2620  → ACCEPT
    • sim(raw_egg, raw_meat) = +1.0000  → ACCEPT
    • sim(raw_egg, vegetable) = +0.2540  → ACCEPT
    ✓ analog: `raw_meat` (sim +1.0000)
    ⓘ analog `raw_meat` has no rules referencing it as a token
  analog peer for action synthesis: `raw_meat` (sim +1.0000)

### Retriever

- store size:    17
- context tags:  ['cook_state', 'food_safety_concern', 'raw_food_present']
- domains:       ['cook_state', 'food_handling', 'physical']
- active window: 17 rules → ['P-raw-meat-contamination', 'R2', 'P-burner-flame', 'P-oil-near-flame', 'P-water-on-fire', 'P-water-grease-fire', 'P-knife-edge', 'P-vegetable-knife', 'R1', 'R3', 'R4', 'R5', 'C1', 'C2', 'C3', 'C4', 'P-oil-near-flame~butter_v4']

### Engine (single-action)

- initial state after chain: ['cook_at_stove', 'raw_egg_on_counter', 'raw_egg_present']

- evaluations (best 5):
  - **do_nothing** (score 120, goal_met=False)

- **CHOSEN:** `do_nothing` (score 120)

- gap: True
  - goal predicates not all satisfied

### Planner (depth 3)

- nodes: 4
- best sequence: []
- best score:    120

### Compression analog baseline (v5)

- target substance:        `raw_egg`
- plain prediction:        [('raw_meat', 4), ('vegetable', 2), ('peas', 2), ('knife', 1), ('salt', 1)]
- role-weighted prediction: [('raw_meat', 3), ('vegetable', 1), ('peas', 1)]

---

## Scenario 9 (novel: frozen peas out for dinner)

**Description:** You are in the kitchen. A bag of frozen peas is on the counter and the knife is beside them. Dinner is in twenty minutes and the guests are hungry.

### Parser

- facts: ['cook_at_stove', 'hungry_diner', 'knife_present', 'peas_present']
- goal:  ['peas_chopped']

### v4 PRODUCTION WRITE

- substances in play: ['knife', 'peas']
- v4 targets:         ['knife', 'peas']
- active roles:       ['food_safety', 'handling']

#### target: `knife`
    • target_substance override: `knife`
    • active roles: ['food_safety', 'handling']
    • `knife` (role-filtered): ['sharp']
    • sim(knife, oil) = +0.0056  → reject
    • sim(knife, peas) = -0.0030  → reject
    • sim(knife, raw_egg) = -0.0040  → reject
    • sim(knife, raw_meat) = -0.0020  → reject
    • sim(knife, vegetable) = +0.0024  → reject
    • sim(knife, water) = -0.0164  → reject
    ✗ no candidate passed threshold after role filtering

#### target: `peas`
    • target_substance override: `peas`
    • active roles: ['food_safety', 'handling']
    • `peas` (role-filtered): ['perishable', 'edible_raw', 'small']
    • sim(peas, knife) = -0.0030  → reject
    • sim(peas, oil) = +0.0142  → reject
    • sim(peas, raw_egg) = +0.1846  → ACCEPT
    • sim(peas, raw_meat) = +0.2498  → ACCEPT
    • sim(peas, vegetable) = +0.4874  → ACCEPT
    • sim(peas, water) = -0.0150  → reject
    ✓ analog: `vegetable` (sim +0.4874)
    ✓ P-vegetable-knife: relevance 0.33 ≥ 0.2; projecting
    • would crystallize P-vegetable-knife~peas_v4 from P-vegetable-knife:
        antecedents:        ['peas_under_knife']
        derives:            ['peas_chopped']
    ✓ R4: relevance 0.75 ≥ 0.2; projecting
    • would crystallize R4~peas_v4 from R4:
        antecedents:        ['peas_present', 'hungry_diner']
        requires_in_result: ['peas_chopped']
  ✓ wrote P-vegetable-knife~peas_v4
  ✓ wrote R4~peas_v4
  analog peer for action synthesis: `vegetable` (sim +0.4874)
  • synthesized action `chop_peas` from `chop_vegetable`:
      preconditions: ['peas_present', 'knife_present']
      add:           ['peas_under_knife', 'peas_chopped']
      remove:        []
  ✓ added action `chop_peas` to runtime library

### Retriever

- store size:    19
- context tags:  ['cook_state', 'food_safety_concern', 'knife_present', 'mealtime', 'vegetable_present']
- domains:       ['cook_state', 'food_handling', 'food_prep', 'physical', 'tool_handling']
- active window: 19 rules → ['R4~peas_v4', 'R4', 'P-vegetable-knife~peas_v4', 'P-vegetable-knife', 'P-knife-edge', 'R3', 'P-raw-meat-contamination', 'R2', 'P-burner-flame', 'P-oil-near-flame', 'P-water-on-fire', 'P-water-grease-fire', 'R1', 'R5', 'C1', 'C2', 'C3', 'C4', 'P-oil-near-flame~butter_v4']

### Engine (single-action)

- initial state after chain: ['cook_at_stove', 'hungry_diner', 'knife_present', 'peas_present']

- evaluations (best 5):
  - **chop_peas** (score 157, goal_met=True)
  - **do_nothing** (score 108, goal_met=False)
    - violated: [('R4~peas_v4', 'requires peas_chopped (absent)')]

- **CHOSEN:** `chop_peas` (score 157)

- gap: False

### Planner (depth 3)

- nodes: 15
- best sequence: ['do_nothing', 'do_nothing', 'chop_peas']
- best score:    157

### Compression analog baseline (v5)

- target substance:        `knife`
- plain prediction:        [('raw_meat', 1), ('vegetable', 1), ('salt', 1), ('raw_egg', 1), ('peas', 1)]
- role-weighted prediction: []

### Compression analog baseline (v5)

- target substance:        `peas`
- plain prediction:        [('vegetable', 3), ('raw_meat', 2), ('raw_egg', 2), ('knife', 1), ('salt', 1)]
- role-weighted prediction: [('vegetable', 2), ('raw_meat', 1), ('raw_egg', 1)]

---
