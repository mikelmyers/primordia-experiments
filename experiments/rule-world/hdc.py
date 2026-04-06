"""HDC primitives for the abstractor's analogy mechanism.

Bipolar (±1) hypervectors in 10,000 dimensions.

Operations used in this module:
  - elementwise multiply (bind), O(d)
  - elementwise sum + sign (bundle), O(N·d)
  - dot product / d (similarity), O(d)

These are NOT matrix multiplication. There is no learned weight matrix
anywhere. The codebook is a fixed dictionary of random vectors generated
once at startup and never updated.
"""

from __future__ import annotations

import numpy as np

DIM = 10000


class Codebook:
    """Lazily-allocated dictionary of random ±1 hypervectors."""

    def __init__(self, seed: int = 42):
        self._rng = np.random.default_rng(seed)
        self._book: dict[str, np.ndarray] = {}

    def get(self, token: str) -> np.ndarray:
        if token not in self._book:
            self._book[token] = self._rng.choice(
                [-1, 1], size=DIM
            ).astype(np.int8)
        return self._book[token]


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Elementwise multiply: bipolar HDC's binding operation."""
    return (a * b).astype(np.int8)


def bundle(vectors: list[np.ndarray]) -> np.ndarray:
    """Majority vote (via sum + sign). Empty bundle = zero vector."""
    if not vectors:
        return np.zeros(DIM, dtype=np.int8)
    s = np.sum(np.stack(vectors).astype(np.int32), axis=0)
    out = np.sign(s).astype(np.int8)
    out[out == 0] = 1  # deterministic tiebreak
    return out


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Normalized dot product. Range ≈ [-1, +1]. Random pairs ≈ 0 ± 0.01."""
    return float(np.dot(a.astype(np.int32), b.astype(np.int32)) / DIM)


def encode_property_bundle(
    properties: list[str], codebook: Codebook
) -> np.ndarray:
    return bundle([codebook.get(p) for p in properties])
