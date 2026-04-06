"""Iteration 10 — close the crystallization → induction loop.

Iteration 9 induced property tables from rule + observation structure
and got 4/6 top-pick agreement with the hand-authored tables. The two
failures were both corpus-coverage: oil (rule-world) and fire_engine
(traffic-world) lacked the structural signal needed to find their
authored analog.

Iteration 10 tests whether adding **crystallized rules** (the rules v4
itself synthesized at runtime by HDC analogy + token substitution) back
into the inducer's corpus closes the gap.

The honest concern: feeding v4-crystallized rules into the inducer is
potentially circular. v4 crystallized `P3a~oil_v4` (oil_in_hearth →
hearth_fed) by analogy to `P3a` (wood_in_hearth → hearth_fed). If we
then use `P3a~oil_v4` to "induce" that oil is structurally like wood,
we have just laundered the original analogy through an extra step.

To test for laundering, this runner reports THREE variants per query:
  A — authored rules only (iteration-9 baseline)
  B — authored + all crystallized rules (full loop closure)
  C — authored + crystallized rules MINUS those mentioning the query
      substance (held-out: tests whether other substances' loop closures
      transfer signal to the held-out one)

If B succeeds where A fails, the loop closes.
If C *also* succeeds, the loop closure is genuinely transferable.
If C fails where B succeeds, the success is laundering, not transfer.
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
    """Minimal Rule-shaped object the inducer can scan."""
    antecedents: list
    derives: list
    requires_in_result: list
    forbids_in_result: list


def _load_crystallized(store_path: Path) -> list[tuple[str, StoredRule]]:
    """Return [(rule_id, StoredRule), ...] for every crystallized entry."""
    data = json.loads(store_path.read_text())
    store = list(data.values())[0]
    out: list[tuple[str, StoredRule]] = []
    for rid, r in store.items():
        if not r.get("source", "").startswith("crystallized"):
            continue
        out.append((
            rid,
            StoredRule(
                antecedents=r.get("antecedents", []) or [],
                derives=r.get("derives", []) or [],
                requires_in_result=r.get("requires_in_result", []) or [],
                forbids_in_result=r.get("forbids_in_result", []) or [],
            ),
        ))
    return out


def _rule_mentions(rule: StoredRule, substance: str) -> bool:
    sub_tokens = substance.split("_")
    n = len(sub_tokens)
    preds = (
        list(rule.antecedents)
        + list(rule.derives)
        + list(rule.requires_in_result)
        + list(rule.forbids_in_result)
    )
    for p in preds:
        toks = p.split("_")
        for i in range(len(toks) - n + 1):
            if toks[i : i + n] == sub_tokens:
                return True
    return False


def _gather_observations(scenarios_path: Path, parser_module) -> list[str]:
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


def _run_variant(
    substances,
    base_rules,
    extra_rules,
    actions,
    observations,
    queries,
    idf=False,
):
    table = induce_property_table(
        substances=substances,
        rules=list(base_rules) + list(extra_rules),
        actions=actions,
        observations=observations,
    )
    pred = CompressionAnalog(table)
    out = {}
    if not idf:
        for q in queries:
            out[q] = pred.predict(q, table.get(q, []))
        return table, out
    # IDF-weighted: features common to many substances count less.
    # weight(f) = 1 / count_of_substances_having_f. Score is sum of
    # weights of shared features (still pure integer + reciprocal,
    # no matmul).
    df: dict = {}
    for s, feats in table.items():
        for f in feats:
            df[f] = df.get(f, 0) + 1
    for q in queries:
        q_feats = set(table.get(q, []))
        scores: dict = {}
        for s, feats in table.items():
            if s == q:
                continue
            shared = q_feats & set(feats)
            score = 0.0
            for f in shared:
                score += 1.0 / df[f]
            if score > 0:
                scores[s] = score
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        out[q] = [(n, round(s, 3)) for n, s in ranked]
    return table, out


def _run_domain(
    name,
    substances,
    authored_table,
    authored_roles,
    authored_active_roles,
    base_rules,
    actions,
    observations,
    crystallized,
    queries,
):
    lines = [f"## {name}", ""]

    # Authored top picks (target) — role-weighted to match iteration 9.
    authored_pred = CompressionAnalog(authored_table)
    authored_top = {}
    for q in queries:
        rank = authored_pred.predict_role_weighted(
            query_substance=q,
            query_properties=authored_table.get(q, []),
            property_roles=authored_roles,
            active_roles=authored_active_roles,
        )
        authored_top[q] = rank[0][0] if rank else None

    # Track wood-rank explicitly for oil to expose signal-vs-score story.
    def _rank_of(target, ranking):
        for i, (n, _) in enumerate(ranking):
            if n == target:
                return i + 1
        return None

    # Variant A — authored rules only (matches iteration 9)
    _, out_A = _run_variant(
        substances, base_rules, [], actions, observations, queries,
    )

    # Variant B — authored + all crystallized
    crystal_rules_all = [r for _, r in crystallized]
    _, out_B = _run_variant(
        substances, base_rules, crystal_rules_all, actions, observations, queries,
    )

    # Variant C — held-out: per query, drop crystallized rules mentioning that substance
    out_C = {}
    held_out_counts = {}
    for q in queries:
        kept = [r for rid, r in crystallized if not _rule_mentions(r, q)]
        held_out_counts[q] = len(crystallized) - len(kept)
        _, c_out = _run_variant(
            substances, base_rules, kept, actions, observations, [q],
        )
        out_C[q] = c_out[q]

    # Variant D — full loop with IDF weighting (discriminator-aware)
    _, out_D = _run_variant(
        substances, base_rules, crystal_rules_all, actions, observations,
        queries, idf=True,
    )

    lines.append(f"Crystallized rules in store: {len(crystallized)}")
    lines.append("")
    lines.append("Top-1 agreement table:")
    lines.append("")
    lines.append("| query | authored target | A baseline | B full loop | C held-out | D loop+IDF |")
    lines.append("|---|---|---|---|---|---|")
    score = {"A": 0, "B": 0, "C": 0, "D": 0, "n": 0}
    rank_rows = []
    for q in queries:
        target = authored_top[q]
        a_top = out_A[q][0][0] if out_A[q] else None
        b_top = out_B[q][0][0] if out_B[q] else None
        c_top = out_C[q][0][0] if out_C[q] else None
        d_top = out_D[q][0][0] if out_D[q] else None
        def ok(t):
            return "✅" if target and t == target else "❌"
        if target:
            score["n"] += 1
            for v, t in [("A", a_top), ("B", b_top), ("C", c_top), ("D", d_top)]:
                if t == target:
                    score[v] += 1
        lines.append(
            f"| {q} | **{target or '(none)'}** | "
            f"{a_top or '-'} {ok(a_top)} | "
            f"{b_top or '-'} {ok(b_top)} | "
            f"{c_top or '-'} {ok(c_top)} | "
            f"{d_top or '-'} {ok(d_top)} |"
        )
        if target:
            rank_rows.append((q, target, [
                _rank_of(target, out_A[q]),
                _rank_of(target, out_B[q]),
                _rank_of(target, out_C[q]),
                _rank_of(target, out_D[q]),
            ]))
    lines.append("")
    if score["n"]:
        lines.append(
            f"**Top-1 agreement:** A={score['A']}/{score['n']} · "
            f"B={score['B']}/{score['n']} · C={score['C']}/{score['n']} · "
            f"D={score['D']}/{score['n']}"
        )
        lines.append("")
        lines.append(
            "Rank of the authored target inside each variant's full ranking "
            "(lower is better; — = not in ranking):"
        )
        lines.append("")
        lines.append("| query | target | A | B | C | D |")
        lines.append("|---|---|---|---|---|---|")
        for q, target, ranks in rank_rows:
            cells = [str(r) if r else "—" for r in ranks]
            lines.append(f"| {q} | {target} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("Full top-3 rankings:")
    lines.append("")
    lines.append("| query | A baseline | B full loop | C held-out | D loop+IDF |")
    lines.append("|---|---|---|---|---|")
    for q in queries:
        lines.append(
            f"| {q} | {_format(out_A[q])} | {_format(out_B[q])} | "
            f"{_format(out_C[q])} (-{held_out_counts[q]}) | {_format(out_D[q])} |"
        )
    lines.append("")
    return lines, score


def main():
    out = ["# Iteration 10 — Crystallization → induction loop closure", ""]
    out.append(
        "Tests whether feeding v4-crystallized rules back into the structural "
        "inducer closes iteration 9's corpus-coverage failures, and whether "
        "any closure is genuine signal transfer or laundering of the original "
        "v4 analogy."
    )
    out.append("")
    out.append(
        "**Variants:** A=authored rules only (i9 baseline) · "
        "B=authored + all crystallized · "
        "C=authored + crystallized minus rules mentioning the query substance "
        "(held-out honesty check) · "
        "D=full loop with IDF weighting (rare/discriminating features count more)."
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
        crystallized=_load_crystallized(ROOT / "rule_store.json"),
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
        crystallized=_load_crystallized(
            ROOT.parent / "traffic-world" / "traffic_rule_store.json",
        ),
        queries=["horse_carriage", "robotaxi", "fire_engine"],
    )
    out += tw_lines

    out.append("---")
    out.append("")
    out.append("## Reading")
    out.append("")
    out.append(
        "- **B > A**: closing the loop produces signal the baseline lacked.\n"
        "- **C ≥ A and C close to B**: the closure is real signal transfer — "
        "other substances' crystallizations help find the held-out substance's "
        "analog.\n"
        "- **B > C ≈ A**: the closure is laundering. The success comes from "
        "the v4 crystallization specifically about that substance, not from "
        "transferable structural learning."
    )
    out.append("")

    text = "\n".join(out)
    out_path = Path(__file__).parent / "iteration10_results.md"
    out_path.write_text(text)
    print(text)
    print(f"\n[wrote {out_path}]")


if __name__ == "__main__":
    main()
