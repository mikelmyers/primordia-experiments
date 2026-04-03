"""
Test 6 — Local Learning Only: Visualization

Generates receptive field plots, selectivity distributions, training curves,
and comparison with baseline.
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR = os.path.dirname(os.path.abspath(__file__))


def plot_receptive_fields():
    """Plot receptive fields of the most selective nodes."""
    W_in = np.load(os.path.join(OUTDIR, "W_in.npy"))
    selectivity = np.load(os.path.join(OUTDIR, "selectivity_per_node.npy"))
    preferred = np.load(os.path.join(OUTDIR, "preferred_class.npy"))

    # Top 25 most selective nodes
    top_idx = np.argsort(selectivity)[-25:][::-1]

    fig, axes = plt.subplots(5, 5, figsize=(12, 12))
    for i, ax in enumerate(axes.flat):
        if i < len(top_idx):
            node_idx = top_idx[i]
            rf = W_in[node_idx].reshape(28, 28)
            ax.imshow(rf, cmap="RdBu_r", aspect="equal")
            ax.set_title(f"Node {node_idx}\nsel={selectivity[node_idx]:.3f}, "
                        f"pref={preferred[node_idx]}", fontsize=8)
        ax.axis("off")

    plt.suptitle("Receptive Fields of 25 Most Selective Nodes\n(Input weights reshaped to 28x28)",
                 fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "receptive_fields.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved receptive_fields.png")


def plot_selectivity():
    """Plot selectivity distribution across all nodes."""
    selectivity = np.load(os.path.join(OUTDIR, "selectivity_per_node.npy"))
    preferred = np.load(os.path.join(OUTDIR, "preferred_class.npy"))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram of selectivity
    ax1.hist(selectivity, bins=50, color="#3498db", alpha=0.7, edgecolor="white")
    ax1.axvline(x=0.3, color="orange", linestyle="--", label="Moderate threshold (0.3)")
    ax1.axvline(x=0.5, color="red", linestyle="--", label="High threshold (0.5)")
    ax1.set_xlabel("Selectivity Index")
    ax1.set_ylabel("Number of Nodes")
    ax1.set_title("Selectivity Distribution Across All Nodes")
    ax1.legend(fontsize=9)

    # Preferred class distribution
    unique, counts = np.unique(preferred, return_counts=True)
    ax2.bar(unique, counts, color="#2ecc71", alpha=0.7, edgecolor="white")
    ax2.set_xlabel("Preferred Digit Class")
    ax2.set_ylabel("Number of Nodes")
    ax2.set_title("How Many Nodes Prefer Each Class")
    ax2.set_xticks(unique)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "selectivity.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved selectivity.png")


def plot_training_curves():
    """Plot training statistics over time."""
    with open(os.path.join(OUTDIR, "training_log.json")) as f:
        log = json.load(f)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Weight magnitude
    steps = [s["step"] for s in log["weight_stats"]]
    w_mean = [s["W_rec_mean"] for s in log["weight_stats"]]
    w_max = [s["W_rec_max"] for s in log["weight_stats"]]
    axes[0, 0].plot(steps, w_mean, label="Mean |W_rec|", color="#3498db")
    axes[0, 0].plot(steps, w_max, label="Max |W_rec|", color="#e74c3c", alpha=0.7)
    axes[0, 0].set_xlabel("Step")
    axes[0, 0].set_ylabel("Weight Magnitude")
    axes[0, 0].set_title("Recurrent Weight Evolution")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Activation sparsity
    act_sparsity = [s["sparsity"] for s in log["activation_stats"]]
    act_mean = [s["mean_abs"] for s in log["activation_stats"]]
    axes[0, 1].plot(steps, act_sparsity, label="Sparsity (<0.1)", color="#2ecc71")
    axes[0, 1].set_xlabel("Step")
    axes[0, 1].set_ylabel("Fraction of Near-Zero Nodes")
    axes[0, 1].set_title("Activation Sparsity Over Training")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Threshold evolution
    th_mean = [s["mean"] for s in log["threshold_stats"]]
    th_std = [s["std"] for s in log["threshold_stats"]]
    th_mean = np.array(th_mean)
    th_std = np.array(th_std)
    axes[1, 0].plot(steps, th_mean, label="Mean threshold", color="#9b59b6")
    axes[1, 0].fill_between(steps, th_mean - th_std, th_mean + th_std, alpha=0.2, color="#9b59b6")
    axes[1, 0].set_xlabel("Step")
    axes[1, 0].set_ylabel("Threshold Value")
    axes[1, 0].set_title("Homeostatic Threshold Evolution")
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Input weight evolution
    w_in_mean = [s["W_in_mean"] for s in log["weight_stats"]]
    w_in_max = [s["W_in_max"] for s in log["weight_stats"]]
    axes[1, 1].plot(steps, w_in_mean, label="Mean |W_in|", color="#f39c12")
    axes[1, 1].plot(steps, w_in_max, label="Max |W_in|", color="#e74c3c", alpha=0.7)
    axes[1, 1].set_xlabel("Step")
    axes[1, 1].set_ylabel("Weight Magnitude")
    axes[1, 1].set_title("Input Weight Evolution")
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.suptitle("Training Dynamics — Local Learning Network", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "training_curves.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved training_curves.png")


def plot_comparison():
    """Plot comparison between local learning and baseline."""
    with open(os.path.join(OUTDIR, "results.json")) as f:
        results = json.load(f)

    fig, ax = plt.subplots(figsize=(8, 5))

    labels = ["Local Learning\n(Hebbian)", "Baseline\n(Backprop Autoencoder)"]
    sil_scores = [
        results["comparison"]["local_silhouette"],
        results["comparison"]["baseline_silhouette"],
    ]
    colors = ["#3498db", "#e74c3c"]

    bars = ax.bar(labels, sil_scores, color=colors, alpha=0.8, edgecolor="white", width=0.5)
    for bar, val in zip(bars, sil_scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{val:.4f}", ha="center", fontsize=11)

    ax.set_ylabel("Silhouette Score")
    ax.set_title("Representational Quality: Local Learning vs Backprop Baseline\n"
                 "(Higher = better class separation in learned representations)")
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylim(bottom=min(0, min(sil_scores) - 0.05))

    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved comparison.png")


def main():
    print("Generating visualizations...")
    plot_receptive_fields()
    plot_selectivity()
    plot_training_curves()
    plot_comparison()
    print("All visualizations complete.")


if __name__ == "__main__":
    main()
