"""PPM-D order-k predictor. Pure Python ints. No matmul.

Prediction by Partial Matching with escape method D (Howard 1993).

For each context of length <= max_order, keep a count of symbols seen
following that context. To compute P(symbol | context):

  1. Start at the highest order. If the context exists and the symbol
     was seen in it, use the escape-D estimate:
         P(s | ctx) = (count[s] - 0.5) / total[ctx]
     with "exclusion": symbols already seen at a higher order are not
     considered when computing total at lower orders.
  2. If the symbol is novel in this context, the model emits an escape
     with probability:
         P(esc | ctx) = 0.5 * distinct[ctx] / total[ctx]
     and we drop one order and retry.
  3. Order -1 is a uniform distribution over the 27-char alphabet,
     with exclusions removed.

This implementation trains (updates counts) on a training stream, then
**freezes** and evaluates on a held-out stream. No counts are updated
during evaluation. This is the cleanest split for a research bpc number.

All arithmetic is integer + one float division + one log2 per byte.
No matmul, no dense linear algebra, no gradient descent.
"""
from __future__ import annotations

import math
from array import array

ALPHABET_SIZE = 27  # text8: a-z + space


def _encode(b: bytes) -> list[int]:
    """Map text8 bytes to 0..26. space=26, a..z=0..25."""
    out = [0] * len(b)
    for i, c in enumerate(b):
        if c == 0x20:  # space
            out[i] = 26
        else:
            out[i] = c - 0x61  # 'a' = 97
    return out


class PPMD:
    def __init__(self, max_order: int = 5):
        self.max_order = max_order
        # For each order 0..max_order:
        #   contexts[order][ctx_tuple] = array('i', [count_0, ..., count_26, total])
        # ctx_tuple is a tuple of ints of length `order`.
        self.contexts: list[dict[tuple, array]] = [
            {} for _ in range(max_order + 1)
        ]

    def train(self, data: bytes) -> None:
        seq = _encode(data)
        max_order = self.max_order
        ctxs = self.contexts
        n = len(seq)
        # Slide a window of length max_order+1. For each position, update
        # counts for all orders 0..max_order using the context ending
        # just before the current symbol.
        for i in range(n):
            s = seq[i]
            # longest available context is min(i, max_order) bytes ending at i-1
            avail = i if i < max_order else max_order
            # Build the full tuple once and slice
            if avail > 0:
                full = tuple(seq[i - avail : i])
            else:
                full = ()
            for order in range(avail + 1):
                key = full[avail - order :] if order > 0 else ()
                table = ctxs[order]
                row = table.get(key)
                if row is None:
                    row = array("i", [0] * (ALPHABET_SIZE + 1))
                    table[key] = row
                row[s] += 1
                row[ALPHABET_SIZE] += 1

    def _prob_symbol(self, context: tuple, symbol: int) -> float:
        """Compute P(symbol | context) under PPM-D with exclusion.

        Returns a float in (0, 1]. Never returns exactly 0 because of
        the order -1 uniform backoff.
        """
        excluded: set[int] = set()
        escape_product = 1.0
        ctxs = self.contexts
        # Try orders from longest down to 0
        for order in range(min(len(context), self.max_order), -1, -1):
            key = context[len(context) - order :] if order > 0 else ()
            table = ctxs[order]
            row = table.get(key)
            if row is None:
                continue
            # Compute effective total (excluding already-excluded symbols)
            # and effective distinct (symbols with count > 0 not excluded)
            total = 0
            distinct = 0
            for sym in range(ALPHABET_SIZE):
                c = row[sym]
                if c > 0 and sym not in excluded:
                    total += c
                    distinct += 1
            if total == 0:
                continue
            c_s = row[symbol] if symbol not in excluded else 0
            if c_s > 0:
                # Method D: (count - 0.5) / total
                p_here = (c_s - 0.5) / total
                return escape_product * p_here
            # Escape: probability = 0.5 * distinct / total
            # (Howard's method D escape mass)
            p_esc = (0.5 * distinct) / total
            escape_product *= p_esc
            # Add all symbols seen at this order to exclusion set
            for sym in range(ALPHABET_SIZE):
                if row[sym] > 0:
                    excluded.add(sym)
        # Order -1: uniform over remaining (non-excluded) symbols
        remaining = ALPHABET_SIZE - len(excluded)
        if remaining <= 0:
            # Degenerate: everything excluded. Fall back to 1/alphabet.
            return escape_product * (1.0 / ALPHABET_SIZE)
        return escape_product * (1.0 / remaining)

    def eval_bpc(self, data: bytes) -> tuple[float, int]:
        """Return (bpc, n_bytes). No count updates."""
        seq = _encode(data)
        n = len(seq)
        total_bits = 0.0
        max_order = self.max_order
        for i in range(n):
            s = seq[i]
            avail = i if i < max_order else max_order
            if avail > 0:
                ctx = tuple(seq[i - avail : i])
            else:
                ctx = ()
            p = self._prob_symbol(ctx, s)
            if p <= 0.0:
                # Should not happen; guard anyway.
                p = 1e-300
            total_bits += -math.log2(p)
        return total_bits / n, n


if __name__ == "__main__":
    # Smoke test on a small string
    model = PPMD(max_order=3)
    model.train(b"the quick brown fox jumps over the lazy dog " * 200)
    bpc, n = model.eval_bpc(b"the quick brown fox")
    print(f"smoke test: bpc={bpc:.3f} n={n}")
