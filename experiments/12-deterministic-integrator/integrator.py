"""
Experiment 012 — Deterministic Mechanical Integrator.

Replaces the LLM Integrator from Experiment 011 with a pure Python function
that enforces a strict interface contract between Frontend and Backend.

The contract is the Architect's machine-readable schema (extracted from the
Architect's payload as a ```json fenced block). The integrator:

  1. Verifies the Backend exposes every method declared in the schema.
  2. Verifies the Frontend calls at least one method from the schema
     (and doesn't call undeclared ones).
  3. Verifies the Frontend contains no banned patterns (localStorage,
     duplicate API-method function declarations).
  4. Verifies the Frontend contains every required DOM id.
  5. If all checks pass, mechanically merges Frontend HTML + Backend JS
     into a single self-contained index.html, with the Backend JS injected
     BEFORE any frontend script (so `window.kanbanAPI` is defined first).
  6. If any check fails, returns a structured ContractReport that the run
     loop feeds back into the next iteration of Frontend and Backend.

There is NO repair step. There is NO semantic rewriting. The integrator
either merges cleanly or refuses and tells you why.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Contract report — the structured feedback the run loop sends back to nodes
# ---------------------------------------------------------------------------

@dataclass
class ContractReport:
    ok: bool
    backend_violations: list[str] = field(default_factory=list)
    frontend_violations: list[str] = field(default_factory=list)
    schema_violations: list[str] = field(default_factory=list)
    merged_html: str = ""
    stats: dict[str, Any] = field(default_factory=dict)

    def as_feedback(self) -> str:
        """Render this report as a prose feedback string that can be
        injected into the next iteration of Frontend and Backend."""
        if self.ok:
            return "MECHANICAL INTEGRATOR: contract satisfied, merged successfully."
        lines = ["MECHANICAL INTEGRATOR REJECTED THE OUTPUT."]
        lines.append(
            "The integrator is a regex-based contract checker. It does not "
            "interpret intent. Fix the SPECIFIC violations listed below "
            "literally — do not rewrite everything."
        )
        if self.schema_violations:
            lines.append("\nSCHEMA VIOLATIONS (Architect):")
            for v in self.schema_violations:
                lines.append(f"  - {v}")
        if self.backend_violations:
            lines.append("\nBACKEND VIOLATIONS:")
            for v in self.backend_violations:
                lines.append(f"  - {v}")
        if self.frontend_violations:
            lines.append("\nFRONTEND VIOLATIONS:")
            for v in self.frontend_violations:
                lines.append(f"  - {v}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "backend_violations": self.backend_violations,
            "frontend_violations": self.frontend_violations,
            "schema_violations": self.schema_violations,
            "stats": self.stats,
            "merged_html_chars": len(self.merged_html),
        }


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_schema(schema: dict[str, Any]) -> list[str]:
    """Check that the Architect's schema has the required shape.

    Returns a list of violation strings (empty if the schema is well-formed).
    """
    violations: list[str] = []

    if not isinstance(schema, dict):
        return [f"schema is not a JSON object (got {type(schema).__name__})"]

    api_name = schema.get("api_name")
    if not isinstance(api_name, str) or not api_name.startswith("window."):
        violations.append(
            f"schema.api_name must be a string starting with 'window.' "
            f"(got {api_name!r})"
        )

    methods = schema.get("methods")
    if not isinstance(methods, dict) or not methods:
        violations.append("schema.methods must be a non-empty object")
    else:
        for name, spec in methods.items():
            if not isinstance(spec, dict):
                violations.append(f"schema.methods.{name} must be an object")
                continue
            if "args" not in spec or not isinstance(spec["args"], list):
                violations.append(f"schema.methods.{name}.args must be a list")
            if "returns" not in spec:
                violations.append(f"schema.methods.{name}.returns is missing")

    dom = schema.get("dom_contract")
    if not isinstance(dom, dict):
        violations.append("schema.dom_contract must be an object")
    else:
        if "root_id" not in dom or not isinstance(dom["root_id"], str):
            violations.append("schema.dom_contract.root_id must be a string")
        required_ids = dom.get("required_ids")
        if not isinstance(required_ids, list):
            violations.append(
                "schema.dom_contract.required_ids must be a list of strings"
            )

    forbidden = schema.get("forbidden_in_frontend")
    if forbidden is not None and not isinstance(forbidden, list):
        violations.append(
            "schema.forbidden_in_frontend must be a list of strings if provided"
        )

    return violations


# ---------------------------------------------------------------------------
# Backend contract checking
# ---------------------------------------------------------------------------

def _backend_exposes_method(backend_js: str, api_name: str, method: str) -> bool:
    """True iff `api_name.method` is assigned/defined somewhere in backend_js.

    We accept several common idioms:
      window.kanbanAPI.addCard = function() ...
      window.kanbanAPI.addCard = (args) => ...
      window.kanbanAPI = { addCard, ... }
      window.kanbanAPI = { addCard: function() {...}, ... }
      Object.assign(window.kanbanAPI, { addCard })
    """
    escaped_api = re.escape(api_name)
    escaped_method = re.escape(method)

    # Direct assignment: window.kanbanAPI.addCard = ...
    pat_direct = rf"{escaped_api}\.{escaped_method}\s*="
    if re.search(pat_direct, backend_js):
        return True

    # Object literal containing the key. We find `window.kanbanAPI = {`
    # and walk to the matching closing brace, then look for the method name
    # as a key. Accepted forms inside the body:
    #   addCard: function() {...}
    #   addCard: (x) => {...}
    #   addCard(x, y) { ... }            (ES6 shorthand — the key case
    #                                     the original regex missed)
    #   addCard,                          (punning shorthand)
    for start in _object_literal_bodies(backend_js, escaped_api):
        body = start
        # key followed by ':' (long form), '(' (ES6 shorthand), or
        # ',' / end-of-body (punning shorthand)
        key_pat = (
            rf"(^|[,\s\{{]){escaped_method}\s*(:|\(|,|\}}|$)"
        )
        if re.search(key_pat, body):
            return True

    # Object.assign(window.kanbanAPI, { addCard, ... })
    pat_assign = (
        rf"Object\.assign\s*\(\s*{escaped_api}\s*,\s*\{{([\s\S]*?)\}}\s*\)"
    )
    for m in re.finditer(pat_assign, backend_js):
        obj_body = m.group(1)
        key_pat = (
            rf"(^|[,\s\{{]){escaped_method}\s*(:|\(|,|\}}|$)"
        )
        if re.search(key_pat, obj_body):
            return True

    return False


def _object_literal_bodies(src: str, escaped_api: str) -> list[str]:
    """Yield the body (between `{` and matching `}`) of every object literal
    assigned to `<api_name> = {...}` in the source.

    Uses brace counting so nested braces inside method bodies don't confuse
    us. Ignores braces inside string literals (rudimentary parser)."""
    bodies: list[str] = []
    pat = rf"{escaped_api}\s*=\s*\{{"
    for m in re.finditer(pat, src):
        start = m.end() - 1  # position of the opening `{`
        depth = 0
        in_str: str | None = None
        i = start
        while i < len(src):
            ch = src[i]
            if in_str:
                if ch == "\\":
                    i += 2
                    continue
                if ch == in_str:
                    in_str = None
            else:
                if ch in ("'", '"', "`"):
                    in_str = ch
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        bodies.append(src[start + 1 : i])
                        break
            i += 1
    return bodies


def check_backend(backend_js: str, schema: dict[str, Any]) -> list[str]:
    """Return a list of violation strings for the backend JS."""
    violations: list[str] = []
    api_name = schema["api_name"]

    # 1. `window.kanbanAPI` must be assigned somewhere.
    escaped_api = re.escape(api_name)
    if not re.search(rf"{escaped_api}\s*=", backend_js):
        # Also accept Object.assign on a pre-existing object (rare but legal)
        if not re.search(rf"Object\.assign\s*\(\s*{escaped_api}", backend_js):
            violations.append(
                f"Backend does not assign `{api_name}` anywhere. "
                f"The Frontend cannot call into a nonexistent API."
            )

    # 2. Each declared method must be exposed.
    for method in schema.get("methods", {}).keys():
        if not _backend_exposes_method(backend_js, api_name, method):
            violations.append(
                f"Backend does not expose `{api_name}.{method}(...)`. "
                f"Add an assignment `{api_name}.{method} = function ...` "
                f"or include `{method}` as a key in the object literal "
                f"assigned to `{api_name}`."
            )

    # 3. Backend must implement persistence (Frontend is forbidden from it).
    if "localStorage" not in backend_js:
        violations.append(
            "Backend does not reference localStorage. The schema requires "
            "persistence across reloads, and the Frontend is forbidden "
            "from touching localStorage directly."
        )

    # 4. Backend should not contain HTML boilerplate.
    if "<!DOCTYPE" in backend_js or re.search(r"<html[\s>]", backend_js, re.I):
        violations.append(
            "Backend payload contains HTML boilerplate. The Backend is JS-only."
        )

    return violations


# ---------------------------------------------------------------------------
# Frontend contract checking
# ---------------------------------------------------------------------------

def _strip_html_comments(src: str) -> str:
    return re.sub(r"<!--[\s\S]*?-->", "", src)


def _extract_scripts(html: str) -> str:
    """Concatenate the bodies of all <script> tags (not src-attribute scripts).

    Frontend 'business logic' rules only apply inside <script> bodies. We
    ignore `<script src="..."></script>` tags — there shouldn't be any in
    a self-contained file anyway.
    """
    parts: list[str] = []
    for m in re.finditer(
        r"<script\b([^>]*)>([\s\S]*?)</script>", html, re.IGNORECASE
    ):
        attrs = m.group(1) or ""
        body = m.group(2) or ""
        if "src=" in attrs.lower():
            continue
        parts.append(body)
    return "\n".join(parts)


def check_frontend(frontend_html: str, schema: dict[str, Any]) -> list[str]:
    """Return a list of violation strings for the frontend HTML."""
    violations: list[str] = []
    api_name = schema["api_name"]
    api_short = api_name.split(".")[-1]  # "kanbanAPI"
    methods = list(schema.get("methods", {}).keys())

    no_comments = _strip_html_comments(frontend_html)
    script_bodies = _extract_scripts(no_comments)

    # 1. Every forbidden pattern is banned.
    forbidden = schema.get("forbidden_in_frontend", []) or []
    # Always enforce the core localStorage ban regardless of schema.
    baseline_forbidden = [
        "localStorage.setItem",
        "localStorage.getItem",
        "localStorage.removeItem",
    ]
    all_forbidden = list({*forbidden, *baseline_forbidden})
    for pattern in all_forbidden:
        if pattern in script_bodies:
            violations.append(
                f"Frontend uses forbidden pattern `{pattern}`. Persistence "
                f"belongs to the Backend — call `{api_name}.<method>(...)` "
                f"instead."
            )

    # 2. Frontend must not declare top-level functions named after
    #    schema methods.
    for method in methods:
        # `function addCard(` at word boundary
        pat_decl = rf"\bfunction\s+{re.escape(method)}\s*\("
        if re.search(pat_decl, script_bodies):
            violations.append(
                f"Frontend declares `function {method}(...)`. This shadows "
                f"the Backend's `{api_name}.{method}`. Replace with "
                f"`{api_name}.{method}(...)` at each call site and remove "
                f"the local declaration."
            )
        # `const addCard = (...) =>` or `let addCard = function(...)`
        pat_arrow = (
            rf"\b(?:const|let|var)\s+{re.escape(method)}\s*="
            r"\s*(?:\([^)]*\)\s*=>|function\b)"
        )
        if re.search(pat_arrow, script_bodies):
            violations.append(
                f"Frontend defines a local `{method}` via const/let/var. "
                f"This shadows the Backend's `{api_name}.{method}`. Use "
                f"`{api_name}.{method}(...)` at the call site instead."
            )

    # 3. Frontend must CALL the API at least once (otherwise it's not
    #    actually using the Backend, which is the whole point).
    api_call_pat = rf"\b{re.escape(api_name)}\.\w+\s*\("
    api_calls = re.findall(api_call_pat, script_bodies)
    if not api_calls:
        violations.append(
            f"Frontend makes zero calls to `{api_name}.<method>(...)`. "
            f"The Frontend is supposed to consume the Backend's API for "
            f"all business logic. Wire your event handlers to call "
            f"`{api_name}.addCard(...)`, `{api_name}.moveCard(...)`, etc."
        )

    # 4. Every Frontend call to the API must reference a DECLARED method.
    if methods:
        method_calls = re.findall(
            rf"\b{re.escape(api_name)}\.(\w+)\s*\(", script_bodies
        )
        declared = set(methods)
        for called in set(method_calls):
            if called not in declared:
                violations.append(
                    f"Frontend calls undeclared method "
                    f"`{api_name}.{called}(...)`. The Architect's schema "
                    f"declared only: {sorted(declared)}. Either stop "
                    f"calling it, or ask for a schema revision."
                )

    # 5. DOM contract — every required id must appear in the HTML.
    dom = schema.get("dom_contract") or {}
    required_ids: list[str] = dom.get("required_ids") or []
    root_id = dom.get("root_id")
    if root_id and root_id not in required_ids:
        required_ids = [root_id, *required_ids]
    for rid in required_ids:
        # Match id="foo" or id='foo' or id=foo (unquoted)
        pat_id = rf"""id\s*=\s*(?:"{re.escape(rid)}"|'{re.escape(rid)}'|{re.escape(rid)}\b)"""
        if not re.search(pat_id, no_comments):
            violations.append(
                f"Frontend does not contain DOM element with id=\"{rid}\" "
                f"(required by schema.dom_contract)."
            )

    # 6. HTML must start with a doctype (after whitespace).
    if not re.match(r"\s*<!DOCTYPE\s+html", frontend_html, re.IGNORECASE):
        violations.append(
            "Frontend payload does not start with `<!DOCTYPE html>`."
        )

    return violations


# ---------------------------------------------------------------------------
# Mechanical merge
# ---------------------------------------------------------------------------

def mechanical_merge(frontend_html: str, backend_js: str) -> str:
    """Produce a single self-contained HTML file.

    Strategy: take the Frontend HTML as the skeleton and inject the Backend
    JS as a new `<script>` tag right before `</head>`, so `window.kanbanAPI`
    is defined before any Frontend wiring script runs. No semantic rewriting,
    no cleanup — this function is pure string composition.

    If the Frontend has no `</head>`, inject before the first `<script>`
    instead. If there's no `<script>` either, inject before `</body>`.
    """
    # Wrap the backend JS in its own script tag. Use a marker so humans
    # reading the output can see what the integrator inserted.
    backend_block = (
        "<script id=\"backend-injected-by-mechanical-integrator\">\n"
        + backend_js.strip()
        + "\n</script>"
    )

    # 1. Prefer injecting right before </head>.
    head_close = re.search(r"</head\s*>", frontend_html, re.IGNORECASE)
    if head_close:
        idx = head_close.start()
        return frontend_html[:idx] + backend_block + "\n" + frontend_html[idx:]

    # 2. Otherwise inject before the first <script> in the document.
    first_script = re.search(r"<script\b", frontend_html, re.IGNORECASE)
    if first_script:
        idx = first_script.start()
        return frontend_html[:idx] + backend_block + "\n" + frontend_html[idx:]

    # 3. Last resort: inject before </body>.
    body_close = re.search(r"</body\s*>", frontend_html, re.IGNORECASE)
    if body_close:
        idx = body_close.start()
        return frontend_html[:idx] + backend_block + "\n" + frontend_html[idx:]

    # 4. If the frontend has none of those, append.
    return frontend_html + "\n" + backend_block + "\n"


# ---------------------------------------------------------------------------
# The top-level integrator entry point
# ---------------------------------------------------------------------------

def integrate(
    architect_schema: dict[str, Any],
    frontend_html: str,
    backend_js: str,
) -> ContractReport:
    """Run all checks and, if they pass, produce a merged HTML file.

    Returns a ContractReport. On success `report.ok is True` and
    `report.merged_html` is the final file. On failure `report.ok is False`
    and the *_violations fields describe what went wrong.
    """
    report = ContractReport(ok=False)

    # 0. Schema well-formedness (Architect violation)
    report.schema_violations = validate_schema(architect_schema)
    if report.schema_violations:
        return report

    # 1. Backend contract
    report.backend_violations = check_backend(backend_js, architect_schema)

    # 2. Frontend contract
    report.frontend_violations = check_frontend(frontend_html, architect_schema)

    report.stats = {
        "backend_js_chars": len(backend_js),
        "frontend_html_chars": len(frontend_html),
        "declared_methods": list(architect_schema.get("methods", {}).keys()),
        "n_backend_violations": len(report.backend_violations),
        "n_frontend_violations": len(report.frontend_violations),
    }

    if report.backend_violations or report.frontend_violations:
        return report

    # 3. Mechanical merge
    report.merged_html = mechanical_merge(frontend_html, backend_js)
    report.ok = True
    report.stats["merged_html_chars"] = len(report.merged_html)
    return report
