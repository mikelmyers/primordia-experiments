"""
Test 9 — Temporal Field: Visualization
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR = os.path.dirname(os.path.abspath(__file__))


def load_data():
    with open(os.path.join(OUTDIR, "simulation_log.json")) as f:
        log = json.load(f)
    with open(os.path.join(OUTDIR, "results.json")) as f:
        results = json.load(f)
    return log, results


def plot_field_evolution(log):
    """Plot the temporal field T(τ) at multiple time points."""
    snapshots = log["field_snapshots"]
    n_snap = len(snapshots)

    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    axes = axes.flat

    # Select 9 representative snapshots
    indices = np.linspace(0, n_snap - 1, 9, dtype=int)
    for ax_idx, snap_idx in enumerate(indices):
        snap = snapshots[snap_idx]
        tau = np.array(snap["tau"])
        field = np.array(snap["field"])

        ax = axes[ax_idx]
        ax.fill_between(tau[tau < 0], field[tau < 0], alpha=0.3, color="#3498db", label="Past")
        ax.fill_between(tau[tau > 0], field[tau > 0], alpha=0.3, color="#e74c3c", label="Future")
        ax.plot(tau, field, color="#2c3e50", linewidth=1)
        ax.axvline(x=0, color="green", linestyle="--", alpha=0.7, label="Present")
        ax.set_title(f"Step {snap['step']}", fontsize=10)
        ax.set_xlabel("τ (internal time)")
        ax.set_ylabel("T(τ)")
        ax.set_xlim(-50, 50)
        if ax_idx == 0:
            ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    plt.suptitle("Temporal Field Evolution — T(τ) Over 300 Interactions\n"
                 "(Past=blue, Future=red, Present=green line)", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "field_evolution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved field_evolution.png")


def plot_temporal_lean(log):
    """Plot how the temporal lean evolves."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

    steps = range(len(log["past_masses"]))
    ax1.stackplot(steps,
                  log["past_masses"],
                  log["present_masses"],
                  log["future_masses"],
                  labels=["Past", "Present", "Future"],
                  colors=["#3498db", "#2ecc71", "#e74c3c"],
                  alpha=0.7)
    ax1.set_xlabel("Interaction")
    ax1.set_ylabel("Fraction of Field Mass")
    ax1.set_title("Temporal Lean — Where Does the Field's Mass Concentrate?")
    ax1.legend(loc="upper right")
    ax1.set_ylim(0, 1)

    # Phase boundaries
    for boundary, label in [(50, "→Ramp"), (100, "→Callback"),
                             (150, "→Novel"), (200, "→Alternating"),
                             (250, "→Return")]:
        ax1.axvline(x=boundary, color="gray", linestyle="--", alpha=0.5)
        ax1.text(boundary + 2, 0.95, label, fontsize=7, va="top")

    # State vs input
    ax2.plot(log["amplitudes"], alpha=0.4, color="#e74c3c", label="Input amplitude")
    ax2.plot(log["states"], alpha=0.7, color="#3498db", label="Integrated state S")
    ax2.plot(log["present_values"], alpha=0.5, color="#2ecc71", label="Present value T(0)")
    ax2.set_xlabel("Interaction")
    ax2.set_ylabel("Value")
    ax2.set_title("Input vs Integrated State vs Present Field Value")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    for boundary in [50, 100, 150, 200, 250]:
        ax2.axvline(x=boundary, color="gray", linestyle="--", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "temporal_lean.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved temporal_lean.png")


def plot_sensitivity(results):
    """Plot present sensitivity by input type."""
    sens = results["present_sensitivity"]

    fig, ax = plt.subplots(figsize=(10, 5))

    types = list(sens.keys())
    means = [sens[t]["mean_delta"] for t in types]
    stds = [sens[t]["std_delta"] for t in types]
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]

    bars = ax.bar(types, means, yerr=stds, color=colors[:len(types)],
                 alpha=0.7, edgecolor="white", capsize=5)

    ax.set_xlabel("Input Type")
    ax.set_ylabel("Mean |ΔT(0)| (Present Sensitivity)")
    ax.set_title("Present Sensitivity by Input Type\n(How much does τ=0 respond?)")
    ax.grid(True, alpha=0.3, axis="y")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "sensitivity.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved sensitivity.png")


def plot_anticipation(results, log):
    """Plot anticipation accuracy and coherence."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Anticipation vs baseline
    ant = results["anticipation"]
    labels = ["Field Anticipation", "Baseline (Δinput)"]
    vals = [ant["mean_error"], ant["baseline_error"]]
    ax1.bar(labels, vals, color=["#3498db", "#e74c3c"], alpha=0.8)
    for i, v in enumerate(vals):
        ax1.text(i, v + 0.01, f"{v:.4f}", ha="center", fontsize=10)
    ax1.set_ylabel("Mean Absolute Error")
    ax1.set_title("Anticipation Accuracy\n(Lower = better prediction of next input)")

    # Autocorrelation comparison
    coh = results["state_coherence"]
    labels2 = ["State S\n(integrated)", "Raw Input"]
    vals2 = [coh["state_autocorrelation"], coh["input_autocorrelation"]]
    colors2 = ["#3498db", "#e74c3c"]
    ax2.bar(labels2, vals2, color=colors2, alpha=0.8)
    for i, v in enumerate(vals2):
        ax2.text(i, v + 0.01, f"{v:.4f}", ha="center", fontsize=10)
    ax2.set_ylabel("Autocorrelation (lag-1)")
    ax2.set_title("State Coherence\n(Higher = smoother temporal dynamics)")

    plt.suptitle("Does Having Time Improve Temporal Processing?", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "anticipation.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved anticipation.png")


def main():
    print("Generating visualizations...")
    log, results = load_data()
    plot_field_evolution(log)
    plot_temporal_lean(log)
    plot_sensitivity(results)
    plot_anticipation(results, log)
    print("All visualizations complete.")


if __name__ == "__main__":
    main()
