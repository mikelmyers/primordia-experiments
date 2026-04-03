"""
Test 6 — Local Learning Only: Network and Learning Rules

A network of N=500 nodes that learns using only Hebbian, anti-Hebbian,
and homeostatic rules. No loss function, no backpropagation, no optimizer.
"""

import numpy as np


class LocalNetwork:
    """Network with purely local learning rules."""

    def __init__(self, n_nodes=500, input_dim=784, seed=42):
        self.rng = np.random.RandomState(seed)
        self.n_nodes = n_nodes
        self.input_dim = input_dim

        # Input-to-node weights (how input maps to node activations)
        self.W_in = self.rng.randn(n_nodes, input_dim) * 0.01

        # Recurrent weights (node-to-node)
        self.W_rec = self.rng.randn(n_nodes, n_nodes) * 0.01
        np.fill_diagonal(self.W_rec, 0)  # no self-connections

        # Homeostatic thresholds (one per node)
        self.thresholds = np.zeros(n_nodes)

        # Learning rates
        self.eta_hebb = 0.001      # Hebbian learning rate
        self.eta_anti = 0.0005     # Anti-Hebbian learning rate
        self.anti_threshold = 0.5  # Weight threshold for anti-Hebbian
        self.eta_home = 0.01       # Homeostatic learning rate
        self.target_rate = 0.1     # Target mean squared activation

        # State
        self.activations = np.zeros(n_nodes)
        self.step_count = 0

    def forward(self, x):
        """Compute node activations for input x.

        x: (input_dim,) flattened input
        Returns: (n_nodes,) activations
        """
        # Input drive + recurrent drive - threshold
        drive = self.W_in @ x + self.W_rec @ self.activations - self.thresholds
        self.activations = np.tanh(drive)
        return self.activations

    def learn(self, x):
        """Apply all local learning rules after a forward pass.

        x: the input that produced current activations
        """
        a = self.activations  # (n_nodes,)

        # --- Hebbian: strengthen connections between co-active nodes ---
        # ΔW_ij = η_hebb * x_i * x_j
        outer = np.outer(a, a)
        self.W_rec += self.eta_hebb * outer

        # Also update input weights (Hebbian between input and node)
        self.W_in += self.eta_hebb * np.outer(a, x)

        # --- Anti-Hebbian: decorrelate when weights are too strong ---
        # ΔW_ij = -η_anti * x_i * x_j * (W_ij > threshold)
        mask = np.abs(self.W_rec) > self.anti_threshold
        self.W_rec -= self.eta_anti * outer * mask

        # --- Homeostatic: each node adjusts threshold to maintain target rate ---
        # Δθ_i = η_home * (x_i² - target_rate)
        self.thresholds += self.eta_home * (a ** 2 - self.target_rate)

        # --- Synaptic normalization (every 10 steps) ---
        self.step_count += 1
        if self.step_count % 10 == 0:
            # Normalize recurrent weights per node (row-wise)
            norms = np.linalg.norm(self.W_rec, axis=1, keepdims=True)
            norms = np.maximum(norms, 1e-8)
            self.W_rec /= norms

            # Normalize input weights per node
            norms_in = np.linalg.norm(self.W_in, axis=1, keepdims=True)
            norms_in = np.maximum(norms_in, 1e-8)
            self.W_in /= norms_in

        # No self-connections
        np.fill_diagonal(self.W_rec, 0)

    def get_population_response(self, x):
        """Get activation pattern for a given input without learning."""
        drive = self.W_in @ x + self.W_rec @ self.activations - self.thresholds
        return np.tanh(drive)

    def get_receptive_fields(self):
        """Return input weight matrix — each row is a node's receptive field."""
        return self.W_in.copy()
