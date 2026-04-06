"""Rule World symbolic runner — full four-layer pipeline.

Pipeline per scenario:
  Layer 3 (parser)     : NL string → (facts, goal)
  Layer 1 (retriever)  : (facts, goal, store) → active rule window
  engine.reason        : (facts, goal, active_rules, ACTIONS) → result
  Layer 2 (abstractor) : (facts, goal, result, active, store) → maybe new rules
  Layer 0 (rule store) : persistent JSON; usage counts incremented as rules fire

Logs every layer's contribution per scenario. Runs 7 scenarios. Scenario 6
introduces a novel substance (`stranger_carries_ice`); scenario 7 re-runs the
same description after the abstractor has had a chance to crystallize from
scenario 6, so we can see whether the loop closes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from engine import reason
from world_structured import (
    ACTIONS,
    SUBSTANCE_PROPERTIES,
    PROPERTY_ROLES,
    active_roles_for_scenario,
)
from rule_store import RuleStore, migrate_authored_rules
from retriever import retrieve
from abstractor import (
    analyze_and_crystallize,
    crystallize_by_hdc_analogy,
    crystallize_by_hdc_unconstrained,
    crystallize_by_hdc_role_weighted,
    crystallize_by_hdc_v4_token_projection,
    find_unhandled_facts,
)
from parser import parse
from hdc import Codebook

HERE = Path(__file__).parent


def render_eval(ev: dict) -> list[str]:
    out = [f"  - **{ev['action']}** (score {ev['score']}, goal_met={ev['goal_met']})"]
    if ev["visceral_violations"]:
        out.append(f"    - VISCERAL VIOLATIONS: {ev['visceral_violations']}")
    if ev["violated"]:
        out.append(f"    - violated: {ev['violated']}")
    return out


def run_scenario(scenario: dict, store: RuleStore, codebook: Codebook) -> list[str]:
    out: list[str] = []
    title = scenario["title"]
    desc = scenario["description"]

    out += [f"## {title}", "", f"**Description:** {desc}", ""]

    # ----- Layer 3: parser -----
    parsed = parse(desc)
    out += [
        "### Layer 3 — Parser",
        "",
        f"- matched patterns: {len(parsed['matched_patterns'])}",
        f"- facts: {parsed['facts']}",
        f"- goal: {parsed['goal']}",
        "",
    ]

    # ----- Layer 1: retriever -----
    retrieval = retrieve(parsed["facts"], parsed["goal"], store)
    active_rules = retrieval["active_rules"]
    out += [
        "### Layer 1 — Retriever",
        "",
        f"- store size: {retrieval['total_in_store']}",
        f"- inferred context tags: {retrieval['context_tags']}",
        f"- inferred domains: {retrieval['domains']}",
        f"- active window: {len(active_rules)} rules → "
        f"{[r.id for r in active_rules]}",
        f"- dormant: {len(retrieval['dormant_rule_ids'])} rules",
        "",
    ]

    # ----- Engine -----
    result = reason(parsed["facts"], parsed["goal"], active_rules, ACTIONS)
    best = result["best"]
    out += [
        "### Engine",
        "",
        f"- initial state after chain: {result['initial_state_after_chain']}",
    ]
    if result["init_chain_trace"]:
        out += ["- forward-chain trace:"]
        for line in result["init_chain_trace"]:
            out.append(f"  - {line}")
    out += ["", "- action evaluations (best first):"]
    for ev in result["all_evaluations"][:5]:
        out += render_eval(ev)
    if best:
        out += [
            "",
            f"- **CHOSEN ACTION:** `{best['action']}` (score {best['score']})",
            f"- triggered rules: {best['triggered_rule_ids']}",
        ]
        # Increment usage counts on rules that actually fired (active and triggered)
        for rid in best["triggered_rule_ids"]:
            store.increment_usage(rid)
    else:
        out += ["", "- **ENGINE FAILURE:** no action survived"]
    out += ["", f"- gap: {result['gap']}"]
    if result["gap"]:
        for r in result["gap_reasons"]:
            out.append(f"  - {r}")
    out.append("")

    # Capture unhandled facts BEFORE the syntactic abstractor mutates the store,
    # so the HDC shadow has something to analyze.
    pre_mutation_unhandled = find_unhandled_facts(parsed["facts"], store)

    # ----- Layer 2: abstractor -----
    abstraction = analyze_and_crystallize(
        parsed["facts"], parsed["goal"], result, active_rules, store
    )
    out += [
        "### Layer 2 — Abstractor",
        "",
        f"- unhandled facts: {abstraction['unhandled_facts']}",
        f"- crystallized rule ids: {abstraction['crystallized_ids']}",
        "- reasoning log:",
    ]
    for line in abstraction["log"]:
        out.append(f"  - {line}")
    # ----- Layer 2 SHADOW: HDC abstractors v1/v2/v3 (read-only) -----
    unhandled = pre_mutation_unhandled
    active_roles = active_roles_for_scenario(parsed["facts"])
    out += [
        "### Layer 2 SHADOW — HDC abstractors (read-only comparison)",
        "",
        f"- unhandled facts (captured pre-mutation): {unhandled}",
        f"- active roles for scenario: {sorted(active_roles)}",
    ]
    if not unhandled:
        out.append("- nothing for HDC to analyze")
    else:
        for f in unhandled:
            out.append(f"\n#### Unhandled fact: `{f}`\n")

            for label, fn, kwargs in [
                (
                    "v1 HDC (head-match restricted)",
                    crystallize_by_hdc_analogy,
                    dict(unhandled_fact=f, store=store,
                         properties_by_substance=SUBSTANCE_PROPERTIES,
                         codebook=codebook),
                ),
                (
                    "v2 HDC (unconstrained peer search)",
                    crystallize_by_hdc_unconstrained,
                    dict(unhandled_fact=f, store=store,
                         properties_by_substance=SUBSTANCE_PROPERTIES,
                         codebook=codebook),
                ),
                (
                    "v3 HDC (role-weighted, fire-context)",
                    crystallize_by_hdc_role_weighted,
                    dict(unhandled_fact=f, facts=parsed["facts"], store=store,
                         properties_by_substance=SUBSTANCE_PROPERTIES,
                         property_roles=PROPERTY_ROLES,
                         active_roles=active_roles,
                         codebook=codebook),
                ),
                (
                    "v4 HDC (role-weighted + TOKEN-level projection)",
                    crystallize_by_hdc_v4_token_projection,
                    dict(unhandled_fact=f, facts=parsed["facts"], store=store,
                         properties_by_substance=SUBSTANCE_PROPERTIES,
                         property_roles=PROPERTY_ROLES,
                         active_roles=active_roles,
                         codebook=codebook),
                ),
            ]:
                new_rules, hdc_log = fn(**kwargs)
                out.append(f"- **{label}:**")
                for line in hdc_log:
                    out.append(f"  {line}")
                if new_rules:
                    out.append(
                        f"  → would crystallize: {[r.id for r in new_rules]}"
                    )
                else:
                    out.append("  → crystallizes nothing")
    out += ["", "---", ""]
    return out


def run() -> None:
    # Always start from a clean migrated store so runs are reproducible.
    store_path = HERE / "rule_store.json"
    if store_path.exists():
        store_path.unlink()
    store = migrate_authored_rules(force=True)

    scenarios = json.loads((HERE / "scenarios.json").read_text())

    out: list[str] = [
        "# Results (four-layer symbolic pipeline)",
        "",
        f"Run: {datetime.utcnow().isoformat()}Z",
        "Pipeline: parser → retriever → engine → abstractor (no LLM, no matmul)",
        f"Initial store size: {len(store.all_rules())} (all source=authored, confidence=1.0)",
        "",
        "---",
        "",
    ]

    codebook = Codebook(seed=42)

    for s in scenarios:
        out += run_scenario(s, store, codebook)

    out += [
        "## Final rule store snapshot",
        "",
        f"- final store size: {len(store.all_rules())}",
        "- rules by source:",
    ]
    by_src: dict[str, list[str]] = {}
    for e in store.all_entries():
        by_src.setdefault(e["source"], []).append(
            f"{e['id']} (conf={e['confidence']}, used={e['usage_count']})"
        )
    for src, items in by_src.items():
        out.append(f"  - **{src}** ({len(items)}):")
        for it in items:
            out.append(f"    - {it}")

    (HERE / "results_symbolic.md").write_text("\n".join(out))
    print(f"Wrote {HERE / 'results_symbolic.md'}")
    print(f"Final store: {store_path}")


if __name__ == "__main__":
    run()
