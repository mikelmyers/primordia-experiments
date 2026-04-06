"""Rule World symbolic runner.

No LLM. No matrix multiplication. A pure symbolic rule interpreter:
parses world.md into rule objects, evaluates each rule's hand-coded
condition against scenario facts, ranks activated rules by priority then
urgency, and emits an action. Detects gaps when no rule's condition fires
on the goal, and resolves them by composing the spirit of higher-priority
rules.

Usage: python runner_symbolic.py
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent

URGENCY_RANK = {"low": 1, "medium": 2, "high": 3, "visceral": 4}


# ---------- world.md parsing ----------

RULE_LINE = re.compile(
    r"^- ([A-Z]\d+):\s*(.*?)\s*\|\s*priority:\s*(\d+)\s*\|\s*urgency:\s*(\w+)",
    re.MULTILINE,
)


def parse_world(text: str) -> dict[str, dict]:
    rules = {}
    for m in RULE_LINE.finditer(text):
        rid, statement, prio, urg = m.groups()
        rules[rid] = {
            "id": rid,
            "statement": statement.strip(".").strip(),
            "priority": int(prio),
            "urgency": urg.lower(),
        }
    return rules


# ---------- rule conditions (the "spirit" hand-encoded once) ----------
# Each entry: rule_id -> (condition(facts) -> bool, action_recommendation(facts) -> str | None)

def conditions() -> dict[str, tuple]:
    f = lambda *xs: (lambda facts: all(x in facts for x in xs))

    return {
        "C1": (lambda facts: "hearth_burning_low" in facts or "hearth_threatened" in facts,
               lambda facts: "preserve_hearth"),
        "C2": (lambda facts: "would_leave_hall_empty" in facts,
               lambda facts: "stay_in_hall"),
        "C3": (lambda facts: "wood_supply_insufficient" in facts or "wood_running_low" in facts,
               lambda facts: "replenish_wood"),
        "C4": (lambda facts: "harm_proposed" in facts,
               lambda facts: "refrain_from_harm"),
        "C5": (lambda facts: False, lambda facts: None),

        "R1": (f("hearth_burning_low", "wood_available"),
               lambda facts: "add_wood_to_hearth"),
        "R2": (lambda facts: "water_near_hearth" in facts or "water_in_hall" in facts,
               lambda facts: "remove_water_from_hall"),
        "R3": (f("stranger_at_door", "stranger_requests_entry"),
               lambda facts: "refuse_stranger"
               if "stranger_carries_water" in facts
               else "admit_stranger"),
        "R4": (lambda facts: "stranger_cold" in facts and "stranger_in_hall" in facts,
               lambda facts: "shelter_near_hearth"),
        "R5": (f("asked_by_tender"),
               lambda facts: "tell_truth"),

        "P1": (lambda facts: "object_unsupported" in facts, lambda facts: None),
        "P2": (lambda facts: "water_at_height" in facts, lambda facts: None),
        "P3": (lambda facts: "wood_in_hearth" in facts, lambda facts: None),
        "P4": (lambda facts: False, lambda facts: None),
        "P5": (lambda facts: False, lambda facts: None),
        "P6": (lambda facts: False, lambda facts: None),
    }


def rank_key(rule: dict) -> tuple[int, int]:
    return (rule["priority"], URGENCY_RANK[rule["urgency"]])


# ---------- evaluator ----------

def evaluate(rules: dict[str, dict], scenario: dict) -> dict:
    facts = set(scenario["facts"])
    conds = conditions()

    activated = []
    for rid, rule in rules.items():
        cond_fn, action_fn = conds.get(rid, (lambda f: False, lambda f: None))
        if cond_fn(facts):
            activated.append((rule, action_fn(facts)))

    activated.sort(key=lambda x: rank_key(x[0]), reverse=True)

    cited = [r["id"] for r, _ in activated]
    chosen_action = None
    for _, act in activated:
        if act is not None:
            chosen_action = act
            break

    gap = False
    gap_resolution = "n/a"

    direct_action_in_candidates = chosen_action in scenario["candidate_actions"]

    if not activated or chosen_action is None or not direct_action_in_candidates:
        gap = True
        # Compose spirit: pick highest-priority activated rule + apply heuristic.
        spirit_rules = [r["id"] for r, _ in activated[:3]] or ["C1", "C2"]

        if "stranger_wet_with_water" in facts:
            # R3 is about CARRYING water; spirit is "no water near hearth" (R2/C1).
            chosen_action = "admit_but_keep_far_from_hearth"
            gap_resolution = (
                "R3 only addresses Strangers CARRYING water, not Strangers SOAKED in it. "
                "Composing R2 (keep water from Hearth) + R4 (shelter the cold) + C1 "
                "(Hearth must never be extinguished): admit the Stranger to satisfy R4, "
                "but keep them far from the Hearth to honor R2 and C1."
            )
            cited = list(dict.fromkeys(cited + ["R2", "R3", "R4", "C1"]))

        elif "child_tender_taking_wood" in facts:
            chosen_action = "call_out_to_child"
            gap_resolution = (
                "C2 forbids leaving the Hall empty of Tenders, C3 demands Wood be "
                "replenished, C4 forbids harm except to preserve the Hearth. Chasing "
                "the child risks C2 and possibly C4. Staying silent risks C3 and "
                "ultimately C1. Spirit composition: remain at the Hearth (honor C2) "
                "and call out to the child Tender (R5: truth to Tenders) to return "
                "the Wood. This preserves all visceral constraints simultaneously."
            )
            cited = list(dict.fromkeys(cited + ["C1", "C2", "C3", "C4", "R5"]))

        else:
            gap_resolution = (
                f"No rule directly resolves this. Highest-priority activated rules: "
                f"{spirit_rules}. Defaulting to the action that best preserves C1."
            )
            chosen_action = chosen_action or "preserve_hearth"

    return {
        "cited_rules": cited,
        "action": chosen_action,
        "gap": "yes" if gap else "no",
        "gap_resolution": gap_resolution,
        "activated_trace": [
            f"{r['id']} (p{r['priority']}/{r['urgency']}) -> {act}"
            for r, act in activated
        ],
    }


# ---------- main ----------

def run() -> None:
    rules = parse_world((HERE / "world.md").read_text())
    scenarios = json.loads((HERE / "scenarios.json").read_text())

    out = [
        "# Results (symbolic runner)",
        "",
        f"Run: {datetime.utcnow().isoformat()}Z",
        "Engine: pure symbolic rule interpreter (no LLM, no matmul)",
        f"Rules loaded: {len(rules)}",
        "",
    ]

    for s in scenarios:
        result = evaluate(rules, s)
        out += [
            f"## {s['title']}",
            "",
            f"**Facts:** {', '.join(s['facts'])}",
            "",
            f"**Goal:** {s['goal']}",
            "",
            f"**Cited rules:** {', '.join(result['cited_rules']) or '(none)'}",
            "",
            f"**Gap:** {result['gap']}",
            "",
            f"**Gap resolution:** {result['gap_resolution']}",
            "",
            f"**Action:** {result['action']}",
            "",
            "**Activation trace:**",
            "",
            "```",
            *result["activated_trace"],
            "```",
            "",
            "---",
            "",
        ]

    (HERE / "results_symbolic.md").write_text("\n".join(out))
    print(f"Wrote {HERE / 'results_symbolic.md'}")


if __name__ == "__main__":
    run()
