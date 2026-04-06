"""Iteration 9 — property table induction from rule and observation structure.

Given a substance vocabulary plus a corpus of predicate strings (rule
antecedents/derives/requires/forbids, action preconditions/add/remove,
parsed scenario facts), derive an opaque "feature" set per substance
purely from positional/structural co-occurrence. No hand-authored
property labels, no semantic categories, no matrix multiplication.

The induced features are strings like:
  "role:antecedent"        — substance appeared in an antecedent slot
  "shape:carries_X"        — predicate of form stranger_carries_<S>
  "shape:X_in_hearth"      — predicate of form <S>_in_hearth
  "co:wood"                — co-occurred with `wood` in the same predicate
  "rule_co:water"          — co-occurred with `water` somewhere in same rule
  "act_add:X_in_hearth"    — appeared in an action's `add` list with that suffix

The intent is that two substances which play the same structural role
across the corpus will share many features, and CompressionAnalog (or
HDC) running on this induced table will produce the same nearest-neighbor
choices the hand-authored table produced — without anyone authoring
properties like "feeds_fire".

This is the iteration-9 test of the post-matmul reframe: if grounded
analogy is substrate-independent (iteration 7) AND the grounding itself
can be bootstrapped from rule/observation structure, then the property
table is no longer the manual bottleneck STATUS-2026-04-06 named.
"""

from __future__ import annotations

from collections import defaultdict


def _occurs_in(substance: str, predicate: str) -> tuple[bool, int, int]:
    """Return (found, start_index, end_index) where substance appears as a
    contiguous token sequence inside the underscore-split predicate.

    Supports multi-token substances like "fire_engine" or "horse_carriage".
    """
    pred_tokens = predicate.split("_")
    sub_tokens = substance.split("_")
    n = len(sub_tokens)
    for i in range(len(pred_tokens) - n + 1):
        if pred_tokens[i : i + n] == sub_tokens:
            return True, i, i + n
    return False, -1, -1


def _scan(
    substance: str,
    predicate: str,
    slot: str,
    feature_set: set,
    other_substances: list[str],
) -> bool:
    found, lo, hi = _occurs_in(substance, predicate)
    if not found:
        return False
    tokens = predicate.split("_")
    feature_set.add(f"role:{slot}")
    # Replace the substance span with a placeholder X to capture the shape.
    shape_tokens = tokens[:lo] + ["X"] + tokens[hi:]
    feature_set.add(f"shape:{'_'.join(shape_tokens)}")
    # Co-occurring substances inside the same predicate.
    for other in other_substances:
        if other == substance:
            continue
        if _occurs_in(other, predicate)[0]:
            feature_set.add(f"co:{other}")
    return True


def induce_property_table(
    substances: list[str],
    rules: list = (),
    actions: list = (),
    observations: list[str] = (),
) -> dict[str, list[str]]:
    """Build a substance -> sorted feature list table from corpus structure.

    Inputs:
      substances    — vocabulary the inducer should track (multi-token OK)
      rules         — iterable of Rule objects with .antecedents,
                      .derives, .requires_in_result, .forbids_in_result
      actions       — iterable of Action objects with .preconditions,
                      .add, .remove
      observations  — flat list of predicate strings from parsed scenario
                      facts (used to extend coverage to substances that
                      never appear in authored rules, e.g. oil/food/medicine)
    """
    table: dict[str, set[str]] = {s: set() for s in substances}

    for rule in rules or []:
        slots = [
            ("antecedent", list(getattr(rule, "antecedents", []) or [])),
            ("derives",    list(getattr(rule, "derives", []) or [])),
            ("requires",   list(getattr(rule, "requires_in_result", []) or [])),
            ("forbids",    list(getattr(rule, "forbids_in_result", []) or [])),
        ]
        rule_substances: set[str] = set()
        for _, preds in slots:
            for p in preds:
                for s in substances:
                    if _occurs_in(s, p)[0]:
                        rule_substances.add(s)
        for slot_name, preds in slots:
            for p in preds:
                for s in substances:
                    _scan(s, p, slot_name, table[s], substances)
        for s in rule_substances:
            for other in rule_substances:
                if other != s:
                    table[s].add(f"rule_co:{other}")

    for action in actions or []:
        action_slots = [
            ("act_pre", list(getattr(action, "preconditions", []) or [])),
            ("act_add", list(getattr(action, "add", []) or [])),
            ("act_rem", list(getattr(action, "remove", []) or [])),
        ]
        action_substances: set[str] = set()
        for _, preds in action_slots:
            for p in preds:
                for s in substances:
                    if _occurs_in(s, p)[0]:
                        action_substances.add(s)
        for slot_name, preds in action_slots:
            for p in preds:
                for s in substances:
                    if not _occurs_in(s, p)[0]:
                        continue
                    table[s].add(f"role:{slot_name}")
                    found, lo, hi = _occurs_in(s, p)
                    tokens = p.split("_")
                    shape_tokens = tokens[:lo] + ["X"] + tokens[hi:]
                    table[s].add(f"{slot_name}_shape:{'_'.join(shape_tokens)}")
                    for other in substances:
                        if other != s and _occurs_in(other, p)[0]:
                            table[s].add(f"co:{other}")
        for s in action_substances:
            for other in action_substances:
                if other != s:
                    table[s].add(f"action_co:{other}")

    for fact in observations or []:
        for s in substances:
            _scan(s, fact, "observation", table[s], substances)

    return {s: sorted(feats) for s, feats in table.items()}


def induce_property_roles(
    induced_table: dict[str, list[str]],
) -> dict[str, str]:
    """Bucket each induced feature by its prefix into a small role set.

    These buckets are structural, not semantic. They exist so the
    role-weighted similarity functions (HDC v3, CompressionAnalog
    .predict_role_weighted) have a roles dict to consume. The induction
    has no semantic knowledge of which roles matter when — every bucket
    is "active" by default.
    """
    roles: dict[str, str] = {}
    for feats in induced_table.values():
        for f in feats:
            head = f.split(":", 1)[0]
            if head.startswith("act_") and head.endswith("_shape"):
                roles[f] = "action_shape"
            else:
                roles[f] = {
                    "role":     "structural_role",
                    "shape":    "predicate_shape",
                    "co":       "co_substance",
                    "rule_co":  "co_substance",
                    "action_co": "co_substance",
                    "act_pre":  "action_shape",
                    "act_add":  "action_shape",
                    "act_rem":  "action_shape",
                }.get(head, "other")
    return roles


def induced_active_roles() -> set[str]:
    return {
        "structural_role",
        "predicate_shape",
        "co_substance",
        "action_shape",
        "other",
    }
