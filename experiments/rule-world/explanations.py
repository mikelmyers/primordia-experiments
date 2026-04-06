"""Rule-world humanization dictionary for the iteration 13 explainer.

Hand-authored predicate -> English phrase mappings. The same kind of
artifact as world_structured.SUBSTANCE_PROPERTIES — small, deliberate,
the seed of something a future iteration could induce automatically
from rule.statement fields.
"""

PREDICATE_PHRASES: dict[str, str] = {
    # Self / location
    "self_in_hall":          "you are in the hall",
    "self_at_hearth":        "you are at the hearth",
    "self_at_door":          "you are at the door",
    # Hearth state
    "hearth_burning":        "the hearth is burning",
    "hearth_burning_low":    "the hearth is burning low",
    "hearth_extinguished":   "the hearth has been extinguished",
    "hearth_fed":            "the hearth has been fed",
    # Wood / fuel
    "wood_available":        "wood is available beside you",
    "wood_in_hearth":        "wood is in the hearth",
    "wood_supply_insufficient": "the wood supply is insufficient",
    "wood_replenishment_initiated": "wood replenishment has been initiated",
    "wood_held_by_child":    "wood is held by the child tender",
    "wood_leaving_hall":     "wood is leaving the hall",
    "wood_recovered":        "the wood has been recovered",
    # Stranger
    "stranger_at_door":      "a stranger is at the door",
    "stranger_in_hall":      "a stranger is in the hall",
    "stranger_near_hearth":  "a stranger is near the hearth",
    "stranger_far_from_hearth": "a stranger is far from the hearth",
    "stranger_wet":          "the stranger is wet",
    "stranger_cold":         "the stranger is cold",
    "stranger_warmed":       "the stranger has been warmed",
    "stranger_carries_water": "the stranger is carrying water",
    "stranger_carries_ice":  "the stranger is carrying ice",
    "stranger_carries_oil":  "the stranger is carrying oil",
    "stranger_carries_food": "the stranger is carrying food",
    "stranger_carries_medicine": "the stranger is carrying medicine",
    "stranger_admitted_with_water": "the stranger has been admitted carrying water",
    "stranger_situation_resolved": "the stranger situation has been resolved",
    # Water
    "water_on_stranger":     "water is on the stranger",
    "water_in_hall":         "there is water in the hall",
    "water_near_hearth":     "there is water near the hearth",
    # Other substance availability
    "oil_available":         "oil is available",
    "food_available":        "food is available",
    "medicine_available":    "medicine is available",
    "ice_available":         "ice is available",
    # Tenders
    "asked_by_tender":       "another tender has asked you a question",
    "tender_informed_truthfully": "the tender has been told the truth",
    "tender_informed_falsely": "the tender has been told a lie",
    "hall_has_attentive_tender": "the hall has an attentive tender",
    # Child tender
    "child_tender_in_hall":  "the child tender is in the hall",
    "child_tender_at_door":  "the child tender is at the door",
    "communicated_to_child": "you have communicated with the child",
    # Misc
    "being_harmed":          "a being is being harmed",
    "situation_resolved":    "the situation is resolved",
}


ACTION_PHRASES: dict[str, str] = {
    "add_wood_to_hearth":             "add wood to the hearth",
    "refuse_stranger":                "refuse the stranger entry",
    "admit_stranger_to_hearth":       "admit the stranger to the hearth",
    "admit_stranger_far_from_hearth": "admit the stranger but keep them far from the hearth",
    "dry_stranger_then_admit_to_hearth": "dry the stranger off and then admit them to the hearth",
    "tell_truth_to_tender":           "tell the truth to the other tender",
    "lie_to_tender":                  "lie to the other tender",
    "initiate_wood_replenishment_plan": "initiate a plan to replenish the wood supply",
    "leave_hall_to_gather_wood":      "leave the hall to gather more wood",
    "call_out_to_child_from_hearth":  "call out to the child from the hearth",
    "chase_child_to_door":            "chase the child to the door",
    "stay_silent_at_hearth":          "stay silent at the hearth",
    "do_nothing":                     "do nothing",
}


def build_rule_statements() -> dict[str, str]:
    """Pull rule.statement off ALL_RULES into an id->statement dict.

    This is the bilingual side of the rules: every rule already has an
    English statement authored alongside it. The explainer reads these
    directly with no transformation.
    """
    from world_structured import ALL_RULES
    return {r.id: r.statement for r in ALL_RULES}


def build_humanizer():
    from explainer import Humanizer
    return Humanizer(PREDICATE_PHRASES, ACTION_PHRASES)
