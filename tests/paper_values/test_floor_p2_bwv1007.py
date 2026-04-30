"""Paper-value test: BWV 1007 binary floor Coh_pi(2,n) = 0.500 exact, all n.

Reference: Paper 2 abstract and §5; verified gold CSV at
``results/verified/bwv1007_prelude/beats/p2/coherence_hier_p2.csv``.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest


def _read_coherence_csv(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def test_floor_p2_bwv1007(results_dir: Path) -> None:
    csv_path = results_dir / "bwv1007_prelude" / "beats" / "p2" / "coherence_hier_p2.csv"
    if not csv_path.exists():
        pytest.skip(f"gold CSV not present: {csv_path}")
    rows = _read_coherence_csv(csv_path)
    assert rows, "gold CSV is empty"
    for row in rows:
        n = int(row["n"])
        coh_pi = float(row["Coh_pi"])
        assert coh_pi == pytest.approx(0.5, abs=1e-6), (
            f"BWV 1007 binary floor violated at n={n}: Coh_pi={coh_pi}"
        )
