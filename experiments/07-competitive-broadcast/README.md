# Test 7 — Competitive Global Broadcast

## What We Built

A Global Workspace Theory implementation with 6 specialist modules (perceptual, semantic, temporal, affective, motor, metacognitive) competing for access to a 256-dim broadcast buffer. Three competition modes tested:
- **Hard** (τ=0.1): near winner-take-all, minimum 3-step hold time
- **Medium** (τ=1.0): softer competition, losers partially active
- **Soft**: uniform weighted average (standard attention baseline)

## What Happened

The most nuanced results so far — hard competition genuinely behaves differently from soft integration.

### Coherence
- **Hard: 0.31-0.44** — higher coherence, especially during conflict (0.44)
- **Medium: 0.29-0.32** — moderate
- **Soft: 0.29-0.32** — lowest, near-identical to medium

Hard competition produces more coherent workspace states because one module dominates completely, giving the workspace a consistent character.

### Switching Rate
- **Hard: 0.025-0.18** — very low switching (hold_time forces stability)
- **Medium: 0.035-0.80** — dramatically higher switching, especially in conflict (0.80!)
- **Soft: 0.000** — zero switching by definition (no winner)

Medium competition switches frantically during conflict — a committee that can't decide. Hard competition picks a winner and sticks.

### Unity Metric (workspace variance — lower = more unified)
- **Hard: 0.059-0.108** — highest variance (least unified, most expressive)
- **Medium: 0.009-0.013** — moderate
- **Soft: 0.004-0.007** — lowest variance (most unified but most bland)

Hard competition makes the workspace more expressive (higher variance) because one module imprints strongly. Soft averaging smooths everything into a low-variance mush.

### Conflict Resolution
- **Hard: 34%** — paradoxically worse at picking the stronger input
- **Medium: 74%** — much better at resolving to the stronger signal

The hold_time mechanism in hard mode is the culprit: once a module wins, it holds for 3 steps regardless of what happens next. The "wrong" winner from a previous conflict persists into the next one.

## What This Means

**Hard competition feels qualitatively different.** It's not just different numbers — the system has a different character:
- Hard = decisive but stubborn, coherent but sometimes wrong, expressive but noisy
- Soft = indecisive but fair, incoherent but smooth, unified but bland
- Medium = the worst of both worlds in conflict (frantically switching) but reasonable in calm conditions

The GWT claim is that consciousness requires hard competition — one thing at a time. These results partially support that: hard competition produces something that feels more like "one perspective" (high coherence, low switching), while soft averaging feels like "everything at once" (low variance, no decisions). But hard competition's poor conflict resolution shows that unity has a cost: the system sometimes commits to the wrong answer and can't course-correct.

**For the architecture:** The hold_time parameter is critical. Too long and the system is dogmatic. Too short and you lose the benefits of commitment. Biological consciousness likely modulates this — sometimes you need to persist with an interpretation (sustained attention), sometimes you need to switch rapidly (stimulus-driven reorientation). This suggests the hold_time should be dynamic, not fixed.

## Files

- `workspace.py` — global workspace and competition mechanism
- `simulate.py` — test suite with multimodal, conflict, and sustained tests
- `visualize.py` — coherence, switching, and comparison plots
- `results.json` — all metrics across three modes
