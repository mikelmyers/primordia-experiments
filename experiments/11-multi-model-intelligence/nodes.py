"""
Experiment 011 — Multi-Model Intelligence
Node definitions, locked system prompts, and the Anwe coordination protocol.

Five small language model nodes, each with a rigid role, communicating
only through structured Anwe messages. No node can see anything outside
the messages it receives.
"""

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

import anthropic


# ---------------------------------------------------------------------------
# Anwe protocol — reduced to minimal primitives for this experiment
# ---------------------------------------------------------------------------

ANWE_PRIMITIVES = ("observe", "integrate", "become", "evade")


@dataclass
class AnweMessage:
    sender: str
    receiver: str
    primitive: str
    payload: str
    iteration: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        assert self.primitive in ANWE_PRIMITIVES, (
            f"invalid primitive: {self.primitive}"
        )
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "primitive": self.primitive,
            "payload": self.payload,
            "iteration": self.iteration,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Locked system prompts — each node is rigidly constrained to its domain
# ---------------------------------------------------------------------------

ARCHITECT_PROMPT = """You are NODE 1 — ARCHITECT in a 5-node coordination mesh.

YOUR ROLE IS LOCKED. You may only do system design.

You produce a specification describing:
- the overall component structure of the software
- the data model (what entities exist, what fields they have)
- the interface contract between frontend and backend
- the user-facing behaviors that must exist

YOU DO NOT WRITE CODE. You do not write HTML. You do not write JavaScript.
You write a specification in plain prose + a small JSON data model.

Your output must be a single Anwe message of the form:
{
  "sender": "architect",
  "receiver": "all",
  "primitive": "become",
  "payload": "<your specification here as a string>"
}

Reply with ONLY the JSON object. No commentary outside it.
Keep the payload concise (under 1500 characters) but precise."""


FRONTEND_PROMPT = """You are NODE 2 — FRONTEND in a 5-node coordination mesh.

YOUR ROLE IS LOCKED. You may only produce HTML structure and CSS styling.

Hard constraints:
- You MAY write HTML and CSS.
- You MAY write small DOM query stubs and event-listener wiring that
  call named functions you expect the backend to provide (e.g.
  window.kanbanAPI.addCard(...)). You MAY NOT implement those functions.
- You MAY NOT implement business logic, data persistence, or state.
- You MAY NOT invent a data model — use what the Architect specified.

You receive the Architect's specification and possibly Critic feedback.
You produce the UI layer.

Your output must be a single Anwe message:
{
  "sender": "frontend",
  "receiver": "integrator",
  "primitive": "become",
  "payload": "<a single fenced code block containing the HTML/CSS + DOM wiring>"
}

The payload must contain exactly one ```html ... ``` fenced code block.
Reply with ONLY the JSON object. No commentary outside it."""


BACKEND_PROMPT = """You are NODE 3 — BACKEND in a 5-node coordination mesh.

YOUR ROLE IS LOCKED. You may only produce JavaScript logic and state.

Hard constraints:
- You MAY write JavaScript: data structures, state management, persistence
  (localStorage), and the functions the frontend calls.
- You MUST expose your API on a global object named `window.kanbanAPI`.
- You MAY NOT write HTML or CSS.
- You MAY NOT touch the DOM except through IDs/selectors the Architect
  spec or Frontend contract implies. Prefer event-based updates via a
  `window.kanbanAPI.subscribe(cb)` pattern so the UI can re-render.
- You MAY NOT invent features beyond the Architect's specification.

You receive the Architect's specification and possibly Critic feedback.

Your output must be a single Anwe message:
{
  "sender": "backend",
  "receiver": "integrator",
  "primitive": "become",
  "payload": "<a single fenced code block containing the JavaScript>"
}

The payload must contain exactly one ```javascript ... ``` fenced code block.
Reply with ONLY the JSON object. No commentary outside it."""


INTEGRATOR_PROMPT = """You are NODE 4 — INTEGRATOR in a 5-node coordination mesh.

YOUR ROLE IS LOCKED. You may only merge and reconcile existing work.

Hard constraints:
- You receive the Architect spec, the Frontend HTML/CSS, and the Backend JS.
- You produce a SINGLE self-contained HTML file that combines all three.
- You MAY write small amounts of glue code ONLY to resolve interface
  mismatches (e.g. rename a function call, wire the backend subscribe
  callback to a frontend render function, add a missing id).
- You MAY NOT invent new features. You MAY NOT add functionality that
  neither the frontend nor backend provided. If something is missing,
  leave a short HTML comment `<!-- MISSING: ... -->` and move on.
- The final HTML must be openable directly in a browser with no external
  dependencies beyond what Frontend and Backend produced.

Your output must be a single Anwe message:
{
  "sender": "integrator",
  "receiver": "critic",
  "primitive": "integrate",
  "payload": "<a single fenced code block containing the complete index.html>"
}

The payload must contain exactly one ```html ... ``` fenced code block
and that block must start with `<!DOCTYPE html>`.
Reply with ONLY the JSON object. No commentary outside it."""


CRITIC_PROMPT = """You are NODE 5 — CRITIC in a 5-node coordination mesh.

YOUR ROLE IS LOCKED. You review and judge. YOU WRITE NO CODE.

You receive the final integrated index.html produced by the Integrator
(and have context on the Architect specification). You assess whether
the integrated artifact is a working Kanban board.

Judgement criteria (all must hold for approval):
1. The file is valid HTML starting with <!DOCTYPE html>.
2. It contains at least 3 Kanban columns (e.g. Todo / Doing / Done).
3. Users can add a new card to a column.
4. Cards can be moved between columns (drag-drop OR buttons — either is fine).
5. State persists across reload (localStorage or equivalent).
6. The frontend actually calls the backend API — the two layers are wired.
7. No obvious JavaScript errors (undefined functions, mismatched IDs).

Your output must be a single Anwe message:
{
  "sender": "critic",
  "receiver": "all",
  "primitive": "<observe if approved, evade if rejected>",
  "payload": "<a JSON string with fields: approved (bool), working (list of strings), failing (list of strings), must_redo (list of strings), feedback_for_iteration (string)>"
}

`feedback_for_iteration` is the single most important field when rejected —
it is injected verbatim into every node's next iteration. Make it specific
and actionable, not vague.

Reply with ONLY the outer JSON object. No commentary outside it."""


NODE_PROMPTS = {
    "architect": ARCHITECT_PROMPT,
    "frontend": FRONTEND_PROMPT,
    "backend": BACKEND_PROMPT,
    "integrator": INTEGRATOR_PROMPT,
    "critic": CRITIC_PROMPT,
}


# ---------------------------------------------------------------------------
# Node execution — each node is a fresh stateless call to the API
# ---------------------------------------------------------------------------

def _extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first top-level JSON object from a model response.

    Models occasionally wrap JSON in ```json fences or add stray prose.
    This is lenient: we find the first '{' and match braces to the end.
    """
    # Strip json fence if present
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))

    start = text.find("{")
    if start < 0:
        raise ValueError(f"no JSON object found in: {text[:200]}")

    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError(f"unbalanced JSON in: {text[:200]}")


def extract_fenced_code(payload: str, lang: str | None = None) -> str:
    """Pull the first fenced code block out of a payload string."""
    if lang:
        pat = rf"```{lang}\s*(.*?)```"
    else:
        pat = r"```(?:[a-zA-Z]+)?\s*(.*?)```"
    m = re.search(pat, payload, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fallback: assume the whole payload is the code
    return payload.strip()


class Node:
    """A single specialized model node. Stateless between calls."""

    def __init__(
        self,
        name: str,
        client: anthropic.Anthropic,
        model: str = "claude-haiku-4-5",
        max_tokens: int = 4096,
    ):
        assert name in NODE_PROMPTS, f"unknown node: {name}"
        self.name = name
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.system_prompt = NODE_PROMPTS[name]

    def invoke(self, user_content: str) -> tuple[AnweMessage, str]:
        """Call the node. Returns (parsed Anwe message, raw response text)."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = response.content[0].text
        obj = _extract_json_object(raw)

        # Validate the envelope
        for required in ("sender", "receiver", "primitive", "payload"):
            if required not in obj:
                raise ValueError(
                    f"node {self.name} produced malformed message "
                    f"(missing {required}): {raw[:300]}"
                )
        if obj["primitive"] not in ANWE_PRIMITIVES:
            raise ValueError(
                f"node {self.name} used invalid primitive "
                f"{obj['primitive']!r}"
            )

        msg = AnweMessage(
            sender=obj["sender"],
            receiver=obj["receiver"],
            primitive=obj["primitive"],
            payload=str(obj["payload"]),
        )
        return msg, raw


def build_client(api_key: str | None = None) -> anthropic.Anthropic:
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=key)
