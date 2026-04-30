"""Unit tests for window aggregation by p-adic residue (W_n[a])."""

from __future__ import annotations

import numpy as np

from padicmidi.core.hierarchical import (
    aggregate_median,
    build_W_n,
    get_windows,
)


def test_get_windows_step_and_length():
    X = np.arange(20 * 13, dtype=float).reshape(20, 13)
    win = get_windows(X, N=4, step=2)
    starts = [s for s, _ in win]
    assert starts == [0, 2, 4, 6, 8, 10, 12, 14, 16]
    for _, w in win:
        assert w.shape == (4, 13)


def test_aggregate_median_componentwise():
    w1 = np.array([[1.0, 2.0], [3.0, 4.0]])
    w2 = np.array([[5.0, 6.0], [7.0, 8.0]])
    w3 = np.array([[9.0, 10.0], [11.0, 12.0]])
    out = aggregate_median([w1, w2, w3])
    expected = np.array([[5.0, 6.0], [7.0, 8.0]])  # median componentwise
    np.testing.assert_allclose(out, expected)


def test_build_W_n_residues_partition():
    """Residue partition: every aggregated W_n[a] has shape (p^n, 13)."""
    rng = np.random.default_rng(0)
    X = rng.standard_normal((64, 13))
    p = 2
    n_max = 3
    W_n = build_W_n(X, p=p, n_max=n_max, step=1)
    for n in range(1, n_max + 1):
        for a, w in W_n[n].items():
            assert 0 <= a < p ** n
            assert w.shape == (p ** n, 13)


def test_build_W_n_ternary_residues_in_range():
    rng = np.random.default_rng(1)
    X = rng.standard_normal((81, 13))
    W_n = build_W_n(X, p=3, n_max=2, step=1)
    for n in range(1, 3):
        keys = list(W_n[n].keys())
        for a in keys:
            assert 0 <= a < 3 ** n
