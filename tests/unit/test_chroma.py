"""Unit tests for the chroma + onset density representation."""

from __future__ import annotations

import numpy as np

from padicmidi.core.echo import (
    chroma_series_duration,
    onset_density_series,
    series_with_rhythm,
    spectral_flux_series,
    zscore_series,
)


def test_chroma_l1_normalised_per_row():
    events = [
        (0.0, 1.0, 60, 100),  # C4
        (1.0, 2.0, 62, 100),  # D4
    ]
    H = chroma_series_duration(events, bin_size=0.5)
    row_sums = H.sum(axis=1)
    nonzero = row_sums > 0
    np.testing.assert_allclose(row_sums[nonzero], 1.0, atol=1e-12)


def test_chroma_pitch_class_assignment():
    """A C major sustained for one second occupies pitch class 0."""
    events = [(0.0, 1.0, 60, 127)]
    H = chroma_series_duration(events, bin_size=0.5)
    assert H[0, 0] == 1.0
    assert H[0, 1:].sum() == 0.0


def test_onset_density_units():
    events = [
        (0.0, 0.1, 60, 127),  # one onset, vel 127
        (0.0, 0.1, 64, 64),   # second onset, vel 64
    ]
    a = onset_density_series(events, bin_size=1.0)
    expected = (127 + 64) / 127.0
    np.testing.assert_allclose(a[0], expected, atol=1e-12)


def test_series_with_rhythm_dim_13():
    H = np.zeros((10, 12))
    a = np.zeros(10)
    X = series_with_rhythm(H, a, alpha=1.0)
    assert X.shape == (10, 13)


def test_spectral_flux_zero_constant():
    H = np.tile(np.eye(1, 12), (10, 1))
    f = spectral_flux_series(H)
    assert f.shape == (10,)
    np.testing.assert_allclose(f, 0.0)


def test_zscore_zero_when_constant():
    x = np.ones(20)
    out = zscore_series(x)
    np.testing.assert_allclose(out, 0.0)
