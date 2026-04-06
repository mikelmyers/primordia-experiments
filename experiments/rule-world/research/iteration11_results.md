# Iteration 11 — Filter symmetric syntactic crystallizations

Tests the one-line fix from iteration 10: include only `crystallized_v4` rules in the inducer's corpus, excluding the symmetric `crystallized` rules (R3~X, P-admitted-with-water~X) that add identical features to every novel substance and drown the discriminating signal.

**Variants:** A=baseline (i9) · B=full loop (i10) · E=v4-only loop (i11 fix).

## rule-world

Crystallized rules in store: 9 total, 1 v4-only

| query | target | A baseline | B full loop (i10) | E v4-only loop |
|---|---|---|---|---|
| oil | **wood** | food ❌ | food ❌ | wood ✅ |
| food | **medicine** | medicine ✅ | medicine ✅ | medicine ✅ |
| medicine | **food** | food ✅ | food ✅ | food ✅ |
| ice | **(none)** | food ❌ | food ❌ | food ❌ |

**Top-1 agreement:** A=2/3 · B=2/3 · E=3/3

Rank of authored target (lower is better):

| query | target | A | B | E |
|---|---|---|---|---|
| oil | wood | 5 | 5 | 1 |
| food | medicine | 1 | 1 | 1 |
| medicine | food | 1 | 1 | 1 |

Top-3 rankings under E (v4-only loop):

- **oil** → wood:4, water:3, food:3
- **food** → medicine:3, oil:3, ice:2
- **medicine** → food:3, oil:3, ice:2
- **ice** → food:2, medicine:2, oil:2

## traffic-world

Crystallized rules in store: 2 total, 2 v4-only

| query | target | A baseline | B full loop (i10) | E v4-only loop |
|---|---|---|---|---|
| horse_carriage | **bicycle** | bicycle ✅ | bicycle ✅ | bicycle ✅ |
| robotaxi | **car** | car ✅ | car ✅ | car ✅ |
| fire_engine | **truck** | ambulance ❌ | ambulance ❌ | ambulance ❌ |

**Top-1 agreement:** A=2/3 · B=2/3 · E=2/3

Rank of authored target (lower is better):

| query | target | A | B | E |
|---|---|---|---|---|
| horse_carriage | bicycle | 1 | 1 | 1 |
| robotaxi | car | 1 | 1 | 1 |
| fire_engine | truck | — | — | — |

Top-3 rankings under E (v4-only loop):

- **horse_carriage** → bicycle:5, robotaxi:5, car:4
- **robotaxi** → car:5, horse_carriage:5, bicycle:4
- **fire_engine** → ambulance:2, bicycle:1, car:1
