"""
Test 2 — Visualization
Primordia Systems LLC — Pre-Paradigm Research

Generates:
1. State drift plot over time
2. UMAP trajectory of state evolution
3. Sensitivity curve
4. Response consistency analysis
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import json
import os

from persistent_entity import PersistentEntity
from simulate import run_simulation


def plot_drift(results, save_dir):
    """Plot L2 distance from initial state over interactions."""
    drift_log = results['drift_log']
    interactions = [d['interaction'] for d in drift_log]
    drifts = [d['drift_from_origin'] for d in drift_log]
    norms = [d['state_norm'] for d in drift_log]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle('State Drift Over 1000 Interactions', fontsize=14)

    ax = axes[0]
    ax.plot(interactions, drifts, 'b-o', markersize=5, linewidth=2)
    ax.set_ylabel('L2 Distance from S(0)', fontsize=11)
    ax.set_title('Drift from Origin — How far has the entity wandered?', fontsize=12)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(interactions, norms, 'r-o', markersize=5, linewidth=2)
    ax.set_ylabel('State Norm ||S(t)||', fontsize=11)
    ax.set_xlabel('Interaction', fontsize=11)
    ax.set_title('State Magnitude — Is the entity growing or stabilizing?', fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'drift.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved drift.png")


def plot_sensitivity(history, save_dir):
    """Plot how sensitivity changes over time — does the entity become rigid?"""
    interactions = [h['interaction'] for h in history]
    deltas = [h['delta_norm'] for h in history]
    categories = [h['category'] for h in history]

    fig, axes = plt.subplots(2, 1, figsize=(14, 9))
    fig.suptitle('Sensitivity Analysis — Does the Entity Develop Habits?', fontsize=14)

    # Raw sensitivity over time
    ax = axes[0]
    ax.scatter(interactions, deltas, c=range(len(interactions)),
               cmap='viridis', s=3, alpha=0.5)
    # Rolling average
    window = 50
    if len(deltas) >= window:
        rolling_avg = np.convolve(deltas, np.ones(window)/window, mode='valid')
        ax.plot(range(window-1, len(deltas)), rolling_avg, color='red',
                linewidth=2, label=f'Rolling avg (window={window})')
    ax.set_ylabel('State Change |ΔS|', fontsize=11)
    ax.set_xlabel('Interaction', fontsize=11)
    ax.set_title('Response Magnitude Over Time', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

    # Sensitivity by category over time
    ax = axes[1]
    cat_colors = {
        'questions': '#2196F3',
        'statements': '#4CAF50',
        'emotional': '#FF5722',
        'contradictions': '#9C27B0',
        'abstract': '#FF9800',
    }
    for cat, color in cat_colors.items():
        cat_interactions = [interactions[i] for i in range(len(interactions))
                           if categories[i] == cat]
        cat_deltas = [deltas[i] for i in range(len(interactions))
                     if categories[i] == cat]
        if cat_interactions:
            ax.scatter(cat_interactions, cat_deltas, c=color, s=5, alpha=0.4,
                      label=cat)

    ax.set_ylabel('State Change |ΔS|', fontsize=11)
    ax.set_xlabel('Interaction', fontsize=11)
    ax.set_title('Sensitivity by Input Category', fontsize=12)
    ax.legend(fontsize=9, markerscale=3)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'sensitivity.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved sensitivity.png")


def plot_state_trajectory(entity, save_dir):
    """
    Visualize state trajectory using PCA (UMAP requires extra dep).
    Color by time to show the path of state evolution.
    """
    if not entity.state_snapshots:
        print("  No state snapshots — skipping trajectory plot")
        return

    states = np.array(entity.state_snapshots)
    n_states = len(states)

    # PCA to 3D
    pca = PCA(n_components=3)
    states_3d = pca.fit_transform(states)

    var_explained = pca.explained_variance_ratio_
    print(f"  PCA variance explained: {var_explained[0]:.3f}, "
          f"{var_explained[1]:.3f}, {var_explained[2]:.3f} "
          f"(total: {sum(var_explained):.3f})")

    fig = plt.figure(figsize=(16, 6))

    # 2D projection (PC1 vs PC2)
    ax1 = fig.add_subplot(131)
    scatter = ax1.scatter(states_3d[:, 0], states_3d[:, 1],
                         c=range(n_states), cmap='viridis', s=2, alpha=0.5)
    ax1.scatter(*states_3d[0, :2], color='green', s=100, zorder=5,
               marker='o', edgecolors='black', label='Start')
    ax1.scatter(*states_3d[-1, :2], color='red', s=100, zorder=5,
               marker='s', edgecolors='black', label='End')
    ax1.set_xlabel(f'PC1 ({var_explained[0]:.1%})', fontsize=10)
    ax1.set_ylabel(f'PC2 ({var_explained[1]:.1%})', fontsize=10)
    ax1.set_title('State Trajectory (PC1 vs PC2)', fontsize=11)
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.2)
    plt.colorbar(scatter, ax=ax1, label='Interaction #')

    # PC1 vs PC3
    ax2 = fig.add_subplot(132)
    scatter2 = ax2.scatter(states_3d[:, 0], states_3d[:, 2],
                          c=range(n_states), cmap='viridis', s=2, alpha=0.5)
    ax2.scatter(states_3d[0, 0], states_3d[0, 2], color='green', s=100,
               zorder=5, marker='o', edgecolors='black')
    ax2.scatter(states_3d[-1, 0], states_3d[-1, 2], color='red', s=100,
               zorder=5, marker='s', edgecolors='black')
    ax2.set_xlabel(f'PC1 ({var_explained[0]:.1%})', fontsize=10)
    ax2.set_ylabel(f'PC3 ({var_explained[2]:.1%})', fontsize=10)
    ax2.set_title('State Trajectory (PC1 vs PC3)', fontsize=11)
    ax2.grid(True, alpha=0.2)

    # PC components over time
    ax3 = fig.add_subplot(133)
    for i, (label, color) in enumerate(zip(
            ['PC1', 'PC2', 'PC3'], ['#2196F3', '#FF5722', '#4CAF50'])):
        ax3.plot(range(n_states), states_3d[:, i], color=color,
                linewidth=0.8, alpha=0.7, label=label)
    ax3.set_xlabel('Interaction', fontsize=10)
    ax3.set_ylabel('PC Value', fontsize=10)
    ax3.set_title('Principal Components Over Time', fontsize=11)
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'trajectory.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved trajectory.png")

    # Also save PCA info
    return {
        'variance_explained': var_explained.tolist(),
        'n_components_95pct': int(np.argmax(
            np.cumsum(PCA().fit(states).explained_variance_ratio_) >= 0.95
        ) + 1),
    }


def plot_response_consistency(results, save_dir):
    """Visualize how the same input produces different responses over time."""
    consistency = results['response_consistency']
    probe_sens = results['probe_sensitivities']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Response Consistency — Same Input at Different Times', fontsize=14)

    # Cosine similarity between probe responses
    ax = axes[0]
    pairs = sorted(consistency.keys())
    cos_sims = [consistency[p]['cosine_similarity'] for p in pairs]
    l2_dists = [consistency[p]['l2_distance'] for p in pairs]

    x = range(len(pairs))
    bars = ax.bar(x, cos_sims, color='#2196F3', edgecolor='black', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(pairs, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Cosine Similarity', fontsize=11)
    ax.set_title('Response Similarity Across Time', fontsize=12)
    ax.axhline(y=1.0, color='green', linestyle='--', alpha=0.3, label='Perfect consistency')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2, axis='y')

    # Sensitivity to probe over time
    ax = axes[1]
    times = sorted([int(k) for k in probe_sens.keys()])
    sens_vals = [probe_sens[str(t)] for t in times]
    ax.plot(times, sens_vals, 'ro-', markersize=8, linewidth=2)
    ax.set_xlabel('Interaction', fontsize=11)
    ax.set_ylabel('Sensitivity to Probe Input', fontsize=11)
    ax.set_title('How Much the Probe Input Would Change State', fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'consistency.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved consistency.png")


def plot_dimension_analysis(entity, save_dir):
    """Analyze which dimensions are active and how they evolve."""
    states = np.array(entity.state_snapshots)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Dimension-Level Analysis', fontsize=14)

    # Heatmap of state over time (subsample for visibility)
    ax = axes[0, 0]
    step = max(1, len(states) // 200)
    im = ax.imshow(states[::step].T, aspect='auto', cmap='RdBu_r',
                   interpolation='nearest')
    ax.set_xlabel('Interaction (subsampled)', fontsize=10)
    ax.set_ylabel('Dimension', fontsize=10)
    ax.set_title('State Heatmap Over Time', fontsize=11)
    plt.colorbar(im, ax=ax, label='Activation')

    # Final state bar chart
    ax = axes[0, 1]
    final_state = entity.S
    sorted_idx = np.argsort(np.abs(final_state))[::-1]
    ax.bar(range(len(final_state)), final_state[sorted_idx],
           color=np.where(final_state[sorted_idx] > 0, '#2196F3', '#FF5722'),
           width=1.0)
    ax.set_xlabel('Dimension (sorted by magnitude)', fontsize=10)
    ax.set_ylabel('Activation', fontsize=10)
    ax.set_title('Final State — Sorted by Magnitude', fontsize=11)
    ax.grid(True, alpha=0.2, axis='y')

    # Variance per dimension over time
    ax = axes[1, 0]
    dim_variance = np.var(states, axis=0)
    ax.bar(range(len(dim_variance)), np.sort(dim_variance)[::-1],
           color='#4CAF50', width=1.0)
    ax.set_xlabel('Dimension (sorted by variance)', fontsize=10)
    ax.set_ylabel('Variance Over Time', fontsize=10)
    ax.set_title('Which Dimensions Changed Most?', fontsize=11)
    ax.grid(True, alpha=0.2, axis='y')

    # Autocorrelation of state changes
    ax = axes[1, 1]
    deltas = np.diff(states, axis=0)
    delta_norms = np.linalg.norm(deltas, axis=1)
    # Autocorrelation
    n = len(delta_norms)
    mean = np.mean(delta_norms)
    var = np.var(delta_norms)
    max_lag = min(100, n // 2)
    autocorr = np.zeros(max_lag)
    for lag in range(max_lag):
        autocorr[lag] = np.mean(
            (delta_norms[:n-lag] - mean) * (delta_norms[lag:] - mean)
        ) / (var + 1e-10)
    ax.plot(range(max_lag), autocorr, 'b-', linewidth=1.5)
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xlabel('Lag (interactions)', fontsize=10)
    ax.set_ylabel('Autocorrelation', fontsize=10)
    ax.set_title('Temporal Structure in State Changes', fontsize=11)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'dimensions.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved dimensions.png")


def main():
    save_dir = 'experiments/02-persistent-state'
    os.makedirs(save_dir, exist_ok=True)

    print("Running persistent state simulation...")
    entity, results, sensitivity_log = run_simulation()

    print("\nGenerating visualizations...")
    plot_drift(results, save_dir)
    plot_sensitivity(results['history'], save_dir)
    pca_info = plot_state_trajectory(entity, save_dir)
    plot_response_consistency(results, save_dir)
    plot_dimension_analysis(entity, save_dir)

    # Update results with PCA info
    if pca_info:
        results_path = os.path.join(save_dir, 'results.json')
        with open(results_path, 'r') as f:
            results_data = json.load(f)
        results_data['pca_info'] = pca_info
        with open(results_path, 'w') as f:
            json.dump(results_data, f, indent=2)

    print(f"\nAll visualizations saved to {save_dir}/")


if __name__ == '__main__':
    main()
