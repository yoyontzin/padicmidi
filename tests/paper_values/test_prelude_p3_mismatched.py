"""Paper-value test: BWV 1007 Prelude mismatched (r=2, p=3) at n=3 falls near floor 1/3.

Reference: Paper 2 §5 (mismatched branching: Coh_pi(3,3) drops to ~ 0.36, near floor 1/p = 1/3).
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest


def test_prelude_p3_mismatched(results_dir: Path) -> None:
    csv_path = results_dir / "bwv1007_prelude" / "beats" / "p3" / "coherence_hier_p3.csv"
    if not csv_path.exists():
        pytest.skip(f"gold CSV not present: {csv_path}")
    with open(csv_path, newline="") as fh:
        rows = {int(r["n"]): r for r in csv.DictReader(fh)}
    assert 3 in rows, "Coh_pi(3,3) not present in gold CSV"
    coh_pi_n3 = float(rows[3]["Coh_pi"])
    assert 0.32 <= coh_pi_n3 <= 0.40, (
        f"Prelude mismatched: expected Coh_pi(3,3) ~ 0.36 (near 1/3 floor), got {coh_pi_n3:.6f}"
    )
