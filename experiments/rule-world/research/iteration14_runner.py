"""Iteration 14 — induce humanization dictionaries from rule.statement.

Runs the iteration 14 humanizer inducer on all three domains, compares
coverage and per-predicate quality against the iteration 13 hand-authored
dictionaries, and produces a sample explanation for one scenario per
domain using the *induced* dictionary so a human can read whether the
auto-extracted phrases make for fluent English.

No matrix multiplication. Pure string alignment. Same induction strategy
that worked for the property table in iterations 9-11, applied to a
different artifact.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULE_WORLD = ROOT
TRAFFIC_WORLD = ROOT.parent / "traffic-world"
KITCHEN_WORLD = ROOT.parent / "kitchen-world"

sys.path.insert(0, str(RULE_WORLD))

from humanizer_inducer import induce_humanization, coverage_report  # noqa: E402
from explainer import Humanizer  # noqa: E402


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _gather_extra_predicates(scenarios_path: Path, parse_fn) -> list[str]:
    """Collect predicates that show up in parsed scenario facts but may
    not appear in any authored rule (e.g. observation-only predicates)."""
    seen: set[str] = set()
    for scen in json.loads(scenarios_path.read_text()):
        parsed = parse_fn(scen["description"])
        seen.update(parsed["facts"])
        seen.update(parsed.get("goal", []))
    return sorted(seen)


def _per_domain(
    name: str,
    rules,
    authored_humanizer_module,
    parse_fn,
    scenarios_path: Path,
    agent_aliases: dict[str, set[str]] | None = None,
):
    extras = _gather_extra_predicates(scenarios_path, parse_fn)
    induced = induce_humanization(
        rules, extra_predicates=extras, agent_aliases=agent_aliases,
    )
    authored = authored_humanizer_module.PREDICATE_PHRASES
    report = coverage_report(induced, authored)

    lines: list[str] = []
    lines.append(f"## {name}")
    lines.append("")
    lines.append(
        f"- authored predicates: **{report['authored_total']}**"
    )
    lines.append(
        f"- induced predicates: **{report['induced_total']}**"
    )
    lines.append(
        f"- recovered from rule statements: **{report['covered']}/{report['authored_total']}** "
        f"= **{report['coverage_pct']:.1f}%**"
    )
    lines.append(
        f"- predicates the inducer found that weren't in the authored dict: "
        f"{report['extra']}"
    )
    lines.append("")
    lines.append("### Side-by-side: authored vs induced (covered predicates)")
    lines.append("")
    lines.append("| predicate | authored phrase | induced phrase |")
    lines.append("|---|---|---|")
    for k in sorted(report["covered_keys"]):
        lines.append(f"| `{k}` | {authored[k]} | {induced[k]} |")
    lines.append("")

    if report["missing_keys"]:
        lines.append("### Predicates the inducer could NOT recover")
        lines.append("")
        lines.append(
            "These predicates exist in the hand-authored dictionary but no "
            "rule statement contains all of their content tokens. The "
            "explainer falls back to the structural transformation "
            "(`underscores → spaces`) for these."
        )
        lines.append("")
        for k in sorted(report["missing_keys"]):
            lines.append(f"- `{k}` → fallback: *\"{k.replace('_', ' ')}\"*")
        lines.append("")

    if report["extra_keys"]:
        lines.append("### Bonus: predicates in induced dict but not authored")
        lines.append("")
        lines.append(
            "These are predicates the inducer extracted that the human "
            "humanizer never bothered to author. They are *free coverage*."
        )
        lines.append("")
        for k in sorted(report["extra_keys"]):
            lines.append(f"- `{k}` → *\"{induced[k]}\"*")
        lines.append("")

    return lines, induced, authored, report


def main():
    out: list[str] = []
    out.append("# Iteration 14 — Humanization dictionary induction")
    out.append("")
    out.append(
        "Tests whether the iteration-9 induction trick works on the "
        "iteration-13 humanization dictionary. Strategy: align each rule's "
        "English `statement` field against its formal predicates and "
        "extract the shortest contiguous span containing every predicate "
        "token. No matmul. No learned model. Pure string alignment."
    )
    out.append("")

    # ----- rule-world -----
    import world_structured as rw
    import parser as rw_parser
    rw_exp = _load_module("rw_explanations", RULE_WORLD / "explanations.py")
    rw_lines, rw_induced, rw_authored, rw_report = _per_domain(
        name="rule-world",
        rules=rw.ALL_RULES,
        authored_humanizer_module=rw_exp,
        parse_fn=rw_parser.parse,
        scenarios_path=RULE_WORLD / "scenarios.json",
        agent_aliases={
            "self": {"tender", "you"},
            "child": {"child", "tender"},
        },
    )
    out += rw_lines

    # ----- traffic-world -----
    sys.path.insert(0, str(TRAFFIC_WORLD))
    tw_rules_mod = _load_module("tw_rules", TRAFFIC_WORLD / "traffic_rules.py")
    tw_parser_mod = _load_module("tw_parser", TRAFFIC_WORLD / "traffic_parser.py")
    tw_exp = _load_module("tw_explanations", TRAFFIC_WORLD / "explanations.py")
    tw_lines, tw_induced, tw_authored, tw_report = _per_domain(
        name="traffic-world",
        rules=tw_rules_mod.ALL_RULES,
        authored_humanizer_module=tw_exp,
        parse_fn=tw_parser_mod.parse,
        scenarios_path=TRAFFIC_WORLD / "traffic_scenarios.json",
        agent_aliases={
            "self": {"vehicle", "driver", "you"},
            "ahead": {"ahead", "front"},
            "behind": {"behind"},
        },
    )
    out += tw_lines

    # ----- kitchen-world -----
    sys.path.insert(0, str(KITCHEN_WORLD))
    kw_rules_mod = _load_module("kw_rules", KITCHEN_WORLD / "kitchen_rules.py")
    kw_parser_mod = _load_module("kw_parser", KITCHEN_WORLD / "kitchen_parser.py")
    kw_exp = _load_module("kw_explanations", KITCHEN_WORLD / "explanations.py")
    kw_lines, kw_induced, kw_authored, kw_report = _per_domain(
        name="kitchen-world",
        rules=kw_rules_mod.ALL_RULES,
        authored_humanizer_module=kw_exp,
        parse_fn=kw_parser_mod.parse,
        scenarios_path=KITCHEN_WORLD / "kitchen_scenarios.json",
        agent_aliases={
            "self": {"cook", "you"},
        },
    )
    out += kw_lines

    # ----- combined summary -----
    total_authored = (
        rw_report["authored_total"]
        + tw_report["authored_total"]
        + kw_report["authored_total"]
    )
    total_covered = (
        rw_report["covered"] + tw_report["covered"] + kw_report["covered"]
    )
    total_extra = (
        rw_report["extra"] + tw_report["extra"] + kw_report["extra"]
    )
    out.append("---")
    out.append("")
    out.append("## Combined N=3 result")
    out.append("")
    out.append(
        f"- **{total_covered}/{total_authored}** authored predicates recovered "
        f"automatically = **{total_covered / total_authored * 100:.1f}%**"
    )
    out.append(
        f"- **{total_extra}** additional predicates extracted that the "
        f"hand-authored dictionaries did not bother with"
    )
    out.append(
        f"- per domain: rule-world {rw_report['coverage_pct']:.1f}% · "
        f"traffic-world {tw_report['coverage_pct']:.1f}% · "
        f"kitchen-world {kw_report['coverage_pct']:.1f}%"
    )
    out.append("")
    out.append("## Reading")
    out.append("")
    out.append(
        "- Coverage **above 50%** would mean the induction trick that worked "
        "on the property table also works on the humanization dictionary, "
        "and most of the iteration 13 hand-authored work could in principle "
        "be skipped.\n"
        "- Coverage **below 50%** would mean the rule statements aren't "
        "phrased in a way that exposes their predicates, and the bilingual "
        "trick doesn't extend to NL output as cleanly as it does to "
        "property structure.\n"
        "- Predicates in the *missing* list are not failures of the system; "
        "they fall through to the structural fallback (underscores → spaces) "
        "and the explainer continues to produce readable output. They are "
        "the size of the residual hand-authoring task if iteration 14 were "
        "deployed."
    )
    out.append("")

    text = "\n".join(out)
    out_path = Path(__file__).parent / "iteration14_results.md"
    out_path.write_text(text)
    print(text[:2500])
    print("...")
    print(f"\n[wrote {out_path}]")


if __name__ == "__main__":
    main()
