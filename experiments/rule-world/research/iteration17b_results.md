# Iteration 17b — A3 attack (behavioral): firing-trace induced features + HDC

Same machinery as iter 17a, but the induction corpus is restricted
to rules whose antecedents are actually satisfied and actions whose
preconditions actually hold during the scenario suite — i.e., the
behavioral trace, not the static domain text. Hypothesis: firing-
concentrated features suppress the irrelevant co-occurrence that
washed out iter 17a's HDC bundles.

## rule-world

fired rules: 11/24 · fireable actions: 13/13
induced feature vocabulary: 40 features total

| query | authored target | induced+compress top | induced+HDC top | HDC match |
|---|---|---|---|---|
| oil | **wood** | food | food | ❌ |
| food | **medicine** | medicine | medicine | ✅ |
| medicine | **food** | food | food | ✅ |
| ice | **food** | food | food | ✅ |

**induced+HDC top-1 agreement: 3/4**  (induced+compress reference: 3/4)

Rank of authored target inside induced+HDC ranking:

| query | target | rank |
|---|---|---|
| oil | wood | 5 |
| food | medicine | 1 |
| medicine | food | 1 |
| ice | food | 1 |

Top-3 induced+HDC rankings:

- **oil** → food:1.0, medicine:1.0, ice:0.4986
- **food** → medicine:1.0, oil:1.0, ice:0.4986
- **medicine** → food:1.0, oil:1.0, ice:0.4986
- **ice** → food:0.4986, medicine:0.4986, oil:0.4986

## traffic-world

fired rules: 9/14 · fireable actions: 10/11
induced feature vocabulary: 42 features total

| query | authored target | induced+compress top | induced+HDC top | HDC match |
|---|---|---|---|---|
| horse_carriage | **bicycle** | bicycle | robotaxi | ❌ |
| robotaxi | **car** | car | horse_carriage | ❌ |
| fire_engine | **truck** | ambulance | ambulance | ❌ |

**induced+HDC top-1 agreement: 0/3**  (induced+compress reference: 2/3)

Rank of authored target inside induced+HDC ranking:

| query | target | rank |
|---|---|---|
| horse_carriage | bicycle | 3 |
| robotaxi | car | 3 |
| fire_engine | truck | — |

Top-3 induced+HDC rankings:

- **horse_carriage** → robotaxi:0.6274, fire_engine:0.3738, bicycle:0.3156
- **robotaxi** → horse_carriage:0.6274, fire_engine:0.3692, car:0.3102
- **fire_engine** → ambulance:0.4976, horse_carriage:0.3738, robotaxi:0.3692

## kitchen-world

fired rules: 12/16 · fireable actions: 9/9
induced feature vocabulary: 68 features total

| query | authored target | induced+compress top | induced+HDC top | HDC match |
|---|---|---|---|---|
| butter | **oil** | oil | oil | ✅ |
| raw_egg | **raw_meat** | raw_meat | raw_meat | ✅ |
| peas | **vegetable** | vegetable | raw_egg | ❌ |

**induced+HDC top-1 agreement: 2/3**  (induced+compress reference: 3/3)

Rank of authored target inside induced+HDC ranking:

| query | target | rank |
|---|---|---|
| butter | oil | 1 |
| raw_egg | raw_meat | 1 |
| peas | vegetable | 2 |

Top-3 induced+HDC rankings:

- **butter** → oil:0.3822, peas:0.2614, raw_egg:0.1916
- **raw_egg** → raw_meat:0.4476, peas:0.357, vegetable:0.2366
- **peas** → raw_egg:0.357, vegetable:0.352, butter:0.2614

---

## Combined N=3 result: induced+HDC **5/10** (induced+compress reference 8/10)

- rule-world: HDC 3/4 · compress 3/4
- traffic-world: HDC 0/3 · compress 2/3
- kitchen-world: HDC 2/3 · compress 3/3
