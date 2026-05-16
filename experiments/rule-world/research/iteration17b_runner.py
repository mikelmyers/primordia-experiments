"""Iteration 17b — A3 attack (behavioral variant).

Iter 17a fed structurally-induced features (from static rule text +
action text + observation strings) into the HDC role-weighted path
and hit 7/10 top-1 agreement — underperforming the iter-12
CompressionAnalog reference (10/10) on the exact same induced table.

The failure mode matched the inventory's prediction for HTM-style
walls: surface co-occurrence across the full rule text dominates the
bundle, washing out the role-specific conditional structure that
makes oil→wood correct. Bundle cardinality is collapsed by HDC's
sign-majority operator in a way CompressionAnalog's count-based
similarity does not.

Iter 17b asks the same A3 question with a sharper corpus: instead of
inducing features from *every* rule and action in the domain, induce
from only those rules and actions whose antecedents are *actually
satisfied* during the scenario suite — i.e., the behavioral trace.
The hypothesis is that behaviorally-concentrated features suppress
the irrelevant co-occurrence that washed out iter 17a's bundles.

Concretely, for each scenario:
  1. Parse scenario description into facts.
  2. forward_chain to fixed point; any rule whose antecedents matched
     (derives trace + active obligations/constraints) counts as fired.
  3. Any action whose preconditions hold in the post-chain state
     counts as a fireable action.
Union the fired rules and fireable actions across all scenarios in
the domain; induce features from that restricted corpus; feed to HDC.

Scope: reuses iter 17a's runner scaffolding and the same 10 queries.
No edits to existing modules.
"""

from __future__ import annotations

import json
import sys
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

from engine import forward_chain, active_obligations_and_constraints  # noqa: E402
from hdc import Codebook  # noqa: E402
from compression import CompressionAnalog  # noqa: E402
from property_inducer import (  # noqa: E402
    induce_property_table,
    induce_property_roles,
    induced_active_roles,
)

# Reuse iter 17a's helpers.
from iteration17a_runner import (  # noqa: E402
    _hdc_rank,
    _gather_observations,
    _load_v4,
    _format,
    _rank_of,
)


def _fired_rules_and_actions(
    scenarios_path: Path, parser_module, all_rules, all_actions
):
    fired_rule_ids: set[str] = set()
    fireable_action_ids: set[str] = set()
    all_observed_facts: set[str] = set()

    for scen in json.loads(scenarios_path.read_text()):
        parsed = parser_module.parse(scen["description"])
        facts = set(parsed["facts"]) | set(parsed.get("goal", []))
        all_observed_facts.update(facts)

        state, trace = forward_chain(facts, list(all_rules))
        all_observed_facts.update(state)
        # Pull rule ids from trace lines formatted "RID: ..." (see engine.py).
        for line in trace:
            rid = line.split(":", 1)[0].strip()
            fired_rule_ids.add(rid)
        for r in active_obligations_and_constraints(state, list(all_rules)):
            fired_rule_ids.add(r.id)

        # An action counts as fireable when its preconditions hold in state.
        for a in all_actions:
            pre = getattr(a, "preconditions", []) or []
            if all(p in state for p in pre):
                fireable_action_ids.add(a.name)

    fired_rules = [r for r in all_rules if r.id in fired_rule_ids]
    fireable_actions = [a for a in all_actions if a.name in fireable_action_ids]
    return fired_rules, fireable_actions, sorted(all_observed_facts)


def _run_domain(
    name, substances, authored_table, authored_roles, authored_active_roles,
    base_rules, actions, scenarios_path, parser_module, queries, codebook,
):
    lines = [f"## {name}", ""]

    # Oracle target (same as iter 17a).
    authored_targets = {}
    for q in queries:
        ranking = _hdc_rank(
            q, authored_table, authored_roles, authored_active_roles, codebook,
        )
        authored_targets[q] = ranking[0][0] if ranking else None

    fired_rules, fireable_actions, obs = _fired_rules_and_actions(
        scenarios_path, parser_module, list(base_rules), list(actions),
    )

    induced_table = induce_property_table(
        substances=substances,
        rules=fired_rules,
        actions=fireable_actions,
        observations=obs,
    )
    induced_roles_map = induce_property_roles(induced_table)
    induced_active = induced_active_roles()

    compress_pred = CompressionAnalog(induced_table)
    compress_out = {
        q: compress_pred.predict(q, induced_table.get(q, [])) for q in queries
    }
    hdc_out = {
        q: _hdc_rank(q, induced_table, induced_roles_map, induced_active, codebook)
        for q in queries
    }

    lines.append(
        f"fired rules: {len(fired_rules)}/{len(list(base_rules))} · "
        f"fireable actions: {len(fireable_actions)}/{len(list(actions))}"
    )
    lines.append(
        f"induced feature vocabulary: "
        f"{sum(len(v) for v in induced_table.values())} features total"
    )
    lines.append("")
    lines.append(
        "| query | authored target | induced+compress top | induced+HDC top "
        "| HDC match |"
    )
    lines.append("|---|---|---|---|---|")
    hdc_matches = 0
    comp_matches = 0
    total = 0
    rank_rows = []
    for q in queries:
        target = authored_targets[q]
        comp_top = compress_out[q][0][0] if compress_out[q] else None
        hdc_top = hdc_out[q][0][0] if hdc_out[q] else None
        hdc_ok = (
            "✅" if target and hdc_top == target
            else ("—" if not target else "❌")
        )
        if target:
            total += 1
            if comp_top == target:
                comp_matches += 1
            if hdc_top == target:
                hdc_matches += 1
        lines.append(
            f"| {q} | **{target or '(none)'}** | "
            f"{comp_top or '-'} | {hdc_top or '-'} | {hdc_ok} |"
        )
        if target:
            rank_rows.append((q, target, _rank_of(target, hdc_out[q])))
    lines.append("")
    lines.append(
        f"**induced+HDC top-1 agreement: {hdc_matches}/{total}**  "
        f"(induced+compress reference: {comp_matches}/{total})"
    )
    lines.append("")
    if rank_rows:
        lines.append("Rank of authored target inside induced+HDC ranking:")
        lines.append("")
        lines.append("| query | target | rank |")
        lines.append("|---|---|---|")
        for q, target, rk in rank_rows:
            lines.append(f"| {q} | {target} | {rk if rk else '—'} |")
    lines.append("")
    lines.append("Top-3 induced+HDC rankings:")
    lines.append("")
    for q in queries:
        lines.append(f"- **{q}** → {_format(hdc_out[q])}")
    lines.append("")
    return lines, (hdc_matches, comp_matches, total)


def main():
    codebook = Codebook(seed=42)
    out = [
        "# Iteration 17b — A3 attack (behavioral): firing-trace induced features + HDC",
        "",
        "Same machinery as iter 17a, but the induction corpus is restricted",
        "to rules whose antecedents are actually satisfied and actions whose",
        "preconditions actually hold during the scenario suite — i.e., the",
        "behavioral trace, not the static domain text. Hypothesis: firing-",
        "concentrated features suppress the irrelevant co-occurrence that",
        "washed out iter 17a's HDC bundles.",
        "",
    ]

    rw_lines, rw_score = _run_domain(
        name="rule-world",
        substances=sorted(rw.SUBSTANCE_PROPERTIES.keys()),
        authored_table=rw.SUBSTANCE_PROPERTIES,
        authored_roles=rw.PROPERTY_ROLES,
        authored_active_roles={"fire_relevant"},
        base_rules=rw.ALL_RULES,
        actions=rw.ACTIONS,
        scenarios_path=ROOT / "scenarios.json",
        parser_module=rw_parser,
        queries=["oil", "food", "medicine", "ice"],
        codebook=codebook,
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
        scenarios_path=ROOT.parent / "traffic-world" / "traffic_scenarios.json",
        parser_module=tw_parser,
        queries=["horse_carriage", "robotaxi", "fire_engine"],
        codebook=codebook,
    )
    out += tw_lines

    kw_lines, kw_score = _run_domain(
        name="kitchen-world",
        substances=sorted(kw.SUBSTANCE_PROPERTIES.keys()),
        authored_table=kw.SUBSTANCE_PROPERTIES,
        authored_roles=kw.PROPERTY_ROLES,
        authored_active_roles={"fire_relevant", "food_safety"},
        base_rules=kw.ALL_RULES,
        actions=kw.ACTIONS,
        scenarios_path=ROOT.parent / "kitchen-world" / "kitchen_scenarios.json",
        parser_module=kw_parser,
        queries=["butter", "raw_egg", "peas"],
        codebook=codebook,
    )
    out += kw_lines

    hdc_total = rw_score[0] + tw_score[0] + kw_score[0]
    comp_total = rw_score[1] + tw_score[1] + kw_score[1]
    n_total = rw_score[2] + tw_score[2] + kw_score[2]
    out.append("---")
    out.append("")
    out.append(
        f"## Combined N=3 result: induced+HDC **{hdc_total}/{n_total}** "
        f"(induced+compress reference {comp_total}/{n_total})"
    )
    out.append("")
    out.append(
        f"- rule-world: HDC {rw_score[0]}/{rw_score[2]} · "
        f"compress {rw_score[1]}/{rw_score[2]}"
    )
    out.append(
        f"- traffic-world: HDC {tw_score[0]}/{tw_score[2]} · "
        f"compress {tw_score[1]}/{tw_score[2]}"
    )
    out.append(
        f"- kitchen-world: HDC {kw_score[0]}/{kw_score[2]} · "
        f"compress {kw_score[1]}/{kw_score[2]}"
    )
    out.append("")

    text = "\n".join(out)
    out_path = Path(__file__).parent / "iteration17b_results.md"
    out_path.write_text(text)
    print(text)
    print(f"\n[wrote {out_path}]")


if __name__ == "__main__":
    main()
