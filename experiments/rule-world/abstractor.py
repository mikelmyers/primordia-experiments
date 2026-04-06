"""Layer 2 — Abstractor.

Watches engine runs. When a gap is found — or when a fact in the scenario is
referenced by no rule in the active window OR the full store — the abstractor
analyzes and tries to crystallize a new rule.

Two crystallization paths:

  PATH A — predicate analogy.
    A scenario fact has the shape `<entity>_<verb>_<object>` (e.g.
    `stranger_carries_ice`). No rule references that exact predicate, but
    rules DO reference structurally parallel predicates with a different
    object (e.g. `stranger_carries_water`). The abstractor copies every such
    rule, substituting the new object for the old, and saves the copies as
    crystallized rules with confidence 0.4.

  PATH B — unmet obligation.
    The engine reports an unmet obligation predicate. The abstractor looks
    for any action whose effects are "almost" the obligation, and writes a
    second-order rule mapping the antecedent fact set onto the obligation.
    (Best-effort; logged honestly when it can't.)

Every crystallization attempt — successful or not — is logged with the full
chain of reasoning that led to it.
"""

from __future__ import annotations

from engine import Rule
from rule_store import RuleStore, _dict_to_rule
from hdc import Codebook, encode_property_bundle, similarity


def _split_predicate(p: str) -> tuple[str, str] | None:
    """Split `<entity>_<verb>_<object>` into (head, object). Heuristic."""
    parts = p.split("_")
    if len(parts) < 3:
        return None
    head = "_".join(parts[:-1])
    obj = parts[-1]
    return head, obj


def _all_predicates_in_rule(entry: dict) -> set[str]:
    return set(
        entry.get("antecedents", [])
        + entry.get("forbidden", [])
        + entry.get("derives", [])
        + entry.get("requires_in_result", [])
        + entry.get("forbids_in_result", [])
    )


def _substitute_object(text: str, old_obj: str, new_obj: str) -> str:
    """Replace the trailing `_<old_obj>` with `_<new_obj>` if present."""
    suffix = "_" + old_obj
    if text.endswith(suffix):
        return text[: -len(suffix)] + "_" + new_obj
    return text


def _substitute_in_list(items: list[str], old_obj: str, new_obj: str) -> list[str]:
    return [_substitute_object(x, old_obj, new_obj) for x in items]


def find_unhandled_facts(facts: list[str], store: RuleStore) -> list[str]:
    """Facts whose predicates appear in zero rules in the entire store."""
    seen: set[str] = set()
    for entry in store.all_entries():
        seen.update(_all_predicates_in_rule(entry))
    return [f for f in facts if f not in seen]


def _references_object(pred: str, obj: str) -> bool:
    """True if `pred` ends with `_<obj>`."""
    return pred.endswith("_" + obj)


def crystallize_by_analogy(
    unhandled_fact: str, store: RuleStore
) -> tuple[list[Rule], list[str]]:
    """Identify a peer object via the unhandled fact (e.g. ice ↔ water),
    then crystallize a copy of EVERY rule that references any predicate
    suffixed by the peer object, substituting the new object throughout.

    This is a stronger analogy than head-only matching: it propagates the
    substitution across the whole rule subgraph that touches the peer.
    """
    log: list[str] = []
    split = _split_predicate(unhandled_fact)
    if split is None:
        log.append(f"  • cannot split `{unhandled_fact}` into head/object form; skipping analogy")
        return [], log
    head, new_obj = split
    log.append(f"  • split `{unhandled_fact}` → head=`{head}` object=`{new_obj}`")

    # Step 1: find peer objects via head match (e.g. stranger_carries_water).
    peer_objects: set[str] = set()
    for entry in store.all_entries():
        for pred in _all_predicates_in_rule(entry):
            other = _split_predicate(pred)
            if other and other[0] == head and other[1] != new_obj:
                peer_objects.add(other[1])
    if not peer_objects:
        log.append(f"  • no peer predicates with head `{head}` found in store")
        return [], log
    log.append(f"  • peer objects with same head: {sorted(peer_objects)}")

    new_rules: list[Rule] = []
    for old_obj in peer_objects:
        # Step 2: scan EVERY rule for any predicate suffixed `_<old_obj>`.
        # Substitute old_obj → new_obj across that rule's whole predicate set.
        for entry in store.all_entries():
            preds = _all_predicates_in_rule(entry)
            if not any(_references_object(p, old_obj) for p in preds):
                continue
            if entry.get("source") == "crystallized":
                continue  # don't analogize from analogies
            new_id = f"{entry['id']}~{new_obj}"
            if store.get_rule(new_id) is not None:
                continue
            new_rule = Rule(
                id=new_id,
                antecedents=_substitute_in_list(entry["antecedents"], old_obj, new_obj),
                forbidden=_substitute_in_list(entry["forbidden"], old_obj, new_obj),
                derives=_substitute_in_list(entry["derives"], old_obj, new_obj),
                requires_in_result=_substitute_in_list(entry["requires_in_result"], old_obj, new_obj),
                forbids_in_result=_substitute_in_list(entry["forbids_in_result"], old_obj, new_obj),
                priority=entry["priority"],
                urgency=entry["urgency"],
                statement=f"[crystallized from {entry['id']} by {old_obj}→{new_obj} analogy] " + entry.get("statement", ""),
            )
            new_rules.append(new_rule)
            log.append(
                f"  • crystallized {new_id} from {entry['id']} "
                f"(substitute {old_obj}→{new_obj} across rule)"
            )
    return new_rules, log


def crystallize_by_hdc_analogy(
    unhandled_fact: str,
    store: RuleStore,
    properties_by_substance: dict[str, list[str]],
    codebook: Codebook,
    similarity_threshold: float = 0.10,
) -> tuple[list[Rule], list[str]]:
    """HDC-grounded analogy: only substitute when property bundles overlap.

    The syntactic abstractor would happily substitute `water → oil` because
    both end the predicate `stranger_carries_<X>`. The HDC abstractor first
    checks whether oil and water actually share the properties that made the
    rule about water *forbid* admission. If they don't, it refuses to
    substitute, even though syntactic structure permits it.

    This is the test of whether distributed property representations can
    discriminate semantically inappropriate analogies that string matching
    cannot.

    NOTE: this function does NOT mutate the store. It is run as a shadow
    alongside the production syntactic abstractor for comparison.
    """
    log: list[str] = []
    split = _split_predicate(unhandled_fact)
    if split is None:
        log.append(f"  • cannot split `{unhandled_fact}`")
        return [], log
    head, new_obj = split
    log.append(f"  • split `{unhandled_fact}` → head=`{head}`, object=`{new_obj}`")

    if new_obj not in properties_by_substance:
        log.append(
            f"  • `{new_obj}` has no entry in property table; "
            f"HDC analogy declines (would be ungrounded)"
        )
        return [], log

    new_props = properties_by_substance[new_obj]
    log.append(f"  • `{new_obj}` properties: {new_props}")
    new_hv = encode_property_bundle(new_props, codebook)

    # Find peer objects via head match (same as syntactic).
    peer_objects: set[str] = set()
    for entry in store.all_entries():
        for pred in _all_predicates_in_rule(entry):
            other = _split_predicate(pred)
            if other and other[0] == head and other[1] != new_obj:
                peer_objects.add(other[1])
    if not peer_objects:
        log.append(f"  • no peer objects with head `{head}`")
        return [], log
    log.append(f"  • candidate peer objects (head match): {sorted(peer_objects)}")

    # Score each peer by HDC property similarity.
    scored_peers: list[tuple[str, float]] = []
    for peer in sorted(peer_objects):
        if peer not in properties_by_substance:
            log.append(f"  • peer `{peer}` not in property table; cannot score")
            continue
        peer_props = properties_by_substance[peer]
        peer_hv = encode_property_bundle(peer_props, codebook)
        sim = similarity(new_hv, peer_hv)
        verdict = "ACCEPT" if sim >= similarity_threshold else "REJECT"
        log.append(
            f"  • HDC similarity({new_obj}, {peer}) = {sim:+.4f}  "
            f"[{peer} props: {peer_props}]  → {verdict}"
        )
        if sim >= similarity_threshold:
            scored_peers.append((peer, sim))

    if not scored_peers:
        log.append(
            f"  ✗ no peer passed similarity threshold {similarity_threshold}; "
            f"HDC abstractor REFUSES to crystallize an analogy "
            f"(this is the win condition vs syntactic substitution)"
        )
        return [], log

    scored_peers.sort(key=lambda x: -x[1])
    best_peer, best_sim = scored_peers[0]
    log.append(
        f"  ✓ selected peer for substitution: `{best_peer}` (sim {best_sim:+.4f})"
    )

    new_rules: list[Rule] = []
    for entry in store.all_entries():
        preds = _all_predicates_in_rule(entry)
        if not any(_references_object(p, best_peer) for p in preds):
            continue
        if entry.get("source") == "crystallized":
            continue
        new_id = f"{entry['id']}~{new_obj}_hdc"
        new_rule = Rule(
            id=new_id,
            antecedents=_substitute_in_list(entry["antecedents"], best_peer, new_obj),
            forbidden=_substitute_in_list(entry["forbidden"], best_peer, new_obj),
            derives=_substitute_in_list(entry["derives"], best_peer, new_obj),
            requires_in_result=_substitute_in_list(entry["requires_in_result"], best_peer, new_obj),
            forbids_in_result=_substitute_in_list(entry["forbids_in_result"], best_peer, new_obj),
            priority=entry["priority"],
            urgency=entry["urgency"],
            statement=(
                f"[HDC-crystallized from {entry['id']} by "
                f"{best_peer}→{new_obj} (sim {best_sim:+.3f})] "
                + entry.get("statement", "")
            ),
        )
        new_rules.append(new_rule)
        log.append(f"  • would crystallize {new_id} from {entry['id']}")
    return new_rules, log


def analyze_and_crystallize(
    facts: list[str],
    goal: list[str],
    engine_result: dict,
    active_window: list[Rule],
    store: RuleStore,
) -> dict:
    """Run after the engine. Detects gaps and tries to write new rules.

    Returns a structured log + a list of crystallized rule IDs added to the store.
    """
    log: list[str] = []
    crystallized_ids: list[str] = []

    # ---------- Detect Path A: unhandled predicates in scenario ----------
    unhandled = find_unhandled_facts(facts, store)
    if unhandled:
        log.append(f"PATH A — unhandled predicates: {unhandled}")
        for f in unhandled:
            new_rules, sublog = crystallize_by_analogy(f, store)
            log.extend(sublog)
            for nr in new_rules:
                # Tag inheritance: take tags from the source rule, plus
                # an "<object>_present" tag derived from the new object.
                src_id = nr.id.split("~")[0]
                src_meta = store.get_meta(src_id) or {"domain": "misc", "context_tags": []}
                obj = nr.id.split("~")[-1]
                new_tags = list(set(src_meta["context_tags"] + [f"{obj}_present"]))
                store.add_rule(
                    nr,
                    domain=src_meta["domain"],
                    context_tags=new_tags,
                    source="crystallized",
                    confidence=0.4,
                )
                crystallized_ids.append(nr.id)
                log.append(f"  ✓ added {nr.id} to store with tags {new_tags}, conf=0.4")
    else:
        log.append("PATH A — all scenario predicates referenced by some rule; nothing to analogize")

    # ---------- Detect Path B: unmet obligations from engine result ----------
    if engine_result.get("gap"):
        log.append(f"PATH B — engine reported gap: {engine_result.get('gap_reasons')}")
        best = engine_result.get("best")
        if best:
            for rid, desc in best.get("violated", []):
                log.append(f"  • unmet from {rid}: {desc}")
            log.append(
                "  • Path B (cross-rule synthesis from unmet obligations) is not"
                " implemented in this iteration. Logging only."
            )
    else:
        log.append("PATH B — no engine-reported gap")

    return {
        "crystallized_ids": crystallized_ids,
        "log": log,
        "unhandled_facts": unhandled,
    }
