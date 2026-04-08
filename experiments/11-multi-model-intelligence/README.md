# Experiment 011 — Multi-Model Intelligence

## Hypothesis

Intelligence does not require a single large model. Given five small language
model nodes with locked roles and a shared coordination protocol (Anwe),
emergent coordination should be sufficient to produce functional software
that no node could generate alone.

This is the minimum-viable scale test of Primordia's core architectural
thesis: that AGI-class behavior is achievable not by scaling one model,
but by connecting many small models through a coordination fabric.

## What We Built

Five Claude API instances, each with a rigid locked system prompt confining
it to a single cognitive role. Nodes communicate only through structured
Anwe messages:

```json
{
  "sender": "architect",
  "receiver": "all",
  "primitive": "become",
  "payload": "..."
}
```

The four Anwe primitives used here are `observe`, `integrate`, `become`,
and `evade`. No node can see anything outside the messages it receives.
Each node call is stateless — the context is re-assembled every iteration
from the coordination log.

### The Mesh

| Node | Role | Can do | Cannot do |
|------|------|--------|-----------|
| 1. Architect  | System design      | Spec + data model           | Write code |
| 2. Frontend   | UI layer           | HTML/CSS + DOM wiring       | Business logic, persistence |
| 3. Backend    | Logic + state      | JS + `window.kanbanAPI`     | Touch HTML/CSS |
| 4. Integrator | Conflict resolution| Merge FE+BE into one file   | Invent features |
| 5. Critic     | Judgement          | Structured assessment       | Write any code |

The coordination loop runs until the Critic approves or `MAX_ITERATIONS=5`
is reached. When the Critic rejects, its `feedback_for_iteration` field is
injected verbatim into every node's context for the next round.

### The Task

Build a minimal self-contained Kanban board (3 columns, add/move/delete
cards, persist across reload, no external dependencies).

## Results

Two full runs: one with `claude-haiku-4-5` (iteration/dev pass), one with
`claude-sonnet-4-6` (final validation pass).

| Metric                              | haiku-4-5     | sonnet-4-6     |
|-------------------------------------|---------------|----------------|
| Iterations to convergence           | **1 / 5**     | **1 / 5**      |
| Critic approved                     | yes           | yes            |
| Behavioral checks passed (headless) | **8 / 8**     | **8 / 8**      |
| Wall-clock duration                 | 42.4 s        | 118.9 s        |
| Role violations detected            | 1             | 1              |
| Total Anwe messages                 | 5             | 5              |

Behavioral validation: each final `index.html` was loaded in a headless
Chromium (Playwright) and exercised end-to-end — add card, persist across
reload, move card, delete card, verify `window.kanbanAPI` is exposed,
and confirm no JS errors. See `validate.mjs` and `results_*/validation.json`.

### Success criteria (from experiment design)

- [x] 5 nodes produced a working Kanban board with no human code intervention
- [x] Critic approved within 5 iterations (approved on iteration 1, both runs)
- [x] Inter-node messages are coherent and traceable — each downstream node
      demonstrably references prior node output (see `coordination_log.json`:
      Integrator's payload cites both Frontend and Backend identifiers)
- [x] Coordination log shows genuine dependency (see finding 3 below —
      Integrator rewrote Frontend's direct function calls into API calls,
      which is only possible by reading both nodes)

### What we couldn't measure

- **Does quality improve across iterations when the Critic rejects?** —
  The Critic never rejected, so no iteration-over-iteration quality curve
  was produced. The task was apparently inside the single-shot competence
  of both models at this scale.
- **Minimum coordination rounds for convergence?** — Trivially 1 here.
  A harder task or a stricter Critic would be needed to observe the
  convergence dynamics.

## What Happened — The Interesting Part

The headline result (approved on iteration 1, 8/8 behavioral checks) is
not by itself surprising — models of this class can write a Kanban board
in a single prompt. The scientifically interesting observation is in
**how the mesh handled a role violation**.

### Finding 1 — Role bleed happens

In both runs, Node 2 (Frontend) violated its locked role by writing
`localStorage` persistence logic directly, instead of calling through to
the Backend's `window.kanbanAPI`. The haiku run was more egregious: its
Frontend payload contained **zero references to `window.kanbanAPI`** — it
produced a complete standalone implementation as if the Backend did not
exist.

```
haiku   frontend payload: localStorage.setItem=1,  window.kanbanAPI=0
sonnet  frontend payload: localStorage.setItem=1,  window.kanbanAPI=6
```

This is consistent with a known failure mode of role-constrained LLMs:
they tend to produce self-sufficient artifacts rather than stubs that
depend on other components they cannot see.

### Finding 2 — Role bleed gets repaired at the integration layer

This is the genuinely emergent behavior. Look at the Integrator's output:

```
haiku   integrator payload: localStorage.setItem=1,  window.kanbanAPI=8
sonnet  integrator payload: localStorage.setItem=1,  window.kanbanAPI=8
```

Both Integrators produced final files with **8 calls to `window.kanbanAPI`**.
In the haiku case, where the Frontend had produced zero such calls, this
means the Integrator **rewrote the Frontend's direct function calls to
route through the Backend's API**. Concretely, handlers like:

```js
btnEl.addEventListener('click', () => { addCard(column.id, inputEl.value); });
```

became

```js
btnEl.addEventListener('click', () => {
  window.kanbanAPI.addCard(column.id, inputEl.value);
});
```

The Integrator was instructed *not to invent features* — and it did not.
What it did was recognize that two components had produced competing
implementations of the same contract, and resolve the conflict by
preferring the Backend's exposed API and rewiring the Frontend's call
sites to go through it.

**No single node knew the full picture.** The Architect didn't know what
the Frontend would produce. The Frontend didn't know the Backend's API
actually existed. The Backend didn't know the Frontend was going to try
to duplicate its logic. The Integrator read all three, saw the conflict,
and resolved it. The coherence of the final artifact is a property of
the mesh, not of any individual node.

### Finding 3 — The Critic didn't catch the role violation

The Critic approved both runs. It was asked to verify behavioral
correctness, not architectural purity — and the integrated artifact was
behaviorally correct. The fact that the Frontend internally misbehaved
but the Integrator corrected it is invisible to a Critic that only sees
the final file. This is a concrete example of the experiment's stated
concern: *lack of visible reasoning chain*. The coordination log
preserves the full trace, but a reviewer looking only at the artifact
cannot tell that role discipline was violated mid-flow.

### Finding 4 — Haiku and Sonnet produced qualitatively different outputs

Both files are 357 and 443 lines respectively. The Sonnet run produced:

- HTML5 drag-and-drop (17 `drag` keyword hits)
- Per-column card-count badges
- Empty-column hint text
- Boundary disabling of directional buttons
- `moveCardByDirection` helper in addition to `moveCard`

Haiku produced buttons-only movement, no badges, simpler headers. Both
implementations pass the same behavioral checks, but the Sonnet version
has strictly more features the Architect's spec did not require — the
kind of "useful embellishment" that tracks model capability rather than
coordination quality. **Scaling model size adds feature-level richness
within each node's scope; it does not visibly change coordination
quality in this task.**

## What This Means for the Thesis

This is a positive result for Primordia's coordination hypothesis at the
smallest viable scale, with two caveats.

**The positive:** five small, rigidly-scoped model calls — no single one
of which was allowed to build a working Kanban board — produced a working
Kanban board. The final artifact is a real, running, user-interactable
piece of software, not a simulation of one. The output emerged from the
mesh topology, not from any one node's competence.

**Caveat 1 — the task was too easy.** The Critic never had to reject, so
we never got to observe the iterative repair loop in action. The
hypothesized dynamic ("does quality improve when the Critic rejects?")
remains untested. A follow-up experiment should either (a) use smaller
models (Haiku 3.5 or open-weights) to raise the failure rate, or
(b) use a harder task (e.g. "multi-user Kanban with conflict resolution"),
or (c) give the Critic stricter acceptance criteria that force at least
one rejection.

**Caveat 2 — role bleed was real.** The Frontend nodes did not respect
their locked roles. In the haiku run, Frontend effectively attempted to
solve the whole task itself. This is expected behavior for
instruction-tuned LLMs, which are trained toward self-sufficient
artifacts rather than component stubs. The mesh compensated for this
through the Integrator, but this compensation is **implicit and
invisible** to any external observer of the final artifact. Any
real deployment of this architecture will need either stronger role
enforcement (structured tool schemas rather than prose instructions),
or more capable Integrators, or both.

**Caveat 3 — the Critic is a weak point.** A Critic that cannot see the
internal coordination log cannot assess whether role discipline was
maintained. In a real mesh this matters for debugging, for learning,
and for detecting drift. The missing reasoning trace Primordia calls
*Aletheia's silence* appears here in its expected form: the mesh
succeeds, but not in the way the locked prompts implied it should, and
the verification layer cannot see the difference.

## Why This Matters Beyond the Experiment

If this works at five nodes, the question is whether it scales —
not in model size but in mesh size. The commercial implications hold
regardless of this experiment's success:

- Deployable on phones and edge devices
- Private by default — no single node has the whole model
- Continuously learning — each node updates on local experience
- Economically accessible — no $200M training run

Experiment 011 does not prove any of that. It proves the floor:
**at N=5 and small model scale, a coordination mesh does produce
coherent, functional software**, and the emergent repair behavior at
the integration layer is the thing to study next.

## Files

- `nodes.py` — locked system prompts, Anwe protocol (`AnweMessage`,
  primitives, JSON extraction), and the `Node` wrapper class
- `run.py` — the coordination loop
- `validate.mjs` — headless Playwright behavioral validation
- `results/` — canonical final validation run (Sonnet)
- `results_sonnet/` — same data, preserved under model-specific name
- `results_haiku/` — initial iteration/dev run
- Per run directory:
  - `coordination_log.json` — every Anwe message, full payload, in order
  - `critic_log.json` — parsed Critic JSON assessments
  - `summary.json` — summary statistics, role-violations, per-iteration breakdown
  - `validation.json` — headless behavioral check results (8 checks)
  - `output/index.html` — the final integrated Kanban board
  - `output/index_iter<N>.html` — artifact snapshot per iteration

## Reproducing

```bash
cd experiments/11-multi-model-intelligence
export ANTHROPIC_API_KEY=...
pip install anthropic
python3 run.py --model claude-haiku-4-5 --results-dir results_haiku
python3 run.py --model claude-sonnet-4-6 --results-dir results_sonnet
node validate.mjs results_haiku/output/index.html haiku
node validate.mjs results_sonnet/output/index.html sonnet
```

The Kanban artifact is directly openable — no build step:

```bash
xdg-open results/output/index.html
```
