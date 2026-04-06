"""Rule World symbolic runner — forward chaining edition.

NO scenario fingerprint branches. NO hard-coded gap resolutions. NO LLM.

Each scenario is (facts, goal). engine.reason() does forward chaining over
the rules in world_structured.ALL_RULES, simulates every action in
world_structured.ACTIONS, and emits the best survivor. If the best survivor
still has unmet obligations, the runner reports the gap honestly: which
rules went unsatisfied, and what the engine could and could not derive.

Usage: python runner_symbolic.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from engine import reason
from world_structured import ALL_RULES, ACTIONS

HERE = Path(__file__).parent


def render_eval(ev: dict) -> list[str]:
    out = [
        f"  - **{ev['action']}** (score {ev['score']}, goal_met={ev['goal_met']})",
    ]
    if ev["visceral_violations"]:
        out.append(f"    - VISCERAL VIOLATIONS: {ev['visceral_violations']}")
    if ev["fulfilled"]:
        out.append(f"    - fulfilled: {ev['fulfilled']}")
    if ev["violated"]:
        out.append(f"    - violated: {ev['violated']}")
    if ev["chain_trace"]:
        out.append(f"    - post-action derivations:")
        for line in ev["chain_trace"]:
            out.append(f"      - {line}")
    return out


def run() -> None:
    scenarios = json.loads((HERE / "scenarios.json").read_text())

    out = [
        "# Results (symbolic forward-chaining engine)",
        "",
        f"Run: {datetime.utcnow().isoformat()}Z",
        "Engine: pure forward chaining over structured rule tuples (no LLM, no matmul)",
        f"Rules loaded: {len(ALL_RULES)} | Actions in library: {len(ACTIONS)}",
        "",
        "No scenario-specific code anywhere in engine.py, world_structured.py, or this file.",
        "Every answer is derived at runtime from the rule set + action library.",
        "",
        "---",
        "",
    ]

    for s in scenarios:
        result = reason(s["facts"], s["goal"], ALL_RULES, ACTIONS)
        best = result["best"]

        out += [
            f"## {s['title']}",
            "",
            f"**Initial facts:** {result['initial_facts']}",
            "",
            f"**Goal predicates:** {result['goal_predicates']}",
            "",
        ]

        if result["init_chain_trace"]:
            out += ["**Initial forward-chain derivations:**", ""]
            for line in result["init_chain_trace"]:
                out.append(f"- {line}")
            out.append("")

        out += [
            f"**State after initial chain:** {result['initial_state_after_chain']}",
            "",
            "**All action evaluations (best first):**",
            "",
        ]
        for ev in result["all_evaluations"]:
            out += render_eval(ev)
        out.append("")

        if best is None:
            out += ["**ENGINE FAILURE:** no action survived. ", ""]
        else:
            out += [
                f"**CHOSEN ACTION:** `{best['action']}`",
                "",
                f"**Triggered rules at decision time:** {best['triggered_rule_ids']}",
                "",
                f"**Score:** {best['score']}",
                "",
            ]

        out += [
            f"**Gap encountered:** {'yes' if result['gap'] else 'no'}",
            "",
        ]
        if result["gap"]:
            out += ["**Gap reasons (honest report — composition failures):**", ""]
            for r in result["gap_reasons"]:
                out.append(f"- {r}")
            out.append("")
            out += [
                "**How the engine resolved (or failed to resolve) the gap:**",
                "",
                "The chosen action above is whatever scored highest after disqualifying",
                "actions that would violate visceral constraints. If unmet obligations",
                "remain, the engine has not 'resolved' the gap — it has revealed exactly",
                "which predicates pure forward chaining cannot bridge.",
                "",
            ]

        out += ["---", ""]

    (HERE / "results_symbolic.md").write_text("\n".join(out))
    print(f"Wrote {HERE / 'results_symbolic.md'}")


if __name__ == "__main__":
    run()
