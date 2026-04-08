# Experiment 012 — Deterministic Integrator

## Hypothesis

Replace Experiment 011's LLM Integrator (Node 4) with a **deterministic
mechanical integrator** enforcing a strict interface contract. Test whether
the mesh still produces equivalent or better output with the Integrator
node removed entirely.

This is designed to test the core architectural question Experiment 011
surfaced but could not answer:

> Is the intelligence in the nodes, or in the protocol?

- **If output quality holds** — the protocol carries the intelligence,
  nodes can be tiny, the on-device thesis survives.
- **If output quality collapses** — the nodes need the LLM Integrator,
  which means the mesh needs a cognitive hierarchy, not a flat
  architecture.

## Why Experiment 011 could not answer this

Experiment 011's headline finding was "Finding 2 — Role bleed gets
repaired at the integration layer": Haiku's Frontend produced **zero**
calls to `window.kanbanAPI`, writing a complete standalone implementation
as if the Backend did not exist. The LLM Integrator silently **rewrote**
Frontend's direct function calls to route through the Backend's API.

That rewriting is the "emergent coordination" finding — but it's also
the most generous possible reading of the mesh, because it depends on
a cognitively strong Integrator doing semantic surgery. Experiment 011
called this out directly:

> **Caveat 2 — role bleed was real.** The Frontend nodes did not
> respect their locked roles. (...) The mesh compensated for this
> through the Integrator, but this compensation is implicit and
> invisible to any external observer of the final artifact.

The question Experiment 012 asks: **what if the Integrator can't repair
anything?** If the protocol is strong enough, upstream nodes should
converge under iterative feedback to meet the contract directly. If the
protocol is weak, removing the repair node should collapse the mesh.

## What we built

The mesh is reduced from 5 LLM nodes to 4, plus a Python function:

| Node | Role | Kind | Change from Exp 011 |
|------|------|------|---------------------|
| 1. Architect  | System design + **machine-readable schema** | LLM | Now emits a ```json schema block |
| 2. Frontend   | UI layer                | LLM | Hard-banned from `localStorage.*`, shadowing API methods |
| 3. Backend    | Logic + state           | LLM | Must expose every declared schema method |
| 4. Integrator | **Contract enforcement + mechanical merge** | **Python** | No LLM |
| 5. Critic     | Judgement               | LLM | Unchanged role; now sees mechanically-merged files |

### The contract

The Architect emits a JSON schema inside its payload:

```json
{
  "api_name": "window.kanbanAPI",
  "methods": {
    "addCard":    {"args": ["columnId", "title"], "returns": "boolean"},
    "moveCard":   {"args": ["fromColumnId", "toColumnId", "cardId"], "returns": "boolean"},
    "deleteCard": {"args": ["columnId", "cardId"], "returns": "boolean"},
    "getBoard":   {"args": [], "returns": "object"},
    "subscribe":  {"args": ["callback"], "returns": "void"}
  },
  "dom_contract": {
    "root_id": "boardContainer",
    "required_ids": ["boardContainer"]
  },
  "forbidden_in_frontend": [
    "localStorage.setItem",
    "localStorage.getItem",
    "localStorage.removeItem"
  ]
}
```

### What the mechanical integrator does

`integrator.py` is a pure Python function (no LLM) that:

1. **Validates the schema** — rejects the Architect if it didn't emit a
   well-formed JSON block.
2. **Checks the Backend** (regex-based):
   - `window.kanbanAPI` is assigned
   - every declared method is defined on the API (direct assignment,
     object literal key, ES6 shorthand, or `Object.assign`)
   - `localStorage` is referenced (persistence must live in Backend)
   - no HTML boilerplate leaked in
3. **Checks the Frontend** (regex-based):
   - every `forbidden_in_frontend` pattern is absent
   - no top-level declarations shadowing API method names
     (`function addCard(...)`, `const addCard = ...`)
   - at least one `window.kanbanAPI.<method>(...)` call exists
   - every called method is one the Architect declared
   - every `required_ids` element appears in the HTML
   - payload starts with `<!DOCTYPE html>`
4. **If any check fails**, returns a structured `ContractReport` enumerating
   the violations in concrete terms. The run loop feeds this verbatim back
   into the next iteration of Architect/Frontend/Backend. The Critic is
   **not run** on a rejected integration.
5. **If all checks pass**, performs a pure string-composition merge:
   injects the Backend JS as a `<script>` tag right before `</head>` in
   the Frontend HTML (so `window.kanbanAPI` exists before Frontend wiring
   runs). No semantic rewriting. No repair.

### The iteration loop

```
Architect ──► Frontend ─┐
     │                  ├──► MECHANICAL INTEGRATOR ──► Critic
     └─► Backend ───────┘          (pure Python)
```

On rejection at the mechanical stage, the violation report becomes the
`feedback_for_iteration` for the next pass. Both the integrator and the
Critic must approve for the mesh to converge.

## Retrospective result (no API calls required)

Before running the full experiment, we ran the deterministic integrator
against the **cached Experiment 011 payloads** using a schema synthesized
from Exp 011's Architect prose. See `retrospective.py` and
`retrospective.json`.

| Run   | Integrator satisfied? | Backend violations | Frontend violations |
|-------|-----------------------|--------------------|---------------------|
| haiku | no                    | 0                  | **5**               |
| sonnet| no                    | 1                  | **3**               |

Both cached Exp 011 runs **would have been rejected on iteration 1** by
the mechanical integrator:

- **Haiku Frontend:** used `localStorage.setItem`/`localStorage.getItem`,
  declared top-level `function addCard` and `function deleteCard`
  (shadowing the Backend API), and made **zero** calls to
  `window.kanbanAPI.*`. All five violations match Finding 1 of Exp 011
  (Frontend produced a standalone implementation), but where Exp 011's
  LLM Integrator quietly repaired them, the mechanical integrator refuses
  to touch them.
- **Sonnet Frontend:** used `localStorage.setItem`/`localStorage.getItem`
  and did not include a `boardContainer` div. Sonnet's Backend also
  drifted from the canonical naming by exposing `getState` instead of
  `getBoard` — a schema mismatch that surfaces as a Backend violation.
  This is the class of drift a mechanical contract catches that a
  forgiving LLM Integrator silently absorbs.

**This is a concrete pre-result:** Exp 011's "emergent repair at the
integration layer" was doing more work than its README admitted. Without
the repair, neither Haiku nor Sonnet converged in a single shot. Whether
they converge **in multiple shots** under feedback from the mechanical
integrator is the question the API run is designed to answer.

## Reproducing

### The retrospective (no API access required)

```bash
cd experiments/12-deterministic-integrator
python3 retrospective.py
```

Writes `retrospective.json`, prints the rejection report above.

### The full experiment (requires ANTHROPIC_API_KEY)

```bash
cd experiments/12-deterministic-integrator
export ANTHROPIC_API_KEY=...
pip install anthropic

python3 run.py --model claude-haiku-4-5  --results-dir results_haiku
python3 run.py --model claude-sonnet-4-6 --results-dir results_sonnet

node validate.mjs results_haiku/output/index.html  haiku
node validate.mjs results_sonnet/output/index.html sonnet
```

Per-run outputs mirror Experiment 011's layout:

- `coordination_log.json` — every message, including synthetic entries
  for the deterministic integrator (flagged with `"deterministic": true`)
- `integrator_log.json` — per-iteration contract report from the
  mechanical integrator
- `critic_log.json` — parsed Critic verdicts (only entries for iterations
  that reached the Critic)
- `summary.json` — run summary with `integrator_rejection_count`,
  `integrator_acceptance_count`, and `final_reject_reason`
- `output/index_iter<N>.html` — mechanically merged artifact per
  iteration that reached the merge stage
- `output/index.html` — the final merged artifact

## What to look for in the results

| Outcome pattern | Interpretation |
|---|---|
| Converges in 1–2 iterations, 8/8 behavioral checks pass | Protocol carries the intelligence. The LLM Integrator in Exp 011 was doing unnecessary repair. On-device thesis survives, and tightening the contract is enough. |
| Converges in 3–5 iterations, 8/8 behavioral checks pass | Mesh works but pays a latency tax for strictness. Nodes + protocol share the cognitive load. On-device thesis viable with higher round-trip counts. |
| Integrator never accepts (5/5 iterations rejected) | The LLM Integrator was doing essential semantic work that cannot be reduced to a regex contract. Flat mesh architecture does not hold; a cognitive hierarchy is required. |
| Integrator accepts but Critic rejects | Contract is strict but insufficient — behavioral correctness does not follow from schema compliance. The schema needs more coverage (e.g. event wiring, render order). |
| Haiku fails but Sonnet converges | The contract exists but requires a minimum node capability to satisfy. Interesting empirical data on the model-size floor for mesh participation. |

## Files

- `nodes.py` — locked system prompts (tightened vs Exp 011), Anwe
  protocol, `extract_architect_schema`, `Node` wrapper
- `integrator.py` — the deterministic mechanical integrator
- `run.py` — the coordination loop (Architect → Frontend → Backend →
  MECHANICAL INTEGRATOR → Critic)
- `retrospective.py` — runs the integrator against cached Exp 011 payloads
- `retrospective.json` — result of the retrospective run
- `validate.mjs` — headless Playwright behavioral validator (unchanged
  from Exp 011)

## Relationship to Experiment 011

This experiment **does not invalidate** Exp 011. Exp 011 established the
floor: five locked-role LLM nodes can produce working software. Exp 012
asks whether one of those nodes — the Integrator, which turned out to
be doing the most cognitive work — is **architecturally necessary** or
can be replaced by a protocol. The two experiments should be read together.
