"""Build train/held-out splits from text8.

text8 is 100_000_000 bytes of cleaned Wikipedia (a-z + space). We hold
out the final 5 MB as the evaluation slice, and take 1/10/50/90 MB
prefixes from the first 95 MB as training slices.

All splits share the same held-out tail so bpb numbers are directly
comparable across training sizes.
"""
from __future__ import annotations
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEXT8 = os.path.join(DATA_DIR, "text8")
HELDOUT_BYTES = 5_000_000
TRAIN_SIZES_MB = [1, 10, 50, 90]


def load() -> bytes:
    with open(TEXT8, "rb") as f:
        data = f.read()
    assert len(data) == 100_000_000, f"unexpected text8 size: {len(data)}"
    return data


def splits() -> tuple[dict[int, bytes], bytes]:
    """Return ({size_mb: train_bytes}, heldout_bytes)."""
    data = load()
    heldout = data[-HELDOUT_BYTES:]
    train_pool = data[: len(data) - HELDOUT_BYTES]  # first 95 MB
    trains = {mb: train_pool[: mb * 1_000_000] for mb in TRAIN_SIZES_MB}
    return trains, heldout


if __name__ == "__main__":
    trains, heldout = splits()
    print(f"heldout: {len(heldout):,} bytes")
    for mb, buf in trains.items():
        print(f"train {mb:>3} MB: {len(buf):,} bytes  head={buf[:40]!r}")
    # sanity: alphabet
    alphabet = sorted(set(heldout))
    print(f"heldout alphabet size: {len(alphabet)}  chars: {bytes(alphabet)!r}")
