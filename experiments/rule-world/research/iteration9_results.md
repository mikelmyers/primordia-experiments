# Iteration 9 — Property table induction results

Test: replace the hand-authored substance property tables in both domains with structurally-induced feature tables, then check whether the iteration-7 substrate-independence pattern (HDC v3/v4 ≡ compression v5) survives. Top-pick agreement on the adversarial queries is the success metric.

## rule-world

### Induced feature counts per substance

| substance | # induced features | # authored properties |
|---|---|---|
| food | 3 | 3 |
| ice | 2 | 4 |
| medicine | 3 | 2 |
| oil | 3 | 4 |
| water | 11 | 3 |
| wood | 21 | 3 |

### Sample induced features

- **food** (3): ['role:observation', 'shape:X_available', 'shape:stranger_carries_X']
- **ice** (2): ['role:observation', 'shape:stranger_carries_X']
- **medicine** (3): ['role:observation', 'shape:X_available', 'shape:stranger_carries_X']
- **oil** (3): ['role:observation', 'shape:X_available', 'shape:stranger_carries_X']
- **water** (11): ['act_rem_shape:X_on_stranger', 'role:act_rem', 'role:antecedent', 'role:derives', 'role:forbids', 'role:observation', 'shape:X_in_hall', 'shape:X_near_hearth']
- **wood** (21): ['act_add_shape:X_in_hearth', 'act_add_shape:X_recovered', 'act_add_shape:X_replenishment_initiated', 'act_pre_shape:X_available', 'act_pre_shape:X_supply_insufficient', 'act_rem_shape:X_held_by_child', 'act_rem_shape:X_leaving_hall', 'role:act_add']

### Adversarial query comparison (top-3 analogs)

| query | authored (role-weighted) | induced (all-features) | top match? |
|---|---|---|---|
| oil | wood:2 | food:3, medicine:3, ice:2 | ❌ |
| food | medicine:1 | medicine:3, oil:3, ice:2 | ✅ |
| medicine | food:1 | food:3, oil:3, ice:2 | ✅ |
| ice | (no candidates) | food:2, medicine:2, oil:2 | ❌ |

**Top-pick agreement: 2/3**

## traffic-world

### Induced feature counts per substance

| substance | # induced features | # authored properties |
|---|---|---|
| ambulance | 3 | 5 |
| bicycle | 9 | 6 |
| bus | 2 | 5 |
| car | 9 | 5 |
| fire_engine | 2 | 5 |
| horse_carriage | 4 | 6 |
| pedestrian | 11 | 5 |
| robotaxi | 4 | 6 |
| truck | 0 | 5 |

### Sample induced features

- **ambulance** (3): ['role:antecedent', 'role:observation', 'shape:X_behind']
- **bicycle** (9): ['act_add_shape:safe_distance_from_X', 'act_pre_shape:X_ahead', 'role:act_add', 'role:act_pre', 'role:antecedent', 'role:observation', 'role:requires', 'shape:X_ahead']
- **bus** (2): ['role:antecedent', 'shape:X_unloading_ahead']
- **car** (9): ['act_add_shape:safe_following_X', 'act_pre_shape:X_close_ahead', 'role:act_add', 'role:act_pre', 'role:antecedent', 'role:observation', 'role:requires', 'shape:X_close_ahead']
- **fire_engine** (2): ['role:observation', 'shape:X_behind']
- **horse_carriage** (4): ['role:observation', 'shape:X_ahead', 'shape:X_close_ahead', 'shape:safe_distance_from_X']
- **pedestrian** (11): ['act_add_shape:X_safe', 'act_pre_shape:X_in_crosswalk', 'role:act_add', 'role:act_pre', 'role:antecedent', 'role:forbids', 'role:observation', 'role:requires']
- **robotaxi** (4): ['role:observation', 'shape:X_ahead', 'shape:X_close_ahead', 'shape:safe_following_X']
- **truck** (0): []

### Adversarial query comparison (top-3 analogs)

| query | authored (role-weighted) | induced (all-features) | top match? |
|---|---|---|---|
| horse_carriage | bicycle:3, pedestrian:3, bus:2 | bicycle:3, robotaxi:3, car:2 | ✅ |
| robotaxi | car:4, truck:3, ambulance:3 | car:3, horse_carriage:3, bicycle:2 | ✅ |
| fire_engine | truck:3, ambulance:3, car:2 | ambulance:2, bicycle:1, car:1 | ❌ |

**Top-pick agreement: 2/3**

---

Reading: a `✅` means the induced table — built with zero hand-authored property labels — produced the same top analog choice as the hand-authored table. A `❌` means structural induction is not yet sufficient for that query and additional signal is needed.
