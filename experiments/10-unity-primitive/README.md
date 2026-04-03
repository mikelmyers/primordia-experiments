# Test 10 — Unity Primitive (New Math)

## What We Built

A unity vector U ∈ R^256 with 5 orthogonal projection operators (perception, reasoning, affect, action, memory) that partition R^256. Each mode D_k(U) = P_k·U is a perspective on the whole, not a separate part. Σ P_k = I ensures unity is never lost — the sum of all modes exactly reconstitutes U. Salience weights λ_k determine which mode is currently most expressed, learned online via Hebbian rule.

1000 interactions with mode destruction at t=500 (affect mode's projection zeroed out).

## What Happened

### Projection Mathematics: Perfect
- Identity error: 1.6e-14 (machine epsilon)
- Orthogonality error: 4.4e-15
- Idempotency error: 7.1e-15

The mathematical constraints are satisfied to numerical precision. Before destruction, unity is perfectly preserved (error = 0 to 15 decimal places).

### Mode Selectivity: Poor
- **Accuracy: 23%** — barely above random (20% for 5 classes)
- The system rarely expresses the "correct" mode for the input type
- Affect mode dominated pre-destruction (λ_affect = 0.22, highest), regardless of input type

The Hebbian salience rule doesn't create strong mode selectivity because all projections respond somewhat to all inputs (they're random subspaces, not semantically meaningful). The modes are orthogonal but not aligned with the input structure.

### Mode Destruction: The Key Experiment

At t=500, the affect projection was zeroed out.

- **Unity error jumped from 0.0 to 0.46** — unity was immediately broken
- **Error partially recovered to ~0.25** over 100 steps but never healed
- **Perception took over completely** — 100% of affect-type inputs were handled by perception (mode 0)
- **λ redistributed:** affect dropped to 0.01 (minimum), perception rose from 0.21 to 0.29

**The system did NOT reconstitute the lost mode.** Once the projection is zeroed, the subspace is permanently lost from U's expressible repertoire. The remaining modes redistribute salience but don't fill the gap — they can't, because the subspaces are orthogonal by construction. Destroying a mode is like cutting a dimension out of the space.

### U Stability
- **U norm: 1.000000** throughout (normalization ensures this)
- Pre and post-destruction norms are identical to 9 decimal places
- The unity vector itself is perfectly stable — it's the projection that's broken

## What This Means

**Unity-first is mathematically clean but rigidly fragile.** The partition constraint (Σ P_k = I) ensures perfect unity when all modes are present, but it's a brittle unity. Remove one mode and you lose exactly 1/5 of the space with no way to recover it. This is not like losing a capability — it's like losing a dimension. The analogy isn't "a person who can no longer feel emotion" — it's "a person who can no longer represent the part of reality that emotion was tracking."

**Parts-first vs unity-first:** The functional difference is revealing:
- **Parts-first:** destroying a module removes a function but other modules might compensate because they overlap in what they can represent
- **Unity-first:** destroying a projection removes a subspace, and orthogonality guarantees NO other mode can compensate

The orthogonality constraint — which seemed mathematically elegant — is the problem. Biological systems have overlapping representations precisely because overlap provides robustness. Orthogonality provides clean separation but zero redundancy.

**The honest assessment:** Unity-first doesn't feel different from parts-first in this implementation — it feels MORE fragile. The mathematical beauty (Σ P_k = I, perfect reconstruction) is exactly what makes it brittle. A system that truly starts from unity would need non-orthogonal differentiation — modes that overlap, interfere, and can partially compensate for each other. The clean separation we enforced is a parts-in-disguise, not genuine unity.

## Files

- `unity.py` — U object, projection operators, unity update rule
- `simulate.py` — 1000 interactions with mode destruction at t=500
- `verify.py` — continuous unity preservation checking
- `visualize.py` — U trajectory, mode salience, post-destruction analysis
- `results.json` — all measurements including mode destruction analysis
