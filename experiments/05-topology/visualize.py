"""
Test 5 — Topological State Space: Visualization

Generates:
1. 3D UMAP state space plot with category coloring
2. 2D UMAP scatter for clearer category boundaries
3. Reasoning trajectory plots in UMAP space
4. PCA variance explained plot
5. Persistence diagram (if available)
6. Category centroid distance heatmap
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D


OUTDIR = os.path.dirname(os.path.abspath(__file__))

CATEGORY_COLORS = {
    "mathematical": "#e74c3c",
    "emotional": "#3498db",
    "spatial": "#2ecc71",
    "philosophical": "#9b59b6",
    "factual": "#f39c12",
}

CATEGORY_MARKERS = {
    "mathematical": "o",
    "emotional": "s",
    "spatial": "^",
    "philosophical": "D",
    "factual": "v",
}


def load_data():
    labels = np.load(os.path.join(OUTDIR, "labels.npy"), allow_pickle=True)
    umap_3d = np.load(os.path.join(OUTDIR, "umap_3d.npy"))
    umap_2d = np.load(os.path.join(OUTDIR, "umap_2d.npy"))
    with open(os.path.join(OUTDIR, "results.json")) as f:
        results = json.load(f)
    with open(os.path.join(OUTDIR, "trajectories_3d.json")) as f:
        traj_3d = json.load(f)
    with open(os.path.join(OUTDIR, "capture_metadata.json")) as f:
        metadata = json.load(f)
    return labels, umap_3d, umap_2d, results, traj_3d, metadata


def plot_umap_3d(umap_3d, labels):
    """3D UMAP scatter with category coloring."""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection="3d")

    for cat in CATEGORY_COLORS:
        mask = labels == cat
        ax.scatter(umap_3d[mask, 0], umap_3d[mask, 1], umap_3d[mask, 2],
                  c=CATEGORY_COLORS[cat], label=cat, alpha=0.6, s=20,
                  marker=CATEGORY_MARKERS[cat])

    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    ax.set_zlabel("UMAP 3")
    ax.set_title("State Space Topology — GPT-2 Layer 6 Hidden States\n(3D UMAP, cosine metric)")
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "umap_3d.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved umap_3d.png")


def plot_umap_2d(umap_2d, labels):
    """2D UMAP scatter for clearer category visualization."""
    fig, ax = plt.subplots(figsize=(10, 8))

    for cat in CATEGORY_COLORS:
        mask = labels == cat
        ax.scatter(umap_2d[mask, 0], umap_2d[mask, 1],
                  c=CATEGORY_COLORS[cat], label=cat, alpha=0.6, s=30,
                  marker=CATEGORY_MARKERS[cat], edgecolors="white", linewidth=0.3)

    ax.set_xlabel("UMAP 1", fontsize=12)
    ax.set_ylabel("UMAP 2", fontsize=12)
    ax.set_title("Cognitive Category Regions in State Space\n(2D UMAP, cosine metric)", fontsize=14)
    ax.legend(fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "umap_2d.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved umap_2d.png")


def plot_trajectories(traj_3d, metadata):
    """Plot reasoning trajectories in 3D UMAP space."""
    descriptions = metadata.get("trajectory_descriptions", [f"Seq {i}" for i in range(len(traj_3d))])

    # Two views: 3D and 2D projection
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    cmap = plt.cm.tab10
    for i, traj in enumerate(traj_3d):
        traj = np.array(traj)
        color = cmap(i / len(traj_3d))
        label = descriptions[i] if i < len(descriptions) else f"Seq {i}"

        # 2D projection (dim 0 vs dim 1)
        axes[0].plot(traj[:, 0], traj[:, 1], "-o", color=color, markersize=5,
                    label=label, alpha=0.8, linewidth=1.5)
        axes[0].annotate("S", (traj[0, 0], traj[0, 1]), fontsize=7, color=color, fontweight="bold")
        axes[0].annotate("E", (traj[-1, 0], traj[-1, 1]), fontsize=7, color=color, fontweight="bold")

        # 2D projection (dim 1 vs dim 2)
        axes[1].plot(traj[:, 1], traj[:, 2], "-o", color=color, markersize=5,
                    alpha=0.8, linewidth=1.5)
        axes[1].annotate("S", (traj[0, 1], traj[0, 2]), fontsize=7, color=color, fontweight="bold")
        axes[1].annotate("E", (traj[-1, 1], traj[-1, 2]), fontsize=7, color=color, fontweight="bold")

    axes[0].set_xlabel("UMAP 1")
    axes[0].set_ylabel("UMAP 2")
    axes[0].set_title("Reasoning Trajectories (UMAP 1 vs 2)")
    axes[0].legend(fontsize=6, loc="best", ncol=2)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_xlabel("UMAP 2")
    axes[1].set_ylabel("UMAP 3")
    axes[1].set_title("Reasoning Trajectories (UMAP 2 vs 3)")
    axes[1].grid(True, alpha=0.3)

    plt.suptitle("Multi-Step Reasoning Trajectories Through State Space\n(S=Start, E=End)", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "trajectories.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved trajectories.png")


def plot_pca_variance(results):
    """Plot PCA variance explained curve."""
    pca_data = results["intrinsic_dimensionality"]["pca"]
    var_explained = pca_data["pca_variance_explained"]
    cumulative = pca_data["pca_cumulative_20"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Individual variance
    ax1.bar(range(1, len(var_explained) + 1), var_explained, color="#3498db", alpha=0.7)
    ax1.set_xlabel("Principal Component")
    ax1.set_ylabel("Variance Explained")
    ax1.set_title("PCA — Individual Component Variance")
    ax1.grid(True, alpha=0.3, axis="y")

    # Cumulative variance
    ax2.plot(range(1, len(cumulative) + 1), cumulative, "-o", color="#e74c3c", markersize=4)
    for thresh, label in [(0.80, "80%"), (0.90, "90%"), (0.95, "95%")]:
        ax2.axhline(y=thresh, color="gray", linestyle="--", alpha=0.5)
        n_comp = pca_data.get(f"pca_{int(thresh*100)}pct", "?")
        ax2.annotate(f"{label} = {n_comp} PCs", xy=(len(cumulative), thresh),
                    fontsize=8, ha="right", va="bottom")
    ax2.set_xlabel("Number of Components")
    ax2.set_ylabel("Cumulative Variance Explained")
    ax2.set_title("PCA — Cumulative Variance")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.05)

    mle = results["intrinsic_dimensionality"]["mle"]
    fig.suptitle(f"Intrinsic Dimensionality: MLE = {mle['mle_mean']:.1f} "
                 f"(median {mle['mle_median']:.1f}), "
                 f"PCA 95% = {pca_data['pca_95pct']} of 768 dims",
                 fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "dimensionality.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved dimensionality.png")


def plot_centroid_heatmap(results):
    """Heatmap of pairwise category centroid distances."""
    sep = results["category_separability"]
    cats = list(CATEGORY_COLORS.keys())
    n = len(cats)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i, j] = 0.0
            else:
                key1 = f"{cats[i]}_vs_{cats[j]}"
                key2 = f"{cats[j]}_vs_{cats[i]}"
                d = sep["centroid_distances"].get(key1, sep["centroid_distances"].get(key2, 0))
                matrix[i, j] = d

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="equal")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(cats, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(cats, fontsize=10)

    # Annotate cells
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{matrix[i,j]:.3f}", ha="center", va="center", fontsize=9,
                   color="white" if matrix[i,j] > matrix.max()*0.6 else "black")

    plt.colorbar(im, label="Cosine Distance")
    ax.set_title(f"Category Centroid Distances (Cosine)\n"
                 f"Silhouette Score: {sep['silhouette_score']:.4f}, "
                 f"Separation Ratio: {sep['separation_ratio']:.2f}",
                 fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "centroid_distances.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved centroid_distances.png")


def plot_trajectory_metrics(results):
    """Plot trajectory analysis metrics."""
    traj_data = results["trajectory_analysis"]["per_sequence"]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Load descriptions
    try:
        with open(os.path.join(OUTDIR, "capture_metadata.json")) as f:
            meta = json.load(f)
        descriptions = meta.get("trajectory_descriptions", [f"Seq {i}" for i in range(len(traj_data))])
    except FileNotFoundError:
        descriptions = [f"Seq {i}" for i in range(len(traj_data))]

    short_labels = [d[:20] for d in descriptions]

    # Tortuosity
    tort = [t["tortuosity"] for t in traj_data]
    bars = axes[0].barh(range(len(tort)), tort, color="#3498db", alpha=0.7)
    axes[0].set_yticks(range(len(tort)))
    axes[0].set_yticklabels(short_labels, fontsize=7)
    axes[0].set_xlabel("Tortuosity (path/straight)")
    axes[0].set_title("Path Tortuosity")
    axes[0].axvline(x=1.0, color="red", linestyle="--", alpha=0.5, label="Straight line")
    axes[0].legend(fontsize=8)

    # Direction consistency
    cons = [t["mean_direction_consistency"] for t in traj_data]
    axes[1].barh(range(len(cons)), cons, color="#2ecc71", alpha=0.7)
    axes[1].set_yticks(range(len(cons)))
    axes[1].set_yticklabels(short_labels, fontsize=7)
    axes[1].set_xlabel("Mean Direction Consistency (cosine)")
    axes[1].set_title("Direction Consistency")
    axes[1].axvline(x=0.0, color="gray", linestyle="--", alpha=0.5)

    # Step distances
    for i, t in enumerate(traj_data):
        axes[2].plot(range(len(t["step_distances"])), t["step_distances"],
                    "-o", markersize=3, alpha=0.7, label=short_labels[i])
    axes[2].set_xlabel("Step")
    axes[2].set_ylabel("Step Distance (L2)")
    axes[2].set_title("Step-by-Step Distances")
    axes[2].legend(fontsize=5, ncol=2, loc="best")
    axes[2].grid(True, alpha=0.3)

    plt.suptitle("Reasoning Trajectory Analysis", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "trajectory_metrics.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved trajectory_metrics.png")


def main():
    print("Loading data for visualization...")
    labels, umap_3d, umap_2d, results, traj_3d, metadata = load_data()

    print("\nGenerating plots...")
    plot_umap_3d(umap_3d, labels)
    plot_umap_2d(umap_2d, labels)
    plot_trajectories(traj_3d, metadata)
    plot_pca_variance(results)
    plot_centroid_heatmap(results)
    plot_trajectory_metrics(results)
    print("\nAll visualizations complete.")


if __name__ == "__main__":
    main()
