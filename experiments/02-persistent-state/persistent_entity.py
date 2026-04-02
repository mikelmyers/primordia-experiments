"""
Test 2 — Persistent Non-Resetting State
Primordia Systems LLC — Pre-Paradigm Research

An entity with a 128-dimensional internal state that NEVER resets.
Every interaction permanently alters the state. The question:
does accumulated experience create something like character?

Update rule:
    S(t+1) = α·S(t) + β·encode(input) + γ·f(S(t))

No retrieval. No goals. Just accumulation and self-influence.
"""

import numpy as np
import json
import hashlib


# --- Input encoding ---
# We use a deterministic semantic encoder that maps text to vectors.
# This preserves key properties: similar texts -> similar vectors,
# different semantic categories -> different regions of vector space.

class SemanticEncoder:
    """
    Deterministic text encoder that maps strings to 128-dim vectors
    with semantic structure preserved through category-aware hashing.

    Uses a combination of:
    - Character n-gram hashing for base representation
    - Semantic category detection for structured placement
    - Consistent random projection seeded by content
    """

    def __init__(self, dim=128):
        self.dim = dim
        self.rng = np.random.default_rng(seed=12345)
        # Pre-compute random projection matrices for different semantic categories
        # This gives different input types different "directions" in state space
        self.category_bases = {}
        categories = [
            'question', 'statement', 'emotional', 'contradiction',
            'abstract', 'concrete', 'temporal', 'spatial', 'social', 'neutral'
        ]
        for cat in categories:
            seed = int(hashlib.md5(cat.encode()).hexdigest()[:8], 16)
            rng = np.random.default_rng(seed)
            basis = rng.normal(0, 1, (dim, dim))
            # Orthogonalize to give each category a clean subspace
            q, _ = np.linalg.qr(basis)
            self.category_bases[cat] = q

    def detect_category(self, text):
        """Simple rule-based category detection."""
        text_lower = text.lower()
        if '?' in text:
            return 'question'
        if any(w in text_lower for w in ['feel', 'happy', 'sad', 'angry',
                                          'love', 'fear', 'joy', 'pain',
                                          'emotion', 'heart']):
            return 'emotional'
        if any(w in text_lower for w in ['but', 'however', 'yet', 'although',
                                          'contradiction', 'opposite',
                                          'paradox', 'conflict']):
            return 'contradiction'
        if any(w in text_lower for w in ['think', 'believe', 'concept',
                                          'abstract', 'idea', 'theory',
                                          'meaning', 'philosophy']):
            return 'abstract'
        if any(w in text_lower for w in ['yesterday', 'tomorrow', 'time',
                                          'before', 'after', 'when',
                                          'always', 'never', 'remember']):
            return 'temporal'
        return 'statement'

    def encode(self, text):
        """
        Encode text to a 128-dim vector.

        Properties:
        - Deterministic: same text always produces same vector
        - Semantic: similar texts produce similar vectors
        - Category-structured: different input types occupy different subspaces
        """
        # Base encoding from character n-grams
        base = np.zeros(self.dim)
        # Use overlapping 3-grams
        text_bytes = text.encode('utf-8')
        for i in range(len(text_bytes) - 2):
            trigram = text_bytes[i:i+3]
            h = int(hashlib.md5(trigram).hexdigest()[:8], 16)
            idx = h % self.dim
            sign = 1.0 if (h // self.dim) % 2 == 0 else -1.0
            base[idx] += sign * (1.0 / max(1, len(text_bytes) - 2))

        # Project through category basis for semantic structure
        category = self.detect_category(text)
        basis = self.category_bases[category]
        # Use first 32 dimensions of the category subspace
        projected = basis[:, :32] @ basis[:, :32].T @ base

        # Combine base and projected
        encoded = 0.5 * base + 0.5 * projected

        # Normalize to unit length
        norm = np.linalg.norm(encoded)
        if norm > 0:
            encoded = encoded / norm

        return encoded


class PersistentEntity:
    """
    An entity with persistent internal state that never resets.

    The state accumulates experience permanently. The entity is
    nothing but its accumulated history — no separate memory,
    no retrieval mechanism, no goals. Just state.
    """

    def __init__(self, dim=128, alpha=0.95, beta=0.1, gamma=0.3, seed=42):
        self.dim = dim
        self.alpha = alpha  # Decay — most state preserved
        self.beta = beta    # Input influence — small but permanent
        self.gamma = gamma  # Self-influence — state acts on itself

        # The state. Initialized at zero. Never reset.
        self.S = np.zeros(dim)
        self.S0 = self.S.copy()  # Store initial state for drift measurement

        # The encoder
        self.encoder = SemanticEncoder(dim=dim)

        # History — we log everything
        self.history = []
        self.state_snapshots = []
        self.interaction_count = 0

    def interact(self, text):
        """
        Process an interaction. The state changes permanently.

        S(t+1) = α·S(t) + β·encode(input) + γ·tanh(S(t))

        Returns the state change magnitude (how much this input moved us).
        """
        S_before = self.S.copy()

        # Encode the input
        encoded = self.encoder.encode(text)

        # The update — this is the whole entity
        self.S = (
            self.alpha * self.S +        # Persistence: most of what we were
            self.beta * encoded +          # Input: a small permanent mark
            self.gamma * np.tanh(self.S)   # Self-influence: state shapes itself
        )

        # Measure the change
        delta = np.linalg.norm(self.S - S_before)
        drift_from_origin = np.linalg.norm(self.S - self.S0)

        # Log everything
        entry = {
            'interaction': self.interaction_count,
            'input': text,
            'category': self.encoder.detect_category(text),
            'delta_norm': float(delta),
            'state_norm': float(np.linalg.norm(self.S)),
            'drift_from_origin': float(drift_from_origin),
        }
        self.history.append(entry)
        self.state_snapshots.append(self.S.copy())
        self.interaction_count += 1

        return entry

    def get_state(self):
        """Return current state (read-only copy)."""
        return self.S.copy()

    def sensitivity_to(self, text):
        """
        Measure how much a given input WOULD change the state,
        without actually changing it.
        """
        encoded = self.encoder.encode(text)
        S_hypothetical = (
            self.alpha * self.S +
            self.beta * encoded +
            self.gamma * np.tanh(self.S)
        )
        return float(np.linalg.norm(S_hypothetical - self.S))

    def response_vector(self, text):
        """
        What the state would become after this input.
        Does NOT modify state.
        """
        encoded = self.encoder.encode(text)
        return (
            self.alpha * self.S +
            self.beta * encoded +
            self.gamma * np.tanh(self.S)
        )
