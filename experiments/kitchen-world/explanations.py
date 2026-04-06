"""Kitchen-world humanization dictionary for the iteration 13 explainer."""

PREDICATE_PHRASES: dict[str, str] = {
    # Cook / kitchen state
    "cook_at_stove":             "the cook is at the stove",
    "cook_unattentive":          "the cook is no longer attending to the stove",
    "cook_attentive":            "the cook is attending to the stove",
    "cook_injured":              "the cook has been injured",
    # Stove / burner / flame
    "burner_on":                 "the burner is on",
    "flame_on":                  "there is a flame on the stove",
    # Oil
    "oil_in_pan":                "there is oil in the pan",
    "oil_near_flame":            "there is oil near the flame",
    "oil_safely_placed":         "the oil has been moved to a safe place",
    # Butter (novel)
    "butter_in_pan":             "there is butter in the pan",
    "butter_near_flame":         "there is butter near the flame",
    "butter_safely_placed":      "the butter has been moved to a safe place",
    # Fire
    "fire_in_kitchen":           "there is a fire in the kitchen",
    "grease_fire":               "there is a grease fire in the pan",
    "fire_extinguished":         "the fire has been extinguished",
    "fire_risk_high":            "the fire risk is high",
    "fire_risk_high_resolved":   "the high fire risk has been resolved",
    "fire_spread":               "the fire has spread",
    # Water
    "water_on_fire":             "water has been put on the fire",
    "water_spilled":             "there is water spilled on the surface",
    "water_available":           "water is available",
    "counter_dry":               "the counter is dry",
    # Raw meat / raw egg
    "raw_meat_on_counter":       "raw meat is on the counter",
    "raw_meat_present":          "raw meat is present",
    "raw_meat_in_fridge":        "the raw meat has been placed in the fridge",
    "raw_egg_on_counter":        "raw eggs are on the counter",
    "raw_egg_present":           "raw eggs are present",
    "raw_egg_in_fridge":         "the raw eggs have been placed in the fridge",
    "counter_contaminated":      "the counter has been contaminated",
    # Knife
    "knife_at_edge":             "the knife is at the edge of the counter",
    "knife_present":             "a knife is present",
    "knife_stored_safely":       "the knife has been stored safely",
    "fall_hazard":               "there is a fall hazard",
    # Vegetables / peas
    "vegetable_present":         "vegetables are present on the counter",
    "vegetable_under_knife":     "the vegetables are under the knife",
    "vegetable_chopped":         "the vegetables have been chopped",
    "peas_present":              "frozen peas are on the counter",
    "peas_under_knife":          "the peas are under the knife",
    "peas_chopped":              "the peas have been chopped",
    # Mealtime
    "hungry_diner":              "there are hungry diners waiting",
    "foodborne_illness":         "foodborne illness has occurred",
    "situation_resolved":        "the situation is resolved",
}


ACTION_PHRASES: dict[str, str] = {
    "turn_burner_off":             "turn the burner off",
    "move_oil_away_from_flame":    "move the oil away from the flame",
    "move_butter_away_from_flame": "move the butter away from the flame",
    "place_raw_meat_in_fridge":    "place the raw meat in the fridge",
    "place_raw_egg_in_fridge":     "place the raw eggs in the fridge",
    "store_knife_safely":          "store the knife safely",
    "chop_vegetable":              "chop the vegetables",
    "chop_peas":                   "chop the peas",
    "cover_grease_fire_with_lid":  "cover the grease fire with a lid",
    "pour_water_on_fire":          "pour water on the fire",
    "wipe_up_water":               "wipe up the spilled water",
    "do_nothing":                  "do nothing",
}


def build_rule_statements() -> dict[str, str]:
    from kitchen_rules import ALL_RULES
    return {r.id: r.statement for r in ALL_RULES}


def build_humanizer():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "rule-world"))
    from explainer import Humanizer
    return Humanizer(PREDICATE_PHRASES, ACTION_PHRASES)
