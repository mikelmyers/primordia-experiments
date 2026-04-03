"""
Test 10 — Unity Primitive: Visualization
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR = os.path.dirname(os.path.abspath(__file__))
MODE_NAMES = ["perception", "reasoning", "affect", "action", "memory"]
MODE_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"]


def plot_lambda_evolution():
    """Plot mode salience weights over time."""
    lambdas = np.load(os.path.join(OUTDIR, "lambdas.npy"))

    fig, ax = plt.subplots(figsize=(14, 6))
    for k in range(5):
        ax.plot(lambdas[:, k], label=MODE_NAMES[k], color=MODE_COLORS[k], alpha=0.8)

    ax.axvline(x=500, color="black", linestyle="--", linewidth=2, label="MODE DESTRUCTION")
    ax.set_xlabel("Interaction")
    ax.set_ylabel("Salience Weight λ_k")
    ax.set_title("Mode Salience Evolution — Unity Primitive\n"
                 "(Affect mode destroyed at t=500)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "lambda_evolution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved lambda_evolution.png")


def plot_unity_error():
    """Plot unity preservation error over time."""
    errors = np.load(os.path.join(OUTDIR, "unity_errors.npy"))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

    ax1.plot(errors, color="#e74c3c", alpha=0.7)
    ax1.axvline(x=500, color="black", linestyle="--", linewidth=2)
    ax1.axhline(y=0.001, color="green", linestyle="--", alpha=0.5, label="Tolerance (0.001)")
    ax1.set_xlabel("Interaction")
    ax1.set_ylabel("||Σ D_k(U) - U||")
    ax1.set_title("Unity Preservation Error")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Zoom on post-destruction
    ax2.plot(range(490, min(600, len(errors))), errors[490:600], color="#e74c3c", linewidth=2)
    ax2.axvline(x=500, color="black", linestyle="--", linewidth=2, label="Destruction event")
    ax2.axhline(y=0.001, color="green", linestyle="--", alpha=0.5, label="Tolerance")
    ax2.set_xlabel("Interaction")
    ax2.set_ylabel("Unity Error")
    ax2.set_title("Post-Destruction Unity Error (Zoomed)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "unity_error.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved unity_error.png")


def plot_expressed_modes():
    """Visualize which mode is expressed over time."""
    expressed = np.load(os.path.join(OUTDIR, "expressed_modes.npy"))
    labels = np.load(os.path.join(OUTDIR, "input_labels.npy"), allow_pickle=True)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

    # Expressed mode scatter
    for k in range(5):
        mask = expressed == k
        timesteps = np.where(mask)[0]
        ax1.scatter(timesteps, [k] * len(timesteps), c=MODE_COLORS[k],
                   s=3, alpha=0.5, label=MODE_NAMES[k])
    ax1.axvline(x=500, color="black", linestyle="--", linewidth=2)
    ax1.set_yticks(range(5))
    ax1.set_yticklabels(MODE_NAMES)
    ax1.set_xlabel("Interaction")
    ax1.set_title("Expressed Mode Over Time")
    ax1.legend(fontsize=8, loc="upper right")

    # Input type scatter (ground truth)
    for k, name in enumerate(MODE_NAMES):
        mask = labels == name
        timesteps = np.where(mask)[0]
        ax2.scatter(timesteps, [k] * len(timesteps), c=MODE_COLORS[k],
                   s=3, alpha=0.5)
    ax2.axvline(x=500, color="black", linestyle="--", linewidth=2)
    ax2.set_yticks(range(5))
    ax2.set_yticklabels(MODE_NAMES)
    ax2.set_xlabel("Interaction")
    ax2.set_title("Input Type (Ground Truth)")

    plt.suptitle("Expressed Mode vs Input Type — Does the Right Mode Activate?", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "expressed_modes.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved expressed_modes.png")


def plot_destruction_analysis():
    """Analyze mode destruction event."""
    with open(os.path.join(OUTDIR, "results.json")) as f:
        results = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Pre vs post lambda distribution
    pre = results["mode_destruction"]["pre_lambdas"]
    post = results["mode_destruction"]["post_lambdas"]

    x = np.arange(5)
    ax1.bar(x - 0.15, pre, 0.3, label="Pre-destruction", color="#3498db", alpha=0.8)
    ax1.bar(x + 0.15, post, 0.3, label="Post-destruction", color="#e74c3c", alpha=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(MODE_NAMES, rotation=30, ha="right")
    ax1.set_ylabel("Mean λ_k")
    ax1.set_title("Salience Redistribution After Mode Destruction")
    ax1.legend()

    # Takeover distribution
    takeover = results["mode_destruction"]["takeover_distribution"]
    if takeover:
        modes = sorted(takeover.keys(), key=lambda k: int(k))
        counts = [takeover[k] for k in modes]
        colors = [MODE_COLORS[int(k)] for k in modes]
        labels_t = [MODE_NAMES[int(k)] for k in modes]
        ax2.bar(labels_t, counts, color=colors, alpha=0.8)
        ax2.set_ylabel("Count")
        ax2.set_title(f"Which Mode Takes Over for 'Affect' Inputs?")

    plt.suptitle("Mode Destruction Analysis — What Happens When a Part of Unity is Removed?",
                 fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "destruction_analysis.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved destruction_analysis.png")


def main():
    print("Generating visualizations...")
    plot_lambda_evolution()
    plot_unity_error()
    plot_expressed_modes()
    plot_destruction_analysis()
    print("All visualizations complete.")


if __name__ == "__main__":
    main()
