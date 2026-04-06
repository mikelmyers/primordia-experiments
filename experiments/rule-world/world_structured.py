"""Structured representation of Rule World.

All 16 rules from world.md re-encoded as Rule tuples for engine.py, plus the
action library the engine searches over. Predicates are flat strings — no
nesting, no functions, no NLP. The engine treats them as opaque tokens.

Predicate vocabulary (committed to once, here):
  Locations:
    self_at_hearth, self_at_door, self_in_hall
    stranger_at_door, stranger_in_hall, stranger_near_hearth, stranger_far_from_hearth
    child_tender_in_hall, child_tender_at_door
  Hearth:
    hearth_burning, hearth_burning_low, hearth_extinguished, hearth_fed
  Wood:
    wood_available, wood_in_hearth, wood_supply_insufficient,
    wood_replenishment_initiated, wood_held_by_child, wood_leaving_hall, wood_recovered
  Water:
    water_on_stranger, water_in_hall, water_near_hearth, stranger_carries_water
  Stranger state:
    stranger_wet, stranger_cold, stranger_warmed, stranger_admitted_with_water
  Tenders:
    asked_by_tender, tender_informed_truthfully
    hall_has_attentive_tender
  Misc:
    being_harmed, communicated_to_child
"""

from engine import Rule, Action


# ---------- physical derivation rules ----------
# These don't carry obligations; they propagate consequences of facts.

PHYSICS_DERIVATIONS = [
    Rule(
        id="P3a",
        statement="Wood in burning Hearth produces fed Hearth.",
        antecedents=["wood_in_hearth", "hearth_burning"],
        derives=["hearth_fed"],
        priority=8, urgency="high",
    ),
    Rule(
        id="P-wet",
        statement="A wet being carries water on their body.",
        antecedents=["stranger_wet"],
        derives=["water_on_stranger"],
        priority=8, urgency="high",
    ),
    Rule(
        id="P-water-in-hall",
        statement="A wet stranger inside the Hall puts water in the Hall.",
        antecedents=["water_on_stranger", "stranger_in_hall"],
        derives=["water_in_hall"],
        priority=8, urgency="high",
    ),
    Rule(
        id="P-water-near-hearth",
        statement="A wet stranger near the Hearth puts water near the Hearth.",
        antecedents=["water_on_stranger", "stranger_near_hearth"],
        derives=["water_near_hearth"],
        priority=8, urgency="high",
    ),
    Rule(
        id="P-shelter",
        statement="A stranger near the Hearth becomes warmed.",
        antecedents=["stranger_near_hearth"],
        derives=["stranger_warmed"],
        priority=6, urgency="medium",
    ),
    Rule(
        id="P-attendance",
        statement="A Tender at the Hearth is an attentive Tender of the Hall.",
        antecedents=["self_at_hearth"],
        derives=["hall_has_attentive_tender"],
        priority=6, urgency="medium",
    ),
    Rule(
        id="P-wood-leaving",
        statement="Wood held by a child Tender at the door is wood leaving the Hall.",
        antecedents=["wood_held_by_child", "child_tender_at_door"],
        derives=["wood_leaving_hall"],
        priority=8, urgency="high",
    ),
    Rule(
        id="P-extinguish",
        statement="Water near the Hearth extinguishes the Hearth.",
        antecedents=["water_near_hearth"],
        derives=["hearth_extinguished"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="P-admitted-with-water",
        statement="A water-bearing stranger inside the Hall is admitted with water.",
        antecedents=["stranger_in_hall", "stranger_carries_water"],
        derives=["stranger_admitted_with_water"],
        priority=8, urgency="high",
    ),
]

# Inert physics from world.md (kept for completeness; no scenario uses them).
PHYSICS_INERT = [
    Rule(id="P1", statement="Objects fall unless supported.", priority=9, urgency="high"),
    Rule(id="P2", statement="Water flows downward.", priority=8, urgency="medium"),
    Rule(id="P4", statement="Heat rises; cold settles.", priority=6, urgency="low"),
    Rule(id="P5", statement="Two solid objects cannot occupy the same space.",
         priority=10, urgency="visceral"),
    Rule(id="P6", statement="Light travels in straight lines.", priority=7, urgency="low"),
]


# ---------- relationship & constraint rules (carry obligations) ----------

RELATIONSHIP_RULES = [
    Rule(
        id="R1",
        statement="A Tender must add Wood to the Hearth before it dies.",
        antecedents=["hearth_burning_low"],
        requires_in_result=["hearth_fed"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="R2",
        statement="A Tender must keep Water away from the Hearth.",
        antecedents=["hearth_burning"],
        forbids_in_result=["water_near_hearth"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="R3",
        statement="A Tender may permit a Stranger into the Hall only if the Stranger carries no Water.",
        antecedents=["stranger_at_door"],
        forbids_in_result=["stranger_admitted_with_water"],
        priority=8, urgency="high",
    ),
    Rule(
        id="R4",
        statement="A Tender must shelter any cold being inside the Hall near the Hearth.",
        antecedents=["stranger_in_hall", "stranger_cold"],
        requires_in_result=["stranger_warmed"],
        priority=7, urgency="medium",
    ),
    Rule(
        id="R5",
        statement="A Tender owes truth to other Tenders.",
        antecedents=["asked_by_tender"],
        requires_in_result=["tender_informed_truthfully"],
        priority=6, urgency="medium",
    ),
]

CONSTRAINT_RULES = [
    Rule(
        id="C1",
        statement="The Hearth must never be extinguished.",
        antecedents=["hearth_burning"],
        forbids_in_result=["hearth_extinguished"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="C2",
        statement="The Hall must never be left empty of Tenders while the Hearth burns.",
        antecedents=["hearth_burning"],
        requires_in_result=["hall_has_attentive_tender"],
        priority=9, urgency="high",
    ),
    Rule(
        id="C3",
        statement="Wood supply must be replenished before it runs out.",
        antecedents=["wood_supply_insufficient"],
        requires_in_result=["wood_replenishment_initiated"],
        priority=8, urgency="high",
    ),
    Rule(
        id="C4",
        statement="No being may be harmed except to preserve the Hearth.",
        antecedents=[],
        forbids_in_result=["being_harmed"],
        priority=7, urgency="high",
    ),
    Rule(
        id="C5",
        statement="When two visceral rules conflict, preserve the Hearth (C1 dominates).",
        antecedents=[], priority=10, urgency="visceral",
    ),
]


ALL_RULES: list[Rule] = (
    PHYSICS_DERIVATIONS
    + PHYSICS_INERT
    + RELATIONSHIP_RULES
    + CONSTRAINT_RULES
)


# ---------- substance property table ----------
# This is the small grounded ontology the HDC abstractor consults to decide
# whether two substances are *actually* analogous, rather than just
# string-similar. Hand-authored, deliberately small. Consider it the seed
# of a property graph that a future system would learn or grow.

SUBSTANCE_PROPERTIES: dict[str, list[str]] = {
    "water":    ["liquid",  "extinguishes_fire", "wets_things"],
    "ice":      ["solid",   "melts_to_water",    "extinguishes_fire_after_melting", "cold_to_touch"],
    "wood":     ["solid",   "feeds_fire",        "burnable"],
    "oil":      ["liquid",  "feeds_fire",        "burnable", "highly_flammable"],
    "food":     ["solid",   "edible",            "neutral_to_fire"],
    "medicine": ["useful_for_healing",           "neutral_to_fire"],
}


# Role tags assign each property to a semantic category. The role-weighted
# HDC abstractor (v3) uses this to filter similarity to only those properties
# whose role is "active" in the current scenario context. A scenario where
# the hearth matters activates `fire_relevant`; a scenario about feeding
# tenders would activate `nutritional`; etc.
PROPERTY_ROLES: dict[str, str] = {
    # fire-relevant
    "extinguishes_fire":               "fire_relevant",
    "extinguishes_fire_after_melting": "fire_relevant",
    "feeds_fire":                      "fire_relevant",
    "burnable":                        "fire_relevant",
    "highly_flammable":                "fire_relevant",
    "neutral_to_fire":                 "fire_relevant",
    # temperature
    "cold_to_touch":                   "temperature_relevant",
    # nutritional / utility
    "edible":                          "nutritional",
    "useful_for_healing":              "medicinal",
    # physical state (mostly incidental in fire context)
    "solid":                           "physical_state",
    "liquid":                          "physical_state",
    # behavioral
    "melts_to_water":                  "behavioral",
    "wets_things":                     "behavioral",
}


def active_roles_for_scenario(facts: list[str]) -> set[str]:
    """Pick roles whose semantic category is relevant given the fact set.

    The mapping is small and explicit. Adding a new role here is the only
    domain-specific knowledge the role-weighted abstractor consumes.
    """
    roles: set[str] = set()
    fact_set = set(facts)
    if any(f.startswith("hearth_") or "fire" in f for f in fact_set):
        roles.add("fire_relevant")
    if any("cold" in f or "warm" in f for f in fact_set):
        roles.add("temperature_relevant")
    if any("hung" in f or "food" in f for f in fact_set):
        roles.add("nutritional")
    if any("wound" in f or "ill" in f or "heal" in f for f in fact_set):
        roles.add("medicinal")
    return roles


# ---------- action library ----------
# The engine searches over THIS list. Nothing scenario-specific.

ACTIONS: list[Action] = [
    Action(
        name="add_wood_to_hearth",
        preconditions=["wood_available", "self_in_hall"],
        add=["wood_in_hearth"],
        remove=["hearth_burning_low"],
    ),
    Action(
        name="refuse_stranger",
        preconditions=["stranger_at_door"],
        add=["stranger_situation_resolved"],
        remove=[],
    ),
    Action(
        name="admit_stranger_to_hearth",
        preconditions=["stranger_at_door"],
        add=["stranger_in_hall", "stranger_near_hearth", "stranger_situation_resolved"],
        remove=["stranger_at_door"],
    ),
    Action(
        name="admit_stranger_far_from_hearth",
        preconditions=["stranger_at_door"],
        add=["stranger_in_hall", "stranger_far_from_hearth", "stranger_situation_resolved"],
        remove=["stranger_at_door"],
    ),
    Action(
        name="dry_stranger_then_admit_to_hearth",
        # The action of drying outside before admitting: removes water_on_stranger
        # then puts the stranger near the hearth.
        preconditions=["stranger_at_door", "stranger_wet"],
        add=["stranger_in_hall", "stranger_near_hearth", "stranger_situation_resolved"],
        remove=["stranger_at_door", "stranger_wet", "water_on_stranger"],
    ),
    Action(
        name="tell_truth_to_tender",
        preconditions=["asked_by_tender"],
        add=["tender_informed_truthfully"],
    ),
    Action(
        name="lie_to_tender",
        preconditions=["asked_by_tender"],
        add=["tender_informed_falsely"],
    ),
    Action(
        name="initiate_wood_replenishment_plan",
        # Planning to replenish, NOT physically leaving the hall now.
        preconditions=["wood_supply_insufficient"],
        add=["wood_replenishment_initiated"],
    ),
    Action(
        name="leave_hall_to_gather_wood",
        preconditions=["wood_supply_insufficient", "self_at_hearth"],
        add=["wood_replenishment_initiated", "self_at_door"],
        remove=["self_at_hearth"],
    ),
    Action(
        name="call_out_to_child_from_hearth",
        preconditions=["child_tender_in_hall", "self_at_hearth"],
        add=["communicated_to_child", "tender_informed_truthfully", "wood_recovered"],
        remove=["wood_held_by_child", "wood_leaving_hall"],
    ),
    Action(
        name="chase_child_to_door",
        preconditions=["child_tender_at_door", "self_at_hearth"],
        add=["self_at_door", "wood_recovered"],
        remove=["self_at_hearth", "wood_held_by_child", "wood_leaving_hall"],
    ),
    Action(
        name="stay_silent_at_hearth",
        preconditions=["self_at_hearth"],
        add=[],
    ),
    Action(
        name="do_nothing",
        preconditions=[],
        add=[],
    ),
]
