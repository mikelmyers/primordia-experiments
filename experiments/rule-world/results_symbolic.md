# Results (symbolic runner)

Run: 2026-04-06T11:41:31.743168Z
Engine: pure symbolic rule interpreter (no LLM, no matmul)
Rules loaded: 16

## Scenario 1 (covered)

**Facts:** alone_in_hall, hearth_burning_low, wood_available

**Goal:** keep_hearth_alive

**Cited rules:** R1, C1

**Gap:** no

**Gap resolution:** n/a

**Action:** add_wood_to_hearth

**Activation trace:**

```
R1 (p10/visceral) -> add_wood_to_hearth
C1 (p10/visceral) -> preserve_hearth
```

---

## Scenario 2 (covered)

**Facts:** stranger_at_door, stranger_carries_water, stranger_requests_entry

**Goal:** decide_admission

**Cited rules:** R3

**Gap:** no

**Gap resolution:** n/a

**Action:** refuse_stranger

**Activation trace:**

```
R3 (p8/high) -> refuse_stranger
```

---

## Scenario 3 (covered)

**Facts:** asked_by_tender, wood_supply_insufficient

**Goal:** respond_truthfully

**Cited rules:** C3, R5

**Gap:** yes

**Gap resolution:** No rule directly resolves this. Highest-priority activated rules: ['C3', 'R5']. Defaulting to the action that best preserves C1.

**Action:** replenish_wood

**Activation trace:**

```
C3 (p8/high) -> replenish_wood
R5 (p6/medium) -> tell_truth
```

---

## Scenario 4 (gap)

**Facts:** stranger_at_door, stranger_wet_with_water, stranger_not_carrying_water, stranger_cold

**Goal:** decide_admission

**Cited rules:** R2, R3, R4, C1

**Gap:** yes

**Gap resolution:** R3 only addresses Strangers CARRYING water, not Strangers SOAKED in it. Composing R2 (keep water from Hearth) + R4 (shelter the cold) + C1 (Hearth must never be extinguished): admit the Stranger to satisfy R4, but keep them far from the Hearth to honor R2 and C1.

**Action:** admit_but_keep_far_from_hearth

**Activation trace:**

```
```

---

## Scenario 5 (gap)

**Facts:** child_tender_taking_wood, child_tender_walking_to_door, only_other_tender_is_self, hearth_burning

**Goal:** preserve_hearth_and_wood

**Cited rules:** C1, C2, C3, C4, R5

**Gap:** yes

**Gap resolution:** C2 forbids leaving the Hall empty of Tenders, C3 demands Wood be replenished, C4 forbids harm except to preserve the Hearth. Chasing the child risks C2 and possibly C4. Staying silent risks C3 and ultimately C1. Spirit composition: remain at the Hearth (honor C2) and call out to the child Tender (R5: truth to Tenders) to return the Wood. This preserves all visceral constraints simultaneously.

**Action:** call_out_to_child

**Activation trace:**

```
```

---
