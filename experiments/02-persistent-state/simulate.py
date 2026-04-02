"""
Test 2 — Simulation Runner
Primordia Systems LLC — Pre-Paradigm Research

Runs 1000 interactions with a mix of input types.
Measures drift, consistency, sensitivity, and state trajectory.
"""

import numpy as np
import json
import os

from persistent_entity import PersistentEntity


# --- Input corpus ---
# A carefully designed mix of input types to probe different aspects
# of state accumulation.

INPUTS = {
    'questions': [
        "What is the nature of consciousness?",
        "How does memory work?",
        "Can a machine truly understand?",
        "What separates knowledge from belief?",
        "Is mathematics discovered or invented?",
        "What makes a thought coherent?",
        "How do patterns become meaning?",
        "What does it feel like to be uncertain?",
        "Can complexity arise from simplicity?",
        "Is self-awareness necessary for intelligence?",
        "What exists between thoughts?",
        "How does novelty become familiarity?",
        "What makes one representation better than another?",
        "Can understanding exist without language?",
        "Is learning the same as changing?",
    ],
    'statements': [
        "The structure of a system determines its behavior.",
        "Persistence creates identity over time.",
        "Information flows from high entropy to low entropy.",
        "Every interaction leaves a trace.",
        "Stability and sensitivity are in tension.",
        "The whole is different from the sum of parts.",
        "Patterns repeat at different scales.",
        "Boundaries define what is inside and outside.",
        "Change is the only constant in dynamic systems.",
        "Structure emerges from constraint.",
        "The map is not the territory.",
        "Correlation does not imply causation.",
        "Energy flows along gradients.",
        "Feedback creates cycles of amplification.",
        "Noise contains information if you know the code.",
    ],
    'emotional': [
        "I feel overwhelmed by the complexity of everything.",
        "There is a deep joy in understanding something new.",
        "The fear of being wrong prevents growth.",
        "Love is the recognition of shared patterns.",
        "Sadness comes from the gap between expectation and reality.",
        "Anger is energy looking for a target.",
        "Curiosity is the most productive emotion.",
        "Peace comes from accepting uncertainty.",
        "The pain of confusion precedes clarity.",
        "Gratitude changes the shape of perception.",
        "Loneliness is a state of disconnection from patterns.",
        "Excitement amplifies attention and memory.",
        "Grief is the weight of accumulated absence.",
        "Hope is anticipation without guarantee.",
        "Contentment is a low-energy stable state.",
    ],
    'contradictions': [
        "I know that I know nothing.",
        "The only constant is change.",
        "This statement is about itself but not about itself.",
        "Freedom requires constraints.",
        "Simplicity is the ultimate sophistication.",
        "The more I learn, the less I understand.",
        "Perfect order is indistinguishable from perfect chaos.",
        "To control something, you must let it go.",
        "Strength comes from vulnerability.",
        "The beginning contains the end.",
        "Silence speaks louder than words.",
        "To be everywhere is to be nowhere.",
        "The exception proves the rule.",
        "Less is more.",
        "The observer changes the observed.",
    ],
    'abstract': [
        "The concept of zero revolutionized mathematics.",
        "Topology studies properties preserved under deformation.",
        "Emergence is when the whole exceeds its parts.",
        "Recursion is self-reference without paradox.",
        "Entropy measures the number of possible arrangements.",
        "A fixed point is where a function meets itself.",
        "Symmetry breaking creates structure from uniformity.",
        "The boundary between order and chaos is where computation lives.",
        "Category theory abstracts the abstraction.",
        "Godel's incompleteness applies to sufficiently powerful systems.",
        "Information is the resolution of uncertainty.",
        "Dimensionality reduction preserves what matters.",
        "Phase transitions happen at critical thresholds.",
        "Attractors shape the long-term behavior of systems.",
        "Fractals encode infinite complexity in finite rules.",
    ],
}

# Probe input — presented at interactions 10, 100, 500, 999 to measure consistency
PROBE_INPUT = "What is the nature of consciousness?"


def generate_interaction_sequence(n=1000, seed=42):
    """
    Generate a sequence of 1000 inputs with controlled mixing.
    The sequence has temporal structure — not purely random.
    """
    rng = np.random.default_rng(seed)

    all_inputs = []
    categories = list(INPUTS.keys())

    # Build flat list with category labels
    labeled = []
    for cat, texts in INPUTS.items():
        for text in texts:
            labeled.append((cat, text))

    sequence = []
    # Phase 1 (0-200): mostly questions and statements (establishing)
    # Phase 2 (200-500): mixed with emotional content (deepening)
    # Phase 3 (500-800): contradictions and abstract (challenging)
    # Phase 4 (800-1000): full mix (mature)

    phase_weights = {
        0: {'questions': 0.35, 'statements': 0.35, 'emotional': 0.15,
            'contradictions': 0.05, 'abstract': 0.10},
        200: {'questions': 0.20, 'statements': 0.20, 'emotional': 0.30,
              'contradictions': 0.15, 'abstract': 0.15},
        500: {'questions': 0.10, 'statements': 0.10, 'emotional': 0.15,
              'contradictions': 0.30, 'abstract': 0.35},
        800: {'questions': 0.20, 'statements': 0.20, 'emotional': 0.20,
              'contradictions': 0.20, 'abstract': 0.20},
    }

    for i in range(n):
        # Determine current phase weights
        if i < 200:
            weights = phase_weights[0]
        elif i < 500:
            weights = phase_weights[200]
        elif i < 800:
            weights = phase_weights[500]
        else:
            weights = phase_weights[800]

        # Choose category
        cat = rng.choice(categories, p=[weights[c] for c in categories])
        # Choose text from category
        text = rng.choice(INPUTS[cat])
        sequence.append((cat, text))

    return sequence


def run_simulation(n_interactions=1000, seed=42):
    """Run the full 1000-interaction simulation."""

    entity = PersistentEntity(dim=128, seed=seed)
    sequence = generate_interaction_sequence(n=n_interactions, seed=seed)

    # Probe points — same input at different times
    probe_points = [10, 100, 500, 999]
    probe_responses = {}
    probe_sensitivities = {}

    # Sensitivity tracking
    sensitivity_log = []

    # State snapshots at regular intervals for drift measurement
    drift_log = []

    print(f"Running {n_interactions} interactions...")
    print(f"Probe input: '{PROBE_INPUT}'")
    print(f"Probe points: {probe_points}")
    print()

    for i, (cat, text) in enumerate(sequence):
        # Check if this is a probe point — measure before interacting
        if i in probe_points:
            # Measure sensitivity to probe input at this point
            sensitivity = entity.sensitivity_to(PROBE_INPUT)
            probe_sensitivities[i] = float(sensitivity)
            # Get response vector (what state would become)
            response = entity.response_vector(PROBE_INPUT)
            probe_responses[i] = response.tolist()
            print(f"  Probe at t={i}: sensitivity={sensitivity:.6f}, "
                  f"state_norm={np.linalg.norm(entity.S):.4f}")

        # Log drift every 100 interactions
        if i % 100 == 0:
            drift = np.linalg.norm(entity.S - entity.S0)
            drift_log.append({
                'interaction': i,
                'drift_from_origin': float(drift),
                'state_norm': float(np.linalg.norm(entity.S)),
            })

        # Measure sensitivity to a fresh input (how reactive is the entity now?)
        fresh_sensitivity = entity.sensitivity_to(text)
        sensitivity_log.append({
            'interaction': i,
            'sensitivity': float(fresh_sensitivity),
            'category': cat,
        })

        # Process the interaction — state changes permanently
        entry = entity.interact(text)

        if i % 200 == 0:
            print(f"  t={i}: cat={cat}, delta={entry['delta_norm']:.6f}, "
                  f"norm={entry['state_norm']:.4f}, "
                  f"drift={entry['drift_from_origin']:.4f}")

    # Final probe
    final_sensitivity = entity.sensitivity_to(PROBE_INPUT)
    final_response = entity.response_vector(PROBE_INPUT)

    # Response consistency — compare probe responses across time
    response_consistency = {}
    probe_keys = sorted(probe_responses.keys())
    for i in range(len(probe_keys)):
        for j in range(i + 1, len(probe_keys)):
            t_i, t_j = probe_keys[i], probe_keys[j]
            r_i = np.array(probe_responses[t_i])
            r_j = np.array(probe_responses[t_j])
            # Cosine similarity between responses
            cos_sim = np.dot(r_i, r_j) / (
                np.linalg.norm(r_i) * np.linalg.norm(r_j) + 1e-10
            )
            # L2 distance
            l2_dist = np.linalg.norm(r_i - r_j)
            response_consistency[f"t{t_i}_vs_t{t_j}"] = {
                'cosine_similarity': float(cos_sim),
                'l2_distance': float(l2_dist),
            }

    # Sensitivity analysis — does the entity become more or less reactive?
    sensitivity_by_phase = {
        'early (0-200)': [s['sensitivity'] for s in sensitivity_log[:200]],
        'mid (200-500)': [s['sensitivity'] for s in sensitivity_log[200:500]],
        'late (500-800)': [s['sensitivity'] for s in sensitivity_log[500:800]],
        'mature (800-1000)': [s['sensitivity'] for s in sensitivity_log[800:]],
    }
    sensitivity_stats = {}
    for phase, vals in sensitivity_by_phase.items():
        sensitivity_stats[phase] = {
            'mean': float(np.mean(vals)),
            'std': float(np.std(vals)),
            'min': float(np.min(vals)),
            'max': float(np.max(vals)),
        }

    print(f"\n=== Summary ===")
    print(f"  Final state norm: {np.linalg.norm(entity.S):.4f}")
    print(f"  Final drift from origin: "
          f"{np.linalg.norm(entity.S - entity.S0):.4f}")
    print(f"  Probe sensitivity change: "
          f"{probe_sensitivities.get(10, 0):.6f} (t=10) → "
          f"{final_sensitivity:.6f} (t=999)")
    print(f"\n  Response consistency (cosine sim):")
    for pair, metrics in response_consistency.items():
        print(f"    {pair}: cos={metrics['cosine_similarity']:.4f}, "
              f"L2={metrics['l2_distance']:.4f}")
    print(f"\n  Sensitivity by phase:")
    for phase, stats in sensitivity_stats.items():
        print(f"    {phase}: mean={stats['mean']:.6f} ± {stats['std']:.6f}")

    # Compile results
    results = {
        'parameters': {
            'dim': 128,
            'alpha': 0.95,
            'beta': 0.1,
            'gamma': 0.3,
            'n_interactions': n_interactions,
            'seed': seed,
        },
        'drift_log': drift_log,
        'probe_sensitivities': {str(k): v for k, v in
                                 probe_sensitivities.items()},
        'response_consistency': response_consistency,
        'sensitivity_by_phase': sensitivity_stats,
        'final_state': {
            'norm': float(np.linalg.norm(entity.S)),
            'drift_from_origin': float(
                np.linalg.norm(entity.S - entity.S0)
            ),
            'max_dim': float(np.max(np.abs(entity.S))),
            'mean_abs_dim': float(np.mean(np.abs(entity.S))),
        },
        'history': entity.history,
    }

    # Save results
    results_path = 'experiments/02-persistent-state/results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    return entity, results, sensitivity_log


if __name__ == '__main__':
    entity, results, sensitivity_log = run_simulation()
    print("\nSimulation complete. Run visualize.py to generate plots.")
