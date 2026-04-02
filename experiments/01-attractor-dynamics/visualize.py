"""
Test 1 — Visualization
Primordia Systems LLC — Pre-Paradigm Research

Generates:
1. Trajectory plot: first 3 dimensions of X over time
2. Phase portrait: PCA-reduced 2D state space showing where the system dwells
3. Velocity profile: shows basin entrances/exits
4. Basin dwell analysis
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from sklearn.decomposition import PCA
import json
import os

from attractor_dynamics import run_experiment


def plot_trajectory(sol, save_dir):
    """Plot first 3 dimensions of X over time."""
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle('State Trajectory — First 3 Dimensions', fontsize=14)

    colors = ['#2196F3', '#FF5722', '#4CAF50']
    labels = ['$X_0$', '$X_1$', '$X_2$']

    for i, (ax, color, label) in enumerate(zip(axes, colors, labels)):
        ax.plot(sol.t, sol.y[i], color=color, linewidth=0.5, alpha=0.8)
        ax.set_ylabel(label, fontsize=12)
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
        # Mark the double-well equilibria
        well_pos = np.sqrt(1.0 / (2 * 0.25))  # sqrt(a/2b)
        ax.axhline(y=well_pos, color='red', linestyle=':', alpha=0.3,
                    label=f'Well at ±{well_pos:.2f}')
        ax.axhline(y=-well_pos, color='red', linestyle=':', alpha=0.3)
        if i == 0:
            ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.2)

    axes[-1].set_xlabel('Time', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'trajectory.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved trajectory.png")


def plot_phase_portrait(sol, save_dir):
    """PCA-reduce to 2D and plot phase portrait with density."""
    X = sol.y.T  # (n_time, N)

    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X)

    print(f"  PCA explained variance: {pca.explained_variance_ratio_[0]:.3f}, "
          f"{pca.explained_variance_ratio_[1]:.3f} "
          f"(total: {sum(pca.explained_variance_ratio_):.3f})")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Left: trajectory colored by time
    ax = axes[0]
    points = X_2d.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    t_normalized = sol.t[:-1] / sol.t[-1]
    lc = LineCollection(segments, cmap='viridis', linewidth=0.5, alpha=0.6)
    lc.set_array(t_normalized)
    ax.add_collection(lc)
    ax.set_xlim(X_2d[:, 0].min() * 1.1, X_2d[:, 0].max() * 1.1)
    ax.set_ylim(X_2d[:, 1].min() * 1.1, X_2d[:, 1].max() * 1.1)
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} var)', fontsize=11)
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} var)', fontsize=11)
    ax.set_title('Phase Portrait (colored by time)', fontsize=12)
    plt.colorbar(lc, ax=ax, label='Time (normalized)')
    # Mark start and end
    ax.scatter(*X_2d[0], color='green', s=100, zorder=5, marker='o',
               edgecolors='black', label='Start')
    ax.scatter(*X_2d[-1], color='red', s=100, zorder=5, marker='s',
               edgecolors='black', label='End')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

    # Right: density heatmap — where does the system spend its time
    ax = axes[1]
    hb = ax.hexbin(X_2d[:, 0], X_2d[:, 1], gridsize=50, cmap='hot_r',
                   mincnt=1)
    ax.set_xlabel(f'PC1', fontsize=11)
    ax.set_ylabel(f'PC2', fontsize=11)
    ax.set_title('Dwell Density (where the system spends time)', fontsize=12)
    plt.colorbar(hb, ax=ax, label='Time spent (samples)')
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'phase_portrait.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved phase_portrait.png")

    return pca, X_2d


def plot_velocity_and_basins(sol, basins, save_dir):
    """Plot velocity profile with basin regions highlighted."""
    # Compute velocities
    dt = np.diff(sol.t)
    dX = np.diff(sol.y, axis=1)
    velocities = np.linalg.norm(dX / dt[np.newaxis, :], axis=0)
    velocities = np.append(velocities, velocities[-1])

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle('System Velocity & Basin Analysis', fontsize=14)

    # Velocity profile
    ax = axes[0]
    ax.plot(sol.t, velocities, color='#333333', linewidth=0.5, alpha=0.7)
    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5,
               label='Basin threshold')
    ax.set_ylabel('Velocity (||dX/dt||)', fontsize=11)
    ax.set_yscale('log')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)
    ax.set_title('Velocity Profile', fontsize=12)

    # Highlight basin regions
    colors_cycle = plt.cm.Set2(np.linspace(0, 1, 8))
    for b in basins:
        bid = b['basin_id']
        color = colors_cycle[bid % len(colors_cycle)]
        ax.axvspan(b['t_enter'], b['t_exit'], alpha=0.2, color=color)

    # State norm over time
    ax = axes[1]
    state_norms = np.linalg.norm(sol.y, axis=0)
    ax.plot(sol.t, state_norms, color='#9C27B0', linewidth=0.5, alpha=0.7)
    ax.set_ylabel('State Norm (||X||)', fontsize=11)
    ax.set_xlabel('Time', fontsize=11)
    ax.set_title('State Magnitude Over Time', fontsize=12)
    ax.grid(True, alpha=0.2)

    for b in basins:
        bid = b['basin_id']
        color = colors_cycle[bid % len(colors_cycle)]
        ax.axvspan(b['t_enter'], b['t_exit'], alpha=0.2, color=color)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'velocity_basins.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved velocity_basins.png")


def plot_basin_statistics(basins, stats, save_dir):
    """Plot basin dwell time statistics."""
    if not basins:
        print("  No basins found — skipping basin statistics plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Basin Statistics', fontsize=14)

    # Dwell times
    ax = axes[0]
    dwell_times = [b['dwell_time'] for b in basins]
    basin_ids = [b['basin_id'] for b in basins]
    colors_cycle = plt.cm.Set2(np.linspace(0, 1, 8))
    bar_colors = [colors_cycle[bid % len(colors_cycle)] for bid in basin_ids]
    ax.bar(range(len(dwell_times)), dwell_times, color=bar_colors,
           edgecolor='black', linewidth=0.5)
    ax.set_xlabel('Basin Visit #', fontsize=11)
    ax.set_ylabel('Dwell Time', fontsize=11)
    ax.set_title('Dwell Time per Basin Visit', fontsize=12)
    ax.grid(True, alpha=0.2, axis='y')

    # Time per basin (aggregated)
    ax = axes[1]
    time_stats = stats['time_in_basin_stats']
    if time_stats:
        basin_labels = sorted(time_stats.keys(), key=int)
        total_times = [time_stats[b]['total_time'] for b in basin_labels]
        visits = [time_stats[b]['visits'] for b in basin_labels]
        bar_colors = [colors_cycle[int(b) % len(colors_cycle)] for b in basin_labels]

        x = np.arange(len(basin_labels))
        bars = ax.bar(x, total_times, color=bar_colors, edgecolor='black',
                      linewidth=0.5)
        ax.set_xlabel('Basin ID', fontsize=11)
        ax.set_ylabel('Total Time in Basin', fontsize=11)
        ax.set_title('Aggregate Time per Basin', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels([f'Basin {b}\n({v} visits)' for b, v in
                            zip(basin_labels, visits)], fontsize=9)
        ax.grid(True, alpha=0.2, axis='y')

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'basin_stats.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved basin_stats.png")


def plot_pca_spectrum(sol, save_dir):
    """Show how many dimensions the dynamics actually use."""
    X = sol.y.T
    pca_full = PCA().fit(X)
    cumvar = np.cumsum(pca_full.explained_variance_ratio_)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(1, len(cumvar) + 1), cumvar, 'b-o', markersize=3)
    ax.axhline(y=0.95, color='red', linestyle='--', alpha=0.5,
               label='95% variance')
    ax.axhline(y=0.99, color='orange', linestyle='--', alpha=0.5,
               label='99% variance')

    # Find effective dimensionality
    dim_95 = np.argmax(cumvar >= 0.95) + 1
    dim_99 = np.argmax(cumvar >= 0.99) + 1
    ax.axvline(x=dim_95, color='red', linestyle=':', alpha=0.3)
    ax.axvline(x=dim_99, color='orange', linestyle=':', alpha=0.3)

    ax.set_xlabel('Number of Principal Components', fontsize=11)
    ax.set_ylabel('Cumulative Explained Variance', fontsize=11)
    ax.set_title(f'Effective Dimensionality: {dim_95} dims for 95%, '
                 f'{dim_99} dims for 99%', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)
    ax.set_xlim(0, min(64, len(cumvar)))

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'pca_spectrum.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print(f"  Saved pca_spectrum.png (effective dim: {dim_95} for 95%, "
          f"{dim_99} for 99%)")

    return dim_95, dim_99


def main():
    save_dir = 'experiments/01-attractor-dynamics'
    os.makedirs(save_dir, exist_ok=True)

    print("Running attractor dynamics experiment...")
    result = run_experiment()
    if result is None:
        print("Experiment failed!")
        return

    sol, basins, transitions, stats, system = result

    print("\nGenerating visualizations...")
    plot_trajectory(sol, save_dir)
    pca, X_2d = plot_phase_portrait(sol, save_dir)
    plot_velocity_and_basins(sol, basins, save_dir)
    plot_basin_statistics(basins, stats, save_dir)
    dim_95, dim_99 = plot_pca_spectrum(sol, save_dir)

    # Update results with PCA info
    results_path = os.path.join(save_dir, 'results.json')
    with open(results_path, 'r') as f:
        results = json.load(f)

    results['dimensionality'] = {
        'effective_dim_95pct': int(dim_95),
        'effective_dim_99pct': int(dim_99),
        'pca_var_explained_top2': [
            float(pca.explained_variance_ratio_[0]),
            float(pca.explained_variance_ratio_[1])
        ]
    }

    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nAll visualizations saved to {save_dir}/")
    print(f"Results updated in {results_path}")


if __name__ == '__main__':
    main()
