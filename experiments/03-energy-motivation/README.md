# Test 3 — Energy Minimization as Motivation

## What We Built

An entity with no goals, no objectives, no reward function. Only an internal energy:

```
E(S) = tension(S) + incoherence(S) + novelty_cost(S)
```

- **Tension**: variance across state dimensions (high variance = high tension)
- **Incoherence**: 1 - cosine_similarity(S, S_smooth) (drift from running average)
- **Novelty cost**: distance from nearest visited state (unfamiliarity costs energy)

10 available actions. On each timestep, the entity simulates all 10, picks the one that minimizes energy. 5000 timesteps with perturbations every 200 steps.

## What Happened

**The entity became a homing pigeon.** `seek_familiar` was chosen 93.6% of the time. Only 3 of 10 actions were ever selected (seek_familiar, differentiate at 4.9%, integrate at 1.5%). The entity found its low-energy home immediately and spent its entire existence returning there after each perturbation.

Key numbers:
- **Dominant action**: seek_familiar (93.6%)
- **Actions never used**: attend_to_self, suppress_noise, explore, consolidate, expand, rest, reset_partial (0%)
- **Recovery**: 24/24 perturbations recovered, mean 14.7 steps, median 15.0 steps
- **Energy baseline**: ~0.156 (remarkably stable)
- **Energy after perturbation**: spikes to ~20, returns to 0.156 within ~15 steps
- **Behavioral sequences**: just seek_familiar repeated — not real proto-habits

## Why This Happened

The novelty_cost term dominates the energy landscape. It penalizes being far from visited states. `seek_familiar` directly minimizes this by moving toward the nearest historical centroid. The other actions either increase novelty_cost (explore, expand, differentiate) or are suboptimal at reducing it (rest, suppress_noise, attend_to_self).

The energy minimization is *too effective*. The entity finds the global minimum of its energy function almost immediately and then has no reason to do anything else. It's not developing preferences — it's solving a trivial optimization.

The perturbation-recovery pattern is perfectly regular: spike → ~15 steps of seek_familiar → baseline. No adaptation, no learning, no change in strategy. The 24th recovery looks identical to the 1st.

## What This Means

1. **Energy minimization alone produces trivial behavior.** When the energy landscape has a clear global minimum and one action is the direct path to it, you get a degenerate solution. The entity doesn't "want" something — it's a ball rolling downhill on a smooth surface.

2. **The action space matters enormously.** 7 of 10 actions were never selected because the energy function doesn't create situations where they're optimal. The energy landscape and action space need to be co-designed so that different situations favor different actions.

3. **Novelty cost as formulated is a trap.** It creates an entity that is afraid of the unfamiliar and always retreats. For motivation-like behavior, novelty should have a *non-monotonic* relationship with energy — some novelty should reduce energy (curiosity), while too much novelty increases it (overwhelm).

4. **The recovery result is genuinely interesting.** 100% recovery with consistent ~15-step timescale shows genuine resilience. But it's resilience without adaptation — the entity recovers to exactly the same state every time, learning nothing from repeated perturbations. A more interesting entity would recover differently after being perturbed many times.

5. **Compare to Test 1**: both experiments found systems that collapse to a fixed point. Test 1 crystallized in state space, Test 3 crystallized in behavior space. The common failure mode is that the "physics" is too simple — there's one obvious minimum and the system finds it.

## What Would Be Different

For energy minimization to produce motivation-like behavior:
- **Competing energy terms**: tension and novelty_cost should pull in opposite directions, creating frustration states where no single action is optimal
- **Non-stationary energy**: the energy landscape should shift over time, so the entity can't memorize the minimum
- **Curiosity term**: energy should *increase* when the entity has been in the same state too long (boredom as energy)
- **Action costs**: each action should have its own energy cost, preventing trivial repeated solutions
- **History-dependent energy**: the cost of an action should change based on how recently it was used

## Files

- `energy_entity.py` — energy functions, 10 actions, step logic
- `simulate.py` — 5000-step simulation with perturbation analysis
- `visualize.py` — energy curves, action distribution, recovery, sequences
- `results.json` — all measurements
- `energy_curve.png` — energy over time with perturbation spikes
- `action_distribution.png` — action frequency (dominated by seek_familiar)
- `action_timeline.png` — action preferences over time windows
- `recovery.png` — recovery times after perturbations
- `sequences.png` — recurring action sequences
