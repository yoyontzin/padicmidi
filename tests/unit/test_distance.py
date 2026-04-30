"""Unit tests for the L^2-time-average distance between windows."""

from __future__ import annotations

import numpy as np

from padicmidi.core.hierarchical import dist_matrix


def test_distance_identity():
    """d(W, W) == 0 on the diagonal."""
    rng = np.random.default_rng(0)
    W = rng.standard_normal((5, 8, 13))
    D = dist_matrix(W, W)
    np.testing.assert_allclose(np.diag(D), 0.0, atol=1e-12)


def test_distance_symmetry():
    rng = np.random.default_rng(1)
    A = rng.standard_normal((4, 6, 13))
    B = rng.standard_normal((3, 6, 13))
    D_AB = dist_matrix(A, B)
    D_BA = dist_matrix(B, A)
    np.testing.assert_allclose(D_AB, D_BA.T, atol=1e-12)


def test_distance_shape():
    A = np.zeros((4, 6, 13))
    B = np.zeros((3, 6, 13))
    D = dist_matrix(A, B)
    assert D.shape == (4, 3)


def test_distance_value_simple():
    """Closed form on a hand-checked example."""
    A = np.zeros((1, 2, 3))
    B = np.ones((1, 2, 3))
    D = dist_matrix(A, B)
    # diff = -1 across all entries; sum_axis=3 -> 3 per timestep; mean over 2 timesteps -> 3; sqrt -> sqrt(3)
    np.testing.assert_allclose(D[0, 0], np.sqrt(3.0), atol=1e-12)
