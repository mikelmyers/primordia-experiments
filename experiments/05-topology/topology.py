"""
Test 5 — Topological State Space: Topological Analysis

Performs UMAP reduction, persistent homology, intrinsic dimensionality estimation,
and category separability analysis on captured hidden states.
"""

import json
import os
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import pairwise_distances, silhouette_score
from sklearn.preprocessing import LabelEncoder
import umap

# giotto-tda is incompatible with current scikit-learn; use distance-based approach
HAS_GTDA = False


def load_data(datadir):
    """Load hidden states and labels."""
    states = np.load(os.path.join(datadir, "hidden_states.npy"))
    labels = np.load(os.path.join(datadir, "labels.npy"), allow_pickle=True)
    with open(os.path.join(datadir, "trajectories.json")) as f:
        traj_data = json.load(f)
    trajectories = [np.array(traj_data[f"seq_{i}"]) for i in range(len(traj_data))]
    return states, labels, trajectories


def compute_umap(states, n_components=3, n_neighbors=15, min_dist=0.1):
    """Reduce to 3D using UMAP."""
    reducer = umap.UMAP(n_components=n_components, n_neighbors=n_neighbors,
                        min_dist=min_dist, random_state=42, metric="cosine")
    embedding = reducer.fit_transform(states)
    return embedding, reducer


def compute_umap_2d(states, n_neighbors=15, min_dist=0.1):
    """Reduce to 2D using UMAP for clearer visualization."""
    reducer = umap.UMAP(n_components=2, n_neighbors=n_neighbors,
                        min_dist=min_dist, random_state=42, metric="cosine")
    embedding = reducer.fit_transform(states)
    return embedding


def estimate_intrinsic_dimensionality(states, k=10):
    """Estimate intrinsic dimensionality using Maximum Likelihood Estimation (Levina-Bickel).

    For each point, estimate local dimension from k nearest neighbor distances.
    """
    nn = NearestNeighbors(n_neighbors=k + 1, metric="cosine")
    nn.fit(states)
    distances, _ = nn.kneighbors(states)
    # Skip distance to self (column 0)
    distances = distances[:, 1:]

    # MLE estimator for intrinsic dimension
    # d_hat = 1 / (1/k * sum(log(T_k / T_j) for j=1..k-1))
    local_dims = []
    for i in range(len(states)):
        dists = distances[i]
        dists = dists[dists > 0]  # avoid log(0)
        if len(dists) < 2:
            continue
        T_k = dists[-1]
        log_ratios = np.log(T_k / dists[:-1])
        log_ratios = log_ratios[log_ratios > 0]
        if len(log_ratios) > 0:
            d_hat = len(log_ratios) / np.sum(log_ratios)
            local_dims.append(d_hat)

    local_dims = np.array(local_dims)
    return {
        "mle_mean": float(np.mean(local_dims)),
        "mle_median": float(np.median(local_dims)),
        "mle_std": float(np.std(local_dims)),
        "mle_min": float(np.min(local_dims)),
        "mle_max": float(np.max(local_dims)),
    }


def estimate_pca_dimensionality(states, thresholds=(0.80, 0.90, 0.95, 0.99)):
    """Estimate dimensionality using PCA variance explained."""
    pca = PCA(n_components=min(50, states.shape[0], states.shape[1]))
    pca.fit(states)
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    dims = {}
    for t in thresholds:
        dims[f"pca_{int(t*100)}pct"] = int(np.searchsorted(cumvar, t) + 1)
    dims["pca_variance_explained"] = pca.explained_variance_ratio_[:20].tolist()
    dims["pca_cumulative_20"] = cumvar[:20].tolist()
    return dims


def compute_persistent_homology(states, max_dim=2, n_subsample=200):
    """Compute persistent homology to find topological features.

    Uses giotto-tda VietorisRipsPersistence if available.
    Subsamples for computational tractability.
    """
    # Subsample for speed
    if len(states) > n_subsample:
        idx = np.random.RandomState(42).choice(len(states), n_subsample, replace=False)
        sub_states = states[idx]
    else:
        sub_states = states

    if HAS_GTDA:
        # giotto-tda expects 3D input: (n_samples, n_points, n_features)
        # For point cloud, we reshape
        vr = VietorisRipsPersistence(
            homology_dimensions=list(range(max_dim + 1)),
            max_edge_length=np.inf,
            n_jobs=-1,
        )
        diagrams = vr.fit_transform(sub_states[np.newaxis, :, :])[0]

        # Parse diagrams: each row is (birth, death, dimension)
        features = {f"H{d}": [] for d in range(max_dim + 1)}
        for row in diagrams:
            birth, death, dim = row
            if not np.isinf(death):
                persistence = death - birth
                features[f"H{int(dim)}"].append({
                    "birth": float(birth),
                    "death": float(death),
                    "persistence": float(persistence),
                })

        # Summary stats
        summary = {}
        for dim_name, feats in features.items():
            persistences = [f["persistence"] for f in feats]
            summary[dim_name] = {
                "n_features": len(feats),
                "max_persistence": float(max(persistences)) if persistences else 0.0,
                "mean_persistence": float(np.mean(persistences)) if persistences else 0.0,
                "total_persistence": float(sum(persistences)) if persistences else 0.0,
            }

        return summary, features, diagrams
    else:
        # Fallback: use distance matrix analysis
        dist_matrix = pairwise_distances(sub_states, metric="cosine")
        # Rough topological proxy: connected components at various thresholds
        thresholds = np.percentile(dist_matrix[dist_matrix > 0], [10, 25, 50, 75, 90])
        components_at_threshold = []
        for thresh in thresholds:
            adj = dist_matrix < thresh
            # Simple component counting via BFS
            visited = set()
            n_components = 0
            for i in range(len(adj)):
                if i not in visited:
                    n_components += 1
                    queue = [i]
                    while queue:
                        node = queue.pop()
                        if node not in visited:
                            visited.add(node)
                            neighbors = np.where(adj[node])[0]
                            queue.extend(neighbors.tolist())
            components_at_threshold.append({
                "threshold": float(thresh),
                "n_components": n_components,
            })

        summary = {"components_at_thresholds": components_at_threshold}
        return summary, {}, None


def compute_category_separability(states, labels):
    """Compute pairwise distances between category centroids and silhouette score."""
    unique_labels = np.unique(labels)
    centroids = {}
    for label in unique_labels:
        mask = labels == label
        centroids[label] = states[mask].mean(axis=0)

    # Pairwise centroid distances (cosine)
    centroid_matrix = np.array([centroids[l] for l in unique_labels])
    centroid_dists = pairwise_distances(centroid_matrix, metric="cosine")

    pairwise = {}
    for i, l1 in enumerate(unique_labels):
        for j, l2 in enumerate(unique_labels):
            if i < j:
                pairwise[f"{l1}_vs_{l2}"] = float(centroid_dists[i, j])

    # Silhouette score
    le = LabelEncoder()
    numeric_labels = le.fit_transform(labels)
    sil = float(silhouette_score(states, numeric_labels, metric="cosine",
                                  sample_size=min(500, len(states))))

    # Within-class vs between-class distance ratio
    within_dists = []
    between_dists = []
    for label in unique_labels:
        mask = labels == label
        class_states = states[mask]
        # Within-class: mean pairwise distance
        if len(class_states) > 1:
            wd = pairwise_distances(class_states, metric="cosine")
            within_dists.append(float(wd[np.triu_indices_from(wd, k=1)].mean()))

    for i, l1 in enumerate(unique_labels):
        for j, l2 in enumerate(unique_labels):
            if i < j:
                s1 = states[labels == l1]
                s2 = states[labels == l2]
                bd = pairwise_distances(s1, s2, metric="cosine")
                between_dists.append(float(bd.mean()))

    ratio = float(np.mean(between_dists) / np.mean(within_dists)) if within_dists else 0.0

    return {
        "centroid_distances": pairwise,
        "silhouette_score": sil,
        "mean_within_class_distance": float(np.mean(within_dists)),
        "mean_between_class_distance": float(np.mean(between_dists)),
        "separation_ratio": ratio,
    }


def analyze_trajectories(trajectories, states_3d=None, reducer=None):
    """Analyze reasoning trajectory properties.

    Measures smoothness, total path length, and curvature.
    """
    results = []
    for i, traj in enumerate(trajectories):
        n_steps = len(traj)

        # Pairwise distances between consecutive steps (in original space)
        step_dists = []
        for j in range(1, n_steps):
            d = np.linalg.norm(traj[j] - traj[j-1])
            step_dists.append(float(d))

        # Total path length
        total_length = sum(step_dists)

        # Straight-line distance (start to end)
        straight_dist = float(np.linalg.norm(traj[-1] - traj[0]))

        # Tortuosity: path_length / straight_line_distance
        tortuosity = total_length / straight_dist if straight_dist > 0 else float("inf")

        # Smoothness: variance of step sizes (low = smooth)
        smoothness = float(np.std(step_dists)) if len(step_dists) > 1 else 0.0

        # Cosine similarity between consecutive direction vectors
        direction_consistency = []
        for j in range(2, n_steps):
            d1 = traj[j-1] - traj[j-2]
            d2 = traj[j] - traj[j-1]
            cos = np.dot(d1, d2) / (np.linalg.norm(d1) * np.linalg.norm(d2) + 1e-10)
            direction_consistency.append(float(cos))

        results.append({
            "sequence_idx": i,
            "n_steps": n_steps,
            "step_distances": step_dists,
            "total_path_length": total_length,
            "straight_line_distance": straight_dist,
            "tortuosity": tortuosity,
            "step_size_std": smoothness,
            "direction_consistency": direction_consistency,
            "mean_direction_consistency": float(np.mean(direction_consistency)) if direction_consistency else 0.0,
        })

    return results


def main():
    datadir = os.path.dirname(os.path.abspath(__file__))
    print("Loading captured hidden states...")
    states, labels, trajectories = load_data(datadir)
    print(f"  States: {states.shape}, Labels: {labels.shape}, Trajectories: {len(trajectories)}")

    # 1. UMAP reduction
    print("\nComputing UMAP (3D)...")
    embedding_3d, reducer = compute_umap(states, n_components=3)
    np.save(os.path.join(datadir, "umap_3d.npy"), embedding_3d)

    print("Computing UMAP (2D)...")
    embedding_2d = compute_umap_2d(states)
    np.save(os.path.join(datadir, "umap_2d.npy"), embedding_2d)

    # 2. Intrinsic dimensionality
    print("\nEstimating intrinsic dimensionality...")
    mle_dims = estimate_intrinsic_dimensionality(states, k=10)
    pca_dims = estimate_pca_dimensionality(states)
    print(f"  MLE estimate: {mle_dims['mle_mean']:.1f} (median: {mle_dims['mle_median']:.1f})")
    print(f"  PCA 95%: {pca_dims['pca_95pct']} components")

    # 3. Persistent homology
    print("\nComputing persistent homology...")
    homology_summary, homology_features, diagrams = compute_persistent_homology(states)
    print(f"  Homology summary: {homology_summary}")

    # 4. Category separability
    print("\nComputing category separability...")
    separability = compute_category_separability(states, labels)
    print(f"  Silhouette score: {separability['silhouette_score']:.4f}")
    print(f"  Separation ratio: {separability['separation_ratio']:.4f}")

    # 5. Trajectory analysis
    print("\nAnalyzing reasoning trajectories...")
    traj_results = analyze_trajectories(trajectories)
    mean_tortuosity = np.mean([t["tortuosity"] for t in traj_results])
    mean_consistency = np.mean([t["mean_direction_consistency"] for t in traj_results])
    print(f"  Mean tortuosity: {mean_tortuosity:.4f}")
    print(f"  Mean direction consistency: {mean_consistency:.4f}")

    # Project trajectories into UMAP space for visualization
    all_traj_points = np.vstack(trajectories)
    traj_3d = reducer.transform(all_traj_points)
    # Split back into sequences
    traj_3d_split = []
    idx = 0
    for traj in trajectories:
        n = len(traj)
        traj_3d_split.append(traj_3d[idx:idx+n].tolist())
        idx += n

    # Compile results
    results = {
        "intrinsic_dimensionality": {
            "mle": mle_dims,
            "pca": pca_dims,
        },
        "topological_features": homology_summary,
        "category_separability": separability,
        "trajectory_analysis": {
            "per_sequence": traj_results,
            "summary": {
                "mean_tortuosity": float(mean_tortuosity),
                "mean_direction_consistency": float(mean_consistency),
                "mean_path_length": float(np.mean([t["total_path_length"] for t in traj_results])),
                "mean_straight_distance": float(np.mean([t["straight_line_distance"] for t in traj_results])),
            },
        },
        "umap_params": {
            "n_neighbors": 15,
            "min_dist": 0.1,
            "metric": "cosine",
        },
    }

    with open(os.path.join(datadir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Save trajectory projections for visualization
    with open(os.path.join(datadir, "trajectories_3d.json"), "w") as f:
        json.dump(traj_3d_split, f)

    print(f"\nResults saved to results.json")
    print("Done.")


if __name__ == "__main__":
    main()
