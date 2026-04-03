"""
Test 8 — Reflexive State: Visualization
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR = os.path.dirname(os.path.abspath(__file__))


def plot_convergence():
    """Plot fixed-point convergence behavior."""
    with open(os.path.join(OUTDIR, "convergence_histories.json")) as f:
        histories = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Sample convergence trajectories
    sample_idx = np.linspace(0, len(histories)-1, 20, dtype=int)
    for i in sample_idx:
        ax1.plot(histories[i], alpha=0.3, color="#3498db")
    ax1.axhline(y=0.001, color="red", linestyle="--", label="Tolerance (0.001)")
    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("||M_{k+1} - M_k||")
    ax1.set_title("Fixed-Point Convergence (20 sample interactions)")
    ax1.set_yscale("log")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Convergence speed over time
    final_deltas = [h[-1] if h else 0 for h in histories]
    n_iters = [len(h) for h in histories]
    ax2.plot(final_deltas, alpha=0.7, color="#e74c3c", label="Final delta")
    ax2.axhline(y=0.001, color="gray", linestyle="--", alpha=0.5)
    ax2.set_xlabel("Interaction")
    ax2.set_ylabel("Final ||M_{k+1} - M_k||")
    ax2.set_title("Convergence Quality Over 500 Interactions")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "convergence.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved convergence.png")


def plot_trajectories():
    """Plot M trajectory and S-M relationship."""
    ref_S = np.load(os.path.join(OUTDIR, "reflexive_S.npy"))
    ref_M = np.load(os.path.join(OUTDIR, "reflexive_M.npy"))
    ctrl_S = np.load(os.path.join(OUTDIR, "control_S.npy"))
    input_types = np.load(os.path.join(OUTDIR, "input_types.npy"), allow_pickle=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # S norm over time
    ref_S_norm = np.linalg.norm(ref_S, axis=1)
    ctrl_S_norm = np.linalg.norm(ctrl_S, axis=1)
    axes[0, 0].plot(ref_S_norm, label="Reflexive", color="#3498db", alpha=0.7)
    axes[0, 0].plot(ctrl_S_norm, label="Control", color="#e74c3c", alpha=0.7)
    # Mark self-referential inputs
    self_idx = [i for i, t in enumerate(input_types) if t == "self"]
    axes[0, 0].scatter(self_idx, ref_S_norm[self_idx], s=5, color="#2ecc71",
                       alpha=0.5, zorder=5, label="Self-ref inputs")
    axes[0, 0].set_xlabel("Interaction")
    axes[0, 0].set_ylabel("||S||")
    axes[0, 0].set_title("Content State Norm")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(True, alpha=0.3)

    # M norm over time
    ref_M_norm = np.linalg.norm(ref_M, axis=1)
    axes[0, 1].plot(ref_M_norm, label="Self-model ||M||", color="#9b59b6", alpha=0.7)
    axes[0, 1].set_xlabel("Interaction")
    axes[0, 1].set_ylabel("||M||")
    axes[0, 1].set_title("Self-Model Norm")
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(True, alpha=0.3)

    # Self-model accuracy
    ref_cos = np.load(os.path.join(OUTDIR, "reflexive_SM_cosine.npy"))
    ctrl_cos = np.load(os.path.join(OUTDIR, "control_SM_cosine.npy"))
    axes[1, 0].plot(ref_cos, label="Reflexive", color="#3498db", alpha=0.5)
    axes[1, 0].plot(ctrl_cos, label="Control", color="#e74c3c", alpha=0.5)
    # Running mean
    window = 20
    ref_smooth = np.convolve(ref_cos, np.ones(window)/window, mode="valid")
    ctrl_smooth = np.convolve(ctrl_cos, np.ones(window)/window, mode="valid")
    axes[1, 0].plot(range(window-1, len(ref_cos)), ref_smooth, color="#2c3e50", linewidth=2, label="Reflexive (smoothed)")
    axes[1, 0].plot(range(window-1, len(ctrl_cos)), ctrl_smooth, color="#c0392b", linewidth=2, label="Control (smoothed)")
    axes[1, 0].set_xlabel("Interaction")
    axes[1, 0].set_ylabel("Cosine(S, W_g^T·M)")
    axes[1, 0].set_title("Self-Model Accuracy")
    axes[1, 0].legend(fontsize=7)
    axes[1, 0].grid(True, alpha=0.3)

    # PCA of S trajectory — reflexive vs control
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    ref_pca = pca.fit_transform(ref_S)
    ctrl_pca = pca.transform(ctrl_S)

    axes[1, 1].plot(ref_pca[:, 0], ref_pca[:, 1], alpha=0.3, color="#3498db", linewidth=0.5)
    axes[1, 1].scatter(ref_pca[0, 0], ref_pca[0, 1], c="green", s=50, zorder=5, label="Start")
    axes[1, 1].scatter(ref_pca[-1, 0], ref_pca[-1, 1], c="red", s=50, zorder=5, label="End (reflexive)")

    axes[1, 1].plot(ctrl_pca[:, 0], ctrl_pca[:, 1], alpha=0.3, color="#e74c3c", linewidth=0.5)
    axes[1, 1].scatter(ctrl_pca[-1, 0], ctrl_pca[-1, 1], c="orange", s=50, zorder=5, label="End (control)")

    axes[1, 1].set_xlabel("PC1")
    axes[1, 1].set_ylabel("PC2")
    axes[1, 1].set_title("State Trajectory (PCA)")
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(True, alpha=0.3)

    plt.suptitle("Reflexive State — Self-Model Dynamics", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "trajectories.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved trajectories.png")


def plot_self_vs_external():
    """Compare processing of self-referential vs external inputs."""
    with open(os.path.join(OUTDIR, "results.json")) as f:
        results = json.load(f)

    ref = results["self_vs_external"]["reflexive"]
    ctrl = results["self_vs_external"]["control"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # State change comparison
    labels = ["Self-ref", "External"]
    ref_vals = [ref["self_referential"]["mean_state_change"], ref["external"]["mean_state_change"]]
    ctrl_vals = [ctrl["self_referential"]["mean_state_change"], ctrl["external"]["mean_state_change"]]

    x = np.arange(len(labels))
    axes[0].bar(x - 0.15, ref_vals, 0.3, label="Reflexive", color="#3498db", alpha=0.8)
    axes[0].bar(x + 0.15, ctrl_vals, 0.3, label="Control", color="#e74c3c", alpha=0.8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels)
    axes[0].set_ylabel("Mean State Change")
    axes[0].set_title("State Change by Input Type")
    axes[0].legend()

    # Self-model accuracy
    ref_acc = [ref["self_referential"]["mean_self_model_accuracy"],
               ref["external"]["mean_self_model_accuracy"]]
    ctrl_acc = [ctrl["self_referential"]["mean_self_model_accuracy"],
                ctrl["external"]["mean_self_model_accuracy"]]
    axes[1].bar(x - 0.15, ref_acc, 0.3, label="Reflexive", color="#3498db", alpha=0.8)
    axes[1].bar(x + 0.15, ctrl_acc, 0.3, label="Control", color="#e74c3c", alpha=0.8)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].set_ylabel("Self-Model Accuracy (cosine)")
    axes[1].set_title("Self-Model Accuracy by Input Type")
    axes[1].legend()

    # Convergence iterations
    ref_iters = [ref["self_referential"]["mean_convergence_iters"],
                 ref["external"]["mean_convergence_iters"]]
    axes[2].bar(labels, ref_iters, color=["#2ecc71", "#f39c12"], alpha=0.8)
    axes[2].set_ylabel("Mean Iterations to Converge")
    axes[2].set_title("Convergence Speed by Input Type")

    plt.suptitle("Self-Referential vs External Input Processing", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "self_vs_external.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved self_vs_external.png")


def main():
    print("Generating visualizations...")
    plot_convergence()
    plot_trajectories()
    plot_self_vs_external()
    print("All visualizations complete.")


if __name__ == "__main__":
    main()
