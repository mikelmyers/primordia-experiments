"""Iteration 11 — filter symmetric syntactic crystallizations from the inducer.

Iteration 10 showed that closing the crystallization → induction loop
adds the right discriminating signal (oil↔wood via shape:X_in_hearth)
but the signal is drowned by symmetric noise from pre-v4 syntactic
crystallizations (R3~oil, P-admitted-with-water~food, etc.) that add
identical features to every novel substance.

Iteration 11 tests the one-line fix: include only `crystallized_v4`
rules in the inducer's corpus (the analogical ones), excluding
`crystallized` (the symmetric syntactic ones). The engine still fires
all crystallizations as before — this filter applies only to property
induction.

Expected: oil → wood flips from rank 5 to rank 1.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "traffic-world"))

import world_structured as rw  # noqa: E402
import parser as rw_parser  # noqa: E402
import traffic_rules as tw  # noqa: E402
import traffic_parser as tw_parser  # noqa: E402
from compression import CompressionAnalog  # noqa: E402
from property_inducer import induce_property_table  # noqa: E402


@dataclass
class StoredRule:
    antecedents: list
    derives: list
    requires_in_result: list
    forbids_in_result: list


def _load_crystallized(store_path: Path, source_filter: str | None):
    data = json.loads(store_path.read_text())
    store = list(data.values())[0]
    out = []
    for rid, r in store.items():
        src = r.get("source", "")
        if not src.startswith("crystallized"):
            continue
        if source_filter is not None and src != source_filter:
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


def _induce_and_predict(substances, rules, actions, observations, queries):
    table = induce_property_table(
        substances=substances,
        rules=rules,
        actions=actions,
        observations=observations,
    )
    pred = CompressionAnalog(table)
    return table, {q: pred.predict(q, table.get(q, [])) for q in queries}


def _run_domain(
    name,
    substances,
    authored_table,
    authored_roles,
    authored_active_roles,
    base_rules,
    actions,
    observations,
    crystal_all,
    crystal_v4_only,
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

    _, out_A = _induce_and_predict(
        substances, list(base_rules), actions, observations, queries,
    )
    _, out_B = _induce_and_predict(
        substances, list(base_rules) + [r for _, r in crystal_all],
        actions, observations, queries,
    )
    _, out_E = _induce_and_predict(
        substances, list(base_rules) + [r for _, r in crystal_v4_only],
        actions, observations, queries,
    )

    lines.append(
        f"Crystallized rules in store: {len(crystal_all)} total, "
        f"{len(crystal_v4_only)} v4-only"
    )
    lines.append("")
    lines.append("| query | target | A baseline | B full loop (i10) | E v4-only loop |")
    lines.append("|---|---|---|---|---|")
    score = {"A": 0, "B": 0, "E": 0, "n": 0}
    rank_rows = []
    for q in queries:
        target = targets[q]
        a_top = out_A[q][0][0] if out_A[q] else None
        b_top = out_B[q][0][0] if out_B[q] else None
        e_top = out_E[q][0][0] if out_E[q] else None
        def ok(t):
            return "✅" if target and t == target else "❌"
        if target:
            score["n"] += 1
            for v, t in [("A", a_top), ("B", b_top), ("E", e_top)]:
                if t == target:
                    score[v] += 1
        lines.append(
            f"| {q} | **{target or '(none)'}** | "
            f"{a_top or '-'} {ok(a_top)} | "
            f"{b_top or '-'} {ok(b_top)} | "
            f"{e_top or '-'} {ok(e_top)} |"
        )
        if target:
            rank_rows.append((q, target, [
                _rank_of(target, out_A[q]),
                _rank_of(target, out_B[q]),
                _rank_of(target, out_E[q]),
            ]))
    lines.append("")
    if score["n"]:
        lines.append(
            f"**Top-1 agreement:** A={score['A']}/{score['n']} · "
            f"B={score['B']}/{score['n']} · E={score['E']}/{score['n']}"
        )
        lines.append("")
        lines.append("Rank of authored target (lower is better):")
        lines.append("")
        lines.append("| query | target | A | B | E |")
        lines.append("|---|---|---|---|---|")
        for q, target, ranks in rank_rows:
            cells = [str(r) if r else "—" for r in ranks]
            lines.append(f"| {q} | {target} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("Top-3 rankings under E (v4-only loop):")
    lines.append("")
    for q in queries:
        lines.append(f"- **{q}** → {_format(out_E[q])}")
    lines.append("")
    return lines, score


def main():
    out = ["# Iteration 11 — Filter symmetric syntactic crystallizations", ""]
    out.append(
        "Tests the one-line fix from iteration 10: include only "
        "`crystallized_v4` rules in the inducer's corpus, excluding the "
        "symmetric `crystallized` rules (R3~X, P-admitted-with-water~X) "
        "that add identical features to every novel substance and drown "
        "the discriminating signal."
    )
    out.append("")
    out.append(
        "**Variants:** A=baseline (i9) · B=full loop (i10) · "
        "E=v4-only loop (i11 fix)."
    )
    out.append("")

    rw_lines, _ = _run_domain(
        name="rule-world",
        substances=sorted(rw.SUBSTANCE_PROPERTIES.keys()),
        authored_table=rw.SUBSTANCE_PROPERTIES,
        authored_roles=rw.PROPERTY_ROLES,
        authored_active_roles={"fire_relevant"},
        base_rules=rw.ALL_RULES,
        actions=rw.ACTIONS,
        observations=_gather_observations(ROOT / "scenarios.json", rw_parser),
        crystal_all=_load_crystallized(ROOT / "rule_store.json", None),
        crystal_v4_only=_load_crystallized(ROOT / "rule_store.json", "crystallized_v4"),
        queries=["oil", "food", "medicine", "ice"],
    )
    out += rw_lines

    tw_store = ROOT.parent / "traffic-world" / "traffic_rule_store.json"
    tw_lines, _ = _run_domain(
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
        crystal_all=_load_crystallized(tw_store, None),
        crystal_v4_only=_load_crystallized(tw_store, "crystallized_v4"),
        queries=["horse_carriage", "robotaxi", "fire_engine"],
    )
    out += tw_lines

    text = "\n".join(out)
    out_path = Path(__file__).parent / "iteration11_results.md"
    out_path.write_text(text)
    print(text)
    print(f"\n[wrote {out_path}]")


if __name__ == "__main__":
    main()
