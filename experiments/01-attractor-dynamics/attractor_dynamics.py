"""
Test 1 — Single Attractor Dynamics
Primordia Systems LLC — Pre-Paradigm Research

A continuous dynamical system governed by:
    dX/dt = -∇V(X) + W·f(X) + noise

Core question: Does the system spontaneously settle into stable modes
without being told to? Do those modes persist? Are they interesting?

No objectives. No targets. One equation, one state, let it run.
"""

import numpy as np
from scipy.integrate import solve_ivp
import json
import time


class AttractorDynamics:
    """
    Continuous dynamical system with:
    - Double-well potential extended to N dimensions
    - Learned recurrent weights
    - Nonlinear activation (tanh)
    - Stochastic perturbation
    """

    def __init__(self, N=64, seed=42):
        self.N = N
        self.rng = np.random.default_rng(seed)

        # Weight matrix — small random initialization
        # This is the "learned" structure that shapes the dynamics
        self.W = self.rng.normal(0, 0.05, (N, N))
        # Make it slightly asymmetric to allow richer dynamics
        self.W = (self.W + self.W.T) / 2 + self.rng.normal(0, 0.01, (N, N))

        # Double-well potential parameters
        # V(x_i) = -a*x_i^2 + b*x_i^4 for each dimension
        # This creates two wells at x = ±sqrt(a/2b)
        self.a = 1.0
        self.b = 0.25  # wells at ±sqrt(2) ≈ ±1.414

        # Noise scale
        self.noise_scale = 0.02

        # Initial state — near origin, slightly perturbed
        self.X0 = self.rng.normal(0, 0.1, N)

    def potential_gradient(self, X):
        """
        Gradient of the double-well potential V(X) = sum_i(-a*x_i^2 + b*x_i^4)
        ∇V = -2a*X + 4b*X^3
        """
        return -2 * self.a * X + 4 * self.b * X**3

    def dynamics(self, t, X):
        """
        dX/dt = -∇V(X) + W·f(X) + noise

        The potential pulls toward wells.
        The recurrent term couples dimensions.
        Noise prevents freezing.
        """
        grad_V = self.potential_gradient(X)
        recurrent = self.W @ np.tanh(X)
        noise = self.rng.normal(0, self.noise_scale, self.N)

        dXdt = -grad_V + recurrent + noise
        return dXdt

    def run(self, t_span=(0, 100), n_eval=10000):
        """
        Integrate the system using solve_ivp.
        t_span: integration time range
        n_eval: number of evaluation points
        """
        t_eval = np.linspace(t_span[0], t_span[1], n_eval)

        print(f"Integrating system: N={self.N}, t=[{t_span[0]}, {t_span[1]}], "
              f"n_eval={n_eval}")
        print(f"Initial state norm: {np.linalg.norm(self.X0):.4f}")

        start_time = time.time()

        sol = solve_ivp(
            self.dynamics,
            t_span,
            self.X0,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-6,
            atol=1e-8,
            max_step=0.1  # prevent large jumps that skip dynamics
        )

        elapsed = time.time() - start_time
        print(f"Integration completed in {elapsed:.2f}s")
        print(f"  Status: {'success' if sol.success else 'FAILED'}")
        print(f"  Message: {sol.message}")
        print(f"  Solution shape: {sol.y.shape}")

        return sol


class BasinAnalyzer:
    """
    Analyzes attractor basins from trajectory data.

    A basin is defined as a region where velocity drops below threshold
    (the system is "settled"). Basin transitions occur when the system
    leaves one low-velocity region and enters another.
    """

    def __init__(self, velocity_threshold=0.5, min_dwell_time=0.5):
        """
        velocity_threshold: below this, the system is considered "in a basin"
        min_dwell_time: minimum time in a low-velocity region to count as a basin visit
        """
        self.velocity_threshold = velocity_threshold
        self.min_dwell_time = min_dwell_time

    def compute_velocities(self, sol):
        """Compute velocity magnitude at each timepoint."""
        # Numerical derivative of trajectory
        dt = np.diff(sol.t)
        dX = np.diff(sol.y, axis=1)
        velocities = np.linalg.norm(dX / dt[np.newaxis, :], axis=0)
        # Pad to match length
        velocities = np.append(velocities, velocities[-1])
        return velocities

    def find_basins(self, sol):
        """
        Identify distinct attractor basins and transitions between them.

        Returns:
            basins: list of basin dicts with centroid, entry/exit times
            transitions: list of transition events
        """
        velocities = self.compute_velocities(sol)
        t = sol.t
        X = sol.y.T  # (n_time, N)

        # Find low-velocity segments
        in_basin = velocities < self.velocity_threshold

        basins = []
        transitions = []
        current_basin_start = None
        current_basin_states = []

        for i in range(len(t)):
            if in_basin[i]:
                if current_basin_start is None:
                    current_basin_start = i
                    current_basin_states = []
                current_basin_states.append(X[i])
            else:
                if current_basin_start is not None:
                    dwell = t[i-1] - t[current_basin_start]
                    if dwell >= self.min_dwell_time:
                        centroid = np.mean(current_basin_states, axis=0)
                        basin_id = self._assign_basin_id(centroid, basins)
                        basin_entry = {
                            'basin_id': basin_id,
                            't_enter': float(t[current_basin_start]),
                            't_exit': float(t[i-1]),
                            'dwell_time': float(dwell),
                            'centroid_norm': float(np.linalg.norm(centroid)),
                            'mean_velocity': float(np.mean(
                                velocities[current_basin_start:i]
                            ))
                        }
                        basins.append(basin_entry)

                        if len(basins) > 1:
                            transitions.append({
                                'timestamp': float(t[current_basin_start]),
                                'from_basin': basins[-2]['basin_id'],
                                'to_basin': basin_id,
                                'transit_time': float(
                                    t[current_basin_start] - basins[-2]['t_exit']
                                )
                            })

                    current_basin_start = None
                    current_basin_states = []

        # Handle case where trajectory ends in a basin
        if current_basin_start is not None:
            dwell = t[-1] - t[current_basin_start]
            if dwell >= self.min_dwell_time:
                centroid = np.mean(current_basin_states, axis=0)
                basin_id = self._assign_basin_id(centroid, basins)
                basins.append({
                    'basin_id': basin_id,
                    't_enter': float(t[current_basin_start]),
                    't_exit': float(t[-1]),
                    'dwell_time': float(dwell),
                    'centroid_norm': float(np.linalg.norm(centroid)),
                    'mean_velocity': float(np.mean(
                        velocities[current_basin_start:]
                    ))
                })
                if len(basins) > 1:
                    transitions.append({
                        'timestamp': float(t[current_basin_start]),
                        'from_basin': basins[-2]['basin_id'],
                        'to_basin': basin_id,
                        'transit_time': float(
                            t[current_basin_start] - basins[-2]['t_exit']
                        )
                    })

        return basins, transitions

    def _assign_basin_id(self, centroid, existing_basins, merge_radius=2.0):
        """
        Assign a basin ID. If the centroid is close to an existing basin's
        centroid, reuse that ID. Otherwise assign a new one.
        """
        existing_ids = set()
        for b in existing_basins:
            existing_ids.add(b['basin_id'])

        for b in existing_basins:
            if 'centroid' in b:
                dist = np.linalg.norm(centroid - b['centroid'])
                if dist < merge_radius:
                    return b['basin_id']

        # New basin
        return len(existing_ids)

    def compute_stats(self, basins, transitions):
        """Compute summary statistics."""
        if not basins:
            return {
                'n_distinct_basins': 0,
                'n_basin_visits': 0,
                'n_transitions': 0,
                'avg_dwell_time': 0,
                'time_in_basin_stats': {}
            }

        basin_ids = [b['basin_id'] for b in basins]
        unique_basins = set(basin_ids)

        # Time spent in each basin
        time_per_basin = {}
        for b in basins:
            bid = b['basin_id']
            if bid not in time_per_basin:
                time_per_basin[bid] = []
            time_per_basin[bid].append(b['dwell_time'])

        time_stats = {}
        for bid, times in time_per_basin.items():
            time_stats[str(bid)] = {
                'visits': len(times),
                'total_time': float(sum(times)),
                'avg_time': float(np.mean(times)),
                'max_time': float(max(times)),
                'min_time': float(min(times))
            }

        dwell_times = [b['dwell_time'] for b in basins]

        return {
            'n_distinct_basins': len(unique_basins),
            'n_basin_visits': len(basins),
            'n_transitions': len(transitions),
            'avg_dwell_time': float(np.mean(dwell_times)),
            'median_dwell_time': float(np.median(dwell_times)),
            'max_dwell_time': float(max(dwell_times)),
            'time_in_basin_stats': time_stats
        }


def run_experiment(N=64, t_end=100, n_eval=10000, seed=42):
    """Run the full experiment and return all data."""

    # Create and run system
    system = AttractorDynamics(N=N, seed=seed)
    sol = system.run(t_span=(0, t_end), n_eval=n_eval)

    if not sol.success:
        print("WARNING: Integration failed!")
        return None

    # Analyze basins
    analyzer = BasinAnalyzer(velocity_threshold=0.5, min_dwell_time=0.5)
    basins, transitions = analyzer.find_basins(sol)
    stats = analyzer.compute_stats(basins, transitions)

    print(f"\n=== Basin Analysis ===")
    print(f"  Distinct basins found: {stats['n_distinct_basins']}")
    print(f"  Total basin visits: {stats['n_basin_visits']}")
    print(f"  Transitions: {stats['n_transitions']}")
    print(f"  Avg dwell time: {stats['avg_dwell_time']:.3f}")

    # Log transitions
    print(f"\n=== Basin Transitions ===")
    for tr in transitions:
        print(f"  t={tr['timestamp']:.2f}: basin {tr['from_basin']} → "
              f"basin {tr['to_basin']} (transit={tr['transit_time']:.3f})")

    # Save results
    results = {
        'parameters': {
            'N': N,
            't_end': t_end,
            'n_eval': n_eval,
            'seed': seed,
            'potential': 'double-well (a=1.0, b=0.25)',
            'noise_scale': system.noise_scale,
            'weight_init': 'normal(0, 0.05) symmetrized + normal(0, 0.01)'
        },
        'basin_analysis': stats,
        'transitions': transitions,
        'trajectory_stats': {
            'final_state_norm': float(np.linalg.norm(sol.y[:, -1])),
            'initial_state_norm': float(np.linalg.norm(sol.y[:, 0])),
            'max_state_norm': float(np.max(np.linalg.norm(sol.y, axis=0))),
            'mean_state_norm': float(np.mean(np.linalg.norm(sol.y, axis=0))),
        }
    }

    results_path = 'experiments/01-attractor-dynamics/results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    return sol, basins, transitions, stats, system


if __name__ == '__main__':
    result = run_experiment()
    if result is not None:
        sol, basins, transitions, stats, system = result
        print("\nExperiment complete. Run visualize.py to generate plots.")
