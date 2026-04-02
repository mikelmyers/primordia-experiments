"""
Test 3 — Energy Minimization as Motivation
Primordia Systems LLC — Pre-Paradigm Research

An entity with no goals, no objectives, no reward function.
It has only an internal energy it tries to minimize.

Energy = tension + incoherence + novelty_cost

The entity selects from 10 actions on each timestep,
always choosing the action that minimizes its energy.

The question: does energy minimization produce behavior
that looks like motivation? Does it feel like the entity
wants something?
"""

import numpy as np
from scipy.spatial.distance import cosine


class EnergyEntity:
    """
    An entity driven purely by energy minimization.
    No reward. No loss function. No objective.
    Just physics: the system falls downhill.
    """

    def __init__(self, dim=64, seed=42):
        self.dim = dim
        self.rng = np.random.default_rng(seed)

        # State vector
        self.S = self.rng.normal(0, 0.5, dim)

        # Smoothed state (exponential moving average)
        self.S_smooth = self.S.copy()
        self.smooth_alpha = 0.9  # EMA decay

        # History of visited states (for novelty cost)
        self.state_history = [self.S.copy()]
        self.history_max = 500  # Keep last 500 states

        # Cluster centroids of historical states
        self.centroids = [self.S.copy()]
        self.centroid_update_interval = 50
        self.steps_since_centroid_update = 0

        # Action history
        self.action_history = []
        self.energy_history = []
        self.state_snapshots = []

        self.step_count = 0

    # --- Energy functions ---

    def tension(self, S):
        """
        Variance across state dimensions.
        High variance = high tension = the entity is "stretched".
        """
        return float(np.var(S))

    def incoherence(self, S):
        """
        1 - cosine_similarity(S, S_smooth).
        How far the current state has drifted from the running average.
        High incoherence = the entity is "confused" — acting unlike itself.
        """
        norm_s = np.linalg.norm(S)
        norm_smooth = np.linalg.norm(self.S_smooth)
        if norm_s < 1e-10 or norm_smooth < 1e-10:
            return 1.0
        cos_sim = np.dot(S, self.S_smooth) / (norm_s * norm_smooth)
        return float(1.0 - cos_sim)

    def novelty_cost(self, S):
        """
        Distance from nearest visited state.
        High novelty = being somewhere unfamiliar = costs energy.
        This creates a preference for the familiar.
        """
        if not self.centroids:
            return 0.0
        distances = [np.linalg.norm(S - c) for c in self.centroids]
        return float(min(distances))

    def energy(self, S):
        """Total energy. The entity minimizes this."""
        return self.tension(S) + self.incoherence(S) + self.novelty_cost(S)

    def energy_components(self, S):
        """Return individual energy components for logging."""
        return {
            'tension': self.tension(S),
            'incoherence': self.incoherence(S),
            'novelty_cost': self.novelty_cost(S),
            'total': self.energy(S),
        }

    # --- Action space ---
    # Each action is a pure function: S → S'
    # No side effects. The entity just reshapes its own state.

    def action_attend_to_self(self, S):
        """Amplify high-magnitude dimensions."""
        magnitudes = np.abs(S)
        mask = magnitudes > np.median(magnitudes)
        S_new = S.copy()
        S_new[mask] *= 1.2
        return S_new

    def action_suppress_noise(self, S):
        """Reduce low-magnitude dimensions toward zero."""
        magnitudes = np.abs(S)
        threshold = np.percentile(magnitudes, 25)
        S_new = S.copy()
        S_new[magnitudes < threshold] *= 0.3
        return S_new

    def action_integrate(self, S):
        """Average current state with smoothed state."""
        return 0.5 * S + 0.5 * self.S_smooth

    def action_differentiate(self, S):
        """Amplify difference between current and smoothed state."""
        diff = S - self.S_smooth
        return S + 0.3 * diff

    def action_seek_familiar(self, S):
        """Move state toward nearest historical cluster centroid."""
        if not self.centroids:
            return S.copy()
        distances = [np.linalg.norm(S - c) for c in self.centroids]
        nearest = self.centroids[np.argmin(distances)]
        return 0.7 * S + 0.3 * nearest

    def action_explore(self, S):
        """Add structured noise in low-variance dimensions."""
        # Find dimensions with low recent variance
        if len(self.state_history) < 10:
            noise = self.rng.normal(0, 0.1, self.dim)
        else:
            recent = np.array(self.state_history[-10:])
            dim_var = np.var(recent, axis=0)
            noise = self.rng.normal(0, 0.1, self.dim)
            # Scale noise inversely with variance — explore stagnant dimensions
            scale = 1.0 / (dim_var + 0.01)
            scale = scale / np.max(scale)  # normalize
            noise *= scale
        return S + noise

    def action_consolidate(self, S):
        """Reduce dimensionality by merging correlated dimensions."""
        S_new = S.copy()
        # Find pairs of highly correlated dimensions and average them
        if len(self.state_history) >= 10:
            recent = np.array(self.state_history[-10:])
            # Simple: merge adjacent dimensions that have similar values
            for i in range(0, self.dim - 1, 2):
                if abs(S[i] - S[i+1]) < 0.5:
                    avg = (S[i] + S[i+1]) / 2
                    S_new[i] = avg
                    S_new[i+1] = avg
        return S_new

    def action_expand(self, S):
        """Increase variance by splitting high-variance dimensions."""
        S_new = S.copy()
        magnitudes = np.abs(S)
        high_var = magnitudes > np.percentile(magnitudes, 75)
        perturbation = self.rng.normal(0, 0.2, self.dim)
        S_new[high_var] += perturbation[high_var]
        return S_new

    def action_rest(self, S):
        """Minimal update — let decay dominate."""
        return 0.98 * S

    def action_reset_partial(self, S):
        """Zero out bottom 10% magnitude dimensions."""
        S_new = S.copy()
        magnitudes = np.abs(S)
        threshold = np.percentile(magnitudes, 10)
        S_new[magnitudes < threshold] = 0.0
        return S_new

    def get_actions(self):
        """Return dict of action name → action function."""
        return {
            'attend_to_self': self.action_attend_to_self,
            'suppress_noise': self.action_suppress_noise,
            'integrate': self.action_integrate,
            'differentiate': self.action_differentiate,
            'seek_familiar': self.action_seek_familiar,
            'explore': self.action_explore,
            'consolidate': self.action_consolidate,
            'expand': self.action_expand,
            'rest': self.action_rest,
            'reset_partial': self.action_reset_partial,
        }

    # --- Step ---

    def step(self):
        """
        One timestep:
        1. Compute energy for each possible action (simulate ahead)
        2. Select action that minimizes energy
        3. Apply action
        4. Update smoothed state and history
        """
        actions = self.get_actions()

        # Simulate each action and compute resulting energy
        action_energies = {}
        for name, action_fn in actions.items():
            S_candidate = action_fn(self.S)
            action_energies[name] = self.energy(S_candidate)

        # Select the action that minimizes energy
        best_action = min(action_energies, key=action_energies.get)
        best_energy = action_energies[best_action]

        # Apply the chosen action
        self.S = actions[best_action](self.S)

        # Update smoothed state (EMA)
        self.S_smooth = self.smooth_alpha * self.S_smooth + \
                        (1 - self.smooth_alpha) * self.S

        # Update history
        self.state_history.append(self.S.copy())
        if len(self.state_history) > self.history_max:
            self.state_history.pop(0)

        # Update centroids periodically
        self.steps_since_centroid_update += 1
        if self.steps_since_centroid_update >= self.centroid_update_interval:
            self._update_centroids()
            self.steps_since_centroid_update = 0

        # Log
        components = self.energy_components(self.S)
        entry = {
            'step': self.step_count,
            'action': best_action,
            'energy': components,
            'all_action_energies': action_energies,
            'state_norm': float(np.linalg.norm(self.S)),
        }
        self.action_history.append(entry)
        self.energy_history.append(components['total'])
        self.state_snapshots.append(self.S.copy())

        self.step_count += 1
        return entry

    def perturb(self, scale=2.0):
        """
        Inject a random perturbation to disturb equilibrium.
        This is an external shock — the entity didn't choose this.
        """
        perturbation = self.rng.normal(0, scale, self.dim)
        self.S += perturbation
        return float(np.linalg.norm(perturbation))

    def _update_centroids(self, n_centroids=10):
        """Update cluster centroids from recent history using k-means-like update."""
        if len(self.state_history) < n_centroids:
            self.centroids = [s.copy() for s in self.state_history]
            return

        # Simple k-means-like: pick n_centroids evenly spaced from history
        indices = np.linspace(0, len(self.state_history) - 1,
                             n_centroids, dtype=int)
        self.centroids = [self.state_history[i].copy() for i in indices]
