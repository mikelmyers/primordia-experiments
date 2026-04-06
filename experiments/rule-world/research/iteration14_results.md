# Iteration 14 — Humanization dictionary induction

Tests whether the iteration-9 induction trick works on the iteration-13 humanization dictionary. Strategy: align each rule's English `statement` field against its formal predicates and extract the shortest contiguous span containing every predicate token. No matmul. No learned model. Pure string alignment.

## rule-world

- authored predicates: **44**
- induced predicates: **17**
- recovered from rule statements: **17/44** = **38.6%**
- predicates the inducer found that weren't in the authored dict: 0

### Side-by-side: authored vs induced (covered predicates)

| predicate | authored phrase | induced phrase |
|---|---|---|
| `being_harmed` | a being is being harmed | harmed |
| `child_tender_at_door` | the child tender is at the door | tender at the door |
| `hearth_burning` | the hearth is burning | burning hearth |
| `hearth_extinguished` | the hearth has been extinguished | hearth must never be extinguished |
| `hearth_fed` | the hearth has been fed | fed hearth |
| `self_at_hearth` | you are at the hearth | tender at the hearth |
| `stranger_admitted_with_water` | the stranger has been admitted carrying water | stranger inside the hall is admitted with water |
| `stranger_carries_water` | the stranger is carrying water | stranger carrie no water |
| `stranger_in_hall` | a stranger is in the hall | stranger inside the hall puts water in |
| `stranger_near_hearth` | a stranger is near the hearth | stranger near the hearth |
| `stranger_warmed` | the stranger has been warmed | stranger near the hearth become warmed |
| `stranger_wet` | the stranger is wet | wet stranger |
| `water_in_hall` | there is water in the hall | hall puts water in |
| `water_near_hearth` | there is water near the hearth | hearth puts water near |
| `wood_held_by_child` | wood is held by the child tender | wood held by a child |
| `wood_in_hearth` | wood is in the hearth | wood in burning hearth |
| `wood_leaving_hall` | wood is leaving the hall | wood leaving the hall |

### Predicates the inducer could NOT recover

These predicates exist in the hand-authored dictionary but no rule statement contains all of their content tokens. The explainer falls back to the structural transformation (`underscores → spaces`) for these.

- `asked_by_tender` → fallback: *"asked by tender"*
- `child_tender_in_hall` → fallback: *"child tender in hall"*
- `communicated_to_child` → fallback: *"communicated to child"*
- `food_available` → fallback: *"food available"*
- `hall_has_attentive_tender` → fallback: *"hall has attentive tender"*
- `hearth_burning_low` → fallback: *"hearth burning low"*
- `ice_available` → fallback: *"ice available"*
- `medicine_available` → fallback: *"medicine available"*
- `oil_available` → fallback: *"oil available"*
- `self_at_door` → fallback: *"self at door"*
- `self_in_hall` → fallback: *"self in hall"*
- `situation_resolved` → fallback: *"situation resolved"*
- `stranger_at_door` → fallback: *"stranger at door"*
- `stranger_carries_food` → fallback: *"stranger carries food"*
- `stranger_carries_ice` → fallback: *"stranger carries ice"*
- `stranger_carries_medicine` → fallback: *"stranger carries medicine"*
- `stranger_carries_oil` → fallback: *"stranger carries oil"*
- `stranger_cold` → fallback: *"stranger cold"*
- `stranger_far_from_hearth` → fallback: *"stranger far from hearth"*
- `stranger_situation_resolved` → fallback: *"stranger situation resolved"*
- `tender_informed_falsely` → fallback: *"tender informed falsely"*
- `tender_informed_truthfully` → fallback: *"tender informed truthfully"*
- `water_on_stranger` → fallback: *"water on stranger"*
- `wood_available` → fallback: *"wood available"*
- `wood_recovered` → fallback: *"wood recovered"*
- `wood_replenishment_initiated` → fallback: *"wood replenishment initiated"*
- `wood_supply_insufficient` → fallback: *"wood supply insufficient"*

## traffic-world

- authored predicates: **37**
- induced predicates: **8**
- recovered from rule statements: **8/37** = **21.6%**
- predicates the inducer found that weren't in the authored dict: 0

### Side-by-side: authored vs induced (covered predicates)

| predicate | authored phrase | induced phrase |
|---|---|---|
| `ambulance_behind` | there is an ambulance behind you | ambulance behind |
| `bicycle_ahead` | there is a bicycle ahead | bicycle ahead |
| `pedestrian_in_crosswalk` | there is a pedestrian in the crosswalk | pedestrian in crosswalk |
| `self_actively_driving` | you are actively driving | actively driving the vehicle |
| `self_at_intersection` | you are at an intersection | vehicle that is stopped at an intersection |
| `self_in_motion` | your vehicle is in motion | driver in motion |
| `self_pulled_over` | your vehicle is pulled over | pulled over vehicle |
| `self_stopped` | your vehicle is stopped | vehicle that is stopped |

### Predicates the inducer could NOT recover

These predicates exist in the hand-authored dictionary but no rule statement contains all of their content tokens. The explainer falls back to the structural transformation (`underscores → spaces`) for these.

- `bus_unloading_ahead` → fallback: *"bus unloading ahead"*
- `car_close_ahead` → fallback: *"car close ahead"*
- `collision_occurred` → fallback: *"collision occurred"*
- `emergency_path_clear` → fallback: *"emergency path clear"*
- `exceeding_speed_limit` → fallback: *"exceeding speed limit"*
- `fire_engine_behind` → fallback: *"fire engine behind"*
- `green_light_ahead` → fallback: *"green light ahead"*
- `horse_carriage_ahead` → fallback: *"horse carriage ahead"*
- `horse_carriage_close_ahead` → fallback: *"horse carriage close ahead"*
- `intent_to_turn` → fallback: *"intent to turn"*
- `intersection_safe` → fallback: *"intersection safe"*
- `intersection_traversed` → fallback: *"intersection traversed"*
- `pedestrian_safe` → fallback: *"pedestrian safe"*
- `pedestrian_struck` → fallback: *"pedestrian struck"*
- `red_light_ahead` → fallback: *"red light ahead"*
- `robotaxi_ahead` → fallback: *"robotaxi ahead"*
- `robotaxi_close_ahead` → fallback: *"robotaxi close ahead"*
- `safe_distance_from_bicycle` → fallback: *"safe distance from bicycle"*
- `safe_distance_from_horse_carriage` → fallback: *"safe distance from horse carriage"*
- `safe_following_car` → fallback: *"safe following car"*
- `safe_following_robotaxi` → fallback: *"safe following robotaxi"*
- `self_in_left_lane` → fallback: *"self in left lane"*
- `self_in_right_lane` → fallback: *"self in right lane"*
- `signal_active` → fallback: *"signal active"*
- `signaling_left` → fallback: *"signaling left"*
- `signaling_right` → fallback: *"signaling right"*
- `situation_resolved` → fallback: *"situation resolved"*
- `vehicle_through_intersection` → fallback: *"vehicle through intersection"*
- `yellow_light_ahead` → fallback: *"yellow light ahead"*

## kitchen-world

- authored predicates: **42**
- induced predicates: **16**
- recovered from rule statements: **16/42** = **38.1%**
- predicates the inducer found that weren't in the authored dict: 0

### Side-by-side: authored vs induced (covered predicates)

| predicate | authored phrase | induced phrase |
|---|---|---|
| `burner_on` | the burner is on | burner that is on |
| `cook_injured` | the cook has been injured | cook must never be injured |
| `fall_hazard` | there is a fall hazard | fall hazard |
| `fire_extinguished` | the fire has been extinguished | fire must be extinguished |
| `fire_risk_high` | the fire risk is high | high fire risk |
| `fire_spread` | the fire has spread | fire spread |
| `flame_on` | there is a flame on the stove | flame on |
| `foodborne_illness` | foodborne illness has occurred | foodborne illness |
| `grease_fire` | there is a grease fire in the pan | grease fire |
| `knife_at_edge` | the knife is at the edge of the counter | knife at the edge |
| `knife_stored_safely` | the knife has been stored safely | knife at the edge must be stored safely |
| `oil_near_flame` | there is oil near the flame | oil near a flame |
| `raw_meat_on_counter` | raw meat is on the counter | raw meat on the counter |
| `vegetable_chopped` | the vegetables have been chopped | vegetable under a knife become chopped |
| `vegetable_under_knife` | the vegetables are under the knife | vegetable under a knife |
| `water_on_fire` | water has been put on the fire | water on fire |

### Predicates the inducer could NOT recover

These predicates exist in the hand-authored dictionary but no rule statement contains all of their content tokens. The explainer falls back to the structural transformation (`underscores → spaces`) for these.

- `butter_in_pan` → fallback: *"butter in pan"*
- `butter_near_flame` → fallback: *"butter near flame"*
- `butter_safely_placed` → fallback: *"butter safely placed"*
- `cook_at_stove` → fallback: *"cook at stove"*
- `cook_attentive` → fallback: *"cook attentive"*
- `cook_unattentive` → fallback: *"cook unattentive"*
- `counter_contaminated` → fallback: *"counter contaminated"*
- `counter_dry` → fallback: *"counter dry"*
- `fire_in_kitchen` → fallback: *"fire in kitchen"*
- `fire_risk_high_resolved` → fallback: *"fire risk high resolved"*
- `hungry_diner` → fallback: *"hungry diner"*
- `knife_present` → fallback: *"knife present"*
- `oil_in_pan` → fallback: *"oil in pan"*
- `oil_safely_placed` → fallback: *"oil safely placed"*
- `peas_chopped` → fallback: *"peas chopped"*
- `peas_present` → fallback: *"peas present"*
- `peas_under_knife` → fallback: *"peas under knife"*
- `raw_egg_in_fridge` → fallback: *"raw egg in fridge"*
- `raw_egg_on_counter` → fallback: *"raw egg on counter"*
- `raw_egg_present` → fallback: *"raw egg present"*
- `raw_meat_in_fridge` → fallback: *"raw meat in fridge"*
- `raw_meat_present` → fallback: *"raw meat present"*
- `situation_resolved` → fallback: *"situation resolved"*
- `vegetable_present` → fallback: *"vegetable present"*
- `water_available` → fallback: *"water available"*
- `water_spilled` → fallback: *"water spilled"*

---

## Combined N=3 result

- **41/123** authored predicates recovered automatically = **33.3%**
- **0** additional predicates extracted that the hand-authored dictionaries did not bother with
- per domain: rule-world 38.6% · traffic-world 21.6% · kitchen-world 38.1%

## Reading

- Coverage **above 50%** would mean the induction trick that worked on the property table also works on the humanization dictionary, and most of the iteration 13 hand-authored work could in principle be skipped.
- Coverage **below 50%** would mean the rule statements aren't phrased in a way that exposes their predicates, and the bilingual trick doesn't extend to NL output as cleanly as it does to property structure.
- Predicates in the *missing* list are not failures of the system; they fall through to the structural fallback (underscores → spaces) and the explainer continues to produce readable output. They are the size of the residual hand-authoring task if iteration 14 were deployed.
