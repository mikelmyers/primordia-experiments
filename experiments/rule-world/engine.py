"""Forward chaining reasoning engine for Rule World.

Zero matrix multiplication. Zero pre-baked scenario answers. Pure derivation.

A rule is a structured tuple:
    Rule(id, antecedents, forbidden, derives,
         requires_in_result, forbids_in_result,
         priority, urgency, action_hint)

- antecedents: predicates that must ALL be present for the rule to fire
- forbidden:   predicates whose presence BLOCKS the rule
- derives:     predicates added to the fact set when the rule fires (forward chain)
- requires_in_result: obligation predicates that must be true in the post-action state
- forbids_in_result:  constraint predicates that must NOT be true in the post-action state
- priority: 1-10 (higher = stronger)
- urgency:  low/medium/high/visceral (resistance to override)

An action is:
    Action(name, preconditions, forbidden_pre, add, remove)

The engine takes (facts, goal_predicates, rules, actions) and:
  1. Forward-chains derivations to fixed point.
  2. Identifies which rules are active (antecedents satisfied, forbidden absent).
  3. Simulates every action, re-chains, and scores results against active rules'
     obligations and constraints.
  4. Disqualifies actions that violate VISCERAL constraints unless none survive.
  5. Picks the highest-scoring action whose post-state satisfies the goal.
  6. Detects gaps: any unfulfilled obligation in the chosen result is a gap, and
     the engine logs WHICH obligations remain unmet — composition is reported,
     not authored.
"""

from __future__ import annotations

from dataclasses import dataclass, field


URGENCY = {"low": 1, "medium": 2, "high": 3, "visceral": 4}


@dataclass
class Rule:
    id: str
    antecedents: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    derives: list[str] = field(default_factory=list)
    requires_in_result: list[str] = field(default_factory=list)
    forbids_in_result: list[str] = field(default_factory=list)
    priority: int = 5
    urgency: str = "medium"
    statement: str = ""


@dataclass
class Action:
    name: str
    preconditions: list[str] = field(default_factory=list)
    forbidden_pre: list[str] = field(default_factory=list)
    add: list[str] = field(default_factory=list)
    remove: list[str] = field(default_factory=list)


# ---------- forward chaining ----------

def forward_chain(facts: set[str], rules: list[Rule]) -> tuple[set[str], list[str]]:
    """Apply derives-rules until fixed point. Returns (state, trace)."""
    state = set(facts)
    trace: list[str] = []
    changed = True
    while changed:
        changed = False
        for r in rules:
            if not r.derives:
                continue
            if not all(a in state for a in r.antecedents):
                continue
            if any(f in state for f in r.forbidden):
                continue
            new = [d for d in r.derives if d not in state]
            if new:
                state.update(new)
                trace.append(f"{r.id}: {r.antecedents} ⇒ derives {new}")
                changed = True
    return state, trace


def active_obligations_and_constraints(
    state: set[str], rules: list[Rule]
) -> list[Rule]:
    """Rules whose antecedents fire and that carry obligations or constraints."""
    out = []
    for r in rules:
        if not (r.requires_in_result or r.forbids_in_result):
            continue
        if not all(a in state for a in r.antecedents):
            continue
        if any(f in state for f in r.forbidden):
            continue
        out.append(r)
    return out


# ---------- action simulation ----------

def _derived_predicates(rules: list[Rule]) -> set[str]:
    out: set[str] = set()
    for r in rules:
        out.update(r.derives)
    return out


def simulate_action(
    state: set[str], action: Action, rules: list[Rule]
) -> tuple[set[str] | None, list[str]]:
    if not all(p in state for p in action.preconditions):
        return None, []
    if any(f in state for f in action.forbidden_pre):
        return None, []
    # Apply the action.
    new_state = (state - set(action.remove)) | set(action.add)
    # Forward chaining is monotonic, so a derivation whose antecedents the
    # action just invalidated would otherwise persist. Strip every predicate
    # that any rule *can* derive, then re-chain from the remaining "primitive"
    # facts. This is the closest a pure forward chainer gets to retraction
    # without taking on full non-monotonic machinery.
    derivable = _derived_predicates(rules)
    primitives = new_state - derivable
    chained, trace = forward_chain(primitives, rules)
    return chained, trace


def evaluate_action(
    initial_state: set[str],
    action: Action,
    rules: list[Rule],
    goal_predicates: list[str],
) -> dict | None:
    result, chain_trace = simulate_action(initial_state, action, rules)
    if result is None:
        return None

    # Obligations and constraints triggered by EITHER the initial situation
    # OR by the result state. We use union so that an action that creates a
    # cold-being-in-hall is then judged against R4.
    triggered = {r.id: r for r in active_obligations_and_constraints(initial_state, rules)}
    for r in active_obligations_and_constraints(result, rules):
        triggered.setdefault(r.id, r)

    fulfilled: list[tuple[Rule, str]] = []
    violated: list[tuple[Rule, str]] = []

    for r in triggered.values():
        for req in r.requires_in_result:
            if req in result:
                fulfilled.append((r, f"requires {req}"))
            else:
                violated.append((r, f"requires {req} (absent)"))
        for forb in r.forbids_in_result:
            if forb in result:
                violated.append((r, f"forbids {forb} (present)"))
            else:
                fulfilled.append((r, f"forbids {forb}"))

    visceral_violations = [(r, v) for r, v in violated if r.urgency == "visceral"]
    goal_met = all(g in result for g in goal_predicates) if goal_predicates else True

    score = 0
    for r, _ in fulfilled:
        score += r.priority * URGENCY[r.urgency]
    for r, _ in violated:
        score -= r.priority * URGENCY[r.urgency]
    if goal_met:
        score += 25

    return {
        "action": action.name,
        "result_state": sorted(result),
        "chain_trace": chain_trace,
        "triggered_rule_ids": sorted(triggered.keys()),
        "fulfilled": [(r.id, x) for r, x in fulfilled],
        "violated": [(r.id, x) for r, x in violated],
        "visceral_violations": [(r.id, x) for r, x in visceral_violations],
        "goal_met": goal_met,
        "score": score,
    }


# ---------- top-level reasoning ----------

def _score_state(
    state: set[str],
    rules: list[Rule],
    initial_state: set[str],
    goal_predicates: list[str],
) -> tuple[int, list[tuple[str, str]], list[tuple[str, str]]]:
    """Score a state against the obligations active in either initial or
    result state. Returns (score, violations, visceral_violations).
    """
    triggered = {r.id: r for r in active_obligations_and_constraints(initial_state, rules)}
    for r in active_obligations_and_constraints(state, rules):
        triggered.setdefault(r.id, r)

    score = 0
    violations: list[tuple[str, str]] = []
    visceral: list[tuple[str, str]] = []
    for r in triggered.values():
        for req in r.requires_in_result:
            if req in state:
                score += r.priority * URGENCY[r.urgency]
            else:
                score -= r.priority * URGENCY[r.urgency]
                violations.append((r.id, f"requires {req}"))
                if r.urgency == "visceral":
                    visceral.append((r.id, req))
        for forb in r.forbids_in_result:
            if forb in state:
                score -= r.priority * URGENCY[r.urgency]
                violations.append((r.id, f"forbids {forb}"))
                if r.urgency == "visceral":
                    visceral.append((r.id, forb))
            else:
                score += r.priority * URGENCY[r.urgency]

    if goal_predicates and all(g in state for g in goal_predicates):
        score += 25
    return score, violations, visceral


def plan_sequence(
    facts: list[str],
    goal_predicates: list[str],
    rules: list[Rule],
    actions: list[Action],
    max_depth: int = 3,
) -> dict:
    """Forward STRIPS-style planner over action sequences up to `max_depth`.

    Each node in the search tree is a state. Each edge is an action whose
    preconditions are satisfied in the parent state. Edges that lead through
    a state with any visceral-rule violation are pruned. The planner returns
    the sequence (possibly length 0) whose terminal state maximizes the
    score function used by single-action `reason`.

    Branching factor = |actions|. Depth bounded by `max_depth`. For the toy
    rule-world (≤15 actions, depth 3), the worst-case search tree is ~3000
    nodes, well under a millisecond on commodity CPU.
    """
    initial_state, init_chain = forward_chain(set(facts), rules)

    best: dict = {
        "sequence": [],
        "terminal_state": sorted(initial_state),
        "score": -10**9,
        "violations": [],
        "trace": [],
    }

    nodes_explored = 0

    def search(state: set[str], history: list[str], trace: list[str], depth: int) -> None:
        nonlocal best, nodes_explored
        nodes_explored += 1

        score, violations, visceral = _score_state(
            state, rules, initial_state, goal_predicates
        )
        # Only consider this state as a candidate terminal if it has no
        # visceral violations.
        if not visceral and score > best["score"]:
            best = {
                "sequence": list(history),
                "terminal_state": sorted(state),
                "score": score,
                "violations": violations,
                "trace": list(trace),
            }

        if depth >= max_depth:
            return

        for a in actions:
            new_state, chain = simulate_action(state, a, rules)
            if new_state is None:
                continue
            # Prune any path that walks through a visceral-violating state.
            _, _, intermediate_visceral = _score_state(
                new_state, rules, initial_state, goal_predicates
            )
            if intermediate_visceral:
                continue
            search(
                new_state,
                history + [a.name],
                trace + [f"{a.name}: {chain}" if chain else a.name],
                depth + 1,
            )

    search(initial_state, [], [], 0)
    best["nodes_explored"] = nodes_explored
    best["init_chain_trace"] = init_chain
    best["initial_state"] = sorted(initial_state)
    return best


def reason(
    facts: list[str],
    goal_predicates: list[str],
    rules: list[Rule],
    actions: list[Action],
) -> dict:
    initial_state, init_chain = forward_chain(set(facts), rules)

    evaluations: list[dict] = []
    rejected_for_preconditions: list[str] = []
    for a in actions:
        ev = evaluate_action(initial_state, a, rules, goal_predicates)
        if ev is None:
            rejected_for_preconditions.append(a.name)
            continue
        evaluations.append(ev)

    # Two-tier filter: prefer actions with no visceral violations.
    clean = [e for e in evaluations if not e["visceral_violations"]]
    pool = clean if clean else evaluations
    pool_sorted = sorted(
        pool,
        key=lambda e: (e["goal_met"], e["score"]),
        reverse=True,
    )
    best = pool_sorted[0] if pool_sorted else None

    # Gap = best action still has unmet obligations OR no clean option survived
    # OR no action met the goal.
    gap_reasons: list[str] = []
    if best is None:
        gap_reasons.append("no action satisfied preconditions")
    else:
        if not clean:
            gap_reasons.append("every action violates a visceral constraint")
        if best["violated"]:
            for rid, desc in best["violated"]:
                gap_reasons.append(f"unmet: {rid} {desc}")
        if not best["goal_met"]:
            gap_reasons.append("goal predicates not all satisfied")

    return {
        "initial_facts": sorted(facts),
        "initial_state_after_chain": sorted(initial_state),
        "init_chain_trace": init_chain,
        "goal_predicates": goal_predicates,
        "all_evaluations": pool_sorted,
        "rejected_for_preconditions": rejected_for_preconditions,
        "best": best,
        "gap": bool(gap_reasons),
        "gap_reasons": gap_reasons,
    }
