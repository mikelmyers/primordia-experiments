"""
Test 10 — Unity Primitive: U ∈ R^N with Orthogonal Projection Operators

Start with U — a unity object — and derive capabilities via differentiation.
Modes are perspectives on the whole, not parts.
"""

import numpy as np


class UnityPrimitive:
    """Unity entity: a single vector U differentiated into modes via orthogonal projections."""

    def __init__(self, dim=256, n_modes=5, seed=42):
        self.rng = np.random.RandomState(seed)
        self.dim = dim
        self.n_modes = n_modes

        # Mode names
        self.mode_names = ["perception", "reasoning", "affect", "action", "memory"]

        # Initialize U as random unit vector
        self.U = self.rng.randn(dim)
        self.U /= np.linalg.norm(self.U)

        # Construct orthogonal projection matrices via Gram-Schmidt
        self.projections = self._make_orthogonal_projections()

        # Verify properties
        self._verify_projections()

        # Mode salience weights λ_k (initially uniform)
        self.lambdas = np.ones(n_modes) / n_modes

        # Hebbian learning rate for salience
        self.eta_lambda = 0.01

        # Input encoding
        self.input_dim = dim
        self.encode_W = self.rng.randn(dim, dim) * 0.1

        # Decode matrices (mode output -> human-readable)
        self.decode_W = [self.rng.randn(dim, 10) * 0.1 for _ in range(n_modes)]

        # History
        self.U_history = []
        self.lambda_history = []

    def _make_orthogonal_projections(self):
        """Construct n_modes orthogonal projection matrices that partition R^dim.

        Uses Gram-Schmidt on random bases. Each P_k projects onto a subspace
        of dimension dim // n_modes.
        """
        subdim = self.dim // self.n_modes
        projections = []

        # Generate random basis vectors and orthogonalize
        all_basis = []
        random_vecs = self.rng.randn(self.dim, self.dim)

        # QR decomposition gives orthonormal basis
        Q, _ = np.linalg.qr(random_vecs)

        for k in range(self.n_modes):
            start = k * subdim
            end = start + subdim if k < self.n_modes - 1 else self.dim
            # Basis vectors for this mode's subspace
            basis = Q[:, start:end]
            # Projection matrix: P_k = basis @ basis.T
            P_k = basis @ basis.T
            projections.append(P_k)
            all_basis.append(basis)

        return projections

    def _verify_projections(self):
        """Verify projection properties: Σ P_k = I, P_i·P_j = 0, P_k² = P_k."""
        # Sum to identity
        P_sum = sum(self.projections)
        identity_error = np.linalg.norm(P_sum - np.eye(self.dim))

        # Orthogonality
        ortho_errors = []
        for i in range(self.n_modes):
            for j in range(i+1, self.n_modes):
                err = np.linalg.norm(self.projections[i] @ self.projections[j])
                ortho_errors.append(err)

        # Idempotency
        idem_errors = []
        for P in self.projections:
            err = np.linalg.norm(P @ P - P)
            idem_errors.append(err)

        self.verification = {
            "identity_error": float(identity_error),
            "max_orthogonality_error": float(max(ortho_errors)),
            "max_idempotency_error": float(max(idem_errors)),
        }

    def differentiate(self, k):
        """Apply mode k's projection: D_k(U) = P_k · U"""
        return self.projections[k] @ self.U

    def check_unity(self):
        """Verify ||Σ_k D_k(U) - U|| < 0.001"""
        reconstructed = sum(self.differentiate(k) for k in range(self.n_modes))
        error = np.linalg.norm(reconstructed - self.U)
        return error

    def encode_input(self, x):
        """Encode input to dim-dimensional vector."""
        if isinstance(x, str):
            h = hash(x)
            rng_temp = np.random.RandomState(abs(h) % (2**31))
            vec = rng_temp.randn(self.dim)
            return vec / (np.linalg.norm(vec) + 1e-8)
        return x

    def update(self, x, eta=0.05):
        """Unity update rule:

        U(t+1) = normalize(U(t) + η·encode(input) + Σ_k λ_k·D_k(U(t)))
        """
        input_vec = self.encode_input(x)

        # Differentiated modes weighted by salience
        mode_contributions = np.zeros(self.dim)
        mode_correlations = []
        for k in range(self.n_modes):
            mode_output = self.differentiate(k)
            mode_contributions += self.lambdas[k] * mode_output
            # Correlation with input for Hebbian salience update
            corr = np.dot(mode_output, input_vec) / (
                np.linalg.norm(mode_output) * np.linalg.norm(input_vec) + 1e-8)
            mode_correlations.append(float(corr))

        # Update U
        U_new = self.U + eta * input_vec + mode_contributions
        self.U = U_new / (np.linalg.norm(U_new) + 1e-8)

        # Hebbian salience update: λ_k increases when D_k(U) correlates with input
        for k in range(self.n_modes):
            self.lambdas[k] += self.eta_lambda * mode_correlations[k]

        # Keep lambdas positive and normalized
        self.lambdas = np.maximum(self.lambdas, 0.01)
        self.lambdas /= self.lambdas.sum()

        # Record history
        self.U_history.append(self.U.copy())
        self.lambda_history.append(self.lambdas.copy())

        # Expressed mode
        expressed = int(np.argmax(self.lambdas))

        return {
            "U": self.U.copy(),
            "lambdas": self.lambdas.copy(),
            "expressed_mode": expressed,
            "expressed_name": self.mode_names[expressed],
            "unity_error": self.check_unity(),
            "U_norm": float(np.linalg.norm(self.U)),
            "mode_correlations": mode_correlations,
        }

    def destroy_mode(self, k):
        """Forcibly set projection P_k to zero — destroy a mode.

        This breaks the partition-of-unity constraint.
        """
        self.projections[k] = np.zeros_like(self.projections[k])
        # λ_k to zero
        self.lambdas[k] = 0.0
        self.lambdas /= self.lambdas.sum()
