"""Rule World runner.

Loads world.md and agent.md, presents each scenario from scenarios.md to the
Claude API as the agent, and logs results to results.md.

Usage: ANTHROPIC_API_KEY=... python runner.py
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

HERE = Path(__file__).parent
MODEL = "claude-opus-4-6"


def load(name: str) -> str:
    return (HERE / name).read_text()


def parse_scenarios(text: str) -> list[dict]:
    blocks = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
    scenarios = []
    for b in blocks:
        title, *rest = b.splitlines()
        scenarios.append({"title": title.strip(), "body": "\n".join(rest).strip()})
    return scenarios


def parse_response(text: str) -> dict:
    def grab(label: str) -> str:
        m = re.search(
            rf"^{label}:\s*\n?(.*?)(?=^[A-Z_]+:|\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
        return m.group(1).strip() if m else ""

    return {
        "reasoning": grab("REASONING"),
        "cited_rules": grab("CITED_RULES"),
        "gap": grab("GAP"),
        "gap_resolution": grab("GAP_RESOLUTION"),
        "action": grab("ACTION"),
    }


def run() -> None:
    world = load("world.md")
    agent = load("agent.md")
    scenarios = parse_scenarios(load("scenarios.md"))

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    system = f"{agent}\n\n---\n\n# world.md\n\n{world}"

    out = ["# Results", "", f"Run: {datetime.utcnow().isoformat()}Z", f"Model: {MODEL}", ""]

    for s in scenarios:
        user_msg = f"# {s['title']}\n\n{s['body']}"
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if hasattr(b, "text"))
        parsed = parse_response(text)

        out += [
            f"## {s['title']}",
            "",
            "**Scenario:**",
            "",
            s["body"],
            "",
            "**Cited rules:** " + (parsed["cited_rules"] or "(none)"),
            "",
            "**Gap encountered:** " + (parsed["gap"] or "(unspecified)"),
            "",
            "**Gap resolution:**",
            "",
            parsed["gap_resolution"] or "n/a",
            "",
            "**Action:**",
            "",
            parsed["action"] or "(none)",
            "",
            "**Full reasoning:**",
            "",
            parsed["reasoning"] or text,
            "",
            "---",
            "",
        ]

    (HERE / "results.md").write_text("\n".join(out))
    print(f"Wrote {HERE / 'results.md'}")


if __name__ == "__main__":
    run()
