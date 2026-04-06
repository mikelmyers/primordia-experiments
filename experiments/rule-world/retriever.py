"""Layer 1 — Context Retriever.

Given a fact set + goal, returns a small active rule window (<=30) from the
rule store. The engine never sees the full store. The retriever is the only
component that scans everything.

Retrieval signal:
  1. Derive context tags from the fact vocabulary (entity prefixes + table).
  2. Score each rule entry by:
       2 * (domain matches one of the inferred domains)
       + 1 per overlapping context tag
       + 0.5 per direct antecedent/derives match against a fact
       + 0.05 * usage_count (frequency boost)
       + confidence (proven rules slightly preferred)
  3. Return top N entries as Rule objects.

Logs which rules were pulled and which were left dormant.
"""

from __future__ import annotations

from engine import Rule
from rule_store import RuleStore, _dict_to_rule


WINDOW_SIZE = 30


# Direct fact-to-tag overrides for facts that don't follow the prefix convention.
FACT_TAG_OVERRIDES = {
    "asked_by_tender": ["tender_present"],
    "wood_supply_insufficient": ["wood_low", "wood_present"],
    "hearth_burning_low": ["hearth_at_risk", "hearth_present"],
    "hearth_burning": ["hearth_present"],
}

PREFIX_TAGS = {
    "stranger_": ["stranger_present"],
    "water_": ["water_present"],
    "wood_": ["wood_present"],
    "child_": ["child_present"],
    "hearth_": ["hearth_present"],
    "self_": ["tender_present"],
    "ice_": ["ice_present"],
    "oil_": ["oil_present"],
    "snow_": ["snow_present"],
}

# Coarse domain inference from tags.
TAG_TO_DOMAIN = {
    "hearth_at_risk": "fire_safety",
    "hearth_present": "fire_safety",
    "water_present": "fire_safety",
    "wood_low": "fire_safety",
    "wood_present": "fire_safety",
    "stranger_present": "hospitality",
    "cold_being": "hospitality",
    "tender_present": "honesty",
    "child_present": "hospitality",
}


def derive_context_tags(facts: list[str]) -> list[str]:
    tags: set[str] = set()
    for f in facts:
        if f in FACT_TAG_OVERRIDES:
            tags.update(FACT_TAG_OVERRIDES[f])
        for prefix, tag_list in PREFIX_TAGS.items():
            if f.startswith(prefix):
                tags.update(tag_list)
        # Cold-being detection
        if "cold" in f:
            tags.add("cold_being")
    return sorted(tags)


def derive_domains(context_tags: list[str]) -> list[str]:
    domains: set[str] = set()
    for t in context_tags:
        if t in TAG_TO_DOMAIN:
            domains.add(TAG_TO_DOMAIN[t])
    domains.add("physical")  # always include passive physics
    return sorted(domains)


def retrieve(
    facts: list[str],
    goal: list[str],
    store: RuleStore,
    window: int = WINDOW_SIZE,
) -> dict:
    context_tags = derive_context_tags(facts)
    domains = derive_domains(context_tags)
    fact_set = set(facts)
    goal_set = set(goal)

    scored: list[tuple[float, dict]] = []
    for entry in store.all_entries():
        score = 0.0
        if entry["domain"] in domains:
            score += 2.0
        score += len(set(entry["context_tags"]) & set(context_tags))
        # Direct antecedent match
        if any(a in fact_set for a in entry["antecedents"]):
            score += 0.5
        # Direct goal match
        if any(g in entry["requires_in_result"] for g in goal_set):
            score += 1.0
        if any(d in goal_set for d in entry["derives"]):
            score += 0.5
        score += 0.05 * entry.get("usage_count", 0)
        score += 0.1 * entry.get("confidence", 1.0)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: -x[0])
    pulled = [e for _, e in scored[:window]]
    dormant = [e for _, e in scored[window:]] + [
        e for e in store.all_entries() if e not in [x[1] for x in scored]
    ]

    return {
        "context_tags": context_tags,
        "domains": domains,
        "active_rules": [_dict_to_rule(e) for e in pulled],
        "active_rule_meta": pulled,
        "dormant_rule_ids": [e["id"] for e in dormant],
        "total_in_store": len(store.all_entries()),
    }
