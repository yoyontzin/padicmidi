"""
padicmidi.core.config — module-level constants and defaults.

These are the constants that govern the canonical behaviour of the
hierarchical p-adic motor. Changing any of them invalidates the
gold-standard CSVs in ``results/verified/`` and the test suite
``tests/regression/`` and ``tests/paper_values/``.

Conventions and rationale are documented in ``MATH-SPEC.md``.
"""

from __future__ import annotations

ALPHA: float = 1.0
MAX_WINDOWS_PER_RESIDUE: int = 800

DEFAULT_K: int = 16
DEFAULT_KCHILD: int = 2
DEFAULT_M: int = 800
DEFAULT_STEP: int = 2
DEFAULT_SEED: int = 42

DEFAULT_BIN_SECONDS: float = 0.05
DEFAULT_BIN_BEATS: float = 1.0 / 12.0

SUPPORTED_PRIMES: tuple[int, ...] = (2, 3, 5, 7)

_DEFAULT_NMAX_BY_PRIME: dict[int, int] = {2: 6, 3: 5, 5: 4, 7: 3}


def default_nmax(p: int) -> int:
    """Return the default ``Nmax`` for prime ``p`` (memory-aware)."""
    if p not in _DEFAULT_NMAX_BY_PRIME:
        raise ValueError(
            f"Unsupported prime p={p!r}; supported primes are {SUPPORTED_PRIMES}."
        )
    return _DEFAULT_NMAX_BY_PRIME[p]
