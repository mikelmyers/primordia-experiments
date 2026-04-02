"""
Test 3 — Visualization
Primordia Systems LLC — Pre-Paradigm Research

Generates:
1. Energy curve with perturbation spikes
2. Action frequency distribution
3. Recovery analysis
4. Behavioral sequence analysis
5. Energy component breakdown
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
import json
import os

from energy_entity import EnergyEntity
from simulate import run_simulation


def plot_energy_curve(entity, results, save_dir):
    """Plot energy over time with perturbation markers."""
    energies = entity.energy_history
    perturbations = results['perturbation_log']

    fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
    fig.suptitle('Energy Dynamics — Does the Entity Want Something?', fontsize=14)

    # Total energy
    ax = axes[0]
    ax.plot(range(len(energies)), energies, color='#333333', linewidth=0.5,
            alpha=0.7)
    # Rolling average
    window = 50
    if len(energies) >= window:
        rolling = np.convolve(energies, np.ones(window)/window, mode='valid')
        ax.plot(range(window-1, len(energies)), rolling, color='#2196F3',
                linewidth=2, label=f'Rolling avg (w={window})')

    # Mark perturbations
    for p in perturbations:
        ax.axvline(x=p['step'], color='red', linestyle='--', alpha=0.3)

    ax.set_ylabel('Total Energy', fontsize=11)
    ax.set_title('Energy Over Time — Perturbation Spikes and Recovery', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

    # Energy components
    ax = axes[1]
    tensions = [h['energy']['tension'] for h in entity.action_history]
    incoherences = [h['energy']['incoherence'] for h in entity.action_history]
    novelty_costs = [h['energy']['novelty_cost'] for h in entity.action_history]

    steps = range(len(tensions))
    ax.fill_between(steps, 0, tensions, alpha=0.4, color='#FF5722',
                    label='Tension')
    ax.fill_between(steps, tensions,
                    np.array(tensions) + np.array(incoherences),
                    alpha=0.4, color='#2196F3', label='Incoherence')
    ax.fill_between(steps,
                    np.array(tensions) + np.array(incoherences),
                    np.array(tensions) + np.array(incoherences) +
                    np.array(novelty_costs),
                    alpha=0.4, color='#4CAF50', label='Novelty Cost')

    for p in perturbations:
        ax.axvline(x=p['step'], color='red', linestyle='--', alpha=0.3)

    ax.set_ylabel('Energy Components', fontsize=11)
    ax.set_xlabel('Timestep', fontsize=11)
    ax.set_title('Energy Decomposition — What Drives the Entity?', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'energy_curve.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved energy_curve.png")


def plot_action_distribution(results, save_dir):
    """Plot which actions the entity prefers."""
    action_freq = results['action_frequency']

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Action Preferences — What Does the Entity Do?', fontsize=14)

    # Bar chart
    ax = axes[0]
    actions = list(action_freq.keys())
    freqs = [action_freq[a]['frequency'] for a in actions]
    colors = plt.cm.Set3(np.linspace(0, 1, len(actions)))

    bars = ax.barh(actions, freqs, color=colors, edgecolor='black',
                   linewidth=0.5)
    ax.set_xlabel('Frequency', fontsize=11)
    ax.set_title('Action Frequency Distribution', fontsize=12)
    ax.axvline(x=0.1, color='red', linestyle='--', alpha=0.3,
               label='Uniform (10%)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2, axis='x')

    # Action over time (rolling mode)
    ax = axes[1]
    # Encode actions as numbers
    action_names = sorted(action_freq.keys())
    action_to_num = {a: i for i, a in enumerate(action_names)}

    # Get action sequence from results
    action_seq_path = os.path.join(save_dir, 'results.json')
    # We need the entity's action history - read from entity
    # Instead, plot action frequency in sliding windows
    ax.set_xlabel('Timestep', fontsize=11)
    ax.set_ylabel('Action Frequency in Window', fontsize=11)
    ax.set_title('Action Preferences Over Time (window=200)', fontsize=12)
    ax.text(0.5, 0.5, 'See action_timeline.png for detailed view',
            transform=ax.transAxes, ha='center', fontsize=10, alpha=0.5)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'action_distribution.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved action_distribution.png")


def plot_action_timeline(entity, save_dir):
    """Plot action choices over time as a heatmap."""
    actions = [h['action'] for h in entity.action_history]
    action_names = sorted(set(actions))
    action_to_idx = {a: i for i, a in enumerate(action_names)}

    n_steps = len(actions)
    window = 100
    n_windows = n_steps // window

    # Compute action frequencies per window
    freq_matrix = np.zeros((len(action_names), n_windows))
    for w in range(n_windows):
        window_actions = actions[w * window:(w + 1) * window]
        counts = Counter(window_actions)
        for a, c in counts.items():
            freq_matrix[action_to_idx[a], w] = c / window

    fig, ax = plt.subplots(figsize=(16, 6))
    im = ax.imshow(freq_matrix, aspect='auto', cmap='YlOrRd',
                   interpolation='nearest')
    ax.set_yticks(range(len(action_names)))
    ax.set_yticklabels(action_names, fontsize=9)
    ax.set_xlabel(f'Time Window (each = {window} steps)', fontsize=11)
    ax.set_title('Action Frequency Over Time — Do Preferences Change?',
                 fontsize=12)
    plt.colorbar(im, ax=ax, label='Frequency in Window')

    # Mark perturbation windows
    perturbation_interval = 200
    for p in range(perturbation_interval, n_steps, perturbation_interval):
        ax.axvline(x=p / window, color='white', linestyle='--', alpha=0.5,
                   linewidth=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'action_timeline.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved action_timeline.png")


def plot_recovery(results, save_dir):
    """Plot recovery times after perturbations."""
    recovery = results['recovery_analysis']
    details = recovery['details']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Recovery from Perturbation — Resilience', fontsize=14)

    # Recovery times
    ax = axes[0]
    steps = [d['perturbation_step'] for d in details]
    times = [d['recovery_steps'] if d['recovered'] else -1 for d in details]
    colors = ['#4CAF50' if d['recovered'] else '#FF5722' for d in details]
    bars = ax.bar(range(len(steps)), times, color=colors, edgecolor='black',
                  linewidth=0.5)
    ax.set_xlabel('Perturbation #', fontsize=11)
    ax.set_ylabel('Recovery Steps', fontsize=11)
    ax.set_title('Steps to Recover After Each Perturbation', fontsize=12)
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.grid(True, alpha=0.2, axis='y')

    # Energy spike vs recovery
    ax = axes[1]
    spikes = [d['post_peak_energy'] - d['pre_energy']
              if d['post_peak_energy'] is not None else 0 for d in details]
    recovered_mask = [d['recovered'] for d in details]
    rec_times = [d['recovery_steps'] if d['recovered'] else 0 for d in details]

    for i, d in enumerate(details):
        if d['recovered']:
            ax.scatter(spikes[i], rec_times[i], color='#4CAF50', s=50,
                      zorder=3, edgecolors='black', linewidth=0.5)
        else:
            ax.scatter(spikes[i], 0, color='#FF5722', s=50, marker='x',
                      zorder=3)

    ax.set_xlabel('Energy Spike Magnitude', fontsize=11)
    ax.set_ylabel('Recovery Steps', fontsize=11)
    ax.set_title('Bigger Shocks → Longer Recovery?', fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'recovery.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved recovery.png")


def plot_sequences(results, save_dir):
    """Visualize recurring behavioral sequences."""
    sequences = results['behavioral_sequences']

    if not sequences:
        print("  No significant sequences found — skipping sequence plot")
        return

    fig, ax = plt.subplots(figsize=(14, max(4, len(sequences) * 0.3)))

    # Sort by count
    sorted_seqs = sorted(sequences.items(), key=lambda x: x[1]['count'],
                        reverse=True)[:20]

    names = [s[0] for s in sorted_seqs]
    counts = [s[1]['count'] for s in sorted_seqs]
    ratios = [s[1]['ratio_to_random'] for s in sorted_seqs]

    y_pos = range(len(names))
    bars = ax.barh(y_pos, counts, color=plt.cm.viridis(
        np.array(ratios) / max(ratios)), edgecolor='black', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel('Occurrences', fontsize=11)
    ax.set_title('Recurring Action Sequences (Proto-Habits)\n'
                 'Color intensity = surprise ratio vs random', fontsize=12)
    ax.grid(True, alpha=0.2, axis='x')

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'sequences.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved sequences.png")


def main():
    save_dir = 'experiments/03-energy-motivation'
    os.makedirs(save_dir, exist_ok=True)

    print("Running energy motivation simulation...")
    entity, results = run_simulation()

    print("\nGenerating visualizations...")
    plot_energy_curve(entity, results, save_dir)
    plot_action_distribution(results, save_dir)
    plot_action_timeline(entity, save_dir)
    plot_recovery(results, save_dir)
    plot_sequences(results, save_dir)

    print(f"\nAll visualizations saved to {save_dir}/")


if __name__ == '__main__':
    main()
