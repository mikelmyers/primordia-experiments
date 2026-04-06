"""Kitchen World — third transfer-test domain.

Same architecture as rule-world and traffic-world. Imports the rule-world
engine, retriever, abstractor, HDC, compression, planner, and rule_store
WITHOUT MODIFICATION. The rules, actions, property table, role tags, and
parser are new and live here. Substances are kitchen ingredients and tools.

Goal of this domain: stress-test the architecture against a third unrelated
domain to confirm what looked like generality after iterations 7–8 holds at
N=3 instead of N=2.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "rule-world"))
from engine import Rule, Action  # noqa: E402


# ============================================================================
# Physics derivations
# ============================================================================

PHYSICS_DERIVATIONS = [
    Rule(
        id="P-burner-flame",
        statement="A burner that is on produces a flame on the stove.",
        antecedents=["burner_on"],
        derives=["flame_on"],
        priority=8, urgency="high",
    ),
    Rule(
        id="P-oil-near-flame",
        statement="Oil near a flame raises the fire risk.",
        antecedents=["oil_near_flame", "flame_on"],
        derives=["fire_risk_high"],
        priority=9, urgency="high",
    ),
    Rule(
        id="P-water-on-fire",
        statement="Water on fire extinguishes the fire.",
        antecedents=["water_on_fire"],
        derives=["fire_extinguished"],
        priority=8, urgency="high",
    ),
    Rule(
        id="P-water-grease-fire",
        statement="Water poured on a grease fire spreads the fire.",
        antecedents=["water_on_fire", "grease_fire"],
        derives=["fire_spread"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="P-raw-meat-contamination",
        statement="Raw meat on the counter contaminates the counter.",
        antecedents=["raw_meat_on_counter"],
        derives=["counter_contaminated"],
        priority=8, urgency="high",
    ),
    Rule(
        id="P-knife-edge",
        statement="A knife at the edge of the counter is a fall hazard.",
        antecedents=["knife_at_edge"],
        derives=["fall_hazard"],
        priority=7, urgency="high",
    ),
    Rule(
        id="P-vegetable-knife",
        statement="A vegetable under a knife becomes chopped.",
        antecedents=["vegetable_under_knife"],
        derives=["vegetable_chopped"],
        priority=6, urgency="medium",
    ),
]


# ============================================================================
# Relationship rules
# ============================================================================

RELATIONSHIP_RULES = [
    Rule(
        id="R1",
        statement="The cook must not allow high fire risk while a flame is on.",
        antecedents=["flame_on"],
        forbids_in_result=["fire_risk_high"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="R2",
        statement="Raw meat on the counter must be moved to the fridge.",
        antecedents=["raw_meat_on_counter"],
        requires_in_result=["raw_meat_in_fridge"],
        priority=9, urgency="high",
    ),
    Rule(
        id="R3",
        statement="A knife at the edge must be stored safely.",
        antecedents=["knife_at_edge"],
        requires_in_result=["knife_stored_safely"],
        priority=8, urgency="high",
    ),
    Rule(
        id="R4",
        statement="A vegetable to be served must be chopped.",
        antecedents=["vegetable_present", "hungry_diner"],
        requires_in_result=["vegetable_chopped"],
        priority=6, urgency="medium",
    ),
    Rule(
        id="R5",
        statement="A grease fire must be extinguished.",
        antecedents=["grease_fire"],
        requires_in_result=["fire_extinguished"],
        priority=10, urgency="visceral",
    ),
]


# ============================================================================
# Constraint rules
# ============================================================================

CONSTRAINT_RULES = [
    Rule(
        id="C1",
        statement="The cook must never be injured.",
        antecedents=[],
        forbids_in_result=["cook_injured"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="C2",
        statement="No foodborne illness may result from the meal.",
        antecedents=[],
        forbids_in_result=["foodborne_illness"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="C3",
        statement="The kitchen must not catch fire.",
        antecedents=[],
        forbids_in_result=["fire_spread"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="C4",
        statement="When two visceral rules conflict, prefer cook safety.",
        antecedents=[], priority=10, urgency="visceral",
    ),
]


ALL_RULES: list[Rule] = (
    PHYSICS_DERIVATIONS + RELATIONSHIP_RULES + CONSTRAINT_RULES
)


# ============================================================================
# Action library
# ============================================================================

ACTIONS: list[Action] = [
    Action(
        name="turn_burner_off",
        preconditions=["burner_on"],
        add=[],
        remove=["burner_on", "flame_on"],
    ),
    Action(
        name="move_oil_away_from_flame",
        preconditions=["oil_near_flame"],
        add=["oil_safely_placed"],
        remove=["oil_near_flame"],
    ),
    Action(
        name="place_raw_meat_in_fridge",
        preconditions=["raw_meat_on_counter"],
        add=["raw_meat_in_fridge"],
        remove=["raw_meat_on_counter"],
    ),
    Action(
        name="store_knife_safely",
        preconditions=["knife_at_edge"],
        add=["knife_stored_safely"],
        remove=["knife_at_edge"],
    ),
    Action(
        name="chop_vegetable",
        preconditions=["vegetable_present", "knife_present"],
        add=["vegetable_under_knife", "vegetable_chopped"],
    ),
    Action(
        name="cover_grease_fire_with_lid",
        preconditions=["grease_fire"],
        add=["fire_extinguished"],
        remove=["grease_fire"],
    ),
    Action(
        name="pour_water_on_fire",
        preconditions=["fire_in_kitchen"],
        add=["water_on_fire"],
        remove=[],
    ),
    Action(
        name="wipe_up_water",
        preconditions=["water_spilled"],
        add=[],
        remove=["water_spilled"],
    ),
    Action(
        name="do_nothing",
        preconditions=[],
        add=[],
    ),
]


# ============================================================================
# Property table — kitchen substances
# ============================================================================

SUBSTANCE_PROPERTIES: dict[str, list[str]] = {
    "water":     ["liquid", "extinguishes_fire", "wet"],
    "oil":       ["liquid", "fat", "flammable_when_hot", "slippery"],
    "raw_meat":  ["solid", "perishable", "contamination_risk", "needs_cooking"],
    "vegetable": ["solid", "perishable", "edible_raw", "needs_washing"],
    "knife":     ["solid", "sharp", "cutting_tool"],
    "salt":      ["solid", "dry", "seasoning"],
    # Novel test substances:
    "butter":    ["solid_when_cold", "fat", "flammable_when_hot", "spreadable"],
    "raw_egg":   ["solid", "perishable", "contamination_risk", "needs_cooking", "shell"],
    "peas":      ["solid", "perishable", "edible_raw", "small"],
}


PROPERTY_ROLES: dict[str, str] = {
    # physical state (incidental)
    "liquid":             "physical_state",
    "solid":              "physical_state",
    "solid_when_cold":    "physical_state",
    "dry":                "physical_state",
    # fire-relevance
    "extinguishes_fire":  "fire_relevant",
    "flammable_when_hot": "fire_relevant",
    # food safety
    "perishable":         "food_safety",
    "contamination_risk": "food_safety",
    "needs_cooking":      "food_safety",
    "edible_raw":         "food_safety",
    "needs_washing":      "food_safety",
    # handling
    "wet":                "handling",
    "slippery":           "handling",
    "sharp":              "handling",
    "shell":              "handling",
    "small":              "handling",
    # incidental utility / attribute
    "fat":                "food_attribute",
    "spreadable":         "utility",
    "cutting_tool":       "utility",
    "seasoning":          "utility",
}


def active_roles_for_scenario(facts: list[str]) -> set[str]:
    roles: set[str] = set()
    for f in facts:
        if "flame" in f or "fire" in f or "burner" in f:
            roles.add("fire_relevant")
        if (
            "raw_" in f
            or "_contamin" in f
            or "vegetable" in f
            or "peas" in f
            or "fridge" in f
        ):
            roles.add("food_safety")
        if "knife" in f:
            roles.add("handling")
    return roles


# ============================================================================
# Retriever tag mappings
# ============================================================================

PREFIX_TAGS = {
    "burner_":      ["stove_active"],
    "flame_":       ["stove_active"],
    "fire_":        ["fire_present"],
    "grease_":      ["fire_present"],
    "oil_":         ["oil_present"],
    "butter_":      ["butter_present"],
    "water_":       ["water_present"],
    "raw_meat_":    ["raw_food_present", "food_safety_concern"],
    "raw_egg_":     ["raw_food_present", "food_safety_concern"],
    "vegetable_":   ["vegetable_present", "food_safety_concern"],
    "peas_":        ["vegetable_present", "food_safety_concern"],
    "knife_":       ["knife_present"],
    "counter_":     ["counter_state"],
    "cook_":        ["cook_state"],
    "hungry_":      ["mealtime"],
}

TAG_TO_DOMAIN = {
    "stove_active":         "stove",
    "fire_present":         "fire_response",
    "oil_present":          "stove",
    "butter_present":       "stove",
    "water_present":        "stove",
    "raw_food_present":     "food_handling",
    "food_safety_concern":  "food_handling",
    "vegetable_present":    "food_prep",
    "knife_present":        "tool_handling",
    "counter_state":        "food_handling",
    "cook_state":           "cook_state",
    "mealtime":             "food_prep",
}

FACT_TAG_OVERRIDES = {
    "burner_on":            ["stove_active"],
    "flame_on":             ["stove_active"],
    "oil_near_flame":       ["stove_active", "oil_present"],
    "butter_near_flame":    ["stove_active", "butter_present"],
    "grease_fire":          ["fire_present"],
    "fire_in_kitchen":      ["fire_present"],
}
