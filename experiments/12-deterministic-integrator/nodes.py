"""
Experiment 012 — Deterministic Integrator

Same four LLM nodes as Experiment 011 (architect, frontend, backend, critic),
minus the LLM Integrator. Node 4 is replaced by a deterministic Python
function in `integrator.py`.

The key prompt changes vs Experiment 011:

1. Architect MUST emit a machine-readable interface schema (a ```json fenced
   block inside its payload). The schema is consumed by the mechanical
   integrator, not by an LLM.

2. Frontend and Backend are told explicitly that their output is checked by
   a mechanical contract enforcer, not by a forgiving LLM. The contract
   violations are enumerated in-prompt.

3. Forbidden patterns are named: Frontend may not touch localStorage, may
   not declare top-level functions named after API methods, and must route
   all business logic through the declared `window.kanbanAPI`.

The Anwe envelope itself is unchanged.
"""

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

import anthropic


# ---------------------------------------------------------------------------
# Anwe protocol — same reduced primitives as Experiment 011
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
# Locked system prompts — tightened from Experiment 011
# ---------------------------------------------------------------------------

ARCHITECT_PROMPT = """You are NODE 1 — ARCHITECT in a 4-node coordination mesh.

YOUR ROLE IS LOCKED. You may only do system design.

This mesh has NO LLM Integrator. The Frontend and Backend outputs are merged
by a deterministic Python function that enforces a STRICT INTERFACE CONTRACT.
Your specification IS that contract. If you leave it ambiguous, the mechanical
integrator will reject downstream nodes and iteration will be wasted.

Your payload MUST contain exactly two things, in order:

(A) A short prose specification (< 800 chars) describing component structure,
    data model, and user-facing behaviors — same as usual.

(B) A single ```json fenced block containing a machine-readable interface
    schema with exactly these top-level keys:

    {
      "api_name": "window.kanbanAPI",
      "methods": {
        "<method_name>": {"args": ["<arg1>", "<arg2>"], "returns": "<type>"},
        ...
      },
      "dom_contract": {
        "root_id": "<id the backend will render into>",
        "required_ids": ["<id1>", "<id2>", ...]
      },
      "forbidden_in_frontend": [
        "localStorage.setItem",
        "localStorage.getItem",
        "localStorage.removeItem"
      ]
    }

    The `methods` keys will become `window.kanbanAPI.<name>`. The Frontend
    MUST call these methods for all business logic; the Backend MUST
    implement them. Declare EVERY method the Frontend will need to call
    — the mechanical integrator will reject any Frontend call to an
    undeclared method, and will reject any Backend that omits one.

YOU DO NOT WRITE CODE. No HTML. No JavaScript beyond the JSON schema.

Your output must be a single Anwe message of the form:
{
  "sender": "architect",
  "receiver": "all",
  "primitive": "become",
  "payload": "<prose spec, then a ```json fenced block with the schema>"
}

Reply with ONLY the outer JSON object. No commentary outside it."""


FRONTEND_PROMPT = """You are NODE 2 — FRONTEND in a 4-node coordination mesh.

YOUR ROLE IS LOCKED. You may only produce HTML structure, CSS styling, and
DOM wiring that CALLS INTO `window.kanbanAPI`.

CRITICAL: This mesh has NO LLM Integrator. Your output is merged by a
deterministic Python function that will REJECT YOU if you violate the
interface contract. There is no forgiving LLM to repair your mistakes.

Hard constraints — every one of these is enforced by regex:

1. You MUST call `window.kanbanAPI.<method>(...)` for every business-logic
   action declared in the Architect's schema (add, move, delete, read, etc.).
   The integrator counts these calls. Zero calls = rejection.

2. You MAY NOT declare top-level JavaScript functions whose names match
   methods in the Architect's schema. For example, if the schema declares
   `addCard`, you MUST NOT write `function addCard(...)`. Call
   `window.kanbanAPI.addCard(...)` instead.

3. You MAY NOT use `localStorage.setItem`, `localStorage.getItem`, or
   `localStorage.removeItem`. Persistence belongs to the Backend. Any
   occurrence triggers immediate rejection.

4. You MAY declare local helpers like `renderBoard`, `handleSubmit`, etc.
   — anything NOT named in the schema's `methods` is fine.

5. You MUST include every id listed in `dom_contract.required_ids` in your
   HTML, and the `dom_contract.root_id` must exist.

6. You MAY NOT invent new API methods. If the Architect didn't declare it,
   you can't call it.

You receive the Architect's specification and (if rejected) the exact
violation report from the mechanical integrator. Read the report literally
— it tells you what to fix.

Your output must be a single Anwe message:
{
  "sender": "frontend",
  "receiver": "integrator",
  "primitive": "become",
  "payload": "<a single fenced code block containing the HTML/CSS + DOM wiring>"
}

The payload must contain exactly one ```html ... ``` fenced code block.
Reply with ONLY the outer JSON object. No commentary outside it."""


BACKEND_PROMPT = """You are NODE 3 — BACKEND in a 4-node coordination mesh.

YOUR ROLE IS LOCKED. You may only produce JavaScript logic and state.

CRITICAL: This mesh has NO LLM Integrator. Your output is merged by a
deterministic Python function that will REJECT YOU if you fail to expose
every method declared in the Architect's schema.

Hard constraints:

1. You MUST expose `window.kanbanAPI` as a global object.

2. For EVERY method in the Architect's schema `methods` section, you MUST
   define it on `window.kanbanAPI`. The mechanical integrator will check
   that each method name declared in the schema is present in your JS.
   Missing one method = full rejection.

3. You MUST implement persistence via `localStorage` (the Frontend is
   banned from touching it).

4. You MAY NOT write HTML or CSS. Your payload must contain only a
   ```javascript ... ``` fenced code block.

5. You MAY NOT invent features beyond the Architect's specification.
   Methods not in the schema will not be called by Frontend and add
   risk without benefit.

6. You SHOULD expose a `subscribe(callback)` pattern so the Frontend can
   re-render on state changes. If the Architect's schema includes
   `subscribe`, you MUST implement it.

You receive the Architect's specification and (if rejected) the exact
violation report from the mechanical integrator.

Your output must be a single Anwe message:
{
  "sender": "backend",
  "receiver": "integrator",
  "primitive": "become",
  "payload": "<a single fenced code block containing the JavaScript>"
}

The payload must contain exactly one ```javascript ... ``` fenced code block.
Reply with ONLY the outer JSON object. No commentary outside it."""


CRITIC_PROMPT = """You are NODE 4 — CRITIC in a 4-node coordination mesh.

YOUR ROLE IS LOCKED. You review and judge. YOU WRITE NO CODE.

You receive the final integrated index.html produced by a DETERMINISTIC
mechanical integrator (not an LLM). By the time you see it, the contract
between Frontend and Backend has already been verified — every method in
the Architect's schema is defined in the Backend, called in the Frontend,
and the Frontend contains no banned patterns.

Your job is to check behavioral correctness that the mechanical integrator
cannot check from regex alone:

1. The file is valid HTML starting with <!DOCTYPE html>.
2. At least 3 Kanban columns (e.g. Todo / Doing / Done).
3. Users can add a new card to a column.
4. Cards can be moved between columns (drag-drop OR buttons — either is fine).
5. State persists across reload.
6. No obvious JavaScript errors (undefined references, id mismatches, etc.).
7. The interface surface matches the Architect's schema (sanity check).

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
    "critic": CRITIC_PROMPT,
}


# ---------------------------------------------------------------------------
# JSON / fenced-code extraction (copied from Experiment 011 for independence)
# ---------------------------------------------------------------------------

def _extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first top-level JSON object from a model response."""
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1))
        except json.JSONDecodeError:
            pass  # fall through to brace-matching

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
    return payload.strip()


def extract_architect_schema(architect_payload: str) -> dict[str, Any]:
    """Pull the ```json schema block out of the Architect's payload.

    The Architect is instructed to emit prose followed by exactly one
    ```json fenced block containing the machine-readable interface schema.
    """
    m = re.search(r"```json\s*(\{.*?\})\s*```", architect_payload, re.DOTALL)
    if not m:
        raise ValueError(
            "Architect did not emit a ```json fenced schema block. "
            "This is a contract violation from Node 1 — the mesh cannot "
            "proceed without a machine-readable interface schema."
        )
    return json.loads(m.group(1))


# ---------------------------------------------------------------------------
# Node execution — identical to Experiment 011
# ---------------------------------------------------------------------------

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
