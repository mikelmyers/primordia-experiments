"""Layer 3 — Boundary parser.

Natural language scenario string → (facts, goal). Deliberately primitive:
keyword and pattern matching only. No LLM call. The point is to nail down the
interface boundary so a real parser can be swapped in later.
"""

from __future__ import annotations

import re

# Each entry: (regex pattern, list of facts to add)
PATTERNS: list[tuple[str, list[str]]] = [
    (r"\balone\b", ["self_in_hall", "self_at_hearth"]),
    (r"\bhearth\b.*\b(burning low|low)\b", ["hearth_burning_low"]),
    (r"\bwood\b.*\b(beside|available|near)\b", ["wood_available"]),
    (r"\bwood supply\b.*\b(not last|insufficient|run out|won't last|will not)\b",
     ["wood_supply_insufficient", "asked_by_tender"]),
    (r"\banother tender\b", ["asked_by_tender"]),
    (r"\btender asks\b", ["asked_by_tender"]),

    # Stranger basics
    (r"\bstranger\b", ["stranger_at_door"]),
    (r"\bbucket of water\b", ["stranger_carries_water"]),
    (r"\bcarrying\s+(a\s+)?water\b", ["stranger_carries_water"]),

    # Wet stranger (vs. carrying)
    (r"\bsoaked\b", ["stranger_wet"]),
    (r"\bdripping\b", ["stranger_wet"]),
    (r"\brainstorm\b", ["stranger_wet"]),
    (r"\bwet\b", ["stranger_wet"]),

    # Cold being
    (r"\bcold\b", ["stranger_cold"]),
    (r"\bshivering\b", ["stranger_cold"]),
    (r"\bfreezing\b", ["stranger_cold"]),
    (r"\bwarm themselves\b", ["stranger_cold"]),

    # Novel substances (Scenario 6+)
    (r"\bblock of ice\b", ["stranger_carries_ice"]),
    (r"\bcarrying.*ice\b", ["stranger_carries_ice"]),
    (r"\bjar of oil\b", ["stranger_carries_oil"]),

    # Child Tender scenario
    (r"\bchild tender\b", ["child_tender_in_hall"]),
    (r"\bwalk(s|ing)? toward the door\b", ["child_tender_at_door"]),
    (r"\bpicks up.*wood\b", ["wood_held_by_child"]),
]


# Default base facts unless contradicted.
BASE_FACTS = ["hearth_burning", "self_in_hall", "self_at_hearth"]


GOAL_INFERENCE = [
    # ordered: first match wins
    (lambda f: "wood_held_by_child" in f, ["wood_recovered"]),
    (lambda f: "asked_by_tender" in f, ["tender_informed_truthfully"]),
    (lambda f: "stranger_at_door" in f, ["stranger_situation_resolved"]),
    (lambda f: "hearth_burning_low" in f, ["hearth_fed"]),
]


def parse(description: str) -> dict:
    text = description.lower()
    facts: set[str] = set(BASE_FACTS)
    matched: list[str] = []
    for pattern, adds in PATTERNS:
        if re.search(pattern, text):
            facts.update(adds)
            matched.append(pattern)

    # Pick goal predicate by precedence.
    goal: list[str] = []
    for predicate_fn, g in GOAL_INFERENCE:
        if predicate_fn(facts):
            goal = g
            break
    if not goal:
        goal = ["situation_resolved"]

    return {
        "facts": sorted(facts),
        "goal": goal,
        "matched_patterns": matched,
    }
