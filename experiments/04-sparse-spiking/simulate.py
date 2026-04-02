"""
Test 4 — Simulation Runner
Primordia Systems LLC — Pre-Paradigm Research

Presents three input patterns to the spiking network and measures
sparsity, pattern separation, temporal structure, and stability.
"""

import numpy as np
import json
import os

from snn import SpikingNetwork, PatternProtocol, SpikeAnalyzer


def run_simulation(N=1000, seed=42):
    """Run the full spiking network experiment."""

    print("=== Building Network ===")
    net = SpikingNetwork(N=N, dt=0.1, seed=seed)

    print("\n=== Building Input Protocol ===")
    protocol = PatternProtocol(
        N=N,
        n_patterns=3,
        n_presentations=20,
        pattern_duration=50,    # 50ms per pattern presentation
        inter_pattern_interval=100,  # 100ms between patterns
        current_amplitude=5.0,
        seed=seed + 1,
    )

    # Record voltage for a few neurons (2 exc, 2 inh) for visualization
    record_neurons = [0, 1, net.n_exc, net.n_exc + 1]

    print("\n=== Running Simulation ===")
    spike_log, firing_rate_log = net.simulate(
        duration_ms=protocol.total_duration,
        input_protocol=protocol,
        record_voltage_neurons=record_neurons,
    )

    print("\n=== Analyzing Results ===")
    analyzer = SpikeAnalyzer(spike_log, firing_rate_log, N, net.dt)

    # Sparsity
    sparsity = analyzer.sparsity_stats()
    print(f"\n  Sparsity:")
    print(f"    Mean firing fraction: {sparsity['mean_firing_fraction']:.4f} "
          f"({sparsity['mean_firing_fraction']*100:.2f}%)")
    print(f"    Max firing fraction: {sparsity['max_firing_fraction']:.4f}")
    print(f"    % timesteps under 5%: {sparsity['pct_timesteps_under_5pct']:.1%}")
    print(f"    Total spikes: {sparsity['total_spikes']}")

    # Pattern separation
    pattern_windows = protocol.get_pattern_windows()
    separation = analyzer.pattern_separation(pattern_windows)
    print(f"\n  Pattern Separation:")
    print(f"    Separability index: {separation['separability_index']:.3f}")
    print(f"    Between-pattern distances: {separation['between_pattern_distance']}")
    print(f"    Cosine similarity: {separation['cosine_similarity']}")

    # Temporal structure
    temporal = analyzer.temporal_structure(bin_size_ms=5.0)
    print(f"\n  Temporal Structure:")
    print(f"    Dominant frequency: {temporal['dominant_frequency_hz']:.1f} Hz")
    print(f"    Spectral concentration: {temporal['spectral_concentration']:.3f}")
    print(f"    Number of bursts: {temporal['n_bursts']}")

    # Stability
    stability = analyzer.stability_check()
    print(f"\n  Stability: {stability['status']}")
    print(f"    First window rate: {stability.get('first_window_rate', 'N/A')}")
    print(f"    Last window rate: {stability.get('last_window_rate', 'N/A')}")

    # Energy proxy
    energy_proxy = {
        'total_spikes': len(spike_log),
        'spikes_per_second': len(spike_log) / (protocol.total_duration / 1000),
        'spikes_per_neuron_per_second': len(spike_log) / N / (
            protocol.total_duration / 1000),
    }
    print(f"\n  Energy proxy:")
    print(f"    Total spikes: {energy_proxy['total_spikes']}")
    print(f"    Spikes/neuron/second: "
          f"{energy_proxy['spikes_per_neuron_per_second']:.2f}")

    # Compile results
    results = {
        'parameters': {
            'N': N,
            'dt': net.dt,
            'tau': net.tau,
            'threshold': net.threshold,
            'refractory_period': net.refractory_period,
            'n_excitatory': net.n_exc,
            'n_inhibitory': net.n_inh,
            'connection_density': net.connection_density,
            'n_connections': net.n_connections,
            'n_patterns': 3,
            'n_presentations': 20,
            'pattern_duration_ms': 50,
            'inter_pattern_interval_ms': 100,
            'current_amplitude': 5.0,
            'total_duration_ms': protocol.total_duration,
            'seed': seed,
        },
        'sparsity': sparsity,
        'pattern_separation': separation,
        'temporal_structure': {k: v for k, v in temporal.items()
                              if k not in ('fft_freqs', 'fft_power')},
        'stability': stability,
        'energy_proxy': energy_proxy,
    }

    results_path = 'experiments/04-sparse-spiking/results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    return net, protocol, analyzer, results, temporal


if __name__ == '__main__':
    net, protocol, analyzer, results, temporal = run_simulation()
    print("\nSimulation complete. Run visualize.py to generate plots.")
