"""
Test 4 — Sparse Spiking Dynamics
Primordia Systems LLC — Pre-Paradigm Research

A leaky integrate-and-fire spiking neural network with N=1000 neurons.
Implemented from scratch — no frameworks.

The question: can coherent population-level responses emerge from
less than 5% active neurons at any moment? This is the efficiency
argument — intelligence from sparsity, not from flooding every unit.

Neuron model:
    dV/dt = -V/τ + I_input + I_recurrent
    Fire when V > threshold, then V = 0, refractory for 2ms

Network: 80/20 excitatory/inhibitory, 5% sparse connectivity,
Dale's law enforced, inhibition 4x stronger than excitation.
"""

import numpy as np
from scipy.sparse import random as sparse_random, csr_matrix
import json
import time as time_module


class SpikingNetwork:
    """
    Leaky integrate-and-fire network.
    All from scratch. No neural network libraries.
    """

    def __init__(self, N=1000, dt=0.1, seed=42):
        """
        N: number of neurons
        dt: simulation timestep in ms
        """
        self.N = N
        self.dt = dt  # ms
        self.rng = np.random.default_rng(seed)

        # Neuron parameters
        self.tau = 20.0       # membrane time constant (ms)
        self.threshold = 1.0  # firing threshold
        self.refractory_period = 2.0  # ms absolute refractory

        # Network structure — 80% excitatory, 20% inhibitory (Dale's law)
        self.n_exc = int(0.8 * N)
        self.n_inh = N - self.n_exc
        self.is_excitatory = np.zeros(N, dtype=bool)
        self.is_excitatory[:self.n_exc] = True

        # Sparse random connectivity: each neuron connects to 5% of others
        self._build_weight_matrix()

        # State
        self.V = np.zeros(N)  # membrane potential
        self.refractory_timer = np.zeros(N)  # time remaining in refractory
        self.spikes = np.zeros(N, dtype=bool)  # current spike state

        # Recording
        self.spike_log = []     # (time, neuron_id) pairs
        self.voltage_log = []   # optional: subsample of voltages
        self.firing_rate_log = []  # population firing rate per timestep

    def _build_weight_matrix(self):
        """
        Build sparse weight matrix with Dale's law.
        - Excitatory weights: positive, exponential distribution
        - Inhibitory weights: negative, 4x stronger
        """
        connectivity = 0.05  # 5% connection probability
        N = self.N

        # Generate sparse random connectivity
        # Use dense matrix since 5% of 1000x1000 = 50,000 entries (manageable)
        mask = self.rng.random((N, N)) < connectivity
        np.fill_diagonal(mask, False)  # no self-connections

        # Initialize weights
        W = np.zeros((N, N))

        # Excitatory weights (from excitatory neurons)
        exc_mask = mask & self.is_excitatory[:, np.newaxis]
        n_exc_connections = np.sum(exc_mask)
        W[exc_mask] = self.rng.exponential(0.1, n_exc_connections)

        # Inhibitory weights (from inhibitory neurons) — 4x stronger
        inh_mask = mask & ~self.is_excitatory[:, np.newaxis]
        n_inh_connections = np.sum(inh_mask)
        W[inh_mask] = -self.rng.exponential(0.4, n_inh_connections)

        self.W = csr_matrix(W)

        # Stats
        self.n_connections = int(mask.sum())
        self.connection_density = self.n_connections / (N * (N - 1))
        print(f"  Network: {N} neurons ({self.n_exc} exc, {self.n_inh} inh)")
        print(f"  Connections: {self.n_connections} "
              f"(density={self.connection_density:.4f})")
        print(f"  Exc weight mean: {np.mean(W[exc_mask]):.4f}")
        print(f"  Inh weight mean: {np.mean(W[inh_mask]):.4f}")

    def step(self, I_input=None):
        """
        Advance one timestep.

        dV/dt = -V/τ + I_input + I_recurrent
        Euler integration with dt.
        """
        if I_input is None:
            I_input = np.zeros(self.N)

        # Recurrent input from spikes on previous step
        I_recurrent = np.zeros(self.N)
        if np.any(self.spikes):
            # W[i,j] means neuron i sends to neuron j
            # spikes are from presynaptic neurons (rows)
            spike_indices = np.where(self.spikes)[0]
            I_recurrent = np.array(
                self.W[spike_indices, :].sum(axis=0)
            ).flatten()

        # Update membrane potential (Euler)
        dV = (-self.V / self.tau + I_input + I_recurrent) * self.dt
        self.V += dV

        # Enforce refractory period
        in_refractory = self.refractory_timer > 0
        self.V[in_refractory] = 0.0
        self.refractory_timer = np.maximum(0, self.refractory_timer - self.dt)

        # Detect spikes
        self.spikes = self.V >= self.threshold

        # Reset spiking neurons
        spike_indices = np.where(self.spikes)[0]
        self.V[spike_indices] = 0.0
        self.refractory_timer[spike_indices] = self.refractory_period

        return self.spikes.copy()

    def simulate(self, duration_ms, input_protocol, record_voltage_neurons=None):
        """
        Run simulation for duration_ms with given input protocol.

        input_protocol: function(t_ms) -> I_input array of shape (N,)
        record_voltage_neurons: list of neuron indices to record voltage traces
        """
        n_steps = int(duration_ms / self.dt)

        # Reset state
        self.V = np.zeros(self.N)
        self.refractory_timer = np.zeros(self.N)
        self.spikes = np.zeros(self.N, dtype=bool)
        self.spike_log = []
        self.voltage_log = []
        self.firing_rate_log = []

        if record_voltage_neurons is None:
            record_voltage_neurons = []

        print(f"  Simulating {duration_ms}ms ({n_steps} steps, dt={self.dt}ms)")
        start = time_module.time()

        for step in range(n_steps):
            t = step * self.dt

            # Get input current
            I_input = input_protocol(t)

            # Step
            spikes = self.step(I_input)

            # Record spikes
            spike_ids = np.where(spikes)[0]
            for nid in spike_ids:
                self.spike_log.append((t, int(nid)))

            # Record firing rate
            n_firing = len(spike_ids)
            self.firing_rate_log.append(n_firing / self.N)

            # Record voltages for selected neurons
            if record_voltage_neurons:
                self.voltage_log.append(
                    (t, self.V[record_voltage_neurons].copy())
                )

            if step % (n_steps // 10) == 0:
                elapsed = time_module.time() - start
                print(f"    t={t:.0f}ms, spikes={n_firing}, "
                      f"rate={n_firing/self.N:.4f}, elapsed={elapsed:.1f}s")

        elapsed = time_module.time() - start
        print(f"  Simulation complete in {elapsed:.1f}s")
        print(f"  Total spikes: {len(self.spike_log)}")

        return self.spike_log, self.firing_rate_log


class PatternProtocol:
    """
    Input protocol with three patterns (A, B, C).
    Each pattern activates a different 10% subset of neurons.
    Patterns are presented 20 times each in random order.
    """

    def __init__(self, N, n_patterns=3, n_presentations=20,
                 pattern_duration=50, inter_pattern_interval=100,
                 current_amplitude=5.0, seed=42):
        self.N = N
        self.rng = np.random.default_rng(seed)

        # Create non-overlapping pattern subsets
        all_neurons = np.arange(N)
        self.rng.shuffle(all_neurons)
        pattern_size = N // 10  # 10% of neurons

        self.patterns = {}
        for i in range(n_patterns):
            label = chr(ord('A') + i)
            start = i * pattern_size
            self.patterns[label] = all_neurons[start:start + pattern_size]

        # Create presentation schedule
        schedule = []
        for label in self.patterns:
            for _ in range(n_presentations):
                schedule.append(label)
        self.rng.shuffle(schedule)

        # Build timeline
        self.events = []
        t = inter_pattern_interval  # Start after a quiet period
        for label in schedule:
            self.events.append({
                'pattern': label,
                't_start': t,
                't_end': t + pattern_duration,
                'neurons': self.patterns[label],
            })
            t += pattern_duration + inter_pattern_interval

        self.total_duration = t + inter_pattern_interval
        self.current_amplitude = current_amplitude
        self.pattern_duration = pattern_duration

        print(f"  Pattern protocol: {n_patterns} patterns × "
              f"{n_presentations} presentations")
        print(f"  Pattern size: {pattern_size} neurons (10%)")
        print(f"  Total duration: {self.total_duration:.0f}ms")
        print(f"  Schedule: {' '.join(schedule)}")

    def __call__(self, t):
        """Return input current at time t."""
        I = np.zeros(self.N)
        for event in self.events:
            if event['t_start'] <= t < event['t_end']:
                I[event['neurons']] = self.current_amplitude
                break
        return I

    def get_pattern_windows(self):
        """Return list of (pattern_label, t_start, t_end) for analysis."""
        return [(e['pattern'], e['t_start'], e['t_end']) for e in self.events]


class SpikeAnalyzer:
    """Analyze spike trains for sparsity, pattern separation, and temporal structure."""

    def __init__(self, spike_log, firing_rate_log, N, dt):
        self.spike_log = spike_log
        self.firing_rate_log = firing_rate_log
        self.N = N
        self.dt = dt

    def sparsity_stats(self):
        """Compute sparsity statistics."""
        rates = np.array(self.firing_rate_log)
        return {
            'mean_firing_fraction': float(np.mean(rates)),
            'max_firing_fraction': float(np.max(rates)),
            'median_firing_fraction': float(np.median(rates)),
            'std_firing_fraction': float(np.std(rates)),
            'pct_timesteps_under_5pct': float(np.mean(rates < 0.05)),
            'pct_timesteps_zero': float(np.mean(rates == 0)),
            'total_spikes': len(self.spike_log),
        }

    def pattern_separation(self, pattern_windows, response_window=50):
        """
        Measure whether different input patterns produce distinguishable
        population activity vectors.

        For each pattern presentation, collect the spike count vector
        (which neurons fired during the response window). Then measure
        pairwise distances between patterns.
        """
        pattern_responses = {}  # pattern_label -> list of response vectors

        for label, t_start, t_end in pattern_windows:
            # Collect spikes during this presentation
            response = np.zeros(self.N)
            for t, nid in self.spike_log:
                if t_start <= t < t_end:
                    response[nid] += 1

            if label not in pattern_responses:
                pattern_responses[label] = []
            pattern_responses[label].append(response)

        # Compute within-pattern and between-pattern distances
        labels = sorted(pattern_responses.keys())
        centroids = {}
        for label in labels:
            responses = np.array(pattern_responses[label])
            centroids[label] = np.mean(responses, axis=0)

        # Within-pattern variance (average L2 from centroid)
        within_var = {}
        for label in labels:
            responses = np.array(pattern_responses[label])
            dists = [np.linalg.norm(r - centroids[label]) for r in responses]
            within_var[label] = float(np.mean(dists))

        # Between-pattern distance (L2 between centroids)
        between_dist = {}
        for i, l1 in enumerate(labels):
            for l2 in labels[i+1:]:
                d = float(np.linalg.norm(centroids[l1] - centroids[l2]))
                between_dist[f'{l1}_vs_{l2}'] = d

        # Cosine similarity between centroids
        cosine_sim = {}
        for i, l1 in enumerate(labels):
            for l2 in labels[i+1:]:
                n1 = np.linalg.norm(centroids[l1])
                n2 = np.linalg.norm(centroids[l2])
                if n1 > 0 and n2 > 0:
                    cos = float(np.dot(centroids[l1], centroids[l2]) /
                                (n1 * n2))
                else:
                    cos = 0.0
                cosine_sim[f'{l1}_vs_{l2}'] = cos

        # Separability index: between / within (higher = more separable)
        avg_between = np.mean(list(between_dist.values())) if between_dist else 0
        avg_within = np.mean(list(within_var.values())) if within_var else 1
        separability = float(avg_between / max(avg_within, 1e-10))

        return {
            'within_pattern_variance': within_var,
            'between_pattern_distance': between_dist,
            'cosine_similarity': cosine_sim,
            'separability_index': separability,
            'n_presentations_per_pattern': {
                l: len(pattern_responses[l]) for l in labels
            },
        }

    def temporal_structure(self, bin_size_ms=5.0):
        """
        Analyze temporal patterns in population activity.
        Look for oscillations, bursts, etc.
        """
        if not self.firing_rate_log:
            return {}

        rates = np.array(self.firing_rate_log)

        # Bin the firing rates
        steps_per_bin = max(1, int(bin_size_ms / self.dt))
        n_bins = len(rates) // steps_per_bin
        binned_rates = np.zeros(n_bins)
        for i in range(n_bins):
            binned_rates[i] = np.mean(
                rates[i * steps_per_bin:(i + 1) * steps_per_bin]
            )

        # FFT to find oscillations
        fft_vals = np.fft.rfft(binned_rates - np.mean(binned_rates))
        fft_power = np.abs(fft_vals) ** 2
        fft_freqs = np.fft.rfftfreq(n_bins, d=bin_size_ms / 1000)  # Hz

        # Find dominant frequency (excluding DC)
        if len(fft_power) > 1:
            peak_idx = np.argmax(fft_power[1:]) + 1
            dominant_freq = float(fft_freqs[peak_idx])
            peak_power = float(fft_power[peak_idx])
            total_power = float(np.sum(fft_power[1:]))
            spectral_concentration = peak_power / max(total_power, 1e-10)
        else:
            dominant_freq = 0
            spectral_concentration = 0

        # Burst detection: periods where firing rate exceeds 2x mean
        mean_rate = np.mean(binned_rates)
        burst_threshold = 2 * mean_rate if mean_rate > 0 else 0.01
        bursts = binned_rates > burst_threshold
        n_bursts = 0
        in_burst = False
        burst_durations = []
        burst_start = 0
        for i, b in enumerate(bursts):
            if b and not in_burst:
                in_burst = True
                burst_start = i
                n_bursts += 1
            elif not b and in_burst:
                in_burst = False
                burst_durations.append((i - burst_start) * bin_size_ms)

        return {
            'dominant_frequency_hz': dominant_freq,
            'spectral_concentration': spectral_concentration,
            'n_bursts': n_bursts,
            'mean_burst_duration_ms': float(np.mean(burst_durations))
                if burst_durations else 0,
            'mean_population_rate': float(mean_rate),
            'fft_freqs': fft_freqs.tolist()[:50],
            'fft_power': fft_power.tolist()[:50],
        }

    def stability_check(self, window_ms=100):
        """Check if activity is stable, exploding, or dying."""
        rates = np.array(self.firing_rate_log)
        n = len(rates)
        steps_per_window = int(window_ms / self.dt)

        if n < steps_per_window * 2:
            return {'status': 'insufficient_data'}

        # Compare first and last windows
        first_window = rates[:steps_per_window]
        last_window = rates[-steps_per_window:]

        first_mean = float(np.mean(first_window))
        last_mean = float(np.mean(last_window))

        # Trend: divide into quarters and check monotonicity
        quarter = n // 4
        quarter_means = [float(np.mean(rates[i*quarter:(i+1)*quarter]))
                        for i in range(4)]

        if last_mean > 0.5:
            status = 'exploding'
        elif last_mean < 1e-6 and first_mean > 1e-4:
            status = 'dying'
        else:
            status = 'stable'

        return {
            'status': status,
            'first_window_rate': first_mean,
            'last_window_rate': last_mean,
            'quarter_means': quarter_means,
            'rate_change_ratio': last_mean / max(first_mean, 1e-10),
        }
