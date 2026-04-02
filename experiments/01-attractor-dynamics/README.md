# Test 1 — Single Attractor Dynamics

## What We Built

A continuous dynamical system governed by:

```
dX/dt = -∇V(X) + W·f(X) + noise
```

- **State**: 64-dimensional vector X
- **Potential**: Double-well V(x_i) = -x_i² + 0.25·x_i⁴ (wells at ±√2 ≈ ±1.414)
- **Coupling**: Random weight matrix W (scale 0.05), applied through tanh nonlinearity
- **Noise**: Gaussian, scale 0.02
- **Integration**: RK45 via scipy.integrate.solve_ivp, 10,000 timesteps over t=[0, 100]

No objectives. No targets. One equation, one state, let it run.

## What Happened

**The system crystallized.** Within ~10 time units, all 64 dimensions snapped to one of the two well positions (±1.414) and stayed there permanently. The entire 64-dimensional dynamics collapsed to an effective dimensionality of **2** (by PCA). One single attractor basin was found, persisting for 96.3 of the 100 time units.

Key numbers:
- **Distinct basins**: 1
- **Basin transitions**: 0
- **Effective dimensionality**: 2 (for 99% variance explained)
- **Final state norm**: 11.47 (consistent with all dims at well positions: √(64 × 2) ≈ 11.31)
- **PCA component 1**: 94.9% of variance (the initial transient from origin to well)
- **PCA component 2**: 4.3% of variance

## What This Means

The double-well potential is too strong relative to the coupling and noise. Each dimension independently falls into its nearest well and the recurrent weights (W at scale 0.05) cannot create enough force to push any dimension over the potential barrier (height ~1.0 at the origin). The noise (0.02) is also orders of magnitude too small.

**This is not a failure — it's an informative null result.** It tells us:

1. **Potentials dominate coupling at this parameter regime.** For spontaneous mode-switching, the recurrent dynamics need to be competitive with the potential gradient. W needs to be stronger, or the potential needs to be shallower.

2. **The system found stability too easily.** Real cognitive dynamics should live in a regime where stability is present but fragile — not crystalline.

3. **64 independent double-wells are boring.** Without strong coupling, each dimension is essentially an independent bistable switch. The interesting dynamics require dimensions to influence each other.

4. **The fast collapse is itself informative.** The transient before crystallization (~10 time units) is the only period with non-trivial dynamics. A cognitive system should live in the transient, not rush past it.

## What Would Be Different

To get richer dynamics (multiple basins, transitions, sustained activity), the system would need:
- Stronger coupling: W scale ~0.5-1.0 (10-20x current)
- Shallower wells: lower potential barrier
- Stronger noise: scale ~0.1-0.5
- Or a qualitatively different potential landscape (not separable per-dimension)

## Files

- `attractor_dynamics.py` — system dynamics, integration, basin analysis
- `visualize.py` — trajectory plots, phase portrait, PCA spectrum
- `results.json` — all quantitative measurements
- `trajectory.png` — X₀, X₁, X₂ over time (shows fast lock-in)
- `phase_portrait.png` — PCA 2D projection and dwell density
- `velocity_basins.png` — velocity profile showing single-basin dominance
- `basin_stats.png` — basin dwell statistics
- `pca_spectrum.png` — effective dimensionality analysis
