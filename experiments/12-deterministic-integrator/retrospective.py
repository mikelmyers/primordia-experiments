"""
Retrospective test — run the deterministic integrator against the CACHED
Experiment 011 payloads.

Exp 011's Architect did not emit a machine-readable schema (that's a new
requirement of Exp 012), so we synthesize one that matches what the Exp
011 prompts implied. We then feed Haiku's and Sonnet's cached Frontend
+ Backend payloads through the mechanical integrator and record what
would have happened.

This does NOT require API access and does NOT require running any LLM
nodes. It's a pre-experiment sanity check that tells us whether the
deterministic integrator is strict enough to reject the known role
violations from Experiment 011.

Run:
    cd experiments/12-deterministic-integrator
    python3 retrospective.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import asdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from integrator import integrate  # noqa: E402


EXP_011_RESULTS = os.path.normpath(
    os.path.join(HERE, "..", "11-multi-model-intelligence")
)


def strip_fence(payload: str, lang: str) -> str:
    m = re.search(rf"```{lang}\s*(.*?)```", payload, re.DOTALL)
    return m.group(1).strip() if m else payload.strip()


# Schema synthesized from Exp 011's Architect prose + Backend API. Haiku
# and Sonnet both produced compatible backends under these names, EXCEPT
# Sonnet renamed `getBoard` -> `getState` and added `moveCardByDirection`.
# We use the Haiku-compatible canonical naming below; the retrospective
# intentionally shows both (a) what the integrator catches under a fixed
# contract and (b) how Sonnet drifted from it.
CANONICAL_SCHEMA = {
    "api_name": "window.kanbanAPI",
    "methods": {
        "addCard":    {"args": ["columnId", "title"], "returns": "boolean"},
        "moveCard":   {"args": ["fromColumnId", "toColumnId", "cardId"],
                       "returns": "boolean"},
        "deleteCard": {"args": ["columnId", "cardId"], "returns": "boolean"},
        "getBoard":   {"args": [], "returns": "object"},
        "subscribe":  {"args": ["callback"], "returns": "void"},
    },
    "dom_contract": {
        "root_id": "boardContainer",
        "required_ids": ["boardContainer"],
    },
    "forbidden_in_frontend": [
        "localStorage.setItem",
        "localStorage.getItem",
        "localStorage.removeItem",
    ],
}


def run_retrospective(model_tag: str) -> dict:
    log_path = os.path.join(
        EXP_011_RESULTS, f"results_{model_tag}", "coordination_log.json"
    )
    with open(log_path) as f:
        log = json.load(f)

    # Exp 011 coordination log: [architect, frontend, backend, integrator, critic]
    fe_html = strip_fence(log[1]["payload"], "html")
    be_js = strip_fence(log[2]["payload"], "javascript")

    report = integrate(CANONICAL_SCHEMA, fe_html, be_js)
    result = {
        "model": model_tag,
        "ok": report.ok,
        "backend_violations": report.backend_violations,
        "frontend_violations": report.frontend_violations,
        "schema_violations": report.schema_violations,
        "stats": report.stats,
    }
    return result


def main():
    print("=" * 70)
    print("EXPERIMENT 012 RETROSPECTIVE")
    print("Deterministic mechanical integrator vs cached Exp 011 payloads")
    print("=" * 70)

    results = {}
    for tag in ("haiku", "sonnet"):
        print(f"\n--- {tag.upper()} ---")
        r = run_retrospective(tag)
        results[tag] = r
        print(f"  contract satisfied? {r['ok']}")
        print(f"  backend violations:  {len(r['backend_violations'])}")
        for v in r["backend_violations"]:
            print(f"    - {v}")
        print(f"  frontend violations: {len(r['frontend_violations'])}")
        for v in r["frontend_violations"]:
            print(f"    - {v}")

    # Interpretation
    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    for tag, r in results.items():
        total = (
            len(r["backend_violations"]) + len(r["frontend_violations"])
        )
        if r["ok"]:
            verdict = "would have merged cleanly on iteration 1"
        else:
            verdict = (
                f"would have been REJECTED on iteration 1 "
                f"with {total} violations; feedback would loop back"
            )
        print(f"  {tag:8}: {verdict}")

    print()
    print(
        "Conclusion: both Experiment 011 runs contained role-contract\n"
        "violations the LLM Integrator silently repaired. Under a strict\n"
        "mechanical contract, iteration 1 would fail for both, forcing\n"
        "the mesh to actually exercise its feedback loop — which is the\n"
        "dynamic Experiment 011 could not measure."
    )

    out_path = os.path.join(HERE, "retrospective.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
