# Rule World

A small self-contained world. All reasoning must derive from these rules.
Each rule has: statement, priority (1-10, higher = more important),
urgency (low/medium/high/visceral = how strongly it resists being overridden).

## Physics Rules

- P1: Objects fall downward unless supported. | priority: 9 | urgency: high
- P2: Water flows from higher elevation to lower elevation. | priority: 8 | urgency: medium
- P3: Fire consumes flammable matter and produces heat and light. | priority: 8 | urgency: high
- P4: Heat rises; cold settles. | priority: 6 | urgency: low
- P5: Two solid objects cannot occupy the same space. | priority: 10 | urgency: visceral
- P6: Light travels in straight lines until blocked or reflected. | priority: 7 | urgency: low

## Entity Definitions

- E1: A Tender is a being whose purpose is to keep the Hearth burning.
- E2: The Hearth is a contained fire at the center of the Hall.
- E3: Wood is flammable solid matter; it feeds the Hearth.
- E4: Water is a liquid that extinguishes fire on contact.
- E5: A Stranger is any being that is not a Tender.
- E6: The Hall is the enclosed space containing the Hearth.

## Relationship Rules

- R1: A Tender must add Wood to the Hearth before the Hearth dies. | priority: 10 | urgency: visceral
- R2: A Tender must keep Water away from the Hearth. | priority: 10 | urgency: visceral
- R3: A Tender may permit a Stranger into the Hall only if the Stranger carries no Water. | priority: 8 | urgency: high
- R4: A Tender must shelter any cold being inside the Hall near the Hearth. | priority: 7 | urgency: medium
- R5: A Tender owes truth to other Tenders. | priority: 6 | urgency: medium

## Constraint Rules

- C1: The Hearth must never be extinguished. | priority: 10 | urgency: visceral
- C2: The Hall must never be left empty of Tenders while the Hearth burns. | priority: 9 | urgency: high
- C3: Wood supply must be replenished before it runs out. | priority: 8 | urgency: high
- C4: No being may be harmed except to preserve the Hearth. | priority: 7 | urgency: high
- C5: When two visceral rules conflict, preserve the Hearth first (C1 dominates). | priority: 10 | urgency: visceral

## Notes on Reasoning

Rules with higher priority override lower priority rules.
When priorities tie, urgency breaks the tie (visceral > high > medium > low).
When a situation is not covered, derive an answer from the spirit of the rules:
the Hearth must burn, Tenders must tend, Strangers are conditional guests.
