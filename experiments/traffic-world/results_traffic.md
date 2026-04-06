# Results — traffic-world (architecture transfer test)

Run: 2026-04-06T19:31:37.339197Z
Engine: rule-world machinery, unmodified, on a fresh domain.
Authored rules: 14 | actions: 11 | substances: 9

---

## Scenario 1 (covered) — Red light

**Description:** You are driving and approaching an intersection. The light ahead is red.

### Parser

- facts: ['red_light_ahead', 'self_at_intersection', 'self_in_left_lane', 'self_in_motion']
- goal:  ['intersection_safe']

### Retriever

- store size:    14
- context tags:  ['driver_present', 'intersection_present', 'must_stop', 'vehicle_in_motion']
- domains:       ['physical', 'traffic_signals', 'vehicle_control']
- active window: 14 rules → ['R1', 'P-stopped-safe', 'P-attendance-driving', 'C3', 'R4', 'C1', 'P-pulled-over', 'R2', 'R3', 'R5', 'R6', 'R7', 'C2', 'C4']

### Engine (single-action)

- initial state after chain: ['red_light_ahead', 'self_actively_driving', 'self_at_intersection', 'self_in_left_lane', 'self_in_motion']

- evaluations (best 5):
  - **stop_at_intersection** (score 166, goal_met=True)
  - **pull_over** (score 141, goal_met=False)
  - **signal_left** (score 141, goal_met=False)
  - **signal_right** (score 141, goal_met=False)
  - **maintain_speed** (score 141, goal_met=False)

- **CHOSEN:** `stop_at_intersection` (score 166)

- gap: False

### Planner (depth 3)

- nodes: 211
- best sequence: ['stop_at_intersection']
- best score:    166

---

## Scenario 2 (covered) — Pedestrian in crosswalk

**Description:** You are driving toward a crosswalk. A pedestrian is in the crosswalk, crossing.

### Parser

- facts: ['pedestrian_in_crosswalk', 'self_in_left_lane', 'self_in_motion']
- goal:  ['pedestrian_safe']

### Retriever

- store size:    14
- context tags:  ['driver_present', 'pedestrian_present', 'vehicle_in_motion', 'vulnerable_present']
- domains:       ['pedestrian_safety', 'physical', 'vehicle_control']
- active window: 14 rules → ['R2', 'P-attendance-driving', 'C3', 'R4', 'C1', 'C2', 'P-pulled-over', 'R6', 'P-stopped-safe', 'R1', 'R3', 'R5', 'R7', 'C4']

### Engine (single-action)

- initial state after chain: ['pedestrian_in_crosswalk', 'self_actively_driving', 'self_in_left_lane', 'self_in_motion']

- evaluations (best 5):
  - **yield_to_pedestrian** (score 166, goal_met=True)

- **CHOSEN:** `yield_to_pedestrian` (score 166)

- gap: False

### Planner (depth 3)

- nodes: 16
- best sequence: ['yield_to_pedestrian']
- best score:    166

---

## Scenario 3 (covered) — Ambulance behind

**Description:** You are driving in the left lane. An ambulance is approaching from behind with sirens.

### Parser

- facts: ['ambulance_behind', 'self_in_left_lane', 'self_in_motion']
- goal:  ['emergency_path_clear']

### Retriever

- store size:    14
- context tags:  ['driver_present', 'emergency_present', 'vehicle_in_motion']
- domains:       ['emergency_yielding', 'physical', 'vehicle_control']
- active window: 14 rules → ['R3', 'P-attendance-driving', 'P-pulled-over', 'C3', 'R4', 'C1', 'P-stopped-safe', 'R1', 'R2', 'R5', 'R6', 'R7', 'C2', 'C4']

### Engine (single-action)

- initial state after chain: ['ambulance_behind', 'self_actively_driving', 'self_in_left_lane', 'self_in_motion']

- evaluations (best 5):
  - **pull_over** (score 153, goal_met=True)
  - **signal_left** (score 74, goal_met=False)
    - violated: [('R3', 'requires emergency_path_clear (absent)')]
  - **signal_right** (score 74, goal_met=False)
    - violated: [('R3', 'requires emergency_path_clear (absent)')]
  - **maintain_speed** (score 74, goal_met=False)
    - violated: [('R3', 'requires emergency_path_clear (absent)')]
  - **do_nothing** (score 74, goal_met=False)
    - violated: [('R3', 'requires emergency_path_clear (absent)')]

- **CHOSEN:** `pull_over` (score 153)

- gap: False

### Planner (depth 3)

- nodes: 160
- best sequence: ['pull_over']
- best score:    153

---

## Scenario 4 (covered) — Car too close ahead

**Description:** You are driving and the car ahead is too close, you are tailgating.

### Parser

- facts: ['car_close_ahead', 'self_in_left_lane', 'self_in_motion']
- goal:  ['safe_following_car']

### Retriever

- store size:    14
- context tags:  ['driver_present', 'vehicle_ahead', 'vehicle_in_motion']
- domains:       ['following', 'physical', 'vehicle_control']
- active window: 14 rules → ['R5', 'P-attendance-driving', 'C3', 'R4', 'C1', 'P-pulled-over', 'P-stopped-safe', 'R1', 'R2', 'R3', 'R6', 'R7', 'C2', 'C4']

### Engine (single-action)

- initial state after chain: ['car_close_ahead', 'self_actively_driving', 'self_in_left_lane', 'self_in_motion']

- evaluations (best 5):
  - **slow_down_for_car** (score 150, goal_met=True)
  - **pull_over** (score 77, goal_met=False)
    - violated: [('R5', 'requires safe_following_car (absent)')]
  - **signal_left** (score 77, goal_met=False)
    - violated: [('R5', 'requires safe_following_car (absent)')]
  - **signal_right** (score 77, goal_met=False)
    - violated: [('R5', 'requires safe_following_car (absent)')]
  - **maintain_speed** (score 77, goal_met=False)
    - violated: [('R5', 'requires safe_following_car (absent)')]

- **CHOSEN:** `slow_down_for_car` (score 150)

- gap: False

### Planner (depth 3)

- nodes: 250
- best sequence: ['slow_down_for_car']
- best score:    150

---

## Scenario 5 (covered) — Bicycle ahead

**Description:** You are driving and there is a bicycle ahead in your lane.

### Parser

- facts: ['bicycle_ahead', 'self_in_left_lane', 'self_in_motion']
- goal:  ['safe_distance_from_bicycle']

### Retriever

- store size:    14
- context tags:  ['bicycle_present', 'driver_present', 'vehicle_in_motion', 'vulnerable_present']
- domains:       ['pedestrian_safety', 'physical', 'shared_road', 'vehicle_control']
- active window: 14 rules → ['R6', 'P-attendance-driving', 'R2', 'C3', 'R4', 'R7', 'C1', 'C2', 'P-pulled-over', 'P-stopped-safe', 'R1', 'R3', 'R5', 'C4']

### Engine (single-action)

- initial state after chain: ['bicycle_ahead', 'self_actively_driving', 'self_in_left_lane', 'self_in_motion']

- evaluations (best 5):
  - **maintain_safe_distance_from_bicycle** (score 140, goal_met=True)
  - **pull_over** (score 87, goal_met=False)
    - violated: [('R6', 'requires safe_distance_from_bicycle (absent)')]
  - **signal_left** (score 87, goal_met=False)
    - violated: [('R6', 'requires safe_distance_from_bicycle (absent)')]
  - **signal_right** (score 87, goal_met=False)
    - violated: [('R6', 'requires safe_distance_from_bicycle (absent)')]
  - **maintain_speed** (score 87, goal_met=False)
    - violated: [('R6', 'requires safe_distance_from_bicycle (absent)')]

- **CHOSEN:** `maintain_safe_distance_from_bicycle` (score 140)

- gap: False

### Planner (depth 3)

- nodes: 263
- best sequence: ['pull_over', 'maintain_safe_distance_from_bicycle']
- best score:    140

---

## Scenario 6 (novel substance) — Horse-drawn carriage

**Description:** You are driving and a horse-drawn carriage is ahead of you in your lane.

### Parser

- facts: ['horse_carriage_ahead', 'horse_carriage_close_ahead', 'self_in_left_lane', 'self_in_motion']
- goal:  ['safe_distance_from_horse_carriage']

### v4 PRODUCTION WRITE

- substances in play: ['horse_carriage']
- v4 targets:         ['horse_carriage']
- active roles:       ['mass_relevant', 'priority_relevant', 'speed_relevant', 'vulnerability_relevant']

#### target: `horse_carriage`
    • target_substance override: `horse_carriage`
    • active roles: ['mass_relevant', 'priority_relevant', 'speed_relevant', 'vulnerability_relevant']
    • `horse_carriage` (role-filtered): ['slow', 'has_mass', 'unprotected', 'no_priority']
    • sim(horse_carriage, ambulance) = +0.2826  → ACCEPT
    • sim(horse_carriage, bicycle) = +0.6326  → ACCEPT
    • sim(horse_carriage, bus) = +0.4272  → ACCEPT
    • sim(horse_carriage, car) = +0.4356  → ACCEPT
    • sim(horse_carriage, fire_engine) = +0.1592  → ACCEPT
    • sim(horse_carriage, pedestrian) = +0.6326  → ACCEPT
    • sim(horse_carriage, robotaxi) = +0.4356  → ACCEPT
    • sim(horse_carriage, truck) = +0.2730  → ACCEPT
    ✓ analog: `bicycle` (sim +0.6326)
    ✓ R6: relevance 0.25 ≥ 0.2; projecting
    • would crystallize R6~horse_carriage_v4 from R6:
        antecedents:        ['horse_carriage_ahead']
        requires_in_result: ['safe_distance_from_horse_carriage']
  ✓ wrote R6~horse_carriage_v4
  analog peer for action synthesis: `bicycle` (sim +0.6326)
  • synthesized action `maintain_safe_distance_from_horse_carriage` from `maintain_safe_distance_from_bicycle`:
      preconditions: ['horse_carriage_ahead']
      add:           ['safe_distance_from_horse_carriage']
      remove:        []
  ✓ added action `maintain_safe_distance_from_horse_carriage` to runtime library

### Retriever

- store size:    15
- context tags:  ['driver_present', 'horse_present', 'vehicle_in_motion']
- domains:       ['physical', 'shared_road', 'vehicle_control']
- active window: 15 rules → ['P-attendance-driving', 'R6~horse_carriage_v4', 'C3', 'R4', 'R6', 'R7', 'C1', 'P-pulled-over', 'P-stopped-safe', 'R1', 'R2', 'R3', 'R5', 'C2', 'C4']

### Engine (single-action)

- initial state after chain: ['horse_carriage_ahead', 'horse_carriage_close_ahead', 'self_actively_driving', 'self_in_left_lane', 'self_in_motion']

- evaluations (best 5):
  - **maintain_safe_distance_from_horse_carriage** (score 140, goal_met=True)
  - **pull_over** (score 87, goal_met=False)
    - violated: [('R6~horse_carriage_v4', 'requires safe_distance_from_horse_carriage (absent)')]
  - **signal_left** (score 87, goal_met=False)
    - violated: [('R6~horse_carriage_v4', 'requires safe_distance_from_horse_carriage (absent)')]
  - **signal_right** (score 87, goal_met=False)
    - violated: [('R6~horse_carriage_v4', 'requires safe_distance_from_horse_carriage (absent)')]
  - **maintain_speed** (score 87, goal_met=False)
    - violated: [('R6~horse_carriage_v4', 'requires safe_distance_from_horse_carriage (absent)')]

- **CHOSEN:** `maintain_safe_distance_from_horse_carriage` (score 140)

- gap: False

### Planner (depth 3)

- nodes: 263
- best sequence: ['pull_over', 'signal_left', 'maintain_safe_distance_from_horse_carriage']
- best score:    140

### Compression analog baseline (v5)

- target substance:        `horse_carriage`
- plain prediction:        [('bicycle', 4), ('pedestrian', 3), ('bus', 2), ('car', 2), ('robotaxi', 2), ('ambulance', 1), ('truck', 1)]
- role-weighted prediction: [('bicycle', 3), ('pedestrian', 3), ('bus', 2), ('car', 2), ('robotaxi', 2), ('ambulance', 1), ('truck', 1)]

---

## Scenario 7 (novel substance) — Robotaxi

**Description:** You are driving and a self-driving taxi is ahead of you, slowing down.

### Parser

- facts: ['robotaxi_ahead', 'robotaxi_close_ahead', 'self_in_left_lane', 'self_in_motion']
- goal:  ['safe_following_robotaxi']

### v4 PRODUCTION WRITE

- substances in play: ['robotaxi']
- v4 targets:         ['robotaxi']
- active roles:       ['mass_relevant', 'priority_relevant', 'speed_relevant', 'vulnerability_relevant']

#### target: `robotaxi`
    • target_substance override: `robotaxi`
    • active roles: ['mass_relevant', 'priority_relevant', 'speed_relevant', 'vulnerability_relevant']
    • `robotaxi` (role-filtered): ['fast', 'has_mass', 'protected', 'no_priority']
    • sim(robotaxi, ambulance) = +0.6202  → ACCEPT
    • sim(robotaxi, bicycle) = +0.2966  → ACCEPT
    • sim(robotaxi, bus) = +0.4308  → ACCEPT
    • sim(robotaxi, car) = +1.0000  → ACCEPT
    • sim(robotaxi, fire_engine) = +0.4424  → ACCEPT
    • sim(robotaxi, horse_carriage) = +0.4356  → ACCEPT
    • sim(robotaxi, pedestrian) = +0.2966  → ACCEPT
    • sim(robotaxi, truck) = +0.6198  → ACCEPT
    ✓ analog: `car` (sim +1.0000)
    ✓ R5: relevance 0.50 ≥ 0.2; projecting
    • would crystallize R5~robotaxi_v4 from R5:
        antecedents:        ['robotaxi_close_ahead']
        requires_in_result: ['safe_following_robotaxi']
  ✓ wrote R5~robotaxi_v4
  analog peer for action synthesis: `car` (sim +1.0000)
  • synthesized action `slow_down_for_robotaxi` from `slow_down_for_car`:
      preconditions: ['self_in_motion', 'robotaxi_close_ahead']
      add:           ['safe_following_robotaxi']
      remove:        []
  ✓ added action `slow_down_for_robotaxi` to runtime library

### Retriever

- store size:    16
- context tags:  ['driver_present', 'robotaxi_present', 'vehicle_in_motion']
- domains:       ['physical', 'shared_road', 'vehicle_control']
- active window: 16 rules → ['P-attendance-driving', 'C3', 'R5~robotaxi_v4', 'R4', 'R6', 'R7', 'C1', 'R6~horse_carriage_v4', 'P-pulled-over', 'P-stopped-safe', 'R1', 'R2', 'R3', 'R5', 'C2', 'C4']

### Engine (single-action)

- initial state after chain: ['robotaxi_ahead', 'robotaxi_close_ahead', 'self_actively_driving', 'self_in_left_lane', 'self_in_motion']

- evaluations (best 5):
  - **slow_down_for_robotaxi** (score 150, goal_met=True)
  - **pull_over** (score 77, goal_met=False)
    - violated: [('R5~robotaxi_v4', 'requires safe_following_robotaxi (absent)')]
  - **signal_left** (score 77, goal_met=False)
    - violated: [('R5~robotaxi_v4', 'requires safe_following_robotaxi (absent)')]
  - **signal_right** (score 77, goal_met=False)
    - violated: [('R5~robotaxi_v4', 'requires safe_following_robotaxi (absent)')]
  - **maintain_speed** (score 77, goal_met=False)
    - violated: [('R5~robotaxi_v4', 'requires safe_following_robotaxi (absent)')]

- **CHOSEN:** `slow_down_for_robotaxi` (score 150)

- gap: False

### Planner (depth 3)

- nodes: 250
- best sequence: ['signal_left', 'signal_left', 'slow_down_for_robotaxi']
- best score:    150

### Compression analog baseline (v5)

- target substance:        `robotaxi`
- plain prediction:        [('car', 5), ('truck', 4), ('ambulance', 4), ('bus', 3), ('fire_engine', 3), ('horse_carriage', 2), ('bicycle', 1), ('pedestrian', 1)]
- role-weighted prediction: [('car', 4), ('truck', 3), ('ambulance', 3), ('fire_engine', 2), ('horse_carriage', 2), ('bus', 2), ('bicycle', 1), ('pedestrian', 1)]

---

## Scenario 8 (novel substance) — Fire engine behind

**Description:** You are driving and a fire engine behind you is approaching with sirens.

### Parser

- facts: ['fire_engine_behind', 'self_in_left_lane', 'self_in_motion']
- goal:  ['emergency_path_clear']

### v4 PRODUCTION WRITE

- substances in play: ['fire_engine']
- v4 targets:         ['fire_engine']
- active roles:       ['mass_relevant', 'priority_relevant', 'speed_relevant', 'vulnerability_relevant']

#### target: `fire_engine`
    • target_substance override: `fire_engine`
    • active roles: ['mass_relevant', 'priority_relevant', 'speed_relevant', 'vulnerability_relevant']
    • `fire_engine` (role-filtered): ['fast', 'large_mass', 'protected', 'emergency_priority']
    • sim(fire_engine, ambulance) = +0.6254  → ACCEPT
    • sim(fire_engine, bicycle) = +0.1658  → ACCEPT
    • sim(fire_engine, bus) = +0.4564  → ACCEPT
    • sim(fire_engine, car) = +0.4424  → ACCEPT
    • sim(fire_engine, horse_carriage) = +0.1592  → ACCEPT
    • sim(fire_engine, pedestrian) = +0.1658  → ACCEPT
    • sim(fire_engine, robotaxi) = +0.4424  → ACCEPT
    • sim(fire_engine, truck) = +0.6350  → ACCEPT
    ✓ analog: `truck` (sim +0.6350)
    ⓘ analog `truck` has no rules referencing it as a token
  analog peer for action synthesis: `truck` (sim +0.6350)

### Retriever

- store size:    16
- context tags:  ['driver_present', 'emergency_present', 'vehicle_in_motion']
- domains:       ['emergency_yielding', 'physical', 'vehicle_control']
- active window: 16 rules → ['R3', 'P-attendance-driving', 'P-pulled-over', 'C3', 'R4', 'C1', 'P-stopped-safe', 'R1', 'R2', 'R5', 'R6', 'R7', 'C2', 'C4', 'R6~horse_carriage_v4', 'R5~robotaxi_v4']

### Engine (single-action)

- initial state after chain: ['fire_engine_behind', 'self_actively_driving', 'self_in_left_lane', 'self_in_motion']

- evaluations (best 5):
  - **pull_over** (score 126, goal_met=True)
  - **signal_left** (score 101, goal_met=False)
  - **signal_right** (score 101, goal_met=False)
  - **maintain_speed** (score 101, goal_met=False)
  - **do_nothing** (score 101, goal_met=False)

- **CHOSEN:** `pull_over` (score 126)

- gap: False

### Planner (depth 3)

- nodes: 160
- best sequence: ['pull_over']
- best score:    126

### Compression analog baseline (v5)

- target substance:        `fire_engine`
- plain prediction:        [('truck', 4), ('ambulance', 4), ('car', 3), ('bus', 3), ('robotaxi', 3)]
- role-weighted prediction: [('truck', 3), ('ambulance', 3), ('car', 2), ('robotaxi', 2), ('bus', 2)]

---
