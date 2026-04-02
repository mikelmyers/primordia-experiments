"""
Test 3 — Simulation Runner
Primordia Systems LLC — Pre-Paradigm Research

Runs 5000 timesteps with perturbations every 200 steps.
Measures energy dynamics, action preferences, recovery, and behavioral sequences.
"""

import numpy as np
import json
import os
from collections import Counter

from energy_entity import EnergyEntity


def find_behavioral_sequences(action_history, min_length=2, max_length=5):
    """
    Find recurring action sequences (proto-habits).
    Look for subsequences that appear more than expected by chance.
    """
    actions = [h['action'] for h in action_history]
    n = len(actions)
    sequence_counts = {}

    for length in range(min_length, max_length + 1):
        for i in range(n - length + 1):
            seq = tuple(actions[i:i+length])
            seq_str = ' → '.join(seq)
            if seq_str not in sequence_counts:
                sequence_counts[seq_str] = 0
            sequence_counts[seq_str] += 1

    # Filter to sequences that appear significantly
    significant = {}
    for seq, count in sequence_counts.items():
        length = len(seq.split(' → '))
        # Expected count if actions were random uniform
        n_actions = 10
        expected = (n - length + 1) / (n_actions ** length)
        if count > max(3, expected * 2):  # At least 3 occurrences and 2x expected
            significant[seq] = {
                'count': count,
                'expected_random': float(expected),
                'ratio_to_random': float(count / max(expected, 0.001)),
                'length': length,
            }

    # Sort by ratio to random (most surprising first)
    sorted_seqs = sorted(significant.items(),
                        key=lambda x: x[1]['ratio_to_random'], reverse=True)
    return dict(sorted_seqs[:30])  # Top 30


def compute_recovery_times(action_history, perturbation_steps, window=5):
    """
    After each perturbation, how many steps to return to pre-perturbation energy level?
    """
    recovery_data = []

    for p_step in perturbation_steps:
        # Get pre-perturbation energy (average of window before)
        pre_start = max(0, p_step - window)
        pre_energies = [action_history[i]['energy']['total']
                       for i in range(pre_start, p_step)
                       if i < len(action_history)]
        if not pre_energies:
            continue
        pre_energy = np.mean(pre_energies)

        # Find when energy returns to pre-perturbation level
        recovery_step = None
        post_peak_energy = None
        for i in range(p_step, min(p_step + 200, len(action_history))):
            e = action_history[i]['energy']['total']
            if post_peak_energy is None or e > post_peak_energy:
                post_peak_energy = e
            if e <= pre_energy * 1.1:  # Within 10% of pre-perturbation
                recovery_step = i - p_step
                break

        recovery_data.append({
            'perturbation_step': p_step,
            'pre_energy': float(pre_energy),
            'post_peak_energy': float(post_peak_energy) if post_peak_energy else None,
            'recovery_steps': recovery_step,
            'recovered': recovery_step is not None,
        })

    return recovery_data


def run_simulation(n_steps=5000, perturbation_interval=200, seed=42):
    """Run the full 5000-step simulation with periodic perturbations."""

    entity = EnergyEntity(dim=64, seed=seed)

    perturbation_steps = list(range(perturbation_interval, n_steps,
                                     perturbation_interval))
    perturbation_log = []

    print(f"Running {n_steps} timesteps...")
    print(f"Perturbations at every {perturbation_interval} steps "
          f"({len(perturbation_steps)} total)")
    print()

    for step in range(n_steps):
        # Check for perturbation
        if step in perturbation_steps:
            pre_energy = entity.energy(entity.S)
            perturbation_magnitude = entity.perturb(scale=2.0)
            post_energy = entity.energy(entity.S)
            perturbation_log.append({
                'step': step,
                'perturbation_magnitude': perturbation_magnitude,
                'pre_energy': float(pre_energy),
                'post_energy': float(post_energy),
                'energy_spike': float(post_energy - pre_energy),
            })
            if step % 1000 == 0:
                print(f"  Perturbation at t={step}: "
                      f"energy {pre_energy:.4f} → {post_energy:.4f}")

        # Take a step
        entry = entity.step()

        if step % 1000 == 0:
            print(f"  t={step}: action={entry['action']}, "
                  f"energy={entry['energy']['total']:.4f} "
                  f"(T={entry['energy']['tension']:.3f}, "
                  f"I={entry['energy']['incoherence']:.3f}, "
                  f"N={entry['energy']['novelty_cost']:.3f})")

    # --- Analysis ---

    print(f"\n=== Analysis ===")

    # Action frequency
    action_counts = Counter(h['action'] for h in entity.action_history)
    total_actions = sum(action_counts.values())
    action_freq = {a: {'count': c, 'frequency': c / total_actions}
                   for a, c in action_counts.most_common()}
    print(f"\n  Action frequency:")
    for action, info in action_freq.items():
        print(f"    {action}: {info['count']} ({info['frequency']:.1%})")

    # Recovery times
    recovery_data = compute_recovery_times(entity.action_history,
                                           perturbation_steps)
    recovered = [r for r in recovery_data if r['recovered']]
    if recovered:
        recovery_times = [r['recovery_steps'] for r in recovered]
        print(f"\n  Recovery: {len(recovered)}/{len(recovery_data)} perturbations recovered")
        print(f"    Mean recovery: {np.mean(recovery_times):.1f} steps")
        print(f"    Median recovery: {np.median(recovery_times):.1f} steps")
    else:
        print(f"\n  Recovery: 0/{len(recovery_data)} perturbations recovered")

    # Behavioral sequences
    sequences = find_behavioral_sequences(entity.action_history)
    print(f"\n  Recurring sequences (proto-habits): {len(sequences)} found")
    for seq, info in list(sequences.items())[:5]:
        print(f"    '{seq}': {info['count']}x "
              f"({info['ratio_to_random']:.0f}x random)")

    # Energy trajectory stats
    energies = entity.energy_history
    print(f"\n  Energy: start={energies[0]:.4f}, end={energies[-1]:.4f}, "
          f"min={min(energies):.4f}, mean={np.mean(energies):.4f}")

    # Compile results
    results = {
        'parameters': {
            'dim': 64,
            'n_steps': n_steps,
            'perturbation_interval': perturbation_interval,
            'perturbation_scale': 2.0,
            'seed': seed,
        },
        'action_frequency': action_freq,
        'recovery_analysis': {
            'perturbation_count': len(perturbation_steps),
            'recovered_count': len(recovered),
            'recovery_times': [r['recovery_steps'] for r in recovered],
            'mean_recovery': float(np.mean(recovery_times)) if recovered else None,
            'median_recovery': float(np.median(recovery_times)) if recovered else None,
            'details': recovery_data,
        },
        'behavioral_sequences': sequences,
        'energy_stats': {
            'initial': float(energies[0]),
            'final': float(energies[-1]),
            'minimum': float(min(energies)),
            'maximum': float(max(energies)),
            'mean': float(np.mean(energies)),
            'std': float(np.std(energies)),
        },
        'perturbation_log': perturbation_log,
    }

    results_path = 'experiments/03-energy-motivation/results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    return entity, results


if __name__ == '__main__':
    entity, results = run_simulation()
    print("\nSimulation complete. Run visualize.py to generate plots.")
