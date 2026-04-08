"""
Experiment 012 — Deterministic Integrator
Coordination loop.

Architecture:

  Architect ──► Frontend ─┐
       │                  ├──► MECHANICAL INTEGRATOR ──► Critic
       └─► Backend ───────┘          (pure Python)

The only difference from Experiment 011's run loop is that Node 4 is a
Python function (`integrator.integrate`) rather than an LLM call. All four
LLM nodes are unchanged in their envelope shape; only the prompts were
tightened (see `nodes.py`).

Iteration semantics:

  1. On each iteration we run architect → frontend → backend.
  2. We invoke the deterministic integrator on the Architect's schema,
     Frontend HTML, and Backend JS.
  3. If the integrator rejects:
       - We DO NOT run the Critic this iteration (the merged file
         doesn't exist).
       - The integrator's violation report becomes the feedback string
         for the next iteration, injected verbatim into Frontend and
         Backend and Architect.
       - We continue to the next iteration (if any).
  4. If the integrator accepts:
       - We write the merged HTML to disk.
       - We run the Critic on the merged file.
       - If the Critic approves, we stop. If not, its
         `feedback_for_iteration` becomes the next iteration's feedback.

The mesh converges when (a) the integrator accepts AND (b) the Critic
approves. Both gates must close.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from nodes import (  # noqa: E402
    AnweMessage,
    Node,
    build_client,
    extract_architect_schema,
    extract_fenced_code,
)
from integrator import integrate, ContractReport  # noqa: E402


TASK = """Build a minimal web-based Kanban task board.

Required features:
- At least three columns (Todo, Doing, Done)
- Add a new card to any column with a title
- Move a card between columns (drag-drop or buttons are both acceptable)
- Delete a card
- State persists across page reload (use localStorage)
- A single self-contained index.html file — no external dependencies,
  no build step, no frameworks."""


MAX_ITERATIONS = 5


def log_message(log: list, msg: AnweMessage, raw: str, iteration: int):
    entry = msg.to_dict()
    entry["iteration"] = iteration
    entry["raw_response_chars"] = len(raw)
    log.append(entry)


def log_integrator_report(
    log: list, report: ContractReport, iteration: int
) -> None:
    """The deterministic integrator does not produce an Anwe message from
    an LLM, but we log its output as if it were one — using primitive
    `integrate` on success and `evade` on rejection — so the coordination
    log remains a single linear record of what happened."""
    synthetic_payload = json.dumps(
        {
            "ok": report.ok,
            "backend_violations": report.backend_violations,
            "frontend_violations": report.frontend_violations,
            "schema_violations": report.schema_violations,
            "stats": report.stats,
        },
        indent=2,
    )
    log.append(
        {
            "sender": "integrator",
            "receiver": "critic" if report.ok else "all",
            "primitive": "integrate" if report.ok else "evade",
            "payload": synthetic_payload,
            "iteration": iteration,
            "timestamp": time.time(),
            "deterministic": True,
        }
    )


def node_input(
    recipient: str,
    task: str,
    iteration: int,
    prior: dict[str, AnweMessage],
    feedback: str | None,
) -> str:
    """Assemble the user message a node sees on invocation.

    `feedback` may be either a Critic feedback string OR a mechanical
    integrator violation report — the run loop passes whichever is most
    recent.
    """
    parts: list[str] = []
    parts.append(f"TASK:\n{task}\n")
    parts.append(f"ITERATION: {iteration} of {MAX_ITERATIONS}")

    if feedback:
        parts.append(
            "PRIOR FEEDBACK (this iteration exists because the previous "
            "attempt was rejected — you MUST address this literally):\n"
            f"{feedback}"
        )

    if recipient == "architect":
        pass  # architect speaks first
    elif recipient in ("frontend", "backend"):
        parts.append(
            "ARCHITECT SPECIFICATION (Anwe message from node 1):\n"
            + json.dumps(prior["architect"].to_dict(), indent=2)
        )
    elif recipient == "critic":
        parts.append(
            "ARCHITECT SPECIFICATION:\n"
            + json.dumps(prior["architect"].to_dict(), indent=2)
        )
        parts.append(
            "\nFRONTEND OUTPUT:\n"
            + json.dumps(prior["frontend"].to_dict(), indent=2)
        )
        parts.append(
            "\nBACKEND OUTPUT:\n"
            + json.dumps(prior["backend"].to_dict(), indent=2)
        )
        parts.append(
            "\nINTEGRATED ARTIFACT (index.html, produced by the "
            "DETERMINISTIC integrator — not an LLM):\n"
            + prior["integrated_html"].payload
        )

    return "\n\n".join(parts)


def parse_critic_payload(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        pass
    import re
    m = re.search(r"\{.*\}", payload, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    raise ValueError(f"could not parse critic payload: {payload[:300]}")


def write_output_html(html: str, iteration: int, results_dir: str) -> str:
    out_dir = os.path.join(results_dir, "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"index_iter{iteration}.html")
    with open(path, "w") as f:
        f.write(html)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(html)
    return path


def run_experiment(
    model: str = "claude-haiku-4-5",
    results_dir: str | None = None,
) -> dict:
    if results_dir is None:
        results_dir = os.path.join(HERE, "results")
    os.makedirs(results_dir, exist_ok=True)

    coord_log_path = os.path.join(results_dir, "coordination_log.json")
    critic_log_path = os.path.join(results_dir, "critic_log.json")
    integrator_log_path = os.path.join(results_dir, "integrator_log.json")
    summary_path = os.path.join(results_dir, "summary.json")

    client = build_client()
    nodes = {
        name: Node(name, client, model=model)
        for name in ("architect", "frontend", "backend", "critic")
    }

    coord_log: list = []
    critic_log: list = []
    integrator_log: list = []
    iteration_summaries: list = []

    feedback: str | None = None
    approved = False
    final_iteration = 0
    reject_reason: str | None = None  # "integrator" | "critic" | None

    t_start = time.time()

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n=== ITERATION {iteration} ===", flush=True)
        prior: dict[str, AnweMessage] = {}
        iter_summary: dict = {"iteration": iteration, "nodes": {}}

        try:
            # --- Node 1: Architect ---
            print("  [1/4] architect...", flush=True)
            user_msg = node_input(
                "architect", TASK, iteration, prior, feedback
            )
            msg, raw = nodes["architect"].invoke(user_msg)
            prior["architect"] = msg
            log_message(coord_log, msg, raw, iteration)
            iter_summary["nodes"]["architect"] = {
                "primitive": msg.primitive,
                "payload_chars": len(msg.payload),
            }

            # Extract the machine-readable schema early so we can detect
            # Architect schema violations before wasting frontend/backend calls.
            try:
                schema = extract_architect_schema(msg.payload)
            except ValueError as e:
                iter_summary["error"] = f"schema extraction failed: {e}"
                iteration_summaries.append(iter_summary)
                feedback = (
                    "MECHANICAL INTEGRATOR REJECTED THE ARCHITECT PAYLOAD. "
                    f"Reason: {e} Emit a single ```json fenced block inside "
                    "your payload containing the machine-readable schema "
                    "described in your system prompt."
                )
                reject_reason = "integrator"
                final_iteration = iteration
                continue

            # --- Node 2: Frontend ---
            print("  [2/4] frontend...", flush=True)
            user_msg = node_input(
                "frontend", TASK, iteration, prior, feedback
            )
            msg, raw = nodes["frontend"].invoke(user_msg)
            prior["frontend"] = msg
            log_message(coord_log, msg, raw, iteration)
            iter_summary["nodes"]["frontend"] = {
                "primitive": msg.primitive,
                "payload_chars": len(msg.payload),
            }

            # --- Node 3: Backend ---
            print("  [3/4] backend...", flush=True)
            user_msg = node_input(
                "backend", TASK, iteration, prior, feedback
            )
            msg, raw = nodes["backend"].invoke(user_msg)
            prior["backend"] = msg
            log_message(coord_log, msg, raw, iteration)
            iter_summary["nodes"]["backend"] = {
                "primitive": msg.primitive,
                "payload_chars": len(msg.payload),
            }

            # --- Node 4: DETERMINISTIC INTEGRATOR ---
            print("  [4/4] mechanical integrator...", flush=True)
            fe_html = extract_fenced_code(prior["frontend"].payload, "html")
            be_js = extract_fenced_code(prior["backend"].payload, "javascript")
            report = integrate(schema, fe_html, be_js)
            log_integrator_report(coord_log, report, iteration)
            integrator_log.append(
                {
                    "iteration": iteration,
                    "ok": report.ok,
                    "backend_violations": report.backend_violations,
                    "frontend_violations": report.frontend_violations,
                    "schema_violations": report.schema_violations,
                    "stats": report.stats,
                }
            )
            iter_summary["nodes"]["integrator"] = {
                "ok": report.ok,
                "n_backend_violations": len(report.backend_violations),
                "n_frontend_violations": len(report.frontend_violations),
            }

            if not report.ok:
                print(
                    f"    integrator REJECTED: "
                    f"{len(report.backend_violations)} backend, "
                    f"{len(report.frontend_violations)} frontend "
                    "violations",
                    flush=True,
                )
                feedback = report.as_feedback()
                reject_reason = "integrator"
                iteration_summaries.append(iter_summary)
                final_iteration = iteration
                continue  # loop back without running the Critic

            print("    integrator accepted — merging", flush=True)
            out_path = write_output_html(
                report.merged_html, iteration, results_dir
            )
            iter_summary["nodes"]["integrator"]["html_path"] = out_path
            iter_summary["nodes"]["integrator"]["html_chars"] = len(
                report.merged_html
            )

            # Synthesize an Anwe-message-shaped object holding the merged
            # HTML so the Critic's node_input can reference it uniformly.
            prior["integrated_html"] = AnweMessage(
                sender="integrator",
                receiver="critic",
                primitive="integrate",
                payload=report.merged_html,
            )

            # --- Node 5 (now 4): Critic ---
            print("  [5/4] critic...", flush=True)
            user_msg = node_input(
                "critic", TASK, iteration, prior, feedback
            )
            msg, raw = nodes["critic"].invoke(user_msg)
            prior["critic"] = msg
            log_message(coord_log, msg, raw, iteration)

            critic_obj = parse_critic_payload(msg.payload)
            critic_obj["iteration"] = iteration
            critic_obj["primitive"] = msg.primitive
            critic_log.append(critic_obj)
            iter_summary["nodes"]["critic"] = {
                "primitive": msg.primitive,
                "approved": bool(critic_obj.get("approved", False)),
                "n_failing": len(critic_obj.get("failing", []) or []),
            }
            iteration_summaries.append(iter_summary)

            print(
                f"    critic approved={critic_obj.get('approved')} "
                f"n_failing={len(critic_obj.get('failing', []) or [])}",
                flush=True,
            )

            if critic_obj.get("approved"):
                approved = True
                final_iteration = iteration
                reject_reason = None
                break

            feedback = critic_obj.get(
                "feedback_for_iteration"
            ) or json.dumps(critic_obj.get("failing", []) or [])
            reject_reason = "critic"
            final_iteration = iteration

        except Exception as e:
            tb = traceback.format_exc()
            print(f"  ERROR in iteration {iteration}: {e}", flush=True)
            print(tb, flush=True)
            iter_summary["error"] = str(e)
            iter_summary["traceback"] = tb
            iteration_summaries.append(iter_summary)
            break

    t_end = time.time()

    with open(coord_log_path, "w") as f:
        json.dump(coord_log, f, indent=2)
    with open(critic_log_path, "w") as f:
        json.dump(critic_log, f, indent=2)
    with open(integrator_log_path, "w") as f:
        json.dump(integrator_log, f, indent=2)

    summary = {
        "experiment": "012-deterministic-integrator",
        "model": model,
        "task": TASK,
        "max_iterations": MAX_ITERATIONS,
        "iterations_run": final_iteration,
        "approved": approved,
        "final_reject_reason": reject_reason,
        "integrator_rejection_count": sum(
            1 for e in integrator_log if not e["ok"]
        ),
        "integrator_acceptance_count": sum(
            1 for e in integrator_log if e["ok"]
        ),
        "per_iteration": iteration_summaries,
        "duration_seconds": round(t_end - t_start, 2),
        "total_messages": len(coord_log),
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary


def print_summary(summary: dict):
    print("\n" + "=" * 60)
    print("EXPERIMENT 012 — SUMMARY")
    print("=" * 60)
    print(f"model:                {summary['model']}")
    print(f"approved:             {summary['approved']}")
    print(
        f"iterations run:       "
        f"{summary['iterations_run']}/{summary['max_iterations']}"
    )
    print(f"messages logged:      {summary['total_messages']}")
    print(
        f"integrator accepts:   {summary['integrator_acceptance_count']}"
    )
    print(
        f"integrator rejects:   {summary['integrator_rejection_count']}"
    )
    print(f"final reject reason:  {summary['final_reject_reason']}")
    print(f"duration:             {summary['duration_seconds']}s")
    print("per-iteration:")
    for it in summary["per_iteration"]:
        nodes = it["nodes"]
        integ = nodes.get("integrator", {})
        critic = nodes.get("critic", {})
        print(
            f"  iter {it['iteration']}: "
            f"integrator_ok={integ.get('ok')} "
            f"critic_approved={critic.get('approved')}"
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-haiku-4-5")
    ap.add_argument("--results-dir", default=None)
    args = ap.parse_args()
    s = run_experiment(model=args.model, results_dir=args.results_dir)
    print_summary(s)
