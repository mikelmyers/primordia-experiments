"""Kitchen-world boundary parser. NL → (facts, goal). Pure regex/keyword."""

from __future__ import annotations

import re

PATTERNS: list[tuple[str, list[str]]] = [
    # Stove / burner state
    (r"\bburner (is )?on\b|\bstove (is )?on\b|\bgas (is )?on\b|\bturned on the (burner|stove)\b",
     ["burner_on"]),
    (r"\bwalked away\b|\bstepped away\b|\bleft the kitchen\b|\bgo answer the door\b",
     ["cook_unattentive"]),

    # Oil / pan
    (r"\boil (is )?in (the |a )?pan\b|\bpan of oil\b|\bfrying oil\b",
     ["oil_in_pan", "oil_near_flame"]),

    # Butter (novel)
    (r"\bbutter (is )?melting\b|\bbutter in (the |a )?pan\b|\bstick of butter\b.*\bpan\b",
     ["butter_in_pan", "butter_near_flame"]),

    # Water spilled / on stovetop
    (r"\bspilled water\b|\bwater on the (counter|stovetop|stove)\b|\bpuddle of water\b",
     ["water_spilled"]),

    # Raw meat
    (r"\braw chicken\b|\braw meat\b|\braw beef\b|\bground beef\b",
     ["raw_meat_on_counter", "raw_meat_present"]),

    # Raw eggs (novel)
    (r"\braw eggs?\b|\bcracked an egg\b|\bcracked eggs?\b|\beggs? (is |are )?on the counter\b",
     ["raw_egg_on_counter", "raw_egg_present"]),

    # Vegetables / peas (novel)
    (r"\bcarrots?\b|\bvegetables?\b|\bveggies\b|\bonions?\b",
     ["vegetable_present"]),
    (r"\bpeas\b|\bbag of peas\b|\bfrozen peas\b",
     ["peas_present"]),

    # Knife
    (r"\bknife\b.*\bedge\b|\bknife near the edge\b|\bknife on the edge\b",
     ["knife_at_edge", "knife_present"]),
    (r"\bknife\b",
     ["knife_present"]),

    # Fires
    (r"\bgrease fire\b|\bsmall fire in the pan\b|\bpan caught fire\b",
     ["grease_fire", "fire_in_kitchen"]),
    (r"\bkitchen (is )?on fire\b|\bfire in the kitchen\b",
     ["fire_in_kitchen"]),

    # Mealtime / hungry diners
    (r"\bdinner\b|\bhungry\b|\bguests are waiting\b|\bmealtime\b",
     ["hungry_diner"]),

    # Cook default
    (r"\b(you are |i am )?cooking\b|\bin the kitchen\b",
     ["cook_at_stove"]),
]


BASE_FACTS: list[str] = ["cook_at_stove"]


GOAL_INFERENCE = [
    (lambda f: "grease_fire" in f or "fire_in_kitchen" in f, ["fire_extinguished"]),
    (lambda f: "oil_near_flame" in f and "burner_on" in f, ["fire_risk_high_resolved"]),
    (lambda f: "butter_near_flame" in f and "burner_on" in f, ["fire_risk_high_resolved"]),
    (lambda f: "raw_meat_on_counter" in f, ["raw_meat_in_fridge"]),
    (lambda f: "raw_egg_on_counter" in f, ["raw_egg_in_fridge"]),
    (lambda f: "knife_at_edge" in f, ["knife_stored_safely"]),
    (lambda f: "vegetable_present" in f and "hungry_diner" in f, ["vegetable_chopped"]),
    (lambda f: "peas_present" in f and "hungry_diner" in f, ["peas_chopped"]),
    (lambda f: "water_spilled" in f, ["counter_dry"]),
]


def parse(description: str) -> dict:
    text = description.lower()
    facts: set[str] = set(BASE_FACTS)
    matched: list[str] = []
    for pattern, adds in PATTERNS:
        if re.search(pattern, text):
            facts.update(adds)
            matched.append(pattern)

    goal: list[str] = []
    for fn, g in GOAL_INFERENCE:
        if fn(facts):
            goal = g
            break
    if not goal:
        goal = ["situation_resolved"]

    return {
        "facts": sorted(facts),
        "goal": goal,
        "matched_patterns": matched,
    }
