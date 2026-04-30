"""Shared pytest fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "midi"
RESULTS_DIR = PROJECT_ROOT / "results" / "verified"

# Ensure src/ is on sys.path even if the editable .pth was mangled by
# backslashes in the project path (a known pip limitation on Windows-style
# escapes inside POSIX paths).
_SRC = PROJECT_ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return DATA_DIR


@pytest.fixture(scope="session")
def results_dir() -> Path:
    return RESULTS_DIR


@pytest.fixture(scope="session")
def bwv1007_prelude(data_dir: Path) -> Path:
    """Path to the canonical BWV 1007 prelude MIDI."""
    candidate = data_dir / "bwv1007-1.mid"
    if not candidate.exists():
        pytest.skip(f"BWV 1007 prelude not found at {candidate}")
    return candidate
