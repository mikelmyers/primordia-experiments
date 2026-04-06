# Iteration 12 — Third domain transfer + N=3 inducer comparison

Runs the iteration-11 v4-only property inducer on all three domains (rule-world, traffic-world, kitchen-world). Measures whether the ~5/6 top-1 agreement result generalizes to a third unrelated domain.

## rule-world

v4 crystallizations in store: 1

| query | authored target | induced top | match |
|---|---|---|---|
| oil | **wood** | wood | ✅ |
| food | **medicine** | medicine | ✅ |
| medicine | **food** | food | ✅ |
| ice | **(none)** | food | — |

**Top-1 agreement: 3/3**

Rank of authored target inside induced ranking:

| query | target | rank |
|---|---|---|
| oil | wood | 1 |
| food | medicine | 1 |
| medicine | food | 1 |

Top-3 induced rankings:

- **oil** → wood:4, water:3, food:3
- **food** → medicine:3, oil:3, ice:2
- **medicine** → food:3, oil:3, ice:2
- **ice** → food:2, medicine:2, oil:2

## traffic-world

v4 crystallizations in store: 2

| query | authored target | induced top | match |
|---|---|---|---|
| horse_carriage | **bicycle** | bicycle | ✅ |
| robotaxi | **car** | car | ✅ |
| fire_engine | **truck** | ambulance | ❌ |

**Top-1 agreement: 2/3**

Rank of authored target inside induced ranking:

| query | target | rank |
|---|---|---|
| horse_carriage | bicycle | 1 |
| robotaxi | car | 1 |
| fire_engine | truck | — |

Top-3 induced rankings:

- **horse_carriage** → bicycle:5, robotaxi:5, car:4
- **robotaxi** → car:5, horse_carriage:5, bicycle:4
- **fire_engine** → ambulance:2, bicycle:1, car:1

## kitchen-world

v4 crystallizations in store: 3

| query | authored target | induced top | match |
|---|---|---|---|
| butter | **oil** | oil | ✅ |
| raw_egg | **raw_meat** | raw_meat | ✅ |
| peas | **vegetable** | vegetable | ✅ |

**Top-1 agreement: 3/3**

Rank of authored target inside induced ranking:

| query | target | rank |
|---|---|---|
| butter | oil | 1 |
| raw_egg | raw_meat | 1 |
| peas | vegetable | 1 |

Top-3 induced rankings:

- **butter** → oil:4, knife:2, peas:2
- **raw_egg** → raw_meat:4, knife:2, peas:2
- **peas** → vegetable:9, knife:4, raw_meat:4

---

## Combined N=3 result: **8/9** top-1 agreement (rule-world 3/3 · traffic-world 2/3 · kitchen-world 3/3)
