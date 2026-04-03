"""
Test 10 — Unity Primitive: Simulation

1000 interactions with mode destruction event at t=500.
Tests whether unity-first produces different behavior than parts-first.
"""

import json
import os
import numpy as np
from unity import UnityPrimitive

SEED = 42
OUTDIR = os.path.dirname(os.path.abspath(__file__))

INPUT_TYPES = ["perception", "reasoning", "affect", "action", "memory"]


def generate_inputs(n=1000, seed=42):
    """Generate 1000 inputs, cycling through 5 types (one per mode)."""
    rng = np.random.RandomState(seed)
    inputs = []
    labels = []
    dim = 256

    for i in range(n):
        # Cycle through input types with some randomness
        if rng.random() < 0.7:
            # 70% of the time, inputs come in blocks
            block_type = (i // 20) % 5
        else:
            block_type = rng.randint(0, 5)

        # Create type-specific input
        vec = rng.randn(dim) * 0.1  # baseline noise
        # Amplify dimensions corresponding to the target mode's subspace
        subdim = dim // 5
        start = block_type * subdim
        end = start + subdim
        vec[start:end] += rng.randn(end - start) * 1.5

        inputs.append(vec)
        labels.append(INPUT_TYPES[block_type])

    return inputs, labels


def run_simulation():
    """Run full simulation with mode destruction at t=500."""
    print("Generating inputs...")
    inputs, labels = generate_inputs(1000, SEED)

    entity = UnityPrimitive(dim=256, n_modes=5, seed=SEED)

    log = {
        "unity_errors": [],
        "expressed_modes": [],
        "lambdas": [],
        "U_norms": [],
        "input_labels": labels,
        "mode_correlations": [],
    }

    # Pre-destruction verification
    pre_verification = entity.verification.copy()
    print(f"Projection verification: {pre_verification}")

    print("\nRunning 1000 interactions (mode destruction at t=500)...")
    destroyed_mode = 2  # destroy "affect" mode

    for i in range(1000):
        # Destroy mode at t=500
        if i == 500:
            print(f"\n  *** DESTROYING MODE {destroyed_mode} ({INPUT_TYPES[destroyed_mode]}) ***")
            entity.destroy_mode(destroyed_mode)

        result = entity.update(inputs[i])

        log["unity_errors"].append(result["unity_error"])
        log["expressed_modes"].append(result["expressed_mode"])
        log["lambdas"].append(result["lambdas"].tolist())
        log["U_norms"].append(result["U_norm"])
        log["mode_correlations"].append(result["mode_correlations"])

        if i % 100 == 0:
            print(f"  Step {i:4d}: expressed={result['expressed_name']:12s}, "
                  f"unity_err={result['unity_error']:.6f}, "
                  f"λ={np.array2string(result['lambdas'], precision=3)}")

    # --- Analysis ---
    print("\nAnalyzing...")

    # Unity preservation
    pre_errors = log["unity_errors"][:500]
    post_errors = log["unity_errors"][500:]

    # Mode selectivity: does the correct mode become dominant?
    correct_selections = 0
    total = 0
    for i in range(1000):
        if i < 500 or labels[i] != INPUT_TYPES[destroyed_mode]:
            expected_mode = INPUT_TYPES.index(labels[i])
            if log["expressed_modes"][i] == expected_mode:
                correct_selections += 1
            total += 1

    # Cross-mode interference: switching time
    switch_times = []
    for i in range(1, len(log["expressed_modes"])):
        if log["expressed_modes"][i] != log["expressed_modes"][i-1]:
            # How long until the new mode stabilizes?
            stable_count = 0
            for j in range(i, min(i + 20, len(log["expressed_modes"]))):
                if log["expressed_modes"][j] == log["expressed_modes"][i]:
                    stable_count += 1
            switch_times.append(stable_count)

    # Post-destruction analysis
    # Does the destroyed mode's input still get processed?
    post_affect_idx = [i for i in range(500, 1000) if labels[i] == INPUT_TYPES[destroyed_mode]]
    post_affect_expressed = [log["expressed_modes"][i] for i in post_affect_idx]
    # Which mode takes over for the destroyed one?
    from collections import Counter
    takeover = Counter(post_affect_expressed)

    # Does U reconstitute the lost mode?
    # Check if unity error recovers after destruction
    recovery_window = log["unity_errors"][500:600]
    final_errors = log["unity_errors"][-100:]

    # Lambda evolution
    lambdas_arr = np.array(log["lambdas"])
    pre_lambdas = lambdas_arr[:500].mean(axis=0)
    post_lambdas = lambdas_arr[500:].mean(axis=0)

    results = {
        "projection_verification": pre_verification,
        "unity_preservation": {
            "pre_destruction_mean_error": float(np.mean(pre_errors)),
            "post_destruction_mean_error": float(np.mean(post_errors)),
            "max_error_ever": float(max(log["unity_errors"])),
            "post_recovery_error": float(np.mean(final_errors)),
        },
        "mode_selectivity": {
            "accuracy": correct_selections / total if total > 0 else 0,
            "n_correct": correct_selections,
            "n_total": total,
        },
        "cross_mode_interference": {
            "mean_switch_stabilization": float(np.mean(switch_times)) if switch_times else 0,
            "n_switches": len(switch_times),
        },
        "mode_destruction": {
            "destroyed_mode": INPUT_TYPES[destroyed_mode],
            "takeover_distribution": dict(takeover),
            "recovery_error_trajectory": [float(e) for e in recovery_window[:20]],
            "pre_lambdas": pre_lambdas.tolist(),
            "post_lambdas": post_lambdas.tolist(),
        },
        "U_stability": {
            "mean_norm": float(np.mean(log["U_norms"])),
            "std_norm": float(np.std(log["U_norms"])),
            "pre_norm": float(np.mean(log["U_norms"][:500])),
            "post_norm": float(np.mean(log["U_norms"][500:])),
        },
    }

    with open(os.path.join(OUTDIR, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Save for visualization
    np.save(os.path.join(OUTDIR, "lambdas.npy"), lambdas_arr)
    np.save(os.path.join(OUTDIR, "unity_errors.npy"), np.array(log["unity_errors"]))
    np.save(os.path.join(OUTDIR, "expressed_modes.npy"), np.array(log["expressed_modes"]))
    np.save(os.path.join(OUTDIR, "U_norms.npy"), np.array(log["U_norms"]))
    np.save(os.path.join(OUTDIR, "input_labels.npy"), np.array(labels))

    print("\nResults saved.")
    return results


if __name__ == "__main__":
    results = run_simulation()
    print(f"\nKey findings:")
    print(f"  Mode selectivity accuracy: {results['mode_selectivity']['accuracy']:.4f}")
    print(f"  Unity error pre-destruction: {results['unity_preservation']['pre_destruction_mean_error']:.6f}")
    print(f"  Unity error post-destruction: {results['unity_preservation']['post_destruction_mean_error']:.6f}")
    print(f"  Destroyed mode takeover: {results['mode_destruction']['takeover_distribution']}")
