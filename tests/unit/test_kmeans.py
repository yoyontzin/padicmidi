"""Unit tests for the in-package K-means implementation."""

from __future__ import annotations

import numpy as np

from padicmidi.core.hierarchical import kmeans_numpy


def test_kmeans_seed_reproducibility():
    """Same seed => same centers, regardless of how many times we call."""
    rng = np.random.default_rng(42)
    samples = np.vstack([
        rng.normal(loc=0.0, scale=0.1, size=(50, 4)),
        rng.normal(loc=5.0, scale=0.1, size=(50, 4)),
    ])

    rng_a = np.random.default_rng(42)
    rng_b = np.random.default_rng(42)
    centers_a = kmeans_numpy(samples, K=2, rng=rng_a)
    centers_b = kmeans_numpy(samples, K=2, rng=rng_b)
    np.testing.assert_allclose(np.sort(centers_a, axis=0), np.sort(centers_b, axis=0))


def test_kmeans_two_well_separated_clusters():
    rng = np.random.default_rng(0)
    cluster_a = rng.normal(loc=0.0, scale=0.05, size=(40, 3))
    cluster_b = rng.normal(loc=10.0, scale=0.05, size=(40, 3))
    samples = np.vstack([cluster_a, cluster_b])
    centers = kmeans_numpy(samples, K=2, rng=np.random.default_rng(1))
    sorted_means = np.sort(centers.mean(axis=1))
    np.testing.assert_allclose(sorted_means, np.array([0.0, 10.0]), atol=0.5)


def test_kmeans_K_larger_than_samples():
    """If K > len(samples), the function should not crash and return at most len(samples) effective centers."""
    samples = np.array([[1.0, 2.0], [3.0, 4.0]])
    centers = kmeans_numpy(samples, K=5, rng=np.random.default_rng(0))
    assert centers.shape[1] == 2
    assert centers.shape[0] <= 2  # K_actual = min(K, len(samples))


def test_kmeans_empty_input():
    """Empty samples: legacy motor returns a degenerate (K, 0) array; we lock
    that behaviour to detect inadvertent changes that would break the gold
    standard. See ``profinite_echo_midi.py`` line ~78."""
    samples = np.zeros((0, 4))
    centers = kmeans_numpy(samples, K=3, rng=np.random.default_rng(0))
    assert centers.shape == (3, 0)
