"""
Test 4 — Visualization
Primordia Systems LLC — Pre-Paradigm Research

Generates:
1. Raster plot — every spike in the network
2. Population firing rate over time
3. Sparsity distribution
4. Pattern response comparison
5. Power spectrum (temporal oscillations)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import os

from snn import SpikingNetwork, PatternProtocol, SpikeAnalyzer
from simulate import run_simulation


def plot_raster(spike_log, protocol, N, save_dir):
    """Raster plot: each spike as a dot. Color by neuron type."""
    if not spike_log:
        print("  No spikes to plot!")
        return

    fig, ax = plt.subplots(figsize=(18, 8))

    times = [s[0] for s in spike_log]
    neurons = [s[1] for s in spike_log]
    n_exc = int(0.8 * N)

    # Color excitatory vs inhibitory
    exc_mask = [n < n_exc for n in neurons]
    inh_mask = [n >= n_exc for n in neurons]

    exc_times = [t for t, m in zip(times, exc_mask) if m]
    exc_neurons = [n for n, m in zip(neurons, exc_mask) if m]
    inh_times = [t for t, m in zip(times, inh_mask) if m]
    inh_neurons = [n for n, m in zip(neurons, inh_mask) if m]

    ax.scatter(exc_times, exc_neurons, s=0.3, c='#2196F3', alpha=0.4,
               label=f'Excitatory ({len(exc_times)} spikes)', rasterized=True)
    ax.scatter(inh_times, inh_neurons, s=0.3, c='#FF5722', alpha=0.4,
               label=f'Inhibitory ({len(inh_times)} spikes)', rasterized=True)

    # Mark pattern presentations
    colors_pattern = {'A': '#4CAF50', 'B': '#FF9800', 'C': '#9C27B0'}
    for event in protocol.events:
        ax.axvspan(event['t_start'], event['t_end'], alpha=0.08,
                   color=colors_pattern[event['pattern']])

    ax.set_xlabel('Time (ms)', fontsize=11)
    ax.set_ylabel('Neuron ID', fontsize=11)
    ax.set_title(f'Spike Raster — {len(spike_log)} total spikes, '
                 f'{N} neurons', fontsize=13)
    ax.legend(fontsize=9, loc='upper right', markerscale=10)
    ax.set_xlim(0, max(times) + 10 if times else 100)
    ax.set_ylim(0, N)

    # Add a zoomed inset for the first few patterns
    if len(protocol.events) >= 3:
        t_zoom_end = protocol.events[2]['t_end'] + 50
        axins = ax.inset_axes([0.02, 0.55, 0.35, 0.4])
        zoom_exc_t = [t for t, n in zip(exc_times, exc_neurons) if t < t_zoom_end]
        zoom_exc_n = [n for t, n in zip(exc_times, exc_neurons) if t < t_zoom_end]
        zoom_inh_t = [t for t, n in zip(inh_times, inh_neurons) if t < t_zoom_end]
        zoom_inh_n = [n for t, n in zip(inh_times, inh_neurons) if t < t_zoom_end]
        axins.scatter(zoom_exc_t, zoom_exc_n, s=0.5, c='#2196F3', alpha=0.5,
                     rasterized=True)
        axins.scatter(zoom_inh_t, zoom_inh_n, s=0.5, c='#FF5722', alpha=0.5,
                     rasterized=True)
        for event in protocol.events[:3]:
            axins.axvspan(event['t_start'], event['t_end'], alpha=0.15,
                         color=colors_pattern[event['pattern']])
        axins.set_xlim(0, t_zoom_end)
        axins.set_ylim(0, N)
        axins.set_title('First 3 patterns (zoom)', fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'raster.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved raster.png")


def plot_population_rate(firing_rate_log, protocol, dt, save_dir):
    """Plot population firing rate over time."""
    rates = np.array(firing_rate_log)
    times = np.arange(len(rates)) * dt

    fig, axes = plt.subplots(2, 1, figsize=(16, 8), sharex=True)
    fig.suptitle('Population Activity', fontsize=14)

    # Raw firing rate
    ax = axes[0]
    ax.plot(times, rates * 100, color='#333333', linewidth=0.3, alpha=0.5)

    # Smoothed
    window = max(1, int(5.0 / dt))  # 5ms smoothing
    if len(rates) >= window:
        smoothed = np.convolve(rates, np.ones(window)/window, mode='valid')
        ax.plot(times[:len(smoothed)], smoothed * 100, color='#2196F3',
                linewidth=1.5, label=f'Smoothed (5ms)')

    # Mark patterns
    colors_pattern = {'A': '#4CAF50', 'B': '#FF9800', 'C': '#9C27B0'}
    for event in protocol.events:
        ax.axvspan(event['t_start'], event['t_end'], alpha=0.08,
                   color=colors_pattern[event['pattern']])

    ax.axhline(y=5, color='red', linestyle='--', alpha=0.5,
               label='5% target')
    ax.set_ylabel('Firing Rate (%)', fontsize=11)
    ax.set_title('Population Firing Rate', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

    # Sparsity over time (cumulative fraction of neurons that have fired)
    ax = axes[1]
    # Compute instantaneous sparsity (fraction NOT firing)
    sparsity = (1 - rates) * 100
    ax.plot(times, sparsity, color='#4CAF50', linewidth=0.3, alpha=0.5)
    if len(sparsity) >= window:
        smoothed_s = np.convolve(sparsity, np.ones(window)/window,
                                 mode='valid')
        ax.plot(times[:len(smoothed_s)], smoothed_s, color='#4CAF50',
                linewidth=1.5)

    ax.axhline(y=95, color='red', linestyle='--', alpha=0.5,
               label='95% sparsity target')
    ax.set_ylabel('Sparsity (%)', fontsize=11)
    ax.set_xlabel('Time (ms)', fontsize=11)
    ax.set_title('Network Sparsity (% neurons silent)', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)
    ax.set_ylim(80, 100.5)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'population_rate.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved population_rate.png")


def plot_pattern_responses(analyzer, protocol, save_dir):
    """Compare population responses to different patterns."""
    pattern_windows = protocol.get_pattern_windows()

    # Collect response vectors per pattern
    N = analyzer.N
    pattern_responses = {}
    for label, t_start, t_end in pattern_windows:
        response = np.zeros(N)
        for t, nid in analyzer.spike_log:
            if t_start <= t < t_end:
                response[nid] += 1
        if label not in pattern_responses:
            pattern_responses[label] = []
        pattern_responses[label].append(response)

    labels = sorted(pattern_responses.keys())

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Pattern Separation Analysis', fontsize=14)

    # Mean response per pattern
    ax = axes[0, 0]
    colors = {'A': '#4CAF50', 'B': '#FF9800', 'C': '#9C27B0'}
    for label in labels:
        mean_resp = np.mean(pattern_responses[label], axis=0)
        # Sort for visualization
        sorted_resp = np.sort(mean_resp)[::-1]
        ax.plot(sorted_resp, color=colors[label], linewidth=1.5,
                label=f'Pattern {label}', alpha=0.8)
    ax.set_xlabel('Neuron (sorted by response)', fontsize=10)
    ax.set_ylabel('Mean Spike Count', fontsize=10)
    ax.set_title('Mean Response per Pattern (sorted)', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)
    ax.set_xlim(0, 200)  # Show top 200

    # Response variability across presentations
    ax = axes[0, 1]
    for label in labels:
        responses = pattern_responses[label]
        total_per_presentation = [np.sum(r) for r in responses]
        ax.plot(total_per_presentation, 'o-', color=colors[label],
                markersize=4, label=f'Pattern {label}', alpha=0.7)
    ax.set_xlabel('Presentation #', fontsize=10)
    ax.set_ylabel('Total Spikes', fontsize=10)
    ax.set_title('Response Consistency Across Presentations', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

    # PCA of responses
    ax = axes[1, 0]
    from sklearn.decomposition import PCA
    all_responses = []
    all_labels = []
    for label in labels:
        for resp in pattern_responses[label]:
            all_responses.append(resp)
            all_labels.append(label)

    if len(all_responses) > 3:
        all_responses = np.array(all_responses)
        pca = PCA(n_components=2)
        projected = pca.fit_transform(all_responses)

        for label in labels:
            mask = [l == label for l in all_labels]
            ax.scatter(projected[mask, 0], projected[mask, 1],
                      color=colors[label], s=30, alpha=0.6,
                      label=f'Pattern {label}', edgecolors='black',
                      linewidth=0.5)
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})',
                     fontsize=10)
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})',
                     fontsize=10)
        ax.set_title('PCA of Pattern Responses', fontsize=11)
        ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

    # Confusion matrix (cosine similarity between pattern centroids)
    ax = axes[1, 1]
    centroids = {l: np.mean(pattern_responses[l], axis=0) for l in labels}
    n_labels = len(labels)
    sim_matrix = np.zeros((n_labels, n_labels))
    for i, l1 in enumerate(labels):
        for j, l2 in enumerate(labels):
            n1 = np.linalg.norm(centroids[l1])
            n2 = np.linalg.norm(centroids[l2])
            if n1 > 0 and n2 > 0:
                sim_matrix[i, j] = np.dot(centroids[l1], centroids[l2]) / (
                    n1 * n2)

    im = ax.imshow(sim_matrix, cmap='RdYlGn', vmin=-0.2, vmax=1.0)
    ax.set_xticks(range(n_labels))
    ax.set_yticks(range(n_labels))
    ax.set_xticklabels([f'Pattern {l}' for l in labels])
    ax.set_yticklabels([f'Pattern {l}' for l in labels])
    ax.set_title('Cosine Similarity Between Pattern Centroids', fontsize=11)
    plt.colorbar(im, ax=ax)

    # Annotate
    for i in range(n_labels):
        for j in range(n_labels):
            ax.text(j, i, f'{sim_matrix[i,j]:.2f}', ha='center',
                   va='center', fontsize=10,
                   color='white' if sim_matrix[i,j] < 0.5 else 'black')

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'pattern_responses.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved pattern_responses.png")


def plot_power_spectrum(temporal, save_dir):
    """Plot frequency spectrum of population activity."""
    if not temporal.get('fft_freqs') or not temporal.get('fft_power'):
        print("  No temporal data for power spectrum")
        return

    fig, ax = plt.subplots(figsize=(12, 5))

    freqs = np.array(temporal['fft_freqs'])
    power = np.array(temporal['fft_power'])

    # Skip DC component
    if len(freqs) > 1:
        ax.semilogy(freqs[1:], power[1:], color='#2196F3', linewidth=1.5)
        ax.fill_between(freqs[1:], power[1:], alpha=0.2, color='#2196F3')

    ax.set_xlabel('Frequency (Hz)', fontsize=11)
    ax.set_ylabel('Power', fontsize=11)
    ax.set_title(f'Power Spectrum — Dominant freq: '
                 f'{temporal["dominant_frequency_hz"]:.1f} Hz, '
                 f'Concentration: {temporal["spectral_concentration"]:.3f}',
                 fontsize=12)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'power_spectrum.png'), dpi=150,
                bbox_inches='tight')
    plt.close()
    print("  Saved power_spectrum.png")


def main():
    save_dir = 'experiments/04-sparse-spiking'
    os.makedirs(save_dir, exist_ok=True)

    print("Running sparse spiking simulation...")
    net, protocol, analyzer, results, temporal = run_simulation()

    print("\nGenerating visualizations...")
    plot_raster(net.spike_log, protocol, net.N, save_dir)
    plot_population_rate(net.firing_rate_log, protocol, net.dt, save_dir)
    plot_pattern_responses(analyzer, protocol, save_dir)
    plot_power_spectrum(temporal, save_dir)

    print(f"\nAll visualizations saved to {save_dir}/")


if __name__ == '__main__':
    main()
