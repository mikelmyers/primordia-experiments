# Iteration 17a — A3 attack (structural): induced features + HDC

Replaces the hand-authored `SUBSTANCE_PROPERTIES`, `PROPERTY_ROLES`,
and `active_roles_for_scenario` inputs to the live HDC role-weighted
analog path with the iteration-9 structurally-induced equivalents.
The HDC codebook itself is unchanged (seed=42, same as live v4). The
authored-table + HDC path is used only as the oracle target.

Measures the same 10 adversarial queries iteration 12 used, on the
same N=3 domains. Reports induced+HDC top-1 agreement (the A3 test)
alongside induced+CompressionAnalog (iter 12's 89% reference).

## rule-world

v4 crystallizations folded into induction: 1
induced feature vocabulary: 45 features total

| query | authored target | induced+compress top | induced+HDC top | HDC match |
|---|---|---|---|---|
| oil | **wood** | wood | food | ❌ |
| food | **medicine** | medicine | medicine | ✅ |
| medicine | **food** | food | food | ✅ |
| ice | **food** | food | food | ✅ |

**induced+HDC top-1 agreement: 3/4**  (induced+compress reference: 4/4)

Rank of authored target inside induced+HDC ranking:

| query | target | rank |
|---|---|---|
| oil | wood | 5 |
| food | medicine | 1 |
| medicine | food | 1 |
| ice | food | 1 |

Top-3 induced+HDC rankings:

- **oil** → food:0.6296, medicine:0.6296, ice:0.395
- **food** → medicine:1.0, oil:0.6296, ice:0.507
- **medicine** → food:1.0, oil:0.6296, ice:0.507
- **ice** → food:0.507, medicine:0.507, oil:0.395

## traffic-world

v4 crystallizations folded into induction: 2
induced feature vocabulary: 48 features total

| query | authored target | induced+compress top | induced+HDC top | HDC match |
|---|---|---|---|---|
| horse_carriage | **bicycle** | bicycle | robotaxi | ❌ |
| robotaxi | **car** | car | horse_carriage | ❌ |
| fire_engine | **ambulance** | ambulance | ambulance | ✅ |

**induced+HDC top-1 agreement: 1/3**  (induced+compress reference: 3/3)

Rank of authored target inside induced+HDC ranking:

| query | target | rank |
|---|---|---|
| horse_carriage | bicycle | 2 |
| robotaxi | car | 2 |
| fire_engine | ambulance | 1 |

Top-3 induced+HDC rankings:

- **horse_carriage** → robotaxi:0.6904, bicycle:0.4466, car:0.3374
- **robotaxi** → horse_carriage:0.6904, car:0.4498, bicycle:0.3658
- **fire_engine** → ambulance:0.4944, horse_carriage:0.3052, robotaxi:0.2992

## kitchen-world

v4 crystallizations folded into induction: 3
induced feature vocabulary: 85 features total

| query | authored target | induced+compress top | induced+HDC top | HDC match |
|---|---|---|---|---|
| butter | **oil** | oil | oil | ✅ |
| raw_egg | **raw_meat** | raw_meat | raw_meat | ✅ |
| peas | **vegetable** | vegetable | vegetable | ✅ |

**induced+HDC top-1 agreement: 3/3**  (induced+compress reference: 3/3)

Rank of authored target inside induced+HDC ranking:

| query | target | rank |
|---|---|---|
| butter | oil | 1 |
| raw_egg | raw_meat | 1 |
| peas | vegetable | 1 |

Top-3 induced+HDC rankings:

- **butter** → oil:0.5176, raw_egg:0.2844, water:0.2734
- **raw_egg** → raw_meat:0.4388, butter:0.2844, peas:0.208
- **peas** → vegetable:0.5916, raw_meat:0.2512, raw_egg:0.208

---

## Combined N=3 result: induced+HDC **7/10** (induced+compress reference 10/10)

- rule-world: HDC 3/4 · compress 4/4
- traffic-world: HDC 1/3 · compress 3/3
- kitchen-world: HDC 3/3 · compress 3/3
