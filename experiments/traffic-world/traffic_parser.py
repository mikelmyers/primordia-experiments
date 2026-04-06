"""Traffic-world boundary parser. Same shape as rule-world's parser:
NL → (facts, goal). Pure regex/keyword. No LLM.
"""

from __future__ import annotations

import re

PATTERNS: list[tuple[str, list[str]]] = [
    # Self state defaults
    (r"\b(driving|in motion)\b",
     ["self_in_motion", "self_in_left_lane"]),

    # Intersection / signals — accept several phrasings
    (r"\bred light\b|\blight (ahead )?is red\b|\bthe light.*\bred\b",
     ["red_light_ahead", "self_at_intersection"]),
    (r"\bgreen light\b|\blight (ahead )?is green\b",
     ["green_light_ahead", "self_at_intersection"]),
    (r"\byellow light\b|\blight (ahead )?is yellow\b",
     ["yellow_light_ahead", "self_at_intersection"]),
    (r"\bintersection\b|\bapproaching an intersection\b",
     ["self_at_intersection"]),

    # Pedestrians
    (r"\bpedestrian\b.*\bcrosswalk\b|\bcrosswalk\b.*\bpedestrian\b",
     ["pedestrian_in_crosswalk"]),
    (r"\bcrossing\b",
     ["pedestrian_in_crosswalk"]),

    # Other road users (lead to <token>_ahead/_behind)
    (r"\bambulance\b.*\bbehind\b|\bbehind\b.*\bambulance\b",
     ["ambulance_behind"]),
    (r"\bfire engine\b.*\bbehind\b|\bbehind\b.*\bfire engine\b",
     ["fire_engine_behind"]),
    # Car ahead — accept any nearby phrasing
    (r"\bcar ahead\b|\btailgating\b|\bcar (is )?too close\b|\bclose (to )?(the )?car ahead\b",
     ["car_close_ahead"]),
    (r"\bbicycle\b.*\b(ahead|in front|in your lane)\b",
     ["bicycle_ahead"]),
    (r"\bbus\b.*\b(unloading|stopped)\b",
     ["bus_unloading_ahead"]),

    # Novel substances
    (r"\bhorse[- ]drawn carriage\b|\bhorse carriage\b",
     ["horse_carriage_ahead", "horse_carriage_close_ahead"]),
    (r"\brobotaxi\b|\bself[- ]driving (taxi|car)\b",
     ["robotaxi_ahead", "robotaxi_close_ahead"]),

    # Lane / signaling intent
    (r"\bin the left lane\b|\bleft lane\b",
     ["self_in_left_lane"]),
    (r"\bin the right lane\b|\bright lane\b",
     ["self_in_right_lane"]),
    (r"\bplanning to turn\b|\bintend to turn\b|\babout to turn\b",
     ["intent_to_turn"]),
]

BASE_FACTS: list[str] = []  # populated by patterns


GOAL_INFERENCE = [
    (lambda f: "red_light_ahead" in f, ["intersection_safe"]),
    (lambda f: "pedestrian_in_crosswalk" in f, ["pedestrian_safe"]),
    (lambda f: "ambulance_behind" in f, ["emergency_path_clear"]),
    (lambda f: "fire_engine_behind" in f, ["emergency_path_clear"]),
    (lambda f: "car_close_ahead" in f, ["safe_following_car"]),
    (lambda f: "bicycle_ahead" in f, ["safe_distance_from_bicycle"]),
    (lambda f: "horse_carriage_ahead" in f, ["safe_distance_from_horse_carriage"]),
    (lambda f: "robotaxi_ahead" in f, ["safe_following_robotaxi"]),
    (lambda f: "green_light_ahead" in f, ["intersection_traversed"]),
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
