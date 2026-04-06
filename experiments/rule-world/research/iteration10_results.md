# Iteration 10 — Crystallization → induction loop closure

Tests whether feeding v4-crystallized rules back into the structural inducer closes iteration 9's corpus-coverage failures, and whether any closure is genuine signal transfer or laundering of the original v4 analogy.

**Variants:** A=authored rules only (i9 baseline) · B=authored + all crystallized · C=authored + crystallized minus rules mentioning the query substance (held-out honesty check) · D=full loop with IDF weighting (rare/discriminating features count more).

## rule-world

Crystallized rules in store: 9

Top-1 agreement table:

| query | authored target | A baseline | B full loop | C held-out | D loop+IDF |
|---|---|---|---|---|---|
| oil | **wood** | food ❌ | food ❌ | food ❌ | food ❌ |
| food | **medicine** | medicine ✅ | medicine ✅ | medicine ✅ | medicine ✅ |
| medicine | **food** | food ✅ | food ✅ | food ✅ | food ✅ |
| ice | **(none)** | food ❌ | food ❌ | food ❌ | food ❌ |

**Top-1 agreement:** A=2/3 · B=2/3 · C=2/3 · D=2/3

Rank of the authored target inside each variant's full ranking (lower is better; — = not in ranking):

| query | target | A | B | C | D |
|---|---|---|---|---|---|
| oil | wood | 5 | 5 | 5 | 3 |
| food | medicine | 1 | 1 | 1 | 1 |
| medicine | food | 1 | 1 | 1 | 1 |

Full top-3 rankings:

| query | A baseline | B full loop | C held-out | D loop+IDF |
|---|---|---|---|---|
| oil | food:3, medicine:3, ice:2 | food:7, medicine:7, ice:6 | food:3, medicine:3, ice:2 (-3) | food:1.35, medicine:1.35, wood:1.25 |
| food | medicine:3, oil:3, ice:2 | medicine:7, oil:7, ice:6 | medicine:3, oil:3, ice:2 (-2) | medicine:1.35, oil:1.35, ice:1.1 |
| medicine | food:3, oil:3, ice:2 | food:7, oil:7, ice:6 | food:3, oil:3, ice:2 (-2) | food:1.35, oil:1.35, ice:1.1 |
| ice | food:2, medicine:2, oil:2 | food:6, medicine:6, oil:6 | food:2, medicine:2, oil:2 (-2) | food:1.1, medicine:1.1, oil:1.1 |

## traffic-world

Crystallized rules in store: 2

Top-1 agreement table:

| query | authored target | A baseline | B full loop | C held-out | D loop+IDF |
|---|---|---|---|---|---|
| horse_carriage | **bicycle** | bicycle ✅ | bicycle ✅ | bicycle ✅ | bicycle ✅ |
| robotaxi | **car** | car ✅ | car ✅ | car ✅ | car ✅ |
| fire_engine | **truck** | ambulance ❌ | ambulance ❌ | ambulance ❌ | ambulance ❌ |

**Top-1 agreement:** A=2/3 · B=2/3 · C=2/3 · D=2/3

Rank of the authored target inside each variant's full ranking (lower is better; — = not in ranking):

| query | target | A | B | C | D |
|---|---|---|---|---|---|
| horse_carriage | bicycle | 1 | 1 | 1 | 1 |
| robotaxi | car | 1 | 1 | 1 | 1 |
| fire_engine | truck | — | — | — | — |

Full top-3 rankings:

| query | A baseline | B full loop | C held-out | D loop+IDF |
|---|---|---|---|---|
| horse_carriage | bicycle:3, robotaxi:3, car:2 | bicycle:5, robotaxi:5, car:4 | bicycle:3, robotaxi:3, car:2 (-1) | bicycle:1.319, robotaxi:1.152, car:0.819 |
| robotaxi | car:3, horse_carriage:3, bicycle:2 | car:5, horse_carriage:5, bicycle:4 | car:3, horse_carriage:3, bicycle:2 (-1) | car:1.319, horse_carriage:1.152, bicycle:0.819 |
| fire_engine | ambulance:2, bicycle:1, car:1 | ambulance:2, bicycle:1, car:1 | ambulance:2, bicycle:1, car:1 (-0) | ambulance:0.643, bicycle:0.143, car:0.143 |

---

## Reading

- **B > A**: closing the loop produces signal the baseline lacked.
- **C ≥ A and C close to B**: the closure is real signal transfer — other substances' crystallizations help find the held-out substance's analog.
- **B > C ≈ A**: the closure is laundering. The success comes from the v4 crystallization specifically about that substance, not from transferable structural learning.
