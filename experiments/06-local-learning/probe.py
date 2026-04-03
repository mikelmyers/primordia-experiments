"""
Test 6 — Local Learning Only: Post-Training Analysis

Probes what the network learned:
1. Population response per digit class
2. Selectivity of individual nodes
3. Stability of representations
4. Comparison to a baseline autoencoder
"""

import json
import os
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from local_network import LocalNetwork

SEED = 42
OUTDIR = os.path.dirname(os.path.abspath(__file__))


def load_model_and_data():
    """Load trained model weights and data."""
    net = LocalNetwork(n_nodes=500, input_dim=784, seed=SEED)
    net.W_in = np.load(os.path.join(OUTDIR, "W_in.npy"))
    net.W_rec = np.load(os.path.join(OUTDIR, "W_rec.npy"))
    net.thresholds = np.load(os.path.join(OUTDIR, "thresholds.npy"))

    X = np.load(os.path.join(OUTDIR, "X_data.npy"))
    y = np.load(os.path.join(OUTDIR, "y_labels.npy"))

    return net, X, y


def measure_population_responses(net, X, y, n_per_class=100):
    """Present each digit class and measure population response patterns."""
    classes = np.unique(y)
    responses = {}

    rng = np.random.RandomState(SEED)

    for c in classes:
        c_idx = np.where(y == c)[0]
        sample_idx = rng.choice(c_idx, min(n_per_class, len(c_idx)), replace=False)

        class_responses = []
        for idx in sample_idx:
            net.activations = np.zeros(net.n_nodes)  # reset state
            resp = net.forward(X[idx])
            class_responses.append(resp.copy())

        responses[int(c)] = np.array(class_responses)

    return responses


def compute_selectivity(responses):
    """Measure how selective each node is for specific digit classes.

    Selectivity index: (max_class_response - mean_response) / (max_class_response + mean_response)
    Ranges from 0 (uniform) to 1 (perfectly selective).
    """
    n_nodes = list(responses.values())[0].shape[1]
    classes = sorted(responses.keys())

    # Mean absolute activation per class per node
    mean_by_class = np.zeros((len(classes), n_nodes))
    for i, c in enumerate(classes):
        mean_by_class[i] = np.mean(np.abs(responses[c]), axis=0)

    # Selectivity per node
    max_response = np.max(mean_by_class, axis=0)
    mean_response = np.mean(mean_by_class, axis=0)

    selectivity = np.zeros(n_nodes)
    nonzero = (max_response + mean_response) > 1e-8
    selectivity[nonzero] = (max_response[nonzero] - mean_response[nonzero]) / \
                           (max_response[nonzero] + mean_response[nonzero])

    # Preferred class per node
    preferred_class = np.argmax(mean_by_class, axis=0)

    return {
        "selectivity_per_node": selectivity,
        "preferred_class": preferred_class,
        "mean_selectivity": float(np.mean(selectivity)),
        "median_selectivity": float(np.median(selectivity)),
        "n_highly_selective": int(np.sum(selectivity > 0.5)),
        "n_moderately_selective": int(np.sum(selectivity > 0.3)),
        "mean_by_class": mean_by_class,
    }


def compute_discriminability(responses):
    """Can we distinguish digit classes from population responses?

    Use silhouette score on population response vectors.
    """
    all_responses = []
    all_labels = []
    for c, resps in responses.items():
        all_responses.append(resps)
        all_labels.extend([c] * len(resps))

    all_responses = np.vstack(all_responses)
    all_labels = np.array(all_labels)

    # Silhouette score
    sil = float(silhouette_score(all_responses, all_labels, sample_size=min(1000, len(all_labels))))

    # Also try k-means clustering and measure alignment with true labels
    kmeans = KMeans(n_clusters=len(np.unique(all_labels)), random_state=SEED, n_init=10)
    cluster_labels = kmeans.fit_predict(all_responses)

    # Compute cluster purity
    from collections import Counter
    purity = 0
    for cluster_id in range(len(np.unique(all_labels))):
        mask = cluster_labels == cluster_id
        if mask.sum() > 0:
            counter = Counter(all_labels[mask])
            purity += counter.most_common(1)[0][1]
    purity /= len(all_labels)

    return {
        "silhouette_score": sil,
        "cluster_purity": float(purity),
        "n_samples": len(all_labels),
    }


def measure_stability(net, X, y, n_repeats=5, n_per_class=20):
    """Test if representations are stable across repeated presentations."""
    classes = np.unique(y)
    rng = np.random.RandomState(SEED + 1)

    stability_scores = []

    for c in classes:
        c_idx = np.where(y == c)[0]
        sample_idx = rng.choice(c_idx, min(n_per_class, len(c_idx)), replace=False)

        for idx in sample_idx:
            # Present same input multiple times
            responses = []
            for _ in range(n_repeats):
                net.activations = np.zeros(net.n_nodes)
                resp = net.forward(X[idx])
                responses.append(resp.copy())

            responses = np.array(responses)
            # Measure consistency: mean pairwise cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            cos_sim = cosine_similarity(responses)
            upper_tri = cos_sim[np.triu_indices_from(cos_sim, k=1)]
            stability_scores.append(float(np.mean(upper_tri)))

    return {
        "mean_stability": float(np.mean(stability_scores)),
        "std_stability": float(np.std(stability_scores)),
        "min_stability": float(np.min(stability_scores)),
    }


def baseline_autoencoder(X, y, encoding_dim=500):
    """Train a simple autoencoder via backprop as baseline comparison."""
    from sklearn.neural_network import MLPRegressor

    rng = np.random.RandomState(SEED)
    n_train = min(5000, len(X))
    train_idx = rng.choice(len(X), n_train, replace=False)
    X_train = X[train_idx]

    # Autoencoder: X -> encoding_dim -> X
    ae = MLPRegressor(
        hidden_layer_sizes=(encoding_dim,),
        activation="tanh",
        max_iter=200,
        random_state=SEED,
        verbose=False,
    )
    ae.fit(X_train, X_train)

    # Get hidden representations
    # Access hidden layer activations
    hidden_activations = np.tanh(X @ ae.coefs_[0] + ae.intercepts_[0])

    # Measure discriminability of autoencoder representations
    n_test = min(1000, len(X))
    test_idx = rng.choice(len(X), n_test, replace=False)
    test_hidden = hidden_activations[test_idx]
    test_labels = y[test_idx]

    sil = float(silhouette_score(test_hidden, test_labels,
                                  sample_size=min(1000, len(test_labels))))

    recon_error = float(np.mean((ae.predict(X_train) - X_train) ** 2))

    return {
        "silhouette_score": sil,
        "reconstruction_error": recon_error,
        "n_train": n_train,
    }


def main():
    print("Loading trained model...")
    net, X, y = load_model_and_data()
    print(f"  Network: {net.n_nodes} nodes, input_dim={net.input_dim}")
    print(f"  Data: {X.shape}, classes: {np.unique(y)}")

    print("\n1. Measuring population responses...")
    responses = measure_population_responses(net, X, y, n_per_class=100)
    for c, r in responses.items():
        print(f"  Class {c}: mean|activation|={np.mean(np.abs(r)):.4f}, "
              f"sparsity={np.mean(np.abs(r) < 0.1):.3f}")

    print("\n2. Computing selectivity...")
    selectivity = compute_selectivity(responses)
    print(f"  Mean selectivity: {selectivity['mean_selectivity']:.4f}")
    print(f"  Highly selective nodes (>0.5): {selectivity['n_highly_selective']}/{net.n_nodes}")
    print(f"  Moderately selective (>0.3): {selectivity['n_moderately_selective']}/{net.n_nodes}")

    print("\n3. Computing discriminability...")
    discrim = compute_discriminability(responses)
    print(f"  Silhouette score: {discrim['silhouette_score']:.4f}")
    print(f"  Cluster purity: {discrim['cluster_purity']:.4f}")

    print("\n4. Measuring stability...")
    stability = measure_stability(net, X, y)
    print(f"  Mean stability: {stability['mean_stability']:.4f}")

    print("\n5. Training baseline autoencoder for comparison...")
    baseline = baseline_autoencoder(X, y)
    print(f"  Baseline silhouette: {baseline['silhouette_score']:.4f}")
    print(f"  Baseline recon error: {baseline['reconstruction_error']:.6f}")

    # Compile results
    results = {
        "selectivity": {
            "mean": selectivity["mean_selectivity"],
            "median": selectivity["median_selectivity"],
            "n_highly_selective": selectivity["n_highly_selective"],
            "n_moderately_selective": selectivity["n_moderately_selective"],
        },
        "discriminability": discrim,
        "stability": stability,
        "baseline_comparison": baseline,
        "comparison": {
            "local_silhouette": discrim["silhouette_score"],
            "baseline_silhouette": baseline["silhouette_score"],
            "ratio": discrim["silhouette_score"] / baseline["silhouette_score"]
            if baseline["silhouette_score"] != 0 else float("inf"),
        },
    }

    # Save selectivity data for visualization
    np.save(os.path.join(OUTDIR, "selectivity_per_node.npy"), selectivity["selectivity_per_node"])
    np.save(os.path.join(OUTDIR, "preferred_class.npy"), selectivity["preferred_class"])
    np.save(os.path.join(OUTDIR, "mean_by_class.npy"), selectivity["mean_by_class"])

    with open(os.path.join(OUTDIR, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to results.json")


if __name__ == "__main__":
    main()
