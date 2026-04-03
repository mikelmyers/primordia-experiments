"""
Test 6 — Local Learning Only: Training Loop

Presents MNIST digits to the local learning network for 10,000 exposures.
Logs activations, weight statistics, and selectivity over time.
"""

import json
import os
import numpy as np
from local_network import LocalNetwork

SEED = 42
OUTDIR = os.path.dirname(os.path.abspath(__file__))


def load_mnist_subset():
    """Load MNIST using sklearn, subsample from 784 to 500 dims if needed.

    Actually, per the spec: flatten to 784, subsample to match network input.
    We keep full 784-dim input and let the network handle it.
    """
    from sklearn.datasets import fetch_openml

    # Try to load MNIST
    try:
        mnist = fetch_openml("mnist_784", version=1, as_frame=False, parser="auto")
        X = mnist.data.astype(np.float32) / 255.0  # normalize to [0, 1]
        y = mnist.target.astype(int)
    except Exception:
        # Fallback: generate synthetic digit-like patterns
        print("MNIST unavailable, generating synthetic structured patterns...")
        return generate_synthetic_digits()

    return X, y


def generate_synthetic_digits():
    """Generate synthetic structured patterns as MNIST fallback.

    Creates 10 classes of 784-dim patterns with internal structure:
    each class has a prototype with variations.
    """
    rng = np.random.RandomState(SEED)
    n_per_class = 1000
    n_classes = 10
    dim = 784  # 28x28

    X = []
    y = []

    for c in range(n_classes):
        # Create class prototype: structured pattern on 28x28 grid
        proto = np.zeros((28, 28))

        # Each class gets a unique spatial pattern
        if c == 0:  # vertical bar
            proto[:, 12:16] = 1.0
        elif c == 1:  # horizontal bar
            proto[12:16, :] = 1.0
        elif c == 2:  # diagonal
            for i in range(28):
                proto[i, max(0, min(27, i))] = 1.0
                proto[i, max(0, min(27, i+1))] = 1.0
        elif c == 3:  # top-left corner
            proto[:14, :14] = 1.0
        elif c == 4:  # bottom-right corner
            proto[14:, 14:] = 1.0
        elif c == 5:  # ring
            for i in range(28):
                for j in range(28):
                    r = np.sqrt((i-14)**2 + (j-14)**2)
                    if 8 < r < 12:
                        proto[i, j] = 1.0
        elif c == 6:  # cross
            proto[12:16, :] = 1.0
            proto[:, 12:16] = 1.0
        elif c == 7:  # checkerboard
            for i in range(0, 28, 4):
                for j in range(0, 28, 4):
                    proto[i:i+2, j:j+2] = 1.0
        elif c == 8:  # border
            proto[:3, :] = 1.0
            proto[-3:, :] = 1.0
            proto[:, :3] = 1.0
            proto[:, -3:] = 1.0
        elif c == 9:  # center blob
            for i in range(28):
                for j in range(28):
                    r = np.sqrt((i-14)**2 + (j-14)**2)
                    if r < 7:
                        proto[i, j] = 1.0

        proto_flat = proto.flatten()

        # Generate variations
        for _ in range(n_per_class):
            noise = rng.randn(dim) * 0.15
            shift_x = rng.randint(-2, 3)
            shift_y = rng.randint(-2, 3)
            shifted = np.roll(np.roll(proto, shift_x, axis=0), shift_y, axis=1)
            sample = np.clip(shifted.flatten() + noise, 0, 1)
            X.append(sample)
            y.append(c)

    return np.array(X, dtype=np.float32), np.array(y)


def train(n_presentations=10000):
    """Train the network with 10,000 pattern presentations."""

    print("Loading data...")
    X, y = load_mnist_subset()
    print(f"  Data shape: {X.shape}, labels: {np.unique(y)}")

    net = LocalNetwork(n_nodes=500, input_dim=X.shape[1], seed=SEED)
    rng = np.random.RandomState(SEED)

    # Training log
    log = {
        "weight_stats": [],
        "activation_stats": [],
        "threshold_stats": [],
    }

    print(f"\nTraining for {n_presentations} presentations...")
    for step in range(n_presentations):
        # Random sample
        idx = rng.randint(0, len(X))
        x = X[idx]

        # Forward + learn
        activations = net.forward(x)
        net.learn(x)

        # Log every 100 steps
        if step % 100 == 0:
            log["weight_stats"].append({
                "step": step,
                "W_rec_mean": float(np.mean(np.abs(net.W_rec))),
                "W_rec_max": float(np.max(np.abs(net.W_rec))),
                "W_rec_std": float(np.std(net.W_rec)),
                "W_in_mean": float(np.mean(np.abs(net.W_in))),
                "W_in_max": float(np.max(np.abs(net.W_in))),
            })
            log["activation_stats"].append({
                "step": step,
                "mean_abs": float(np.mean(np.abs(activations))),
                "sparsity": float(np.mean(np.abs(activations) < 0.1)),
                "max": float(np.max(np.abs(activations))),
            })
            log["threshold_stats"].append({
                "step": step,
                "mean": float(np.mean(net.thresholds)),
                "std": float(np.std(net.thresholds)),
                "max": float(np.max(net.thresholds)),
                "min": float(np.min(net.thresholds)),
            })

        if step % 1000 == 0:
            act_sparsity = np.mean(np.abs(activations) < 0.1)
            print(f"  Step {step:5d}: |W_rec|={np.mean(np.abs(net.W_rec)):.4f}, "
                  f"sparsity={act_sparsity:.3f}, "
                  f"threshold_mean={np.mean(net.thresholds):.4f}")

    # Save model and training log
    np.save(os.path.join(OUTDIR, "W_in.npy"), net.W_in)
    np.save(os.path.join(OUTDIR, "W_rec.npy"), net.W_rec)
    np.save(os.path.join(OUTDIR, "thresholds.npy"), net.thresholds)

    with open(os.path.join(OUTDIR, "training_log.json"), "w") as f:
        json.dump(log, f, indent=2)

    # Save data info for probe
    np.save(os.path.join(OUTDIR, "X_data.npy"), X)
    np.save(os.path.join(OUTDIR, "y_labels.npy"), y)

    print(f"\nTraining complete. Model saved.")
    return net, X, y


if __name__ == "__main__":
    train()
