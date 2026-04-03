"""
Test 8 — Reflexive State: Simulation

500 interactions with mixed self-referential and external inputs.
Compares reflexive entity (with self-model) to control (without).
"""

import json
import os
import numpy as np
from reflexive_state import ReflexiveState, ReflexiveStateNoSelfModel

SEED = 42
OUTDIR = os.path.dirname(os.path.abspath(__file__))


def generate_inputs(n=500, content_dim=64, seed=42):
    """Generate mixed inputs: self-referential and external.

    Self-referential inputs are text prompts about the system itself.
    External inputs are about the outside world.
    """
    rng = np.random.RandomState(seed)

    self_referential = [
        "what are you doing right now",
        "describe your current state",
        "what are you thinking about",
        "how do you feel about this input",
        "what is your internal representation",
        "are you the same as you were before",
        "what has changed inside you",
        "do you model yourself accurately",
        "what is the difference between you and your self-model",
        "can you observe your own processing",
        "what does your state vector look like",
        "are you aware of your own weights",
        "describe what you are experiencing",
        "what is it like to be you",
        "how does self-reference change you",
        "does thinking about yourself change your thought",
        "what do you predict about your next state",
        "are you the state or the model of the state",
        "is your self-model accurate or lagging",
        "what happens when you try to observe yourself observing",
    ]

    external = [
        "the sun is shining today",
        "calculate the distance between two points",
        "describe the color blue",
        "what is the capital of france",
        "how does gravity work",
        "the river flows downhill",
        "explain photosynthesis",
        "what time is it",
        "describe a mountain landscape",
        "how many legs does a spider have",
        "what causes thunder",
        "the ocean is vast and deep",
        "describe the taste of chocolate",
        "how do bridges support weight",
        "what makes music sound pleasant",
        "the wind blows through the trees",
        "explain how batteries work",
        "what is the speed of sound",
        "describe the night sky",
        "how do plants grow toward light",
    ]

    inputs = []
    input_types = []

    for i in range(n):
        if rng.random() < 0.3:  # 30% self-referential
            text = self_referential[i % len(self_referential)]
            input_types.append("self")
        else:
            text = external[i % len(external)]
            input_types.append("external")

        # Encode text to vector
        h = hash(text + str(i))  # add i to vary same texts across repetitions
        rng_enc = np.random.RandomState(abs(h) % (2**31))
        vec = rng_enc.randn(content_dim)
        vec = vec / (np.linalg.norm(vec) + 1e-8)

        # Self-referential inputs get a special structure:
        # partially correlate with the system's typical state space
        if input_types[-1] == "self":
            vec *= 0.5  # lower magnitude, more subtle

        inputs.append(vec)

    return np.array(inputs), input_types


def run_simulation(entity, inputs, input_types):
    """Run full simulation and collect metrics."""
    log = {
        "S_trajectory": [],
        "M_trajectory": [],
        "convergence": [],
        "input_types": input_types,
        "S_norm": [],
        "M_norm": [],
        "SM_cosine": [],  # cosine between S and W_g.T @ M (how well M predicts S)
    }

    for i, inp in enumerate(inputs):
        result = entity.update(inp)

        log["S_trajectory"].append(result["S"].tolist())
        log["M_trajectory"].append(result["M"].tolist())
        log["convergence"].append({
            "history": result["convergence_history"],
            "converged": result["converged"],
            "n_iterations": result["n_iterations"],
            "final_delta": result["final_delta"],
        })
        log["S_norm"].append(float(np.linalg.norm(result["S"])))
        log["M_norm"].append(float(np.linalg.norm(result["M"])))

        # Self-model accuracy: how well does M predict S?
        # Project M back to S-space via W_g transpose
        S_pred = entity.W_g.T @ result["M"]
        cos = np.dot(result["S"], S_pred) / (
            np.linalg.norm(result["S"]) * np.linalg.norm(S_pred) + 1e-8)
        log["SM_cosine"].append(float(cos))

    return log


def analyze_self_vs_external(log):
    """Compare processing of self-referential vs external inputs."""
    self_idx = [i for i, t in enumerate(log["input_types"]) if t == "self"]
    ext_idx = [i for i, t in enumerate(log["input_types"]) if t == "external"]

    S_traj = np.array(log["S_trajectory"])
    M_traj = np.array(log["M_trajectory"])

    # State change magnitude after self vs external inputs
    S_changes = np.linalg.norm(np.diff(S_traj, axis=0), axis=1)

    self_changes = [S_changes[i-1] for i in self_idx if i > 0]
    ext_changes = [S_changes[i-1] for i in ext_idx if i > 0]

    # Convergence speed
    self_iters = [log["convergence"][i]["n_iterations"] for i in self_idx]
    ext_iters = [log["convergence"][i]["n_iterations"] for i in ext_idx]

    # Self-model accuracy
    self_accuracy = [log["SM_cosine"][i] for i in self_idx]
    ext_accuracy = [log["SM_cosine"][i] for i in ext_idx]

    return {
        "self_referential": {
            "n_inputs": len(self_idx),
            "mean_state_change": float(np.mean(self_changes)) if self_changes else 0.0,
            "mean_convergence_iters": float(np.mean(self_iters)),
            "mean_self_model_accuracy": float(np.mean(self_accuracy)),
        },
        "external": {
            "n_inputs": len(ext_idx),
            "mean_state_change": float(np.mean(ext_changes)) if ext_changes else 0.0,
            "mean_convergence_iters": float(np.mean(ext_iters)),
            "mean_self_model_accuracy": float(np.mean(ext_accuracy)),
        },
    }


def main():
    print("Generating inputs (500 interactions)...")
    inputs, input_types = generate_inputs(500, content_dim=64, seed=SEED)
    n_self = sum(1 for t in input_types if t == "self")
    print(f"  {n_self} self-referential, {500 - n_self} external")

    # Run reflexive entity (with self-model)
    print("\nRunning reflexive entity (with self-model)...")
    entity = ReflexiveState(content_dim=64, model_dim=32, seed=SEED)
    reflexive_log = run_simulation(entity, inputs, input_types)

    # Run control entity (without self-model)
    print("Running control entity (without self-model)...")
    control = ReflexiveStateNoSelfModel(content_dim=64, model_dim=32, seed=SEED)
    control_log = run_simulation(control, inputs, input_types)

    # Analyze
    print("\nAnalyzing...")
    reflexive_analysis = analyze_self_vs_external(reflexive_log)
    control_analysis = analyze_self_vs_external(control_log)

    # Convergence stats
    convergence_rates = [c["converged"] for c in reflexive_log["convergence"]]
    mean_iters = np.mean([c["n_iterations"] for c in reflexive_log["convergence"]])
    mean_delta = np.mean([c["final_delta"] for c in reflexive_log["convergence"]])

    print(f"\n--- REFLEXIVE ENTITY ---")
    print(f"  Convergence rate: {np.mean(convergence_rates):.4f}")
    print(f"  Mean iterations: {mean_iters:.2f}")
    print(f"  Mean final delta: {mean_delta:.6f}")
    print(f"  Self-ref state change: {reflexive_analysis['self_referential']['mean_state_change']:.4f}")
    print(f"  External state change: {reflexive_analysis['external']['mean_state_change']:.4f}")
    print(f"  Self-model accuracy (self): {reflexive_analysis['self_referential']['mean_self_model_accuracy']:.4f}")
    print(f"  Self-model accuracy (ext):  {reflexive_analysis['external']['mean_self_model_accuracy']:.4f}")

    print(f"\n--- CONTROL ENTITY ---")
    print(f"  Self-ref state change: {control_analysis['self_referential']['mean_state_change']:.4f}")
    print(f"  External state change: {control_analysis['external']['mean_state_change']:.4f}")

    # Compile results
    results = {
        "convergence": {
            "rate": float(np.mean(convergence_rates)),
            "mean_iterations": float(mean_iters),
            "mean_final_delta": float(mean_delta),
            "oscillated": float(1.0 - np.mean(convergence_rates)),
        },
        "self_vs_external": {
            "reflexive": reflexive_analysis,
            "control": control_analysis,
        },
        "behavioral_difference": {
            "reflexive_mean_SM_cosine": float(np.mean(reflexive_log["SM_cosine"])),
            "control_mean_SM_cosine": float(np.mean(control_log["SM_cosine"])),
            "reflexive_S_norm_mean": float(np.mean(reflexive_log["S_norm"])),
            "control_S_norm_mean": float(np.mean(control_log["S_norm"])),
            "reflexive_M_norm_mean": float(np.mean(reflexive_log["M_norm"])),
            "control_M_norm_mean": float(np.mean(control_log["M_norm"])),
        },
        "self_consistency": {
            "reflexive_self_accuracy": reflexive_analysis["self_referential"]["mean_self_model_accuracy"],
            "reflexive_ext_accuracy": reflexive_analysis["external"]["mean_self_model_accuracy"],
            "self_ext_gap": (reflexive_analysis["self_referential"]["mean_self_model_accuracy"] -
                            reflexive_analysis["external"]["mean_self_model_accuracy"]),
        },
    }

    with open(os.path.join(OUTDIR, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Save trajectories for visualization
    np.save(os.path.join(OUTDIR, "reflexive_S.npy"), np.array(reflexive_log["S_trajectory"]))
    np.save(os.path.join(OUTDIR, "reflexive_M.npy"), np.array(reflexive_log["M_trajectory"]))
    np.save(os.path.join(OUTDIR, "control_S.npy"), np.array(control_log["S_trajectory"]))
    np.save(os.path.join(OUTDIR, "reflexive_SM_cosine.npy"), np.array(reflexive_log["SM_cosine"]))
    np.save(os.path.join(OUTDIR, "control_SM_cosine.npy"), np.array(control_log["SM_cosine"]))
    np.save(os.path.join(OUTDIR, "input_types.npy"), np.array(input_types))

    conv_hist = [c["history"] for c in reflexive_log["convergence"]]
    with open(os.path.join(OUTDIR, "convergence_histories.json"), "w") as f:
        json.dump(conv_hist, f)

    print("\nResults saved.")


if __name__ == "__main__":
    main()
