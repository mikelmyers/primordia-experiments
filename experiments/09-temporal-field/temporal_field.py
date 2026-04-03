"""
Test 9 — Temporal Field: T(τ) as Continuous Scalar Field Over Internal Time

An entity that HAS time as part of its state — past, present, and anticipated
future coexist simultaneously as a field over internal time coordinate τ.
"""

import numpy as np


class TemporalField:
    """Temporal field entity: T(τ) = Σ_k a_k · φ_k(τ)"""

    def __init__(self, field_extent=50, n_basis=30, n_quadrature=100, seed=42):
        self.rng = np.random.RandomState(seed)
        self.L = field_extent
        self.n_basis = n_basis
        self.n_quad = n_quadrature

        # Discretize τ ∈ [-L, +L]
        self.tau = np.linspace(-self.L, self.L, n_quadrature)
        self.dtau = self.tau[1] - self.tau[0]

        # Fourier basis functions φ_k(τ)
        self.basis = self._make_basis()

        # Coefficients a_k — initialized as Gaussian centered at τ=0
        self.a = np.zeros(n_basis)
        # Set initial coefficients to approximate a Gaussian
        gaussian = np.exp(-self.tau**2 / (2 * 5.0**2))
        for k in range(n_basis):
            self.a[k] = np.trapz(gaussian * self.basis[k], self.tau)

        # Temporal weighting function w(τ)
        self.decay = 10.0
        self.anticipation = 5.0
        self.w = self._make_temporal_weight()

        # Learning weights for anticipation (past -> future extrapolation)
        self.anticipation_weights = self.rng.randn(n_basis, n_basis) * 0.01

        # History for experience encoding
        self.recent_deposits = []
        self.interaction_count = 0

    def _make_basis(self):
        """Create Fourier basis functions."""
        basis = np.zeros((self.n_basis, self.n_quad))
        for k in range(self.n_basis):
            if k == 0:
                basis[k] = np.ones(self.n_quad) / np.sqrt(2 * self.L)
            elif k % 2 == 1:
                n = (k + 1) // 2
                basis[k] = np.cos(n * np.pi * self.tau / self.L) / np.sqrt(self.L)
            else:
                n = k // 2
                basis[k] = np.sin(n * np.pi * self.tau / self.L) / np.sqrt(self.L)
        return basis

    def _make_temporal_weight(self):
        """Create temporal weighting function w(τ)."""
        w = np.zeros(self.n_quad)
        for i, t in enumerate(self.tau):
            if t == 0:
                w[i] = 1.0
            elif t < 0:
                w[i] = np.exp(t / self.decay)  # past: exponential decay
            else:
                w[i] = np.exp(-t / self.anticipation)  # future: anticipation weight
        return w

    def evaluate_field(self):
        """Evaluate T(τ) = Σ_k a_k · φ_k(τ)"""
        field = np.zeros(self.n_quad)
        for k in range(self.n_basis):
            field += self.a[k] * self.basis[k]
        return field

    def encode_input(self, x):
        """Encode input to a scalar amplitude."""
        if isinstance(x, str):
            h = hash(x)
            return (h % 1000) / 500.0 - 1.0  # map to [-1, 1]
        elif isinstance(x, np.ndarray):
            return float(np.mean(x))
        return float(x)

    def update(self, x):
        """Full temporal field update for one interaction.

        1. Shift the field (present moves forward)
        2. Deposit experience at τ=0
        3. Update anticipation (future region)
        4. Normalize coefficients
        """
        amplitude = self.encode_input(x)
        self.interaction_count += 1

        # 1. Shift field: T(τ) → T(τ-1) by shifting coefficients
        # In Fourier space, shifting by δ multiplies k-th coefficient by exp(-i·k·δ/L)
        shift = 1.0
        for k in range(self.n_basis):
            if k == 0:
                pass  # DC component unchanged
            elif k % 2 == 1:
                n = (k + 1) // 2
                phase = n * np.pi * shift / self.L
                old_cos = self.a[k]
                old_sin = self.a[k + 1] if k + 1 < self.n_basis else 0
                self.a[k] = old_cos * np.cos(phase) + old_sin * np.sin(phase)
                if k + 1 < self.n_basis:
                    self.a[k + 1] = -old_cos * np.sin(phase) + old_sin * np.cos(phase)

        # 2. Deposit experience: add scaled basis function centered at τ=0
        deposit = amplitude * np.exp(-self.tau**2 / (2 * 2.0**2))  # narrow Gaussian at present
        for k in range(self.n_basis):
            deposit_coeff = np.trapz(deposit * self.basis[k], self.tau)
            self.a[k] += 0.3 * deposit_coeff  # deposit strength

        self.recent_deposits.append(amplitude)
        if len(self.recent_deposits) > 20:
            self.recent_deposits.pop(0)

        # 3. Anticipation update: future region from past pattern
        # Learn to extrapolate: a_future = W · a_past_pattern
        past_field = self.evaluate_field()
        past_mask = self.tau < 0
        past_pattern = np.zeros(self.n_basis)
        for k in range(self.n_basis):
            past_pattern[k] = np.trapz(past_field * past_mask * self.basis[k], self.tau)

        # Update future coefficients via learned extrapolation
        future_prediction = self.anticipation_weights @ past_pattern
        future_field = self.evaluate_field()
        future_mask = self.tau > 0

        # Simple Hebbian update of anticipation weights
        if len(self.recent_deposits) > 5:
            # The "error" is how well past predicted present
            present_amplitude = amplitude
            predicted_present = float(np.mean(future_prediction[:5]))
            error = present_amplitude - predicted_present
            # Hebbian: strengthen connections that would have predicted correctly
            self.anticipation_weights += 0.001 * error * np.outer(
                past_pattern[:self.n_basis], past_pattern[:self.n_basis])

        # Apply future prediction to field
        for k in range(self.n_basis):
            future_coeff = np.trapz(
                future_prediction[k % self.n_basis] * (self.tau > 0).astype(float) * self.basis[k],
                self.tau)
            self.a[k] = 0.9 * self.a[k] + 0.1 * future_coeff

        # 4. L2 normalize coefficients
        norm = np.linalg.norm(self.a)
        if norm > 1e-8:
            self.a /= norm

        # Compute current integrated state
        field = self.evaluate_field()
        S = np.trapz(field * self.w, self.tau)

        return {
            "field": field,
            "state": float(S),
            "amplitude": amplitude,
            "coefficients": self.a.copy(),
            "field_norm": float(np.linalg.norm(field)),
        }

    def get_past_region(self):
        """Return field values in the past region (τ < 0)."""
        field = self.evaluate_field()
        mask = self.tau < 0
        return self.tau[mask], field[mask]

    def get_future_region(self):
        """Return field values in the future region (τ > 0)."""
        field = self.evaluate_field()
        mask = self.tau > 0
        return self.tau[mask], field[mask]

    def get_present_value(self):
        """Return field value at τ ≈ 0."""
        center_idx = self.n_quad // 2
        field = self.evaluate_field()
        return float(field[center_idx])

    def compute_temporal_lean(self):
        """Compute whether the field leans past-heavy, future-heavy, or present-focused.

        Returns (past_mass, present_mass, future_mass) where masses are
        integrated |T(τ)| in each region.
        """
        field = np.abs(self.evaluate_field())
        past_mass = float(np.trapz(field[self.tau < -2], self.tau[self.tau < -2]))
        present_mass = float(np.trapz(field[np.abs(self.tau) <= 2], self.tau[np.abs(self.tau) <= 2]))
        future_mass = float(np.trapz(field[self.tau > 2], self.tau[self.tau > 2]))
        total = past_mass + present_mass + future_mass + 1e-8
        return past_mass / total, present_mass / total, future_mass / total
