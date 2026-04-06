"""Kitchen-world runner. Third transfer test for the rule-world architecture.

Imports rule-world's engine, retriever, abstractor, HDC, compression, and
rule_store WITHOUT MODIFICATION. If this works, the architecture is general
across three unrelated domains. If it breaks, the failure points to a
hidden assumption that survived the rule-world → traffic-world transfer.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
RULE_WORLD = HERE.parent / "rule-world"
sys.path.insert(0, str(RULE_WORLD))

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

from kitchen_rules import (  # noqa: E402
    ALL_RULES,
    ACTIONS,
    SUBSTANCE_PROPERTIES,
    PROPERTY_ROLES,
    PREFIX_TAGS,
    TAG_TO_DOMAIN,
    FACT_TAG_OVERRIDES,
    active_roles_for_scenario,
)
from kitchen_parser import parse  # noqa: E402


V4_WRITE_SCENARIOS = {7, 8, 9}


def render_eval(ev):
    out = [f"  - **{ev['action']}** (score {ev['score']}, goal_met={ev['goal_met']})"]
    if ev["visceral_violations"]:
        out.append(f"    - VISCERAL VIOLATIONS: {ev['visceral_violations']}")
    if ev["violated"]:
        out.append(f"    - violated: {ev['violated']}")
    return out


TAG_MAP = {
    "P-burner-flame":            ("stove", ["stove_active"]),
    "P-oil-near-flame":          ("stove", ["stove_active", "oil_present"]),
    "P-water-on-fire":           ("fire_response", ["fire_present", "water_present"]),
    "P-water-grease-fire":       ("fire_response", ["fire_present", "water_present"]),
    "P-raw-meat-contamination":  ("food_handling", ["raw_food_present"]),
    "P-knife-edge":              ("tool_handling", ["knife_present"]),
    "P-vegetable-knife":         ("food_prep", ["vegetable_present", "knife_present"]),
    "R1": ("stove", ["stove_active"]),
    "R2": ("food_handling", ["raw_food_present"]),
    "R3": ("tool_handling", ["knife_present"]),
    "R4": ("food_prep", ["vegetable_present", "mealtime"]),
    "R5": ("fire_response", ["fire_present"]),
    "C1": ("meta", []),
    "C2": ("meta", []),
    "C3": ("meta", []),
    "C4": ("meta", []),
}


def fresh_store_with_authored_rules() -> RuleStore:
    store_path = HERE / "kitchen_rule_store.json"
    if store_path.exists():
        store_path.unlink()
    store = RuleStore(path=store_path)
    for r in ALL_RULES:
        domain, tags = TAG_MAP.get(r.id, ("misc", []))
        store.add_rule(r, domain=domain, context_tags=tags,
                       source="authored", confidence=1.0)
    return store


def _fact_contains_substance(fact: str, sub: str) -> bool:
    sub_toks = sub.split("_")
    fact_toks = fact.split("_")
    n = len(sub_toks)
    for i in range(len(fact_toks) - n + 1):
        if fact_toks[i : i + n] == sub_toks:
            return True
    return False


def run_scenario(scenario, store, codebook, current_actions, compression):
    out: list[str] = []
    title = scenario["title"]
    desc = scenario["description"]
    out += [f"## {title}", "", f"**Description:** {desc}", ""]

    parsed = parse(desc)
    out += [
        "### Parser",
        "",
        f"- facts: {parsed['facts']}",
        f"- goal:  {parsed['goal']}",
        "",
    ]

    if scenario["id"] in V4_WRITE_SCENARIOS:
        active_roles = active_roles_for_scenario(parsed["facts"])

        substances_in_play: set[str] = set()
        for sub in SUBSTANCE_PROPERTIES:
            if any(_fact_contains_substance(f, sub) for f in parsed["facts"]):
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
                relevance_threshold=0.20,
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

    if scenario["id"] in V4_WRITE_SCENARIOS:
        active_roles = active_roles_for_scenario(parsed["facts"])
        for sub in sorted({s for s in SUBSTANCE_PROPERTIES
                           if any(_fact_contains_substance(f, s) for f in parsed["facts"])}):
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

    scenarios = json.loads((HERE / "kitchen_scenarios.json").read_text())
    out = [
        "# Results — kitchen-world (third transfer test)",
        "",
        f"Run: {datetime.utcnow().isoformat()}Z",
        "Engine: rule-world machinery, unmodified, on a third unrelated domain.",
        f"Authored rules: {len(ALL_RULES)} | actions: {len(ACTIONS)} | "
        f"substances: {len(SUBSTANCE_PROPERTIES)}",
        "",
        "---",
        "",
    ]
    for s in scenarios:
        out += run_scenario(s, store, codebook, current_actions, compression)

    (HERE / "results_kitchen.md").write_text("\n".join(out))
    print(f"Wrote {HERE / 'results_kitchen.md'}")


if __name__ == "__main__":
    run()
