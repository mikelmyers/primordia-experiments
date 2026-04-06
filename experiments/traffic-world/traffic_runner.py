"""Traffic-world runner.

Imports rule-world's engine, retriever, abstractor, HDC, compression, and
rule_store WITHOUT MODIFICATION (with one tiny exception in retriever.py
which now accepts optional tag-mapping parameters with backward-compatible
defaults). Runs traffic scenarios end-to-end.

If this works, the rule-world architecture transfers cleanly. If it
breaks, the failure points to a hidden domain-specific assumption.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
RULE_WORLD = HERE.parent / "rule-world"
sys.path.insert(0, str(RULE_WORLD))

# Imports from rule-world. NOTHING is rewritten.
from engine import reason, plan_sequence  # noqa: E402
from rule_store import RuleStore  # noqa: E402
from retriever import retrieve  # noqa: E402
from abstractor import (  # noqa: E402
    crystallize_by_hdc_v4_token_projection,
    synthesize_actions_by_analogy,
    select_v4_analog,
    suppress_pre_v4_crystallizations,
)
from hdc import Codebook  # noqa: E402
from compression import CompressionAnalog  # noqa: E402

# Traffic-world domain bindings.
from traffic_rules import (  # noqa: E402
    ALL_RULES,
    ACTIONS,
    SUBSTANCE_PROPERTIES,
    PROPERTY_ROLES,
    PREFIX_TAGS,
    TAG_TO_DOMAIN,
    FACT_TAG_OVERRIDES,
    active_roles_for_scenario,
)
from traffic_parser import parse  # noqa: E402


# v4 production write fires for the novel-substance scenarios so the
# engine sees the projected rules and synthesized actions on the same turn.
V4_WRITE_SCENARIOS = {6, 7, 8}


def render_eval(ev):
    out = [f"  - **{ev['action']}** (score {ev['score']}, goal_met={ev['goal_met']})"]
    if ev["visceral_violations"]:
        out.append(f"    - VISCERAL VIOLATIONS: {ev['visceral_violations']}")
    if ev["violated"]:
        out.append(f"    - violated: {ev['violated']}")
    return out


def fresh_store_with_authored_rules() -> RuleStore:
    """Build a fresh traffic-world store. Migrate ALL_RULES with hand-tagged
    domains/contexts so the retriever has something to filter on.
    """
    store_path = HERE / "traffic_rule_store.json"
    if store_path.exists():
        store_path.unlink()
    store = RuleStore(path=store_path)

    # Minimal hand-tagging for traffic rules. Same shape as rule-world's TAG_MAP.
    TAG_MAP = {
        "P-attendance-driving":  ("vehicle_control", ["driver_present"]),
        "P-stopped-safe":        ("traffic_signals", ["intersection_present"]),
        "P-pulled-over":         ("emergency_yielding", ["driver_present"]),
        "R1": ("traffic_signals", ["intersection_present", "must_stop"]),
        "R2": ("pedestrian_safety", ["pedestrian_present", "vulnerable_present"]),
        "R3": ("emergency_yielding", ["emergency_present"]),
        "R4": ("vehicle_control", ["maneuver_planned"]),
        "R5": ("following", ["vehicle_ahead"]),
        "R6": ("shared_road", ["bicycle_present", "vulnerable_present"]),
        "R7": ("shared_road", ["bus_present"]),
        "C1": ("vehicle_control", []),
        "C2": ("pedestrian_safety", []),
        "C3": ("vehicle_control", []),
        "C4": ("meta", []),
    }

    for r in ALL_RULES:
        domain, tags = TAG_MAP.get(r.id, ("misc", []))
        store.add_rule(r, domain=domain, context_tags=tags,
                       source="authored", confidence=1.0)
    return store


def run_scenario(scenario, store, codebook, current_actions, compression):
    out: list[str] = []
    title = scenario["title"]
    desc = scenario["description"]
    out += [f"## {title}", "", f"**Description:** {desc}", ""]

    # Layer 3 — parser
    parsed = parse(desc)
    out += [
        "### Parser",
        "",
        f"- facts: {parsed['facts']}",
        f"- goal:  {parsed['goal']}",
        "",
    ]

    # Layer 2′ — v4 production write for designated scenarios
    if scenario["id"] in V4_WRITE_SCENARIOS:
        active_roles = active_roles_for_scenario(parsed["facts"])

        def fact_contains_substance(fact: str, sub: str) -> bool:
            sub_toks = sub.split("_")
            fact_toks = fact.split("_")
            n = len(sub_toks)
            for i in range(len(fact_toks) - n + 1):
                if fact_toks[i : i + n] == sub_toks:
                    return True
            return False

        substances_in_play: set[str] = set()
        for sub in SUBSTANCE_PROPERTIES:
            if any(fact_contains_substance(f, sub) for f in parsed["facts"]):
                substances_in_play.add(sub)

        already_v4 = {
            e["id"].split("~")[-1].replace("_v4", "")
            for e in store.all_entries(include_suppressed=True)
            if e.get("source") == "crystallized_v4"
        }
        targets = sorted(substances_in_play - already_v4)
        out += [
            "### v4 PRODUCTION WRITE",
            "",
            f"- substances in play: {sorted(substances_in_play)}",
            f"- v4 targets:         {targets}",
            f"- active roles:       {sorted(active_roles)}",
            "",
        ]
        for sub in targets:
            out.append(f"#### target: `{sub}`")
            new_rules, log = crystallize_by_hdc_v4_token_projection(
                unhandled_fact="",
                facts=parsed["facts"],
                store=store,
                properties_by_substance=SUBSTANCE_PROPERTIES,
                property_roles=PROPERTY_ROLES,
                active_roles=active_roles,
                codebook=codebook,
                target_substance=sub,
                relevance_threshold=0.20,  # traffic-world: rules use abstract obligation tokens
            )
            for line in log:
                out.append(f"  {line}")
            for r in new_rules:
                src_id = r.id.split("~")[0]
                src_meta = store.get_meta(src_id)
                if src_meta:
                    new_tags = list(set(src_meta["context_tags"] + [f"{sub}_present"]))
                    store.add_rule(
                        r, domain=src_meta["domain"],
                        context_tags=new_tags,
                        source="crystallized_v4", confidence=0.4,
                    )
                    out.append(f"  ✓ wrote {r.id}")
            if new_rules:
                hyg = suppress_pre_v4_crystallizations(store, sub)
                for line in hyg:
                    out.append(f"  {line}")

            peer, sim, _ = select_v4_analog(
                "", parsed["facts"], SUBSTANCE_PROPERTIES,
                PROPERTY_ROLES, active_roles, codebook,
                target_substance=sub,
            )
            if peer is not None:
                out.append(f"  analog peer for action synthesis: `{peer}` (sim {sim:+.4f})")
                new_acts, alog = synthesize_actions_by_analogy(
                    new_obj=sub, peer=peer, action_library=current_actions
                )
                for line in alog:
                    out.append(line)
                for a in new_acts:
                    current_actions.append(a)
                    out.append(f"  ✓ added action `{a.name}` to runtime library")
            out.append("")

    # Layer 1 — retriever (with traffic-world tag mappings)
    retrieval = retrieve(
        parsed["facts"], parsed["goal"], store,
        prefix_tags=PREFIX_TAGS,
        tag_to_domain=TAG_TO_DOMAIN,
        fact_tag_overrides=FACT_TAG_OVERRIDES,
    )
    active_rules = retrieval["active_rules"]
    out += [
        "### Retriever",
        "",
        f"- store size:    {retrieval['total_in_store']}",
        f"- context tags:  {retrieval['context_tags']}",
        f"- domains:       {retrieval['domains']}",
        f"- active window: {len(active_rules)} rules → {[r.id for r in active_rules]}",
        "",
    ]

    # Engine — single-action
    result = reason(parsed["facts"], parsed["goal"], active_rules, current_actions)
    out += [
        "### Engine (single-action)",
        "",
        f"- initial state after chain: {result['initial_state_after_chain']}",
        "",
        "- evaluations (best 5):",
    ]
    for ev in result["all_evaluations"][:5]:
        out += render_eval(ev)
    if result["best"]:
        out += [
            "",
            f"- **CHOSEN:** `{result['best']['action']}` (score {result['best']['score']})",
        ]
    out += [
        "",
        f"- gap: {result['gap']}",
    ]
    if result["gap"]:
        for r in result["gap_reasons"]:
            out.append(f"  - {r}")
    out.append("")

    # Planner
    plan = plan_sequence(parsed["facts"], parsed["goal"], active_rules,
                         current_actions, max_depth=3)
    out += [
        "### Planner (depth 3)",
        "",
        f"- nodes: {plan['nodes_explored']}",
        f"- best sequence: {plan['sequence']}",
        f"- best score:    {plan['score']}",
        "",
    ]
    if plan["violations"]:
        out.append(f"- remaining violations: {plan['violations']}")
        out.append("")

    # v5 compression-based analog (read-only comparison)
    if scenario["id"] in V4_WRITE_SCENARIOS:
        active_roles = active_roles_for_scenario(parsed["facts"])

        def fact_contains_substance(fact: str, sub: str) -> bool:
            sub_toks = sub.split("_")
            fact_toks = fact.split("_")
            n = len(sub_toks)
            for i in range(len(fact_toks) - n + 1):
                if fact_toks[i : i + n] == sub_toks:
                    return True
            return False

        for sub in sorted({s for s in SUBSTANCE_PROPERTIES
                           if any(fact_contains_substance(f, s) for f in parsed["facts"])}):
            plain = compression.predict(sub, SUBSTANCE_PROPERTIES[sub])
            rw = compression.predict_role_weighted(
                sub, SUBSTANCE_PROPERTIES[sub], PROPERTY_ROLES, active_roles
            )
            out += [
                "### Compression analog baseline (v5)",
                "",
                f"- target substance:        `{sub}`",
                f"- plain prediction:        {plain}",
                f"- role-weighted prediction: {rw}",
                "",
            ]
    out += ["---", ""]
    return out


def run() -> None:
    store = fresh_store_with_authored_rules()
    codebook = Codebook(seed=42)
    compression = CompressionAnalog(SUBSTANCE_PROPERTIES)
    current_actions = list(ACTIONS)

    scenarios = json.loads((HERE / "traffic_scenarios.json").read_text())
    out = [
        "# Results — traffic-world (architecture transfer test)",
        "",
        f"Run: {datetime.utcnow().isoformat()}Z",
        "Engine: rule-world machinery, unmodified, on a fresh domain.",
        f"Authored rules: {len(ALL_RULES)} | actions: {len(ACTIONS)} | "
        f"substances: {len(SUBSTANCE_PROPERTIES)}",
        "",
        "---",
        "",
    ]
    for s in scenarios:
        out += run_scenario(s, store, codebook, current_actions, compression)

    (HERE / "results_traffic.md").write_text("\n".join(out))
    print(f"Wrote {HERE / 'results_traffic.md'}")


if __name__ == "__main__":
    run()
