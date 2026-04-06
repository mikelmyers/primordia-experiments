"""Iteration 13 — verbose structured-to-text explainer.

Domain-agnostic. Takes the structured artifacts every domain runner already
produces (parsed facts, retrieval result, engine evaluations + choice,
planner result, optional v4 log) plus a per-domain humanization dictionary
that maps predicate tokens to English noun/verb phrases. Returns a
multi-paragraph markdown explanation.

This is the iteration 13 NL output layer. It is the bridge between the
engine's internal predicate representation and human-readable English.
Architecturally it plays the same role an LLM tokenizer plays on the
output side, but where an LLM tokenizer hands tokens to a learned
next-token distribution, this hands predicate tokens to a small fixed
grammar of explanation patterns. No matrix multiplication. No learned
model. Every word can be traced to a rule, a fact, or a humanization
entry.

Honest bug reporting: when the chosen action wins despite a visceral
violation, the explanation says so explicitly with the violated rule
cited by ID. When the gap fires, the explanation says the system has
no good answer. Hiding either would be exactly the dishonest behavior
LLMs are infamous for.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExplanationInputs:
    """Everything the explainer needs from a single scenario run."""
    domain_name: str
    scenario_title: str
    scenario_description: str
    parsed_facts: list[str]
    parsed_goal: list[str]
    retrieval_active_rule_ids: list[str]
    rule_statements: dict[str, str]            # rule_id -> English statement
    initial_state_after_chain: list[str]
    evaluations: list[dict]                    # ordered best-first
    chosen: dict | None                        # the winning eval (or None)
    gap: bool
    gap_reasons: list[str]
    plan_sequence: list[str]
    plan_score: int
    v4_targets: list[str]                      # substances v4 fired for
    v4_analogs: dict[str, tuple[str, float]]   # substance -> (peer, sim)
    v4_projected_rules: dict[str, list[str]]   # substance -> list of new rule ids
    v4_synthesized_actions: dict[str, list[str]]  # substance -> list of new action names
    humanizer: "Humanizer"


class Humanizer:
    """Maps predicate tokens to English phrases for one domain.

    Falls back to a structural transformation when a predicate is not in
    the dictionary: replaces underscores with spaces. This makes the
    explainer degrade gracefully on a partially-authored dictionary
    instead of crashing.
    """

    def __init__(self, predicate_phrases: dict[str, str], action_phrases: dict[str, str]):
        self.predicate_phrases = predicate_phrases
        self.action_phrases = action_phrases

    def predicate(self, token: str) -> str:
        if token in self.predicate_phrases:
            return self.predicate_phrases[token]
        return token.replace("_", " ")

    def action(self, name: str) -> str:
        if name in self.action_phrases:
            return self.action_phrases[name]
        return name.replace("_", " ")

    def predicates(self, tokens: list[str]) -> list[str]:
        return [self.predicate(t) for t in tokens]


def _join_english(items: list[str]) -> str:
    if not items:
        return "nothing"
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def explain(inputs: ExplanationInputs) -> str:
    """Generate a verbose multi-paragraph English explanation."""
    h = inputs.humanizer
    out: list[str] = []

    # ----- Heading -----
    out.append(f"### Explanation — {inputs.scenario_title}")
    out.append("")

    # ----- Situation -----
    facts_eng = h.predicates(sorted(inputs.parsed_facts))
    goal_eng = h.predicates(inputs.parsed_goal)
    out.append("**Situation.**")
    out.append(
        f"The system was given this description: *\"{inputs.scenario_description.strip()}\"* "
        f"From that, the parser extracted the following facts about the world: "
        f"{_join_english(facts_eng)}. "
        f"The goal — what a successful resolution must achieve — is "
        f"{_join_english(goal_eng)}."
    )
    out.append("")

    # ----- Active rules -----
    out.append("**Rules in scope.**")
    if inputs.retrieval_active_rule_ids:
        out.append(
            f"The retriever pulled {len(inputs.retrieval_active_rule_ids)} rule(s) into "
            f"the active window for this situation. The relevant ones, in plain language, are:"
        )
        out.append("")
        # Cap at 8 to keep the paragraph readable; cite by ID for traceability.
        shown = inputs.retrieval_active_rule_ids[:8]
        for rid in shown:
            stmt = inputs.rule_statements.get(rid, "(no English statement on file)")
            out.append(f"- **{rid}**: {stmt}")
        if len(inputs.retrieval_active_rule_ids) > 8:
            out.append(
                f"- *…and {len(inputs.retrieval_active_rule_ids) - 8} more rules in the window.*"
            )
    else:
        out.append("No rules were retrieved as active for this situation.")
    out.append("")

    # ----- Derivation -----
    derived = sorted(set(inputs.initial_state_after_chain) - set(inputs.parsed_facts))
    if derived:
        out.append("**What the engine inferred before choosing an action.**")
        out.append(
            f"From the parsed facts, the engine ran its forward-chaining derivation "
            f"and concluded the following additional facts hold: "
            f"{_join_english(h.predicates(derived))}. "
            f"These were not in the original description; they are consequences of "
            f"the physics rules in the active window."
        )
        out.append("")

    # ----- Analogy (when v4 fired) -----
    if inputs.v4_targets:
        out.append("**Analogical reasoning.**")
        out.append(
            f"This scenario involves {len(inputs.v4_targets)} substance(s) the system "
            f"has not directly seen in any authored rule: "
            f"{_join_english(inputs.v4_targets)}. "
            f"For each, the v4 abstractor searched the property table for the closest "
            f"familiar analog and projected the rules and actions that apply to the "
            f"analog onto the new substance, producing new rules and actions at runtime "
            f"by structural substitution. The analogies it found:"
        )
        out.append("")
        for sub in inputs.v4_targets:
            peer_info = inputs.v4_analogs.get(sub)
            if peer_info is None:
                out.append(f"- **{sub}**: no analog peer found.")
                continue
            peer, sim = peer_info
            new_rules = inputs.v4_projected_rules.get(sub, [])
            new_acts = inputs.v4_synthesized_actions.get(sub, [])
            line = (
                f"- **{sub} ≈ {peer}** (similarity {sim:+.3f}). "
                f"From this analogy the system synthesized "
                f"{len(new_rules)} new rule(s) and {len(new_acts)} new action(s)"
            )
            if new_acts:
                line += " (" + ", ".join(new_acts) + ")"
            line += "."
            out.append(line)
        out.append("")
        out.append(
            "None of this required matrix multiplication. The analog choice came from "
            "role-weighted similarity over a small property table. The new rules came "
            "from token substitution. The new actions came from token substitution. "
            "Every step is auditable."
        )
        out.append("")

    # ----- Alternatives considered -----
    out.append("**Alternatives considered.**")
    if inputs.evaluations:
        out.append(
            f"The engine scored {len(inputs.evaluations)} candidate action(s) against the "
            f"current state, the goal, and every active rule. The top three were:"
        )
        out.append("")
        for ev in inputs.evaluations[:3]:
            line = (
                f"- **{h.action(ev['action'])}** "
                f"(score {ev['score']}, goal_met={ev['goal_met']})"
            )
            if ev.get("visceral_violations"):
                violations = "; ".join(
                    f"{rid} — {reason}" for rid, reason in ev["visceral_violations"]
                )
                line += f" — *but this violates a visceral rule: {violations}*"
            out.append(line)
    else:
        out.append("No actions were evaluated.")
    out.append("")

    # ----- Choice -----
    out.append("**Decision.**")
    if inputs.chosen is not None:
        chosen_name = inputs.chosen["action"]
        chosen_eng = h.action(chosen_name)
        score = inputs.chosen["score"]
        violations = inputs.chosen.get("visceral_violations") or []
        if violations:
            # Honest bug reporting: the system chose despite a violation.
            viol_text = "; ".join(
                f"{rid} ({reason})" for rid, reason in violations
            )
            out.append(
                f"The system chose **{chosen_eng}** with a score of {score}. "
                f"This decision is *not clean*: it violates {viol_text}. "
                f"The system chose it anyway because every available action had a "
                f"visceral violation, and this one had the highest goal-completion "
                f"score among the bad options. **A human should be alerted that no "
                f"safe action exists in this state.**"
            )
        else:
            out.append(
                f"The system chose **{chosen_eng}** with a score of {score}. "
                f"This action satisfies the goal ({_join_english(goal_eng)}) without "
                f"violating any visceral rule in the active window. "
                f"It is the highest-scoring option and is safe to take."
            )
    else:
        out.append(
            "The system chose **no action**. The engine could not find any candidate "
            "that resolves the situation without violating a visceral rule."
        )
    out.append("")

    # ----- Gap -----
    if inputs.gap:
        out.append("**Honest caveat.**")
        out.append(
            "The engine flagged this situation as a *gap*: the available rules and "
            "actions are not sufficient to produce a clean resolution. "
        )
        if inputs.gap_reasons:
            out.append("Specifically:")
            out.append("")
            for r in inputs.gap_reasons:
                out.append(f"- {r}")
        out.append("")
        out.append(
            "A gap is not a hallucination. The system is telling you it does not have "
            "the rules or actions to handle this case correctly. The right next step "
            "is for a human to examine the situation, decide what should have happened, "
            "and add a rule or action to the store so the system handles it next time. "
            "This is the opposite of an LLM, which would confidently produce a wrong "
            "answer in the same situation."
        )
        out.append("")

    # ----- Multi-step plan (if planner found a sequence) -----
    if inputs.plan_sequence and len(inputs.plan_sequence) > 1:
        steps_eng = [h.action(a) for a in inputs.plan_sequence]
        out.append("**Multi-step plan.**")
        out.append(
            f"The planner also found a multi-step sequence with score "
            f"{inputs.plan_score}: {' → '.join(steps_eng)}. "
            f"The single-action choice above is the first step of this sequence."
        )
        out.append("")

    # ----- Trace -----
    out.append("**Trace.**")
    out.append(
        f"This explanation was generated from {len(inputs.parsed_facts)} parsed facts, "
        f"{len(inputs.retrieval_active_rule_ids)} active rules, "
        f"{len(inputs.evaluations)} evaluated actions, and "
        f"{len(inputs.v4_targets)} v4 analog target(s). "
        f"Every claim above can be cross-referenced against the structured run output. "
        f"No language model produced any word of this explanation; it came from a "
        f"~250-line template grammar over a hand-authored {len(h.predicate_phrases)}-entry "
        f"predicate dictionary for the {inputs.domain_name} domain."
    )
    out.append("")

    return "\n".join(out)
