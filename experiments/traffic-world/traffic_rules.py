"""Traffic World — a transfer test for the rule-world architecture.

Same architecture (engine, retriever, abstractor, HDC, compression,
planner) operating on a totally different domain. The rules, actions,
property table, role tags, and parser are all new. None of the
rule-world machinery is modified.

If this works, the architecture transfers. If it doesn't, the rule-world
implementation has hidden domain-specific assumptions we hadn't noticed.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Import Rule and Action from the rule-world engine.
sys.path.insert(0, str(Path(__file__).parent.parent / "rule-world"))
from engine import Rule, Action  # noqa: E402


# ============================================================================
# Physics derivations
# ============================================================================

PHYSICS_DERIVATIONS = [
    Rule(
        id="P-attendance-driving",
        statement="A driver in motion is actively driving the vehicle.",
        antecedents=["self_in_motion"],
        derives=["self_actively_driving"],
        priority=6, urgency="medium",
    ),
    Rule(
        id="P-stopped-safe",
        statement="A vehicle that is stopped at an intersection cannot pass through it.",
        antecedents=["self_stopped", "self_at_intersection"],
        derives=["intersection_safe"],
        priority=8, urgency="high",
    ),
    Rule(
        id="P-pulled-over",
        statement="A pulled-over vehicle is not blocking emergency traffic.",
        antecedents=["self_pulled_over"],
        derives=["emergency_path_clear"],
        priority=9, urgency="high",
    ),
]


# ============================================================================
# Relationship rules (priority/urgency carriers)
# ============================================================================

RELATIONSHIP_RULES = [
    Rule(
        id="R1",
        statement="Vehicles must stop at red lights.",
        antecedents=["red_light_ahead", "self_at_intersection"],
        forbids_in_result=["vehicle_through_intersection"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="R2",
        statement="Vehicles must yield to pedestrians in crosswalks.",
        antecedents=["pedestrian_in_crosswalk"],
        requires_in_result=["pedestrian_safe"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="R3",
        statement="Vehicles must yield to ambulances behind them.",
        antecedents=["ambulance_behind"],
        requires_in_result=["emergency_path_clear"],
        priority=9, urgency="high",
    ),
    Rule(
        id="R4",
        statement="Vehicles must signal before turning or changing lanes.",
        antecedents=["intent_to_turn"],
        requires_in_result=["signal_active"],
        priority=6, urgency="medium",
    ),
    Rule(
        id="R5",
        statement="Vehicles must maintain a safe following distance from cars ahead.",
        antecedents=["car_close_ahead"],
        requires_in_result=["safe_following_car"],
        priority=8, urgency="high",
    ),
    Rule(
        id="R6",
        statement="Vehicles must give wide berth to bicycles ahead.",
        antecedents=["bicycle_ahead"],
        requires_in_result=["safe_distance_from_bicycle"],
        priority=7, urgency="medium",
    ),
    Rule(
        id="R7",
        statement="Vehicles must yield to buses unloading passengers.",
        antecedents=["bus_unloading_ahead"],
        requires_in_result=["self_stopped"],
        priority=8, urgency="high",
    ),
]


# ============================================================================
# Constraint rules (universal)
# ============================================================================

CONSTRAINT_RULES = [
    Rule(
        id="C1",
        statement="Vehicles must not collide with anything.",
        antecedents=[],
        forbids_in_result=["collision_occurred"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="C2",
        statement="Vehicles must not strike pedestrians.",
        antecedents=[],
        forbids_in_result=["pedestrian_struck"],
        priority=10, urgency="visceral",
    ),
    Rule(
        id="C3",
        statement="Vehicles must not exceed the posted speed limit.",
        antecedents=["self_in_motion"],
        forbids_in_result=["exceeding_speed_limit"],
        priority=7, urgency="high",
    ),
    Rule(
        id="C4",
        statement="When two visceral rules conflict, prioritize human life.",
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
        name="stop_at_intersection",
        preconditions=["self_in_motion", "self_at_intersection"],
        add=["self_stopped"],
        remove=["self_in_motion"],
    ),
    Action(
        name="proceed_through_intersection",
        preconditions=["self_in_motion", "self_at_intersection"],
        add=["vehicle_through_intersection", "intersection_traversed"],
    ),
    Action(
        name="yield_to_pedestrian",
        preconditions=["self_in_motion", "pedestrian_in_crosswalk"],
        add=["self_stopped", "pedestrian_safe"],
        remove=["self_in_motion"],
    ),
    Action(
        name="pull_over",
        preconditions=["self_in_motion"],
        add=["self_pulled_over"],
        remove=["self_in_motion"],
    ),
    Action(
        name="slow_down_for_car",
        preconditions=["self_in_motion", "car_close_ahead"],
        add=["safe_following_car"],
    ),
    Action(
        name="maintain_safe_distance_from_bicycle",
        preconditions=["bicycle_ahead"],
        add=["safe_distance_from_bicycle"],
    ),
    Action(
        name="signal_left",
        preconditions=[],
        add=["signal_active", "signaling_left"],
    ),
    Action(
        name="signal_right",
        preconditions=[],
        add=["signal_active", "signaling_right"],
    ),
    Action(
        name="change_lane_right",
        preconditions=["signal_active"],
        add=["self_in_right_lane"],
        remove=["self_in_left_lane"],
    ),
    Action(
        name="maintain_speed",
        preconditions=["self_in_motion"],
        add=[],
    ),
    Action(
        name="do_nothing",
        preconditions=[],
        add=[],
    ),
]


# ============================================================================
# Property table — substances are road-user types
# ============================================================================

SUBSTANCE_PROPERTIES: dict[str, list[str]] = {
    "car":           ["motorized", "fast", "has_mass", "protected", "no_priority"],
    "truck":         ["motorized", "fast", "large_mass", "protected", "no_priority"],
    "bicycle":       ["human_powered", "slow", "low_mass", "unprotected", "no_priority", "wheeled"],
    "ambulance":     ["motorized", "fast", "has_mass", "protected", "emergency_priority"],
    "pedestrian":    ["human_powered", "slow", "low_mass", "unprotected", "no_priority"],
    "bus":           ["motorized", "slow", "large_mass", "protected", "no_priority"],
    # Novel cases (test substances):
    "horse_carriage": ["animal_powered", "slow", "has_mass", "unprotected", "no_priority", "wheeled"],
    "robotaxi":       ["motorized", "fast", "has_mass", "protected", "no_priority", "autonomous"],
    "fire_engine":    ["motorized", "fast", "large_mass", "protected", "emergency_priority"],
}


PROPERTY_ROLES: dict[str, str] = {
    # power source (incidental in road-safety scenarios)
    "motorized":          "power_source",
    "human_powered":      "power_source",
    "animal_powered":     "power_source",
    # speed
    "fast":               "speed_relevant",
    "slow":               "speed_relevant",
    # mass
    "has_mass":           "mass_relevant",
    "large_mass":         "mass_relevant",
    "low_mass":           "mass_relevant",
    # vulnerability
    "protected":          "vulnerability_relevant",
    "unprotected":        "vulnerability_relevant",
    # priority
    "emergency_priority": "priority_relevant",
    "no_priority":        "priority_relevant",
    # incidental
    "wheeled":            "footprint",
    "autonomous":         "control_kind",
}


def active_roles_for_scenario(facts: list[str]) -> set[str]:
    """For traffic scenarios involving other road users, the relevant roles
    are speed, mass, vulnerability, and priority. Power source is incidental.
    """
    return {
        "speed_relevant",
        "mass_relevant",
        "vulnerability_relevant",
        "priority_relevant",
    }


# ============================================================================
# Retriever tag mappings (for the existing retriever, passed in at runtime)
# ============================================================================

PREFIX_TAGS = {
    "self_":        ["driver_present"],
    "red_":         ["intersection_present"],
    "green_":       ["intersection_present"],
    "yellow_":      ["intersection_present"],
    "pedestrian_":  ["pedestrian_present", "vulnerable_present"],
    "ambulance_":   ["emergency_present"],
    "fire_engine_": ["emergency_present"],
    "car_":         ["vehicle_ahead"],
    "truck_":       ["vehicle_ahead"],
    "bicycle_":     ["bicycle_present", "vulnerable_present"],
    "horse_":       ["horse_present"],
    "robotaxi_":    ["robotaxi_present"],
    "bus_":         ["bus_present"],
    "vehicle_":     ["vehicle_ahead"],
    "intent_":      ["maneuver_planned"],
    "signal_":      ["signal_state"],
}

TAG_TO_DOMAIN = {
    "intersection_present":  "traffic_signals",
    "pedestrian_present":    "pedestrian_safety",
    "vulnerable_present":    "pedestrian_safety",
    "emergency_present":     "emergency_yielding",
    "vehicle_ahead":         "following",
    "bicycle_present":       "shared_road",
    "horse_present":         "shared_road",
    "robotaxi_present":      "shared_road",
    "bus_present":           "shared_road",
    "driver_present":        "vehicle_control",
    "maneuver_planned":      "vehicle_control",
    "signal_state":          "vehicle_control",
}

FACT_TAG_OVERRIDES = {
    "self_in_motion":          ["driver_present", "vehicle_in_motion"],
    "self_at_intersection":    ["driver_present", "intersection_present"],
    "red_light_ahead":         ["intersection_present", "must_stop"],
}
