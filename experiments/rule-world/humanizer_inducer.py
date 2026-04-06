"""Iteration 14 — induce predicate humanization from rule.statement alignment.

Iteration 13 built a structured-to-text explainer over hand-authored
predicate humanization dictionaries (~40 entries per domain). Iteration 14
tests whether the iteration-9 induction trick works on this artifact too:
align each rule's English statement against its formal predicates and
extract the phrase that covers each predicate's tokens.

The bilingual property of the rule store is the lever. Every Rule has
both formal antecedents/consequents and an English `statement` field
authored alongside it. If "A grease fire must be extinguished" is the
statement and `grease_fire`, `fire_extinguished` are the predicates,
then the substrings "a grease fire" and "fire ... extinguished" can be
recovered by token alignment. No matrix multiplication, no learned
language model — just string search.

Coverage will not be 100%: some predicates never appear in any rule
statement (e.g. `hearth_burning_low` is an antecedent of R1 but R1's
statement doesn't say "burning low"). Those predicates fall through
to the explainer's structural fallback (underscores → spaces). The
question iteration 14 answers is: **what fraction of the hand-authored
humanization dictionary can be recovered automatically, and how
readable is the explainer output when running on the induced
dictionary instead of the hand-authored one?**
"""

from __future__ import annotations

import re


# Words that carry no semantic load and should not block phrase recovery.
# Crucially this does NOT include in/at/on/near/from — those ARE content
# in predicates like `wood_in_hearth` or `stranger_at_door`.
_GRAMMATICAL = {
    "a", "an", "the",
    "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "has", "have", "had",
    "must", "may", "should", "shall", "will", "would", "can", "could",
    "and", "or", "but",
    "to", "of",
    "that", "which", "who",
    "any", "some", "no", "not",
}


def _stem(word: str) -> str:
    """Naive plural/verb stem: drop trailing 's' for words long enough.
    Catches lights→light, vehicles→vehicle, ambulances→ambulance,
    extinguishes→extinguishe (close enough for matching). Does not
    touch short words (is, was, has) or non-s endings.
    """
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _normalize_predicate(predicate: str) -> list[str]:
    """Return the lowercase content tokens of a predicate, stemmed."""
    return [_stem(t) for t in predicate.lower().split("_")]


def _normalize_statement(statement: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace, stem."""
    return [_stem(w) for w in re.findall(r"[a-z]+", statement.lower())]


def induce_phrase_for_predicate(
    predicate: str,
    candidate_statements: list[str],
    agent_aliases: dict[str, set[str]] | None = None,
) -> str | None:
    """Find the shortest contiguous span across candidate statements that
    contains every content token of the predicate.

    Returns the span as a space-joined string, or None if no statement
    contains all tokens.

    `agent_aliases` lets a domain map system tokens like `self` to the
    nouns rule statements actually use ("tender", "vehicle", "driver",
    "cook"). A predicate token in the alias map is satisfied if ANY of
    its aliases appears in the candidate statement.
    """
    pred_tokens = _normalize_predicate(predicate)
    aliases = agent_aliases or {}

    # Expand each predicate token to its set of acceptable surface forms.
    token_alts: list[set[str]] = []
    for t in pred_tokens:
        if t in aliases:
            token_alts.append({_stem(a) for a in aliases[t]} | {t})
        else:
            token_alts.append({t})
    pred_set = set().union(*token_alts) if token_alts else set()

    best_span: list[str] | None = None
    best_len = 10**9

    for stmt in candidate_statements:
        words = _normalize_statement(stmt)
        word_set = set(words)
        # Quick reject: every predicate token must have at least one alt
        # somewhere in this statement.
        if not all(alt_set & word_set for alt_set in token_alts):
            continue
        n = len(words)
        # O(n^2) window search — statements are tiny so this is fine.
        for i in range(n):
            for j in range(i + 1, n + 1):
                window = words[i:j]
                window_set = set(window)
                if all(alt_set & window_set for alt_set in token_alts):
                    if (j - i) < best_len:
                        best_len = j - i
                        best_span = window
                    break  # window found at this i; widening can't help

    if best_span is None:
        return None
    # Strip purely grammatical words from the edges only (keep middle structure).
    while best_span and best_span[0] in _GRAMMATICAL:
        best_span = best_span[1:]
    while best_span and best_span[-1] in _GRAMMATICAL:
        best_span = best_span[:-1]
    if not best_span:
        return None
    return " ".join(best_span)


def induce_humanization(
    rules,
    extra_predicates: list[str] = (),
    agent_aliases: dict[str, set[str]] | None = None,
) -> dict[str, str]:
    """Build a predicate -> English phrase dict by aligning rule statements
    against the formal predicates each rule references.

    Inputs:
      rules            — iterable of Rule objects with .statement and slot
                         lists (.antecedents, .derives, .requires_in_result,
                         .forbids_in_result)
      extra_predicates — additional predicate tokens to attempt induction
                         for (e.g. those parsed from scenario facts but not
                         directly used in any rule slot)
    """
    # Collect (predicate, [candidate_statements]) pairs.
    by_predicate: dict[str, list[str]] = {}
    all_statements: list[str] = []
    for r in rules:
        stmt = getattr(r, "statement", "") or ""
        if not stmt:
            continue
        all_statements.append(stmt)
        slots = (
            list(getattr(r, "antecedents", []) or [])
            + list(getattr(r, "derives", []) or [])
            + list(getattr(r, "requires_in_result", []) or [])
            + list(getattr(r, "forbids_in_result", []) or [])
        )
        for p in slots:
            by_predicate.setdefault(p, []).append(stmt)

    induced: dict[str, str] = {}
    for predicate, stmts in by_predicate.items():
        phrase = induce_phrase_for_predicate(predicate, stmts, agent_aliases)
        if phrase:
            induced[predicate] = phrase

    # For predicates that never appeared in a rule slot, try aligning
    # against the union of all statements (weakest signal).
    for predicate in extra_predicates:
        if predicate in induced:
            continue
        phrase = induce_phrase_for_predicate(predicate, all_statements, agent_aliases)
        if phrase:
            induced[predicate] = phrase

    return induced


def coverage_report(
    induced: dict[str, str],
    authored: dict[str, str],
) -> dict:
    """Compare an induced humanization dictionary against a hand-authored one."""
    authored_keys = set(authored.keys())
    induced_keys = set(induced.keys())
    covered = authored_keys & induced_keys
    missing = authored_keys - induced_keys
    extra = induced_keys - authored_keys
    return {
        "authored_total":   len(authored_keys),
        "induced_total":    len(induced_keys),
        "covered":          len(covered),
        "covered_keys":     sorted(covered),
        "missing":          len(missing),
        "missing_keys":     sorted(missing),
        "extra":            len(extra),
        "extra_keys":       sorted(extra),
        "coverage_pct":     (len(covered) / max(len(authored_keys), 1)) * 100.0,
    }
