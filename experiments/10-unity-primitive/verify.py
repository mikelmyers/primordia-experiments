"""
Test 10 — Unity Primitive: Continuous Unity Verification

Checks that Σ_k D_k(U) = U at every recorded timestep.
"""

import json
import os
import numpy as np
from unity import UnityPrimitive

OUTDIR = os.path.dirname(os.path.abspath(__file__))


def main():
    errors = np.load(os.path.join(OUTDIR, "unity_errors.npy"))

    print("Unity Preservation Check")
    print(f"  Total timesteps: {len(errors)}")
    print(f"  Max error: {np.max(errors):.8f}")
    print(f"  Mean error: {np.mean(errors):.8f}")
    print(f"  Violations (>0.001): {np.sum(errors > 0.001)}")

    # Pre vs post destruction
    pre = errors[:500]
    post = errors[500:]
    print(f"\n  Pre-destruction (t<500):")
    print(f"    Max: {np.max(pre):.8f}")
    print(f"    Mean: {np.mean(pre):.8f}")
    print(f"    All < 0.001: {np.all(pre < 0.001)}")

    print(f"\n  Post-destruction (t>=500):")
    print(f"    Max: {np.max(post):.8f}")
    print(f"    Mean: {np.mean(post):.8f}")
    print(f"    All < 0.001: {np.all(post < 0.001)}")

    if np.any(errors > 0.001):
        violation_steps = np.where(errors > 0.001)[0]
        print(f"\n  First violation at step: {violation_steps[0]}")
        print(f"  Total violations: {len(violation_steps)}")
        print(f"  Violation range: steps {violation_steps[0]}-{violation_steps[-1]}")
    else:
        print("\n  Unity perfectly preserved throughout (no violations).")


if __name__ == "__main__":
    main()
