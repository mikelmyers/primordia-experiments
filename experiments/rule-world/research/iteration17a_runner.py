"""Iteration 17a — A3 attack (structural variant).

The iteration-16 failure-modes inventory identified A3 — "encoder is
fixed / hand-designed, not learned from data" — as the assumption
rule-world shares with HTM and Spaun, the two prior systems most
architecturally similar to ours that both failed to scale to language.
A3 is the assumption whose break would most clearly differentiate the
stack from its closest prior art.

Iteration 9-12 already induced a *feature* table from rule and action
structure (property_inducer.induce_property_table) and fed it into the
CompressionAnalog predictor — hitting 89% top-1 agreement on the N=3
adversarial set (iteration 12). That measurement is one cell in the
matrix. The cell that has never been measured is:

                      CompressionAnalog    HDC (role-weighted v4)
    authored table    live baseline        live baseline (v4)
    induced table     iter 12: 89%         **iter 17a (this file)**
    induced from                           iter 17b (firing traces)
    behavioral traces

If induced features fed into the HDC path match or beat 89% on the
same adversarial queries, then the A3 break is real for the HDC
substrate, not just the compression substrate, and the entire
"learned encoder" claim covers the live v4 path. If it underperforms,
we've localized a signal CompressionAnalog can extract from induced
features that HDC cannot — which is itself an informative finding.

Scope discipline (per the iter-17 plan): one new runner, one results
doc, one progress-log entry. No changes to hdc.py, abstractor.py, or
property_inducer.py. Reuses existing infra end to end.
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

from hdc import Codebook, encode_property_bundle, similarity  # noqa: E402
from compression import CompressionAnalog  # noqa: E402
from property_inducer import (  # noqa: E402
    induce_property_table,
    induce_property_roles,
    induced_active_roles,
)


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


def _hdc_rank(
    query_substance: str,
    properties_by_substance: dict[str, list[str]],
    property_roles: dict[str, str],
    active_roles: set[str],
    codebook: Codebook,
) -> list[tuple[str, float]]:
    """HDC role-weighted analog ranking over every peer substance.

    Mirrors select_v4_analog's math but returns the full ranked list
    instead of just the argmax, so we can compute both top-1 agreement
    and the rank of the authored target.
    """
    def role_filtered(props):
        return [p for p in props if property_roles.get(p) in active_roles]

    if query_substance not in properties_by_substance:
        return []
    new_props_f = role_filtered(properties_by_substance[query_substance])
    if not new_props_f:
        return []
    new_hv = encode_property_bundle(new_props_f, codebook)

    ranked: list[tuple[str, float]] = []
    for peer in sorted(s for s in properties_by_substance if s != query_substance):
        peer_props_f = role_filtered(properties_by_substance[peer])
        if not peer_props_f:
            continue
        peer_hv = encode_property_bundle(peer_props_f, codebook)
        sim = similarity(new_hv, peer_hv)
        ranked.append((peer, round(sim, 4)))
    ranked.sort(key=lambda r: r[1], reverse=True)
    return ranked


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
    name: str,
    substances: list[str],
    authored_table: dict[str, list[str]],
    authored_roles: dict[str, str],
    authored_active_roles: set[str],
    base_rules,
    actions,
    observations: list[str],
    crystal_v4,
    queries: list[str],
    codebook: Codebook,
):
    lines = [f"## {name}", ""]

    # --- Oracle: authored table + live v4 HDC path (what rule-world runs today).
    authored_targets = {}
    for q in queries:
        ranking = _hdc_rank(
            q, authored_table, authored_roles, authored_active_roles, codebook,
        )
        authored_targets[q] = ranking[0][0] if ranking else None

    # --- Iter 17a: induce feature table, induce roles, activate all induced
    # buckets (induced_active_roles returns the full set — no hand-tuning of
    # which features matter). Feed the result into the same HDC path.
    induced_table = induce_property_table(
        substances=substances,
        rules=list(base_rules) + [r for _, r in crystal_v4],
        actions=actions,
        observations=observations,
    )
    induced_roles_map = induce_property_roles(induced_table)
    induced_active = induced_active_roles()

    # --- Reference: iter 12's induced + CompressionAnalog path (89% baseline).
    compress_pred = CompressionAnalog(induced_table)
    compress_out = {
        q: compress_pred.predict(q, induced_table.get(q, [])) for q in queries
    }

    # --- Test: induced + HDC path.
    hdc_out = {
        q: _hdc_rank(q, induced_table, induced_roles_map, induced_active, codebook)
        for q in queries
    }

    lines.append(f"v4 crystallizations folded into induction: {len(crystal_v4)}")
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
    codebook = Codebook(seed=42)  # same fixed codebook as live v4
    out = [
        "# Iteration 17a — A3 attack (structural): induced features + HDC",
        "",
        "Replaces the hand-authored `SUBSTANCE_PROPERTIES`, `PROPERTY_ROLES`,",
        "and `active_roles_for_scenario` inputs to the live HDC role-weighted",
        "analog path with the iteration-9 structurally-induced equivalents.",
        "The HDC codebook itself is unchanged (seed=42, same as live v4). The",
        "authored-table + HDC path is used only as the oracle target.",
        "",
        "Measures the same 10 adversarial queries iteration 12 used, on the",
        "same N=3 domains. Reports induced+HDC top-1 agreement (the A3 test)",
        "alongside induced+CompressionAnalog (iter 12's 89% reference).",
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
        observations=_gather_observations(ROOT / "scenarios.json", rw_parser),
        crystal_v4=_load_v4(ROOT / "rule_store.json"),
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
        observations=_gather_observations(
            ROOT.parent / "traffic-world" / "traffic_scenarios.json", tw_parser,
        ),
        crystal_v4=_load_v4(ROOT.parent / "traffic-world" / "traffic_rule_store.json"),
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
        observations=_gather_observations(
            ROOT.parent / "kitchen-world" / "kitchen_scenarios.json", kw_parser,
        ),
        crystal_v4=_load_v4(ROOT.parent / "kitchen-world" / "kitchen_rule_store.json"),
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
    out_path = Path(__file__).parent / "iteration17a_results.md"
    out_path.write_text(text)
    print(text)
    print(f"\n[wrote {out_path}]")


if __name__ == "__main__":
    main()
