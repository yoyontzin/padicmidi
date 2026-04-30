"""Paper-value test: BWV 1007 Sarabande matched (r=p=3) gives Coh_pi(3,3) ~ 0.90.

Reference: Paper 2 §5 (matched branching figure).
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest


def test_sarabande_p3_n3(results_dir: Path) -> None:
    csv_path = results_dir / "cs1_4sar" / "p3" / "coherence_hier_p3.csv"
    if not csv_path.exists():
        pytest.skip(f"gold CSV not present: {csv_path}")
    with open(csv_path, newline="") as fh:
        rows = {int(r["n"]): r for r in csv.DictReader(fh)}
    assert 3 in rows, "Coh_pi(3,3) not present in gold CSV"
    coh_pi_n3 = float(rows[3]["Coh_pi"])
    assert 0.85 <= coh_pi_n3 <= 0.95, (
        f"Sarabande matched: expected Coh_pi(3,3) ~ 0.90, got {coh_pi_n3:.6f}"
    )
