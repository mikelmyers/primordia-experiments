"""Iteration 12 — third domain transfer + v4-only inducer across N=3 domains.

Tests two things:

1. The full architecture (engine, retriever, abstractor, planner, HDC,
   compression, property inducer) transfers to a third unrelated domain
   (kitchen-world) without modification.
2. The iteration-11 v4-only property induction reproduces the hand-authored
   analog choices on the kitchen-world adversarial set, confirming the
   ~5/6 result was not specific to rule-world + traffic-world.

This runner only does the inducer comparison. The full pipeline run is
in `experiments/kitchen-world/kitchen_runner.py` and produces
`results_kitchen.md`. Run that first.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "traffic-world"))
sys.path.insert(0, str(ROOT.parent / "kitchen-world"))

import world_structured as rw  # noqa: E402
import parser as rw_parser  # noqa: E402
import traffic_rules as tw  # noqa: E402
import traffic_parser as tw_parser  # noqa: E402
import kitchen_rules as kw  # noqa: E402
import kitchen_parser as kw_parser  # noqa: E402
from compression import CompressionAnalog  # noqa: E402
from property_inducer import induce_property_table  # noqa: E402


@dataclass
class StoredRule:
    antecedents: list
    derives: list
    requires_in_result: list
    forbids_in_result: list


def _load_v4(store_path: Path):
    if not store_path.exists():
        return []
    data = json.loads(store_path.read_text())
    store = list(data.values())[0]
    out = []
    for rid, r in store.items():
        if r.get("source") != "crystallized_v4":
            continue
        out.append((rid, StoredRule(
            antecedents=r.get("antecedents", []) or [],
            derives=r.get("derives", []) or [],
            requires_in_result=r.get("requires_in_result", []) or [],
            forbids_in_result=r.get("forbids_in_result", []) or [],
        )))
    return out


def _gather_observations(scenarios_path: Path, parser_module):
    facts: set[str] = set()
    for scen in json.loads(scenarios_path.read_text()):
        parsed = parser_module.parse(scen["description"])
        facts.update(parsed["facts"])
        facts.update(parsed.get("goal", []))
    return sorted(facts)


def _format(ranking, k=3):
    if not ranking:
        return "(none)"
    return ", ".join(f"{n}:{s}" for n, s in ranking[:k])


def _rank_of(target, ranking):
    for i, (n, _) in enumerate(ranking):
        if n == target:
            return i + 1
    return None


def _run_domain(
    name,
    substances,
    authored_table,
    authored_roles,
    authored_active_roles,
    base_rules,
    actions,
    observations,
    crystal_v4,
    queries,
):
    lines = [f"## {name}", ""]
    authored_pred = CompressionAnalog(authored_table)
    targets = {}
    for q in queries:
        rank = authored_pred.predict_role_weighted(
            query_substance=q,
            query_properties=authored_table.get(q, []),
            property_roles=authored_roles,
            active_roles=authored_active_roles,
        )
        targets[q] = rank[0][0] if rank else None

    table = induce_property_table(
        substances=substances,
        rules=list(base_rules) + [r for _, r in crystal_v4],
        actions=actions,
        observations=observations,
    )
    pred = CompressionAnalog(table)
    out = {q: pred.predict(q, table.get(q, [])) for q in queries}

    lines.append(f"v4 crystallizations in store: {len(crystal_v4)}")
    lines.append("")
    lines.append("| query | authored target | induced top | match |")
    lines.append("|---|---|---|---|")
    matches = 0
    total = 0
    rank_rows = []
    for q in queries:
        target = targets[q]
        top = out[q][0][0] if out[q] else None
        ok = "✅" if target and top == target else ("—" if not target else "❌")
        if target:
            total += 1
            if top == target:
                matches += 1
        lines.append(
            f"| {q} | **{target or '(none)'}** | {top or '-'} | {ok} |"
        )
        if target:
            rank_rows.append((q, target, _rank_of(target, out[q])))
    lines.append("")
    lines.append(f"**Top-1 agreement: {matches}/{total}**")
    lines.append("")
    if rank_rows:
        lines.append("Rank of authored target inside induced ranking:")
        lines.append("")
        lines.append("| query | target | rank |")
        lines.append("|---|---|---|")
        for q, target, rk in rank_rows:
            lines.append(f"| {q} | {target} | {rk if rk else '—'} |")
    lines.append("")
    lines.append("Top-3 induced rankings:")
    lines.append("")
    for q in queries:
        lines.append(f"- **{q}** → {_format(out[q])}")
    lines.append("")
    return lines, (matches, total)


def main():
    out = ["# Iteration 12 — Third domain transfer + N=3 inducer comparison", ""]
    out.append(
        "Runs the iteration-11 v4-only property inducer on all three "
        "domains (rule-world, traffic-world, kitchen-world). Measures "
        "whether the ~5/6 top-1 agreement result generalizes to a third "
        "unrelated domain."
    )
    out.append("")

    rw_lines, rw_score = _run_domain(
        name="rule-world",
        substances=sorted(rw.SUBSTANCE_PROPERTIES.keys()),
        authored_table=rw.SUBSTANCE_PROPERTIES,
        authored_roles=rw.PROPERTY_ROLES,
        authored_active_roles={"fire_relevant"},
        base_rules=rw.ALL_RULES,
        actions=rw.ACTIONS,
        observations=_gather_observations(ROOT / "scenarios.json", rw_parser),
        crystal_v4=_load_v4(ROOT / "rule_store.json"),
        queries=["oil", "food", "medicine", "ice"],
    )
    out += rw_lines

    tw_lines, tw_score = _run_domain(
        name="traffic-world",
        substances=sorted(tw.SUBSTANCE_PROPERTIES.keys()),
        authored_table=tw.SUBSTANCE_PROPERTIES,
        authored_roles=tw.PROPERTY_ROLES,
        authored_active_roles=tw.active_roles_for_scenario([]),
        base_rules=tw.ALL_RULES,
        actions=tw.ACTIONS,
        observations=_gather_observations(
            ROOT.parent / "traffic-world" / "traffic_scenarios.json", tw_parser,
        ),
        crystal_v4=_load_v4(ROOT.parent / "traffic-world" / "traffic_rule_store.json"),
        queries=["horse_carriage", "robotaxi", "fire_engine"],
    )
    out += tw_lines

    # kitchen: pick one fire-relevant query (butter), one food-safety (raw_egg),
    # one food-safety mealtime (peas).
    kw_lines, kw_score = _run_domain(
        name="kitchen-world",
        substances=sorted(kw.SUBSTANCE_PROPERTIES.keys()),
        authored_table=kw.SUBSTANCE_PROPERTIES,
        authored_roles=kw.PROPERTY_ROLES,
        authored_active_roles={"fire_relevant", "food_safety"},
        base_rules=kw.ALL_RULES,
        actions=kw.ACTIONS,
        observations=_gather_observations(
            ROOT.parent / "kitchen-world" / "kitchen_scenarios.json", kw_parser,
        ),
        crystal_v4=_load_v4(ROOT.parent / "kitchen-world" / "kitchen_rule_store.json"),
        queries=["butter", "raw_egg", "peas"],
    )
    out += kw_lines

    total_match = rw_score[0] + tw_score[0] + kw_score[0]
    total_n = rw_score[1] + tw_score[1] + kw_score[1]
    out.append("---")
    out.append("")
    out.append(
        f"## Combined N=3 result: **{total_match}/{total_n}** top-1 agreement "
        f"(rule-world {rw_score[0]}/{rw_score[1]} · "
        f"traffic-world {tw_score[0]}/{tw_score[1]} · "
        f"kitchen-world {kw_score[0]}/{kw_score[1]})"
    )
    out.append("")

    text = "\n".join(out)
    out_path = Path(__file__).parent / "iteration12_results.md"
    out_path.write_text(text)
    print(text)
    print(f"\n[wrote {out_path}]")


if __name__ == "__main__":
    main()
