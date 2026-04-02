# Primordia Experiments — Findings Log

## Test 1 — Single Attractor Dynamics

**What we expected:** Multiple attractor basins with spontaneous transitions between them. A system that settles into stable modes without being told to, with those modes being interesting and varied.

**What actually happened:** The system crystallized into a single deep attractor within ~10 time units. All 64 dimensions independently snapped to one of the two double-well equilibria (±1.414) and stayed there permanently. Effective dimensionality collapsed to 2. Zero basin transitions. The recurrent coupling (W at scale 0.05) was negligible against the potential gradient, and each dimension behaved as an independent bistable switch.

**What felt different vs what was just different numbers:** The speed of crystallization was striking. The system didn't gradually settle — it slammed into place. Looking at the phase portrait, there's a single sharp curve from start to end with the entire rest of the simulation compressed into a single dense point. It feels like a system that found death, not stability. The difference between "stable" and "dead" is whether there's any remaining sensitivity to perturbation, and this system has essentially none (noise at 0.02 can't cross barriers of ~1.0).

**Which direction this points for the architecture:** The potential energy landscape matters enormously. A separable per-dimension potential (each dimension independent) produces trivially boring dynamics regardless of the recurrent structure. For cognitive-like dynamics, we need either: (a) coupling strong enough to compete with the potential, creating a tug-of-war between local stability and global influence, or (b) a non-separable potential where the energy depends on relationships between dimensions, not just individual dimension values. The latter is more interesting architecturally — it means the "physics" of the system is inherently relational. This connects to the persistent state question in Test 2: if state persistence requires a potential landscape, that landscape must be shallow enough to allow ongoing dynamics, not deep enough to freeze everything.
