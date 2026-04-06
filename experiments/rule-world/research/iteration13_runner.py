"""Iteration 13 — verbose structured-to-text NL output across all three domains.

Re-runs each domain's pipeline scenario-by-scenario, captures the structured
output (parsed facts, retrieval, engine evaluations + choice, planner
result, v4 analog log), feeds it to the domain-agnostic explainer with
the appropriate per-domain humanization dictionary, and writes a single
markdown report containing every scenario's English explanation.

Architectural contract: the existing runners (runner_symbolic.py,
traffic_runner.py, kitchen_runner.py) are NOT modified. This runner
duplicates the minimum pipeline wiring needed to drive the explainer.
That preserves the iteration 12 contract while letting iteration 13
add the NL layer cleanly.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULE_WORLD = ROOT
TRAFFIC_WORLD = ROOT.parent / "traffic-world"
KITCHEN_WORLD = ROOT.parent / "kitchen-world"

sys.path.insert(0, str(RULE_WORLD))
sys.path.insert(0, str(TRAFFIC_WORLD))
sys.path.insert(0, str(KITCHEN_WORLD))

from engine import reason, plan_sequence  # noqa: E402
from rule_store import RuleStore, migrate_authored_rules  # noqa: E402
from retriever import retrieve  # noqa: E402
from abstractor import (  # noqa: E402
    crystallize_by_hdc_v4_token_projection,
    synthesize_actions_by_analogy,
    select_v4_analog,
    suppress_pre_v4_crystallizations,
)
from hdc import Codebook  # noqa: E402
from explainer import ExplanationInputs, explain  # noqa: E402


def _fact_contains_substance(fact: str, sub: str) -> bool:
    sub_toks = sub.split("_")
    fact_toks = fact.split("_")
    n = len(sub_toks)
    for i in range(len(fact_toks) - n + 1):
        if fact_toks[i : i + n] == sub_toks:
            return True
    return False


def _run_pipeline_for_scenario(
    domain_name: str,
    scenario: dict,
    parse_fn,
    ALL_RULES,
    actions_list,
    SUBSTANCE_PROPERTIES,
    PROPERTY_ROLES,
    active_roles_fn,
    store,
    codebook,
    v4_scenario_ids: set[int],
    prefix_tags=None,
    tag_to_domain=None,
    fact_tag_overrides=None,
    rule_statements: dict | None = None,
    humanizer=None,
    relevance_threshold: float = 0.20,
):
    """Drive one scenario through the full pipeline and return ExplanationInputs."""
    desc = scenario["description"]
    parsed = parse_fn(desc)

    v4_targets: list[str] = []
    v4_analogs: dict[str, tuple[str, float]] = {}
    v4_projected: dict[str, list[str]] = {}
    v4_synthesized: dict[str, list[str]] = {}

    if scenario["id"] in v4_scenario_ids:
        active_roles = active_roles_fn(parsed["facts"])

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
        v4_targets = targets

        for sub in targets:
            new_rules, _log = crystallize_by_hdc_v4_token_projection(
                unhandled_fact="",
                facts=parsed["facts"],
                store=store,
                properties_by_substance=SUBSTANCE_PROPERTIES,
                property_roles=PROPERTY_ROLES,
                active_roles=active_roles,
                codebook=codebook,
                target_substance=sub,
                relevance_threshold=relevance_threshold,
            )
            written: list[str] = []
            for r in new_rules:
                src_id = r.id.split("~")[0]
                src_meta = store.get_meta(src_id)
                if src_meta:
                    new_tags = list(set(src_meta["context_tags"] + [f"{sub}_present"]))
                    store.add_rule(
                        r, domain=src_meta["domain"], context_tags=new_tags,
                        source="crystallized_v4", confidence=0.4,
                    )
                    written.append(r.id)
            v4_projected[sub] = written
            if new_rules:
                suppress_pre_v4_crystallizations(store, sub)

            peer, sim, _ = select_v4_analog(
                "", parsed["facts"], SUBSTANCE_PROPERTIES,
                PROPERTY_ROLES, active_roles, codebook,
                target_substance=sub,
            )
            if peer is not None:
                v4_analogs[sub] = (peer, float(sim))
                new_acts, _alog = synthesize_actions_by_analogy(
                    new_obj=sub, peer=peer, action_library=actions_list,
                )
                synth: list[str] = []
                for a in new_acts:
                    actions_list.append(a)
                    synth.append(a.name)
                v4_synthesized[sub] = synth
            else:
                v4_synthesized[sub] = []

    retrieval = retrieve(
        parsed["facts"], parsed["goal"], store,
        prefix_tags=prefix_tags or {},
        tag_to_domain=tag_to_domain or {},
        fact_tag_overrides=fact_tag_overrides or {},
    ) if (prefix_tags or tag_to_domain or fact_tag_overrides) else retrieve(
        parsed["facts"], parsed["goal"], store,
    )
    active_rules = retrieval["active_rules"]
    active_rule_ids = [r.id for r in active_rules]

    result = reason(parsed["facts"], parsed["goal"], active_rules, actions_list)
    plan = plan_sequence(parsed["facts"], parsed["goal"], active_rules,
                         actions_list, max_depth=3)

    return ExplanationInputs(
        domain_name=domain_name,
        scenario_title=scenario["title"],
        scenario_description=desc,
        parsed_facts=list(parsed["facts"]),
        parsed_goal=list(parsed["goal"]),
        retrieval_active_rule_ids=active_rule_ids,
        rule_statements=rule_statements or {},
        initial_state_after_chain=list(result["initial_state_after_chain"]),
        evaluations=list(result["all_evaluations"]),
        chosen=result["best"],
        gap=bool(result["gap"]),
        gap_reasons=list(result.get("gap_reasons", [])),
        plan_sequence=list(plan.get("sequence", []) or []),
        plan_score=int(plan.get("score", 0) or 0),
        v4_targets=v4_targets,
        v4_analogs=v4_analogs,
        v4_projected_rules=v4_projected,
        v4_synthesized_actions=v4_synthesized,
        humanizer=humanizer,
    )


# ============================================================================
# Domain drivers
# ============================================================================

def run_rule_world(out_lines: list[str]) -> int:
    import world_structured as rw
    import parser as rw_parser
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rule_world_explanations", RULE_WORLD / "explanations.py",
    )
    rw_exp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rw_exp)

    store_path = RULE_WORLD / "rule_store.json"
    if store_path.exists():
        store_path.unlink()
    store = migrate_authored_rules(force=True)

    codebook = Codebook(seed=42)
    actions_list = list(rw.ACTIONS)
    rule_statements = rw_exp.build_rule_statements()
    humanizer = rw_exp.build_humanizer()

    scenarios = json.loads((RULE_WORLD / "scenarios.json").read_text())
    out_lines.append("# Iteration 13 — Rule-world explanations")
    out_lines.append("")
    n = 0
    for scen in scenarios:
        inputs = _run_pipeline_for_scenario(
            domain_name="rule-world",
            scenario=scen,
            parse_fn=rw_parser.parse,
            ALL_RULES=rw.ALL_RULES,
            actions_list=actions_list,
            SUBSTANCE_PROPERTIES=rw.SUBSTANCE_PROPERTIES,
            PROPERTY_ROLES=rw.PROPERTY_ROLES,
            active_roles_fn=rw.active_roles_for_scenario,
            store=store,
            codebook=codebook,
            v4_scenario_ids={11},
            rule_statements=rule_statements,
            humanizer=humanizer,
            relevance_threshold=0.50,
        )
        out_lines.append(explain(inputs))
        out_lines.append("---")
        out_lines.append("")
        n += 1
    return n


def run_traffic_world(out_lines: list[str]) -> int:
    # Reset traffic_world module imports because the parser/rules names
    # collide with rule-world's `parser` module.
    for mod in ("traffic_rules", "traffic_parser", "explanations"):
        if mod in sys.modules:
            del sys.modules[mod]

    sys.path.insert(0, str(TRAFFIC_WORLD))
    import traffic_rules as tw
    import traffic_parser as tw_parser
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "traffic_explanations", TRAFFIC_WORLD / "explanations.py",
    )
    tw_exp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tw_exp)

    store_path = TRAFFIC_WORLD / "traffic_rule_store.json"
    if store_path.exists():
        store_path.unlink()
    store = RuleStore(path=store_path)

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
    for r in tw.ALL_RULES:
        domain, tags = TAG_MAP.get(r.id, ("misc", []))
        store.add_rule(r, domain=domain, context_tags=tags,
                       source="authored", confidence=1.0)

    codebook = Codebook(seed=42)
    actions_list = list(tw.ACTIONS)
    rule_statements = tw_exp.build_rule_statements()
    humanizer = tw_exp.build_humanizer()

    scenarios = json.loads((TRAFFIC_WORLD / "traffic_scenarios.json").read_text())
    out_lines.append("# Iteration 13 — Traffic-world explanations")
    out_lines.append("")
    n = 0
    for scen in scenarios:
        inputs = _run_pipeline_for_scenario(
            domain_name="traffic-world",
            scenario=scen,
            parse_fn=tw_parser.parse,
            ALL_RULES=tw.ALL_RULES,
            actions_list=actions_list,
            SUBSTANCE_PROPERTIES=tw.SUBSTANCE_PROPERTIES,
            PROPERTY_ROLES=tw.PROPERTY_ROLES,
            active_roles_fn=tw.active_roles_for_scenario,
            store=store,
            codebook=codebook,
            v4_scenario_ids={6, 7, 8},
            prefix_tags=tw.PREFIX_TAGS,
            tag_to_domain=tw.TAG_TO_DOMAIN,
            fact_tag_overrides=tw.FACT_TAG_OVERRIDES,
            rule_statements=rule_statements,
            humanizer=humanizer,
            relevance_threshold=0.20,
        )
        out_lines.append(explain(inputs))
        out_lines.append("---")
        out_lines.append("")
        n += 1
    return n


def run_kitchen_world(out_lines: list[str]) -> int:
    for mod in ("kitchen_rules", "kitchen_parser", "explanations"):
        if mod in sys.modules:
            del sys.modules[mod]

    sys.path.insert(0, str(KITCHEN_WORLD))
    import kitchen_rules as kw
    import kitchen_parser as kw_parser
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kitchen_explanations", KITCHEN_WORLD / "explanations.py",
    )
    kw_exp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kw_exp)

    store_path = KITCHEN_WORLD / "kitchen_rule_store.json"
    if store_path.exists():
        store_path.unlink()
    store = RuleStore(path=store_path)

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
    for r in kw.ALL_RULES:
        domain, tags = TAG_MAP.get(r.id, ("misc", []))
        store.add_rule(r, domain=domain, context_tags=tags,
                       source="authored", confidence=1.0)

    codebook = Codebook(seed=42)
    actions_list = list(kw.ACTIONS)
    rule_statements = kw_exp.build_rule_statements()
    humanizer = kw_exp.build_humanizer()

    scenarios = json.loads((KITCHEN_WORLD / "kitchen_scenarios.json").read_text())
    out_lines.append("# Iteration 13 — Kitchen-world explanations")
    out_lines.append("")
    n = 0
    for scen in scenarios:
        inputs = _run_pipeline_for_scenario(
            domain_name="kitchen-world",
            scenario=scen,
            parse_fn=kw_parser.parse,
            ALL_RULES=kw.ALL_RULES,
            actions_list=actions_list,
            SUBSTANCE_PROPERTIES=kw.SUBSTANCE_PROPERTIES,
            PROPERTY_ROLES=kw.PROPERTY_ROLES,
            active_roles_fn=kw.active_roles_for_scenario,
            store=store,
            codebook=codebook,
            v4_scenario_ids={7, 8, 9},
            prefix_tags=kw.PREFIX_TAGS,
            tag_to_domain=kw.TAG_TO_DOMAIN,
            fact_tag_overrides=kw.FACT_TAG_OVERRIDES,
            rule_statements=rule_statements,
            humanizer=humanizer,
            relevance_threshold=0.20,
        )
        out_lines.append(explain(inputs))
        out_lines.append("---")
        out_lines.append("")
        n += 1
    return n


def main():
    header = [
        "# Iteration 13 — Verbose NL explanations across N=3 domains",
        "",
        "Each explanation below was generated by a domain-agnostic template",
        "grammar reading the structured output of the same pipeline iterations",
        "0–12 produced. No language model produced any of these words. Every",
        "phrase traces back to a parsed fact, a fired rule, a chosen action,",
        "or a hand-authored predicate humanization entry.",
        "",
        "---",
        "",
    ]
    out: list[str] = []
    n_rw = run_rule_world(out)
    out.append("")
    n_tw = run_traffic_world(out)
    out.append("")
    n_kw = run_kitchen_world(out)

    full = header + out + [
        "",
        "---",
        "",
        f"## Summary: {n_rw + n_tw + n_kw} scenarios explained "
        f"({n_rw} rule-world + {n_tw} traffic-world + {n_kw} kitchen-world)",
        "",
        "Every explanation above was produced by a ~250-line template grammar",
        "consuming the structured pipeline output and a hand-authored",
        "predicate humanization dictionary per domain (~40-60 entries each).",
        "Zero matrix multiplication. Zero learned model. Every word auditable.",
        "",
    ]

    out_path = Path(__file__).parent / "iteration13_explanations.md"
    out_path.write_text("\n".join(full))
    print(f"[wrote {out_path}]")
    print(f"[scenarios explained: rule-world={n_rw} traffic-world={n_tw} kitchen-world={n_kw}]")


if __name__ == "__main__":
    main()
