"""Layer 0 — Persistent rule store.

Lives on disk as rule_store.json. Holds every rule the system knows about,
authored or crystallized, with metadata: domain tag, context tags, confidence,
usage count, source.

The forward-chaining engine never reads this directly. It only sees what the
retriever pulls into the active window.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from engine import Rule

STORE_PATH = Path(__file__).parent / "rule_store.json"


def _rule_to_dict(r: Rule) -> dict:
    return {
        "id": r.id,
        "antecedents": r.antecedents,
        "forbidden": r.forbidden,
        "derives": r.derives,
        "requires_in_result": r.requires_in_result,
        "forbids_in_result": r.forbids_in_result,
        "priority": r.priority,
        "urgency": r.urgency,
        "statement": r.statement,
    }


def _dict_to_rule(d: dict) -> Rule:
    return Rule(
        id=d["id"],
        antecedents=list(d.get("antecedents", [])),
        forbidden=list(d.get("forbidden", [])),
        derives=list(d.get("derives", [])),
        requires_in_result=list(d.get("requires_in_result", [])),
        forbids_in_result=list(d.get("forbids_in_result", [])),
        priority=int(d.get("priority", 5)),
        urgency=d.get("urgency", "medium"),
        statement=d.get("statement", ""),
    )


class RuleStore:
    def __init__(self, path: Path = STORE_PATH):
        self.path = Path(path)
        if self.path.exists():
            self.data = json.loads(self.path.read_text())
        else:
            self.data = {"rules": {}}

    # ---------- persistence ----------

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2))

    # ---------- writes ----------

    def add_rule(
        self,
        rule: Rule,
        domain: str,
        context_tags: list[str],
        source: str,
        confidence: float = 1.0,
    ) -> None:
        entry = _rule_to_dict(rule)
        entry.update(
            {
                "domain": domain,
                "context_tags": list(context_tags),
                "confidence": float(confidence),
                "usage_count": 0,
                "source": source,
            }
        )
        self.data["rules"][rule.id] = entry
        self.save()

    def update_confidence(self, rule_id: str, confidence: float) -> None:
        if rule_id in self.data["rules"]:
            self.data["rules"][rule_id]["confidence"] = float(confidence)
            self.save()

    def increment_usage(self, rule_id: str) -> None:
        if rule_id in self.data["rules"]:
            self.data["rules"][rule_id]["usage_count"] += 1
            self.save()

    def suppress_rule(self, rule_id: str, reason: str = "") -> None:
        if rule_id in self.data["rules"]:
            self.data["rules"][rule_id]["suppressed"] = True
            self.data["rules"][rule_id]["suppression_reason"] = reason
            self.save()

    # ---------- reads ----------

    def get_rule(self, rule_id: str) -> Rule | None:
        d = self.data["rules"].get(rule_id)
        return _dict_to_rule(d) if d else None

    def get_meta(self, rule_id: str) -> dict | None:
        return self.data["rules"].get(rule_id)

    def all_entries(self, include_suppressed: bool = False) -> list[dict]:
        if include_suppressed:
            return list(self.data["rules"].values())
        return [
            d for d in self.data["rules"].values()
            if not d.get("suppressed", False)
        ]

    def all_rules(self, include_suppressed: bool = False) -> list[Rule]:
        return [_dict_to_rule(d) for d in self.all_entries(include_suppressed)]

    def query_by_tags(
        self, domains: list[str], context_tags: list[str]
    ) -> list[dict]:
        scored: list[tuple[float, dict]] = []
        ctx_set = set(context_tags)
        dom_set = set(domains)
        for entry in self.all_entries(include_suppressed=False):
            score = 0.0
            if entry["domain"] in dom_set:
                score += 2.0
            score += len(set(entry["context_tags"]) & ctx_set)
            if score > 0:
                scored.append((score, entry))
        scored.sort(key=lambda x: -x[0])
        return [e for _, e in scored]


# ---------- one-shot migration of authored rules ----------

TAG_MAP = {
    "R1": ("fire_safety", ["hearth_at_risk", "wood_present"]),
    "R2": ("fire_safety", ["water_present", "hearth_present"]),
    "R3": ("hospitality", ["stranger_present", "water_present"]),
    "R4": ("hospitality", ["stranger_present", "cold_being", "hearth_present"]),
    "R5": ("honesty", ["tender_present"]),
    "C1": ("fire_safety", ["hearth_present"]),
    "C2": ("fire_safety", ["hearth_present", "tender_present"]),
    "C3": ("fire_safety", ["wood_low"]),
    "C4": ("ethics", []),
    "C5": ("meta", []),
    "P1": ("physical", []),
    "P2": ("physical", ["water_present"]),
    "P3a": ("physical", ["wood_present", "hearth_present"]),
    "P4": ("physical", []),
    "P5": ("physical", []),
    "P6": ("physical", []),
    "P-wet": ("physical", ["stranger_present", "water_present"]),
    "P-water-in-hall": ("physical", ["stranger_present", "water_present"]),
    "P-water-near-hearth": ("physical", ["stranger_present", "water_present", "hearth_present"]),
    "P-shelter": ("physical", ["stranger_present", "hearth_present"]),
    "P-attendance": ("physical", ["tender_present", "hearth_present"]),
    "P-wood-leaving": ("physical", ["wood_present", "child_present"]),
    "P-extinguish": ("physical", ["water_present", "hearth_present"]),
    "P-admitted-with-water": ("physical", ["stranger_present", "water_present"]),
}


def migrate_authored_rules(force: bool = False) -> RuleStore:
    """Populate rule_store.json from world_structured.ALL_RULES if missing."""
    store = RuleStore()
    if store.data["rules"] and not force:
        return store
    from world_structured import ALL_RULES

    store.data = {"rules": {}}
    for r in ALL_RULES:
        domain, tags = TAG_MAP.get(r.id, ("misc", []))
        store.add_rule(r, domain=domain, context_tags=tags, source="authored", confidence=1.0)
    return store


if __name__ == "__main__":
    s = migrate_authored_rules(force=True)
    print(f"Migrated {len(s.all_rules())} rules to {s.path}")
