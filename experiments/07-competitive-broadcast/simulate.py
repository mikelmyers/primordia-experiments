"""
Test 7 — Competitive Global Broadcast: Simulation

Tests three competition modes (hard, medium, soft) on:
1. Multi-modal sequences requiring different specialists at different times
2. Conflicting inputs requiring one interpretation to win
3. Sustained processing requiring one module to hold the workspace
"""

import json
import os
import numpy as np
from workspace import GlobalWorkspace

SEED = 42
OUTDIR = os.path.dirname(os.path.abspath(__file__))


def generate_multimodal_sequence(n_steps=200, seed=42):
    """Generate inputs that require different modules at different times.

    Each segment emphasizes a different module's input channel.
    """
    rng = np.random.RandomState(seed)
    inputs = []
    dominant_module = []

    segment_length = n_steps // 6
    for mod_idx in range(6):
        for _ in range(segment_length):
            x = rng.randn(384) * 0.1  # low baseline
            # Amplify the dominant module's input
            x[mod_idx * 64:(mod_idx + 1) * 64] += rng.randn(64) * 2.0
            inputs.append(x)
            dominant_module.append(mod_idx)

    # Fill remaining with random
    while len(inputs) < n_steps:
        x = rng.randn(384) * 0.5
        inputs.append(x)
        dominant_module.append(-1)

    return np.array(inputs), dominant_module


def generate_conflict_inputs(n_steps=100, seed=42):
    """Generate inputs where multiple modules receive strong signals simultaneously."""
    rng = np.random.RandomState(seed)
    inputs = []
    conflict_pairs = []

    for _ in range(n_steps):
        x = rng.randn(384) * 0.1
        # Pick two competing modules
        m1, m2 = rng.choice(6, 2, replace=False)
        strength1 = rng.uniform(1.0, 3.0)
        strength2 = rng.uniform(1.0, 3.0)
        x[m1 * 64:(m1 + 1) * 64] += rng.randn(64) * strength1
        x[m2 * 64:(m2 + 1) * 64] += rng.randn(64) * strength2
        inputs.append(x)
        conflict_pairs.append((int(m1), int(m2), float(strength1), float(strength2)))

    return np.array(inputs), conflict_pairs


def generate_sustained_inputs(n_steps=150, seed=42):
    """Generate inputs requiring one module to hold workspace for extended period."""
    rng = np.random.RandomState(seed)
    inputs = []
    target_module = []

    # 50 steps: module 0 dominant
    for _ in range(50):
        x = rng.randn(384) * 0.1
        x[:64] += rng.randn(64) * 2.5
        inputs.append(x)
        target_module.append(0)

    # 50 steps: module 0 still dominant but with distractors
    for _ in range(50):
        x = rng.randn(384) * 0.3  # higher baseline noise
        x[:64] += rng.randn(64) * 2.0
        distractor = rng.randint(1, 6)
        x[distractor * 64:(distractor + 1) * 64] += rng.randn(64) * 1.5
        inputs.append(x)
        target_module.append(0)

    # 50 steps: transition to module 3
    for _ in range(50):
        x = rng.randn(384) * 0.1
        x[3 * 64:4 * 64] += rng.randn(64) * 2.5
        inputs.append(x)
        target_module.append(3)

    return np.array(inputs), target_module


def compute_coherence(workspace_history):
    """Workspace coherence: cosine similarity between consecutive states."""
    coherence = []
    for i in range(1, len(workspace_history)):
        w1 = workspace_history[i - 1]
        w2 = workspace_history[i]
        n1 = np.linalg.norm(w1)
        n2 = np.linalg.norm(w2)
        if n1 > 1e-8 and n2 > 1e-8:
            coherence.append(float(np.dot(w1, w2) / (n1 * n2)))
        else:
            coherence.append(0.0)
    return coherence


def compute_switching_rate(winner_history):
    """How often does the dominant module change."""
    switches = sum(1 for i in range(1, len(winner_history))
                   if winner_history[i] != winner_history[i-1])
    return switches / max(1, len(winner_history) - 1)


def compute_unity_metric(workspace_history):
    """Subjective unity: variance of workspace representation (lower = more unified)."""
    variances = [float(np.var(w)) for w in workspace_history]
    return variances


def run_mode(gw, inputs, mode_name, mode_fn):
    """Run a competition mode and collect metrics."""
    gw.reset()
    workspace_history = []
    winner_history = []
    urgency_history = []

    for x in inputs:
        result = mode_fn(x)
        workspace_history.append(result["workspace"])
        winner_history.append(result.get("winner", -1))
        if "urgencies" in result:
            urgency_history.append(result["urgencies"].tolist())

    coherence = compute_coherence(workspace_history)
    switching_rate = compute_switching_rate(winner_history)
    unity = compute_unity_metric(workspace_history)

    return {
        "mode": mode_name,
        "coherence": coherence,
        "mean_coherence": float(np.mean(coherence)),
        "switching_rate": switching_rate,
        "mean_unity_variance": float(np.mean(unity)),
        "winner_history": winner_history,
        "urgency_history": urgency_history,
        "workspace_history": [w.tolist() for w in workspace_history[::10]],  # subsample
    }


def main():
    print("Generating test inputs...")
    multimodal_inputs, mm_dominant = generate_multimodal_sequence(200, SEED)
    conflict_inputs, conflict_pairs = generate_conflict_inputs(100, SEED)
    sustained_inputs, sustained_target = generate_sustained_inputs(150, SEED)

    all_results = {}

    for test_name, inputs in [("multimodal", multimodal_inputs),
                                ("conflict", conflict_inputs),
                                ("sustained", sustained_inputs)]:
        print(f"\n--- {test_name.upper()} TEST ---")
        test_results = {}

        for mode_name, temp in [("hard", 0.1), ("medium", 1.0), ("soft", None)]:
            gw = GlobalWorkspace(workspace_dim=256, seed=SEED)
            if mode_name == "soft":
                result = run_mode(gw, inputs, mode_name, gw.step_soft)
            elif mode_name == "hard":
                result = run_mode(gw, inputs, mode_name,
                                 lambda x, t=temp: gw.step_hard(x, temperature=t))
            else:
                result = run_mode(gw, inputs, mode_name,
                                 lambda x, t=temp: gw.step_medium(x, temperature=t))

            print(f"  {mode_name:8s}: coherence={result['mean_coherence']:.4f}, "
                  f"switching={result['switching_rate']:.4f}, "
                  f"unity_var={result['mean_unity_variance']:.6f}")

            # Don't save full workspace history in results (too large)
            test_results[mode_name] = {
                "mean_coherence": result["mean_coherence"],
                "switching_rate": result["switching_rate"],
                "mean_unity_variance": result["mean_unity_variance"],
                "winner_history": result["winner_history"],
                "coherence": result["coherence"],
            }

        all_results[test_name] = test_results

    # Compute conflict resolution accuracy
    print("\n--- CONFLICT RESOLUTION ANALYSIS ---")
    for mode_name in ["hard", "medium"]:
        gw = GlobalWorkspace(workspace_dim=256, seed=SEED)
        correct = 0
        for i, (x, (m1, m2, s1, s2)) in enumerate(zip(conflict_inputs, conflict_pairs)):
            if mode_name == "hard":
                result = gw.step_hard(x, temperature=0.1)
            else:
                result = gw.step_medium(x, temperature=1.0)
            # "Correct" = the stronger input wins
            expected_winner = m1 if s1 > s2 else m2
            if result["winner"] == expected_winner:
                correct += 1

        accuracy = correct / len(conflict_inputs)
        print(f"  {mode_name:8s} conflict resolution accuracy: {accuracy:.4f}")
        all_results["conflict"][mode_name]["conflict_accuracy"] = accuracy

    # Save results
    with open(os.path.join(OUTDIR, "results.json"), "w") as f:
        json.dump(all_results, f, indent=2)

    # Save data for visualization
    np.save(os.path.join(OUTDIR, "mm_dominant.npy"), np.array(mm_dominant))
    np.save(os.path.join(OUTDIR, "sustained_target.npy"), np.array(sustained_target))

    print(f"\nResults saved.")


if __name__ == "__main__":
    main()
