"""
PAdicMIDI — A Python Toolkit for Hierarchical, Ultrametric, and p-adic
Analysis of Symbolic Music Data.

Author: J. Rogelio Pérez-Buendía (CIMAT–Mérida).
Licence: MIT. Documentation and verified results: CC-BY 4.0.

Public API (stable across the v1.x series):

    >>> from padicmidi import run_hierarchical_from_midi
    >>> result = run_hierarchical_from_midi("path/to/file.mid", p=2)
    >>> result["coherence"]      # list of dicts {n, Coh_pi, Coh_grid, ...}

The full motor is available under the submodules ``core``, ``io``,
``analysis``, ``figs``, ``cli``.
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "J. Rogelio Pérez-Buendía"
__email__ = "rogelio@cimat.mx"
__license__ = "MIT"

from padicmidi.core.config import (
    ALPHA,
    DEFAULT_BIN_BEATS,
    DEFAULT_BIN_SECONDS,
    DEFAULT_K,
    DEFAULT_KCHILD,
    DEFAULT_M,
    DEFAULT_SEED,
    DEFAULT_STEP,
    MAX_WINDOWS_PER_RESIDUE,
    SUPPORTED_PRIMES,
    default_nmax,
)


def run_hierarchical_from_midi(
    midi_path: str,
    p: int,
    axis: str = "beats",
    nmax: int | None = None,
    K: int = DEFAULT_K,
    Kchild: int = DEFAULT_KCHILD,
    M: int = DEFAULT_M,
    step: int = DEFAULT_STEP,
    seed: int = DEFAULT_SEED,
    bin_seconds: float = DEFAULT_BIN_SECONDS,
    bin_beats: float = DEFAULT_BIN_BEATS,
) -> dict:
    """High-level entry point: compute the p-adic hierarchical maps for one MIDI.

    Parameters
    ----------
    midi_path : str
        Path to a Standard MIDI file.
    p : int
        Prime in :data:`SUPPORTED_PRIMES` (i.e. 2, 3, 5 or 7).
    axis : {"beats", "seconds"}, default "beats"
        Time axis used to build the bins of the chroma series.
    nmax : int or None, default None
        Maximum tower level. ``None`` uses :func:`default_nmax`.
    K, Kchild, M, step, seed : int
        Algorithm hyper-parameters; defaults reproduce the gold standard.
    bin_seconds, bin_beats : float
        Bin sizes for the seconds and beats axes respectively.

    Returns
    -------
    dict
        Keys: ``prototypes_n``, ``f_n``, ``pi_maps``, ``coherence`` (list of
        dicts), ``audit`` (list of dicts).
    """
    import numpy as np

    from padicmidi.core.hierarchical import (
        build_X_seconds,
        build_X_beats,
        run_hierarchical,
    )

    if axis == "seconds":
        X = build_X_seconds(midi_path, bin_size=bin_seconds)
    elif axis == "beats":
        X = build_X_beats(midi_path, bin_size_beats=bin_beats)
    else:
        raise ValueError(f"axis must be 'seconds' or 'beats'; got {axis!r}")

    if len(X) < 2:
        raise ValueError("Series too short (less than 2 bins).")

    Nmax = nmax if nmax is not None else default_nmax(p)
    rng = np.random.default_rng(seed)
    prototypes_n, f_n, pi_maps, coherence_rows, audit_rows = run_hierarchical(
        X, p, Nmax, step, K, Kchild, M, rng
    )
    return {
        "prototypes_n": prototypes_n,
        "f_n": f_n,
        "pi_maps": pi_maps,
        "coherence": coherence_rows,
        "audit": audit_rows,
    }


__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "ALPHA",
    "DEFAULT_BIN_BEATS",
    "DEFAULT_BIN_SECONDS",
    "DEFAULT_K",
    "DEFAULT_KCHILD",
    "DEFAULT_M",
    "DEFAULT_SEED",
    "DEFAULT_STEP",
    "MAX_WINDOWS_PER_RESIDUE",
    "SUPPORTED_PRIMES",
    "default_nmax",
    "run_hierarchical_from_midi",
]
