"""Iteration 9 — induce property tables from rule + observation structure
and compare analog selection against the hand-authored tables.

Runs both rule-world and traffic-world. For each domain:
  1. Induce a property table for the substance vocabulary using only
     ALL_RULES, ACTIONS, and parsed scenario facts (no hand-authored
     SUBSTANCE_PROPERTIES).
  2. Build a CompressionAnalog over the induced table and over the
     authored table.
  3. For each adversarial query substance, print both predictors'
     top-3 analogs side by side.
  4. Mark whether the induced predictor's top pick matches the authored
     predictor's top pick — i.e. whether the iteration-7 substrate-
     independence finding survives losing the hand-authored table.

Writes a markdown report to research/iteration9_results.md and prints
the same content to stdout. No changes to engine, abstractor, runners.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "traffic-world"))

import world_structured as rw  # noqa: E402
import parser as rw_parser  # noqa: E402
from compression import CompressionAnalog  # noqa: E402
from property_inducer import (  # noqa: E402
    induce_property_table,
    induce_property_roles,
    induced_active_roles,
)

import traffic_rules as tw  # noqa: E402
import traffic_parser as tw_parser  # noqa: E402


def _gather_observations(scenarios_path: Path, parser_module) -> list[str]:
    """Parse all scenarios and return the union of fact strings."""
    facts: set[str] = set()
    with open(scenarios_path) as f:
        scenarios = json.load(f)
    for scen in scenarios:
        parsed = parser_module.parse(scen["description"])
        facts.update(parsed["facts"])
        facts.update(parsed.get("goal", []))
    return sorted(facts)


def _format_ranking(ranking, k=3):
    if not ranking:
        return "(no candidates)"
    return ", ".join(f"{name}:{score}" for name, score in ranking[:k])


def _run_domain(
    name: str,
    substances: list[str],
    authored_table: dict,
    authored_roles: dict,
    authored_active: set,
    rules,
    actions,
    observations: list[str],
    queries: list[str],
) -> list[str]:
    lines = [f"## {name}", ""]

    induced_table = induce_property_table(
        substances=substances,
        rules=rules,
        actions=actions,
        observations=observations,
    )
    induced_roles = induce_property_roles(induced_table)
    induced_active = induced_active_roles()

    lines.append("### Induced feature counts per substance")
    lines.append("")
    lines.append("| substance | # induced features | # authored properties |")
    lines.append("|---|---|---|")
    for s in substances:
        n_ind = len(induced_table.get(s, []))
        n_auth = len(authored_table.get(s, []))
        lines.append(f"| {s} | {n_ind} | {n_auth} |")
    lines.append("")

    lines.append("### Sample induced features")
    lines.append("")
    for s in substances:
        feats = induced_table.get(s, [])
        sample = feats[:8]
        lines.append(f"- **{s}** ({len(feats)}): {sample}")
    lines.append("")

    authored_pred = CompressionAnalog(authored_table)
    induced_pred  = CompressionAnalog(induced_table)

    lines.append("### Adversarial query comparison (top-3 analogs)")
    lines.append("")
    lines.append("| query | authored (role-weighted) | induced (all-features) | top match? |")
    lines.append("|---|---|---|---|")

    matches = 0
    total = 0
    for q in queries:
        a_props = authored_table.get(q, [])
        i_feats = induced_table.get(q, [])
        a_rank = authored_pred.predict_role_weighted(
            query_substance=q,
            query_properties=a_props,
            property_roles={p: r for p, r in authored_roles.items()},
            active_roles=authored_active,
        )
        i_rank = induced_pred.predict(
            query_substance=q,
            query_properties=i_feats,
        )
        a_top = a_rank[0][0] if a_rank else None
        i_top = i_rank[0][0] if i_rank else None
        match = "✅" if (a_top is not None and a_top == i_top) else "❌"
        if a_top is not None:
            total += 1
            if a_top == i_top:
                matches += 1
        lines.append(
            f"| {q} | {_format_ranking(a_rank)} | {_format_ranking(i_rank)} | {match} |"
        )
    lines.append("")
    lines.append(f"**Top-pick agreement: {matches}/{total}**")
    lines.append("")
    return lines


def main():
    out: list[str] = []
    out.append("# Iteration 9 — Property table induction results")
    out.append("")
    out.append(
        "Test: replace the hand-authored substance property tables in both "
        "domains with structurally-induced feature tables, then check whether "
        "the iteration-7 substrate-independence pattern (HDC v3/v4 ≡ "
        "compression v5) survives. Top-pick agreement on the adversarial "
        "queries is the success metric."
    )
    out.append("")

    # ---------- rule-world ----------
    rw_substances = sorted(rw.SUBSTANCE_PROPERTIES.keys())
    rw_authored_table = rw.SUBSTANCE_PROPERTIES
    rw_authored_roles = rw.PROPERTY_ROLES
    rw_authored_active = {"fire_relevant"}
    rw_rules = rw.ALL_RULES
    rw_actions = rw.ACTIONS
    rw_obs = _gather_observations(ROOT / "scenarios.json", rw_parser)
    rw_queries = ["oil", "food", "medicine", "ice"]

    out += _run_domain(
        name="rule-world",
        substances=rw_substances,
        authored_table=rw_authored_table,
        authored_roles=rw_authored_roles,
        authored_active=rw_authored_active,
        rules=rw_rules,
        actions=rw_actions,
        observations=rw_obs,
        queries=rw_queries,
    )

    # ---------- traffic-world ----------
    tw_substances = sorted(tw.SUBSTANCE_PROPERTIES.keys())
    tw_authored_table = tw.SUBSTANCE_PROPERTIES
    tw_authored_roles = tw.PROPERTY_ROLES
    tw_authored_active = tw.active_roles_for_scenario([])
    tw_rules = tw.ALL_RULES
    tw_actions = tw.ACTIONS
    tw_obs = _gather_observations(
        ROOT.parent / "traffic-world" / "traffic_scenarios.json",
        tw_parser,
    )
    tw_queries = ["horse_carriage", "robotaxi", "fire_engine"]

    out += _run_domain(
        name="traffic-world",
        substances=tw_substances,
        authored_table=tw_authored_table,
        authored_roles=tw_authored_roles,
        authored_active=tw_authored_active,
        rules=tw_rules,
        actions=tw_actions,
        observations=tw_obs,
        queries=tw_queries,
    )

    out.append("---")
    out.append("")
    out.append(
        "Reading: a `✅` means the induced table — built with zero "
        "hand-authored property labels — produced the same top analog choice "
        "as the hand-authored table. A `❌` means structural induction is not "
        "yet sufficient for that query and additional signal is needed."
    )
    out.append("")

    text = "\n".join(out)
    out_path = Path(__file__).parent / "iteration9_results.md"
    out_path.write_text(text)
    print(text)
    print(f"\n[wrote {out_path}]")


if __name__ == "__main__":
    main()
