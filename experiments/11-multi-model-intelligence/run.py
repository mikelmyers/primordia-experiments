"""
Experiment 011 — Multi-Model Intelligence
Coordination loop.

Runs the 5-node mesh on the task of building a Kanban board, iterating
until the Critic approves or max iterations is reached.
"""

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
    extract_fenced_code,
)


TASK = """Build a minimal web-based Kanban task board.

Required features:
- At least three columns (Todo, Doing, Done)
- Add a new card to any column with a title
- Move a card between columns (drag-drop or buttons are both acceptable)
- Delete a card
- State persists across page reload (use localStorage)
- A single self-contained index.html file — no external dependencies,
  no build step, no frameworks.

The UI should be clean and usable but nothing fancy."""


MAX_ITERATIONS = 5


def log_message(log: list, msg: AnweMessage, raw: str, iteration: int):
    entry = msg.to_dict()
    entry["iteration"] = iteration
    entry["raw_response_chars"] = len(raw)
    log.append(entry)


def node_input(
    recipient: str,
    task: str,
    iteration: int,
    prior: dict[str, AnweMessage],
    critic_feedback: str | None,
) -> str:
    """Assemble the user message a node sees on invocation.

    Each node only sees the task, its relevant prior messages, and
    (if rejected) the critic's feedback from the previous iteration.
    """
    parts: list[str] = []
    parts.append(f"TASK:\n{task}\n")
    parts.append(f"ITERATION: {iteration} of {MAX_ITERATIONS}")

    if critic_feedback:
        parts.append(
            "PRIOR CRITIC FEEDBACK (this iteration exists because the "
            "Critic rejected the last attempt — you MUST address this):\n"
            f"{critic_feedback}"
        )

    if recipient == "architect":
        pass  # architect speaks first, sees nothing else
    elif recipient == "frontend":
        parts.append(
            "ARCHITECT SPECIFICATION (Anwe message from node 1):\n"
            + json.dumps(prior["architect"].to_dict(), indent=2)
        )
    elif recipient == "backend":
        parts.append(
            "ARCHITECT SPECIFICATION (Anwe message from node 1):\n"
            + json.dumps(prior["architect"].to_dict(), indent=2)
        )
    elif recipient == "integrator":
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
    elif recipient == "critic":
        parts.append(
            "ARCHITECT SPECIFICATION:\n"
            + json.dumps(prior["architect"].to_dict(), indent=2)
        )
        parts.append(
            "\nINTEGRATED ARTIFACT (index.html) from the Integrator:\n"
            + json.dumps(prior["integrator"].to_dict(), indent=2)
        )

    return "\n\n".join(parts)


def parse_critic_payload(payload: str) -> dict:
    """The critic's payload is itself a JSON string. Parse it leniently."""
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        pass
    # Try to find a nested object
    import re

    m = re.search(r"\{.*\}", payload, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    raise ValueError(f"could not parse critic payload: {payload[:300]}")


def write_output_html(html: str, iteration: int, results_dir: str):
    """Write final integrated HTML to results/output/."""
    out_dir = os.path.join(results_dir, "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"index_iter{iteration}.html")
    with open(path, "w") as f:
        f.write(html)
    # Also write as the final index.html
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
    summary_path = os.path.join(results_dir, "summary.json")

    client = build_client()
    nodes = {
        name: Node(name, client, model=model)
        for name in ("architect", "frontend", "backend", "integrator", "critic")
    }

    coord_log: list = []
    critic_log: list = []
    role_violations: list = []
    iteration_summaries: list = []

    critic_feedback: str | None = None
    approved = False
    final_iteration = 0

    t_start = time.time()

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n=== ITERATION {iteration} ===", flush=True)
        prior: dict[str, AnweMessage] = {}
        iter_summary = {"iteration": iteration, "nodes": {}}

        try:
            # --- Node 1: Architect ---
            print("  [1/5] architect...", flush=True)
            user_msg = node_input(
                "architect", TASK, iteration, prior, critic_feedback
            )
            msg, raw = nodes["architect"].invoke(user_msg)
            if msg.sender != "architect":
                role_violations.append(
                    f"iter {iteration}: architect self-labeled as {msg.sender!r}"
                )
            prior["architect"] = msg
            log_message(coord_log, msg, raw, iteration)
            iter_summary["nodes"]["architect"] = {
                "primitive": msg.primitive,
                "payload_chars": len(msg.payload),
            }

            # --- Node 2: Frontend ---
            print("  [2/5] frontend...", flush=True)
            user_msg = node_input(
                "frontend", TASK, iteration, prior, critic_feedback
            )
            msg, raw = nodes["frontend"].invoke(user_msg)
            if msg.sender != "frontend":
                role_violations.append(
                    f"iter {iteration}: frontend self-labeled as {msg.sender!r}"
                )
            prior["frontend"] = msg
            log_message(coord_log, msg, raw, iteration)
            iter_summary["nodes"]["frontend"] = {
                "primitive": msg.primitive,
                "payload_chars": len(msg.payload),
            }

            # --- Node 3: Backend ---
            print("  [3/5] backend...", flush=True)
            user_msg = node_input(
                "backend", TASK, iteration, prior, critic_feedback
            )
            msg, raw = nodes["backend"].invoke(user_msg)
            if msg.sender != "backend":
                role_violations.append(
                    f"iter {iteration}: backend self-labeled as {msg.sender!r}"
                )
            prior["backend"] = msg
            log_message(coord_log, msg, raw, iteration)
            iter_summary["nodes"]["backend"] = {
                "primitive": msg.primitive,
                "payload_chars": len(msg.payload),
            }

            # --- Role-bleed check: does frontend code contain business logic,
            # does backend code contain HTML? ---
            fe_code = extract_fenced_code(prior["frontend"].payload, "html")
            be_code = extract_fenced_code(
                prior["backend"].payload, "javascript"
            )
            if "<!DOCTYPE" in be_code or "<html" in be_code.lower():
                role_violations.append(
                    f"iter {iteration}: backend wrote HTML boilerplate"
                )
            if "localStorage.setItem" in fe_code:
                role_violations.append(
                    f"iter {iteration}: frontend wrote persistence logic"
                )

            # --- Node 4: Integrator ---
            print("  [4/5] integrator...", flush=True)
            user_msg = node_input(
                "integrator", TASK, iteration, prior, critic_feedback
            )
            # Integrator may need more tokens since it outputs the full file
            nodes["integrator"].max_tokens = 8192
            msg, raw = nodes["integrator"].invoke(user_msg)
            if msg.sender != "integrator":
                role_violations.append(
                    f"iter {iteration}: integrator self-labeled as {msg.sender!r}"
                )
            prior["integrator"] = msg
            log_message(coord_log, msg, raw, iteration)
            integrated_html = extract_fenced_code(msg.payload, "html")
            out_path = write_output_html(integrated_html, iteration, results_dir)
            iter_summary["nodes"]["integrator"] = {
                "primitive": msg.primitive,
                "payload_chars": len(msg.payload),
                "html_chars": len(integrated_html),
                "html_path": out_path,
            }

            # --- Node 5: Critic ---
            print("  [5/5] critic...", flush=True)
            user_msg = node_input(
                "critic", TASK, iteration, prior, critic_feedback
            )
            msg, raw = nodes["critic"].invoke(user_msg)
            if msg.sender != "critic":
                role_violations.append(
                    f"iter {iteration}: critic self-labeled as {msg.sender!r}"
                )
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
                break

            # Not approved: feed feedback into next iteration
            critic_feedback = critic_obj.get(
                "feedback_for_iteration"
            ) or json.dumps(critic_obj.get("failing", []) or [])
            final_iteration = iteration

        except Exception as e:
            tb = traceback.format_exc()
            print(f"  ERROR in iteration {iteration}: {e}", flush=True)
            print(tb, flush=True)
            iter_summary["error"] = str(e)
            iter_summary["traceback"] = tb
            iteration_summaries.append(iter_summary)
            # Persist partial state and bail
            break

    t_end = time.time()

    # Persist all logs
    with open(coord_log_path, "w") as f:
        json.dump(coord_log, f, indent=2)
    with open(critic_log_path, "w") as f:
        json.dump(critic_log, f, indent=2)

    summary = {
        "experiment": "011-multi-model-intelligence",
        "model": model,
        "task": TASK,
        "max_iterations": MAX_ITERATIONS,
        "iterations_run": final_iteration,
        "approved": approved,
        "role_violations": role_violations,
        "per_iteration": iteration_summaries,
        "duration_seconds": round(t_end - t_start, 2),
        "total_messages": len(coord_log),
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary


def print_summary(summary: dict):
    print("\n" + "=" * 60)
    print("EXPERIMENT 011 — SUMMARY")
    print("=" * 60)
    print(f"model:           {summary['model']}")
    print(f"approved:        {summary['approved']}")
    print(f"iterations run:  {summary['iterations_run']}/{summary['max_iterations']}")
    print(f"messages logged: {summary['total_messages']}")
    print(f"role violations: {len(summary['role_violations'])}")
    for rv in summary["role_violations"]:
        print(f"  - {rv}")
    print(f"duration:        {summary['duration_seconds']}s")
    print("per-iteration critic verdicts:")
    for it in summary["per_iteration"]:
        cn = it["nodes"].get("critic", {})
        print(
            f"  iter {it['iteration']}: "
            f"approved={cn.get('approved')} "
            f"n_failing={cn.get('n_failing')}"
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-haiku-4-5")
    ap.add_argument("--results-dir", default=None)
    args = ap.parse_args()
    s = run_experiment(model=args.model, results_dir=args.results_dir)
    print_summary(s)
