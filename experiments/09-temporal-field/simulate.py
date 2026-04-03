"""
Test 9 — Temporal Field: Simulation

300 interactions with temporally structured inputs.
Measures past coherence, anticipation accuracy, present sensitivity, temporal lean.
"""

import json
import os
import numpy as np
from temporal_field import TemporalField

SEED = 42
OUTDIR = os.path.dirname(os.path.abspath(__file__))


def generate_temporal_inputs(n=300, seed=42):
    """Generate inputs with temporal structure: sequences, patterns, callbacks.

    Types:
    1. Repeating patterns (test if field encodes periodicity)
    2. Sequential narratives (test if field tracks order)
    3. Callbacks to earlier inputs (test if past region responds)
    4. Novel inputs (test present sensitivity)
    """
    rng = np.random.RandomState(seed)
    inputs = []
    input_metadata = []

    for i in range(n):
        if i < 50:
            # Phase 1: Repeating pattern (period 5)
            val = np.sin(2 * np.pi * i / 5.0)
            inputs.append(val)
            input_metadata.append({"type": "periodic", "period": 5, "phase": i % 5})
        elif i < 100:
            # Phase 2: Linear ramp (monotonic increase)
            val = (i - 50) / 50.0
            inputs.append(val)
            input_metadata.append({"type": "ramp", "position": i - 50})
        elif i < 150:
            # Phase 3: Callbacks — repeat pattern from phase 1
            val = np.sin(2 * np.pi * i / 5.0)
            inputs.append(val)
            input_metadata.append({"type": "callback", "original_phase": 1})
        elif i < 200:
            # Phase 4: Random noise (novel inputs)
            val = rng.randn() * 0.5
            inputs.append(float(val))
            input_metadata.append({"type": "novel"})
        elif i < 250:
            # Phase 5: Alternating pattern (period 2)
            val = 1.0 if i % 2 == 0 else -1.0
            inputs.append(val)
            input_metadata.append({"type": "alternating"})
        else:
            # Phase 6: Return to original periodic pattern
            val = np.sin(2 * np.pi * i / 5.0)
            inputs.append(val)
            input_metadata.append({"type": "return_periodic"})

    return inputs, input_metadata


def run_simulation():
    """Run full simulation and collect measurements."""
    print("Generating temporally structured inputs...")
    inputs, metadata = generate_temporal_inputs(300, SEED)

    entity = TemporalField(field_extent=50, n_basis=30, n_quadrature=100, seed=SEED)

    log = {
        "states": [],
        "amplitudes": [],
        "field_snapshots": [],
        "temporal_lean": [],
        "present_values": [],
        "past_masses": [],
        "future_masses": [],
        "present_masses": [],
        "coefficients": [],
    }

    print(f"Running {len(inputs)} interactions...")
    for i, x in enumerate(inputs):
        result = entity.update(x)

        log["states"].append(result["state"])
        log["amplitudes"].append(result["amplitude"])
        log["present_values"].append(entity.get_present_value())

        past_m, present_m, future_m = entity.compute_temporal_lean()
        log["past_masses"].append(past_m)
        log["present_masses"].append(present_m)
        log["future_masses"].append(future_m)
        log["temporal_lean"].append({"past": past_m, "present": present_m, "future": future_m})

        # Save field snapshots every 10 steps
        if i % 10 == 0:
            field = entity.evaluate_field()
            log["field_snapshots"].append({
                "step": i,
                "field": field.tolist(),
                "tau": entity.tau.tolist(),
            })

        log["coefficients"].append(result["coefficients"].tolist())

        if i % 50 == 0:
            print(f"  Step {i:3d}: state={result['state']:.4f}, "
                  f"lean=({past_m:.2f}/{present_m:.2f}/{future_m:.2f})")

    # --- Measurements ---
    print("\nComputing measurements...")

    # 1. Past coherence: does the past region encode what happened?
    # Compare field at later time to what actually happened
    past_coherence = []
    for i in range(50, len(inputs)):
        # Look back 10 steps in the field
        past_tau, past_field = entity.get_past_region()
        # The amplitude of the past field should correlate with past inputs
        past_10 = inputs[max(0, i-10):i]
        past_field_energy = float(np.mean(np.abs(past_field[:10])))  # near-past region
        past_input_energy = float(np.mean(np.abs(past_10)))
        if past_input_energy > 0:
            past_coherence.append(past_field_energy / (past_input_energy + 1e-8))

    # 2. Anticipation accuracy: does T(τ>0) predict upcoming inputs?
    anticipation_errors = []
    for i in range(10, len(inputs) - 5):
        # What does the future region say vs what actually happens?
        future_prediction = log["present_values"][i]
        actual_future = np.mean(inputs[i+1:i+6])
        anticipation_errors.append(abs(future_prediction - actual_future))

    # 3. Present sensitivity: how does τ=0 respond to novelty vs familiarity?
    present_deltas = []
    for i in range(1, len(inputs)):
        delta = abs(log["present_values"][i] - log["present_values"][i-1])
        present_deltas.append(delta)

    # Sensitivity by input type
    sensitivity_by_type = {}
    for i in range(1, len(inputs)):
        itype = metadata[i]["type"]
        delta = abs(log["present_values"][i] - log["present_values"][i-1])
        if itype not in sensitivity_by_type:
            sensitivity_by_type[itype] = []
        sensitivity_by_type[itype].append(delta)

    sensitivity_summary = {}
    for itype, deltas in sensitivity_by_type.items():
        sensitivity_summary[itype] = {
            "mean_delta": float(np.mean(deltas)),
            "std_delta": float(np.std(deltas)),
            "n_samples": len(deltas),
        }

    # 4. Temporal lean evolution
    lean_by_phase = {}
    phases = {
        "periodic_1": range(0, 50),
        "ramp": range(50, 100),
        "callback": range(100, 150),
        "novel": range(150, 200),
        "alternating": range(200, 250),
        "return_periodic": range(250, 300),
    }
    for phase_name, phase_range in phases.items():
        phase_lean = [log["temporal_lean"][i] for i in phase_range if i < len(log["temporal_lean"])]
        if phase_lean:
            lean_by_phase[phase_name] = {
                "mean_past": float(np.mean([l["past"] for l in phase_lean])),
                "mean_present": float(np.mean([l["present"] for l in phase_lean])),
                "mean_future": float(np.mean([l["future"] for l in phase_lean])),
            }

    # 5. State coherence: does S behave more coherently than raw input?
    state_autocorr = float(np.corrcoef(log["states"][:-1], log["states"][1:])[0, 1])
    input_autocorr = float(np.corrcoef(inputs[:-1], inputs[1:])[0, 1])

    # Compile results
    results = {
        "past_coherence": {
            "mean": float(np.mean(past_coherence)) if past_coherence else 0.0,
            "std": float(np.std(past_coherence)) if past_coherence else 0.0,
        },
        "anticipation": {
            "mean_error": float(np.mean(anticipation_errors)),
            "std_error": float(np.std(anticipation_errors)),
            "baseline_error": float(np.mean(np.abs(np.diff(inputs)))),
        },
        "present_sensitivity": sensitivity_summary,
        "temporal_lean_by_phase": lean_by_phase,
        "state_coherence": {
            "state_autocorrelation": state_autocorr,
            "input_autocorrelation": input_autocorr,
            "coherence_gain": state_autocorr / (input_autocorr + 1e-8),
        },
        "overall": {
            "mean_state": float(np.mean(log["states"])),
            "std_state": float(np.std(log["states"])),
            "final_temporal_lean": log["temporal_lean"][-1],
        },
    }

    with open(os.path.join(OUTDIR, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Save for visualization
    with open(os.path.join(OUTDIR, "simulation_log.json"), "w") as f:
        json.dump({
            "states": log["states"],
            "amplitudes": log["amplitudes"],
            "present_values": log["present_values"],
            "past_masses": log["past_masses"],
            "future_masses": log["future_masses"],
            "present_masses": log["present_masses"],
            "field_snapshots": log["field_snapshots"],
        }, f)

    print("\nResults saved.")
    return results


if __name__ == "__main__":
    results = run_simulation()
    print(f"\nKey metrics:")
    print(f"  Past coherence: {results['past_coherence']['mean']:.4f}")
    print(f"  Anticipation error: {results['anticipation']['mean_error']:.4f}")
    print(f"  State autocorrelation: {results['state_coherence']['state_autocorrelation']:.4f}")
    print(f"  Input autocorrelation: {results['state_coherence']['input_autocorrelation']:.4f}")
