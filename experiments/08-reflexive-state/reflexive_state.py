"""
Test 8 — Reflexive State: R = Φ(R)

A system where the self-model IS part of the state, not a separate observer.
R = (S, M) where M models S, and both update together via contraction mapping Φ.
"""

import numpy as np


class ReflexiveState:
    """Reflexive state entity: R = (S, M) with fixed-point self-model."""

    def __init__(self, content_dim=64, model_dim=32, seed=42):
        self.rng = np.random.RandomState(seed)
        self.content_dim = content_dim
        self.model_dim = model_dim

        # Content state S and self-model M
        self.S = self.rng.randn(content_dim) * 0.1
        self.M = self.rng.randn(model_dim) * 0.1

        # Weight matrices for content update: S(t+1) = tanh(W_s·S + W_i·input + W_m·M)
        self.W_s = self.rng.randn(content_dim, content_dim) * 0.1
        self.W_i = self.rng.randn(content_dim, content_dim) * 0.1  # input -> content
        self.W_m = self.rng.randn(content_dim, model_dim) * 0.1    # model -> content

        # Weight matrices for self-model update: M(t+1) = tanh(W_g·S + α·M)
        self.W_g = self.rng.randn(model_dim, content_dim) * 0.1
        self.alpha = 0.7  # self-model decay

        # Enforce contraction: constrain spectral radius < 1
        self._enforce_contraction()

        # Fixed-point iteration params
        self.fp_iterations = 5
        self.fp_tolerance = 0.001

    def _enforce_contraction(self):
        """Constrain spectral radius of all weight matrices to be < 1."""
        for W in [self.W_s, self.W_i, self.W_m, self.W_g]:
            sr = np.max(np.abs(np.linalg.eigvals(W[:min(W.shape), :min(W.shape)])))
            if sr > 0.95:
                W *= 0.95 / (sr + 1e-8)

    def encode_input(self, text_or_vector):
        """Encode input to content_dim vector."""
        if isinstance(text_or_vector, str):
            # Simple hash-based encoding
            h = hash(text_or_vector)
            self.rng.seed(abs(h) % (2**31))
            vec = self.rng.randn(self.content_dim)
            vec = vec / (np.linalg.norm(vec) + 1e-8)
            # Restore RNG
            self.rng.seed(None)
            return vec
        return text_or_vector

    def update(self, input_vec):
        """Full reflexive update: content + fixed-point self-model iteration.

        Returns convergence info.
        """
        # Content update: S(t+1) = tanh(W_s·S + W_i·input + W_m·M)
        S_new = np.tanh(self.W_s @ self.S + self.W_i @ input_vec + self.W_m @ self.M)

        # Fixed-point iteration for self-model
        M_k = self.M.copy()
        convergence_history = []

        for k in range(self.fp_iterations):
            M_next = np.tanh(self.W_g @ S_new + self.alpha * M_k)
            delta = np.linalg.norm(M_next - M_k)
            convergence_history.append(float(delta))
            M_k = M_next

            if delta < self.fp_tolerance:
                break

        self.S = S_new
        self.M = M_k

        return {
            "S": self.S.copy(),
            "M": self.M.copy(),
            "convergence_history": convergence_history,
            "converged": convergence_history[-1] < self.fp_tolerance if convergence_history else True,
            "n_iterations": len(convergence_history),
            "final_delta": convergence_history[-1] if convergence_history else 0.0,
        }


class ReflexiveStateNoSelfModel(ReflexiveState):
    """Control: identical system WITHOUT self-model (W_m = 0)."""

    def __init__(self, content_dim=64, model_dim=32, seed=42):
        super().__init__(content_dim, model_dim, seed)
        self.W_m = np.zeros_like(self.W_m)  # disable self-model influence

    def update(self, input_vec):
        """Update without self-model influence."""
        S_new = np.tanh(self.W_s @ self.S + self.W_i @ input_vec)
        M_k = self.M.copy()
        convergence_history = []

        for k in range(self.fp_iterations):
            M_next = np.tanh(self.W_g @ S_new + self.alpha * M_k)
            delta = np.linalg.norm(M_next - M_k)
            convergence_history.append(float(delta))
            M_k = M_next
            if delta < self.fp_tolerance:
                break

        self.S = S_new
        self.M = M_k

        return {
            "S": self.S.copy(),
            "M": self.M.copy(),
            "convergence_history": convergence_history,
            "converged": convergence_history[-1] < self.fp_tolerance if convergence_history else True,
            "n_iterations": len(convergence_history),
            "final_delta": convergence_history[-1] if convergence_history else 0.0,
        }
