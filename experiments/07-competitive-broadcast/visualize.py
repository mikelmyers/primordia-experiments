"""
Test 7 — Competitive Global Broadcast: Visualization
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR = os.path.dirname(os.path.abspath(__file__))
MODULE_NAMES = ["perceptual", "semantic", "temporal", "affective", "motor", "metacognitive"]
MODULE_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]


def load_results():
    with open(os.path.join(OUTDIR, "results.json")) as f:
        return json.load(f)


def plot_coherence_comparison(results):
    """Compare coherence across modes for each test."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for i, test_name in enumerate(["multimodal", "conflict", "sustained"]):
        ax = axes[i]
        for mode_name in ["hard", "medium", "soft"]:
            if mode_name in results[test_name]:
                coherence = results[test_name][mode_name]["coherence"]
                ax.plot(coherence, label=mode_name, alpha=0.7)
        ax.set_xlabel("Timestep")
        ax.set_ylabel("Coherence (cosine sim)")
        ax.set_title(f"{test_name.capitalize()} Test")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.1, 1.1)

    plt.suptitle("Workspace Coherence Over Time — Three Competition Modes", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "coherence.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved coherence.png")


def plot_switching(results):
    """Visualize which module wins over time."""
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))

    for col, mode_name in enumerate(["hard", "medium"]):
        for row, test_name in enumerate(["multimodal", "conflict", "sustained"]):
            ax = axes[row, col]
            winners = results[test_name][mode_name]["winner_history"]

            # Color-coded scatter of winners
            for mod_idx in range(6):
                timesteps = [t for t, w in enumerate(winners) if w == mod_idx]
                ax.scatter(timesteps, [mod_idx] * len(timesteps),
                          c=MODULE_COLORS[mod_idx], s=10, alpha=0.7,
                          label=MODULE_NAMES[mod_idx] if row == 0 else None)

            ax.set_yticks(range(6))
            ax.set_yticklabels(MODULE_NAMES, fontsize=8)
            ax.set_xlabel("Timestep")
            ax.set_title(f"{test_name.capitalize()} — {mode_name} (τ={'0.1' if mode_name == 'hard' else '1.0'})")

            # Add expected dominant module for multimodal
            if test_name == "multimodal":
                mm_dom = np.load(os.path.join(OUTDIR, "mm_dominant.npy"))
                for t, dom in enumerate(mm_dom):
                    if dom >= 0:
                        ax.axvspan(t - 0.5, t + 0.5, alpha=0.05,
                                  color=MODULE_COLORS[dom])

    axes[0, 0].legend(fontsize=7, ncol=3, loc="upper right")
    plt.suptitle("Module Dominance Over Time", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "switching.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved switching.png")


def plot_summary_comparison(results):
    """Bar chart comparing metrics across modes."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    modes = ["hard", "medium", "soft"]
    mode_colors = ["#e74c3c", "#f39c12", "#3498db"]

    # Coherence
    for i, test in enumerate(["multimodal", "conflict", "sustained"]):
        vals = [results[test].get(m, {}).get("mean_coherence", 0) for m in modes]
        bars = axes[0].bar([i * 4 + j for j in range(3)], vals,
                          color=mode_colors, alpha=0.8, width=0.8)
    axes[0].set_xticks([1, 5, 9])
    axes[0].set_xticklabels(["multimodal", "conflict", "sustained"])
    axes[0].set_ylabel("Mean Coherence")
    axes[0].set_title("Coherence")
    axes[0].legend(modes, fontsize=8)

    # Switching rate
    for i, test in enumerate(["multimodal", "conflict", "sustained"]):
        vals = [results[test].get(m, {}).get("switching_rate", 0) for m in modes]
        axes[1].bar([i * 4 + j for j in range(3)], vals,
                   color=mode_colors, alpha=0.8, width=0.8)
    axes[1].set_xticks([1, 5, 9])
    axes[1].set_xticklabels(["multimodal", "conflict", "sustained"])
    axes[1].set_ylabel("Switching Rate")
    axes[1].set_title("Switching Rate")

    # Unity variance
    for i, test in enumerate(["multimodal", "conflict", "sustained"]):
        vals = [results[test].get(m, {}).get("mean_unity_variance", 0) for m in modes]
        axes[2].bar([i * 4 + j for j in range(3)], vals,
                   color=mode_colors, alpha=0.8, width=0.8)
    axes[2].set_xticks([1, 5, 9])
    axes[2].set_xticklabels(["multimodal", "conflict", "sustained"])
    axes[2].set_ylabel("Mean Workspace Variance")
    axes[2].set_title("Unity Metric (lower = more unified)")

    plt.suptitle("Competition Mode Comparison Across Test Conditions", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved comparison.png")


def main():
    print("Generating visualizations...")
    results = load_results()
    plot_coherence_comparison(results)
    plot_switching(results)
    plot_summary_comparison(results)
    print("All visualizations complete.")


if __name__ == "__main__":
    main()
