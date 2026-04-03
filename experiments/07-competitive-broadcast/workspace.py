"""
Test 7 — Competitive Global Broadcast: Global Workspace and Competition

Implements Global Workspace Theory with hard competition:
- 6 specialist modules compete for access to a shared broadcast buffer
- Winner-take-all via softmax with temperature control
- Three competition modes: hard (τ=0.1), medium (τ=1.0), soft (weighted average)
"""

import numpy as np


class SpecialistModule:
    """A small feedforward network serving as a specialist module."""

    def __init__(self, name, input_dim, hidden_dim=128, output_dim=64, seed=42):
        self.name = name
        rng = np.random.RandomState(seed)
        # Two-layer network: input -> hidden -> output
        self.W1 = rng.randn(input_dim, hidden_dim) * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = rng.randn(hidden_dim, output_dim) * 0.1
        self.b2 = np.zeros(output_dim)
        # Internal state for urgency computation
        self.internal_state = np.zeros(output_dim)
        self.activation_history = []

    def forward(self, x):
        """Process input through the module."""
        h = np.tanh(x @ self.W1 + self.b1)
        out = np.tanh(h @ self.W2 + self.b2)
        self.internal_state = 0.8 * self.internal_state + 0.2 * out
        return out

    def compute_urgency(self, x):
        """Compute how urgently this module wants to broadcast.

        Based on input salience (magnitude of activation) and internal state change.
        """
        out = self.forward(x)
        input_salience = np.mean(np.abs(out))
        state_change = np.mean(np.abs(out - self.internal_state))
        urgency = input_salience + 0.5 * state_change
        return float(urgency), out


class GlobalWorkspace:
    """Global Workspace with competitive broadcasting."""

    def __init__(self, workspace_dim=256, seed=42):
        self.workspace_dim = workspace_dim
        self.rng = np.random.RandomState(seed)

        # Module definitions: each processes a different input feature subset
        module_configs = [
            ("perceptual", 64),
            ("semantic", 64),
            ("temporal", 64),
            ("affective", 64),
            ("motor", 64),
            ("metacognitive", 64),
        ]

        self.modules = []
        for i, (name, input_dim) in enumerate(module_configs):
            self.modules.append(
                SpecialistModule(name, input_dim, hidden_dim=128, output_dim=64,
                               seed=seed + i)
            )

        # Projection matrices: module output -> workspace
        self.projections = []
        for i in range(len(self.modules)):
            P = self.rng.randn(64, workspace_dim) * 0.1
            self.projections.append(P)

        # Workspace state
        self.workspace = np.zeros(workspace_dim)
        self.current_winner = -1
        self.hold_counter = 0
        self.hold_time = 3  # minimum timesteps to hold broadcast

    def _split_input(self, x):
        """Split a combined input into module-specific inputs.

        x: (384,) vector split into 6 chunks of 64.
        """
        assert len(x) == 384, f"Expected input dim 384, got {len(x)}"
        return [x[i*64:(i+1)*64] for i in range(6)]

    def step_hard(self, x, temperature=0.1):
        """Hard competition: winner-take-all via sharp softmax."""
        inputs = self._split_input(x)

        # Compute urgency for each module
        urgencies = []
        outputs = []
        for mod, inp in zip(self.modules, inputs):
            u, out = mod.compute_urgency(inp)
            urgencies.append(u)
            outputs.append(out)

        urgencies = np.array(urgencies)

        # Check if current winner's hold time has expired
        if self.hold_counter > 0:
            self.hold_counter -= 1
            winner = self.current_winner
        else:
            # Softmax competition
            exp_u = np.exp((urgencies - np.max(urgencies)) / temperature)
            probs = exp_u / exp_u.sum()
            winner = int(np.argmax(probs))
            self.current_winner = winner
            self.hold_counter = self.hold_time

        # Winner broadcasts to workspace; losers get nothing
        broadcast = outputs[winner] @ self.projections[winner]
        self.workspace = 0.3 * self.workspace + 0.7 * broadcast

        return {
            "workspace": self.workspace.copy(),
            "winner": winner,
            "winner_name": self.modules[winner].name,
            "urgencies": urgencies.copy(),
            "outputs": [o.copy() for o in outputs],
        }

    def step_medium(self, x, temperature=1.0):
        """Medium competition: softer softmax, losers partially active."""
        inputs = self._split_input(x)

        urgencies = []
        outputs = []
        for mod, inp in zip(self.modules, inputs):
            u, out = mod.compute_urgency(inp)
            urgencies.append(u)
            outputs.append(out)

        urgencies = np.array(urgencies)

        # Softer softmax
        exp_u = np.exp((urgencies - np.max(urgencies)) / temperature)
        probs = exp_u / exp_u.sum()

        # Weighted broadcast
        broadcast = np.zeros(self.workspace_dim)
        for i, (out, proj, p) in enumerate(zip(outputs, self.projections, probs)):
            broadcast += p * (out @ proj)

        winner = int(np.argmax(probs))
        self.workspace = 0.3 * self.workspace + 0.7 * broadcast

        return {
            "workspace": self.workspace.copy(),
            "winner": winner,
            "winner_name": self.modules[winner].name,
            "urgencies": urgencies.copy(),
            "probs": probs.copy(),
        }

    def step_soft(self, x):
        """Soft integration: uniform weighted average of all modules."""
        inputs = self._split_input(x)

        outputs = []
        for mod, inp in zip(self.modules, inputs):
            out = mod.forward(inp)
            outputs.append(out)

        # Equal-weight broadcast
        broadcast = np.zeros(self.workspace_dim)
        for out, proj in zip(outputs, self.projections):
            broadcast += (1.0 / len(self.modules)) * (out @ proj)

        self.workspace = 0.3 * self.workspace + 0.7 * broadcast

        return {
            "workspace": self.workspace.copy(),
            "winner": -1,
            "winner_name": "all",
        }

    def reset(self):
        """Reset workspace and module states."""
        self.workspace = np.zeros(self.workspace_dim)
        self.current_winner = -1
        self.hold_counter = 0
        for mod in self.modules:
            mod.internal_state = np.zeros(64)
