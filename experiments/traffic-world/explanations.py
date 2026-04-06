"""Traffic-world humanization dictionary for the iteration 13 explainer."""

PREDICATE_PHRASES: dict[str, str] = {
    # Self / vehicle state
    "self_in_motion":            "your vehicle is in motion",
    "self_stopped":              "your vehicle is stopped",
    "self_pulled_over":          "your vehicle is pulled over",
    "self_at_intersection":      "you are at an intersection",
    "self_in_left_lane":         "you are in the left lane",
    "self_in_right_lane":        "you are in the right lane",
    "self_actively_driving":     "you are actively driving",
    # Lights / signals
    "red_light_ahead":           "there is a red light ahead",
    "green_light_ahead":         "there is a green light ahead",
    "yellow_light_ahead":        "there is a yellow light ahead",
    "intersection_safe":         "the intersection is safe to cross",
    "intersection_traversed":    "the intersection has been traversed",
    "vehicle_through_intersection": "the vehicle has gone through the intersection",
    # Pedestrians
    "pedestrian_in_crosswalk":   "there is a pedestrian in the crosswalk",
    "pedestrian_safe":           "the pedestrian is safe",
    "pedestrian_struck":         "a pedestrian has been struck",
    # Other road users
    "ambulance_behind":          "there is an ambulance behind you",
    "fire_engine_behind":        "there is a fire engine behind you",
    "car_close_ahead":           "a car is close ahead of you",
    "bicycle_ahead":             "there is a bicycle ahead",
    "horse_carriage_ahead":      "there is a horse-drawn carriage ahead",
    "horse_carriage_close_ahead": "a horse-drawn carriage is close ahead",
    "robotaxi_ahead":            "there is a robotaxi ahead",
    "robotaxi_close_ahead":      "a robotaxi is close ahead",
    "bus_unloading_ahead":       "a bus is unloading passengers ahead",
    # Following / safety
    "safe_following_car":        "you are following the car at a safe distance",
    "safe_distance_from_bicycle": "you are maintaining a safe distance from the bicycle",
    "safe_distance_from_horse_carriage": "you are maintaining a safe distance from the horse-drawn carriage",
    "safe_following_robotaxi":   "you are following the robotaxi at a safe distance",
    "emergency_path_clear":      "the emergency vehicle's path is clear",
    # Maneuvers
    "intent_to_turn":            "you intend to turn",
    "signal_active":             "your turn signal is active",
    "signaling_left":            "you are signaling left",
    "signaling_right":           "you are signaling right",
    # Constraints
    "collision_occurred":        "a collision has occurred",
    "exceeding_speed_limit":     "you are exceeding the speed limit",
    "situation_resolved":        "the situation is resolved",
}


ACTION_PHRASES: dict[str, str] = {
    "stop_at_intersection":              "stop at the intersection",
    "proceed_through_intersection":      "proceed through the intersection",
    "yield_to_pedestrian":               "yield to the pedestrian",
    "pull_over":                         "pull over to the side of the road",
    "slow_down_for_car":                 "slow down to a safe following distance",
    "maintain_safe_distance_from_bicycle": "maintain a safe distance from the bicycle",
    "signal_left":                       "signal left",
    "signal_right":                      "signal right",
    "change_lane_right":                 "change to the right lane",
    "maintain_speed":                    "maintain current speed",
    "do_nothing":                        "do nothing",
}


def build_rule_statements() -> dict[str, str]:
    from traffic_rules import ALL_RULES
    return {r.id: r.statement for r in ALL_RULES}


def build_humanizer():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "rule-world"))
    from explainer import Humanizer
    return Humanizer(PREDICATE_PHRASES, ACTION_PHRASES)
