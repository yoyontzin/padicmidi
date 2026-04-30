"""Run the hierarchical p-adic motor on the six BWV 1007 movements.

Outputs a table that summarises ``Coh_pi(p, n)`` for ``p`` in {2, 3} across
the suite. This is a programmatic reproduction of part of the gold standard
of Paper 2.
"""

from __future__ import annotations

from pathlib import Path

from padicmidi import run_hierarchical_from_midi

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "midi"

PIECES = [
    ("Prelude",   "bwv1007-1.mid"),
    ("Allemande", "bwv1007-2.mid"),
    ("Courante",  "bwv1007-3.mid"),
    ("Sarabande", "bwv1007-4.mid"),
    ("Menuet",    "bwv1007-5.mid"),
    ("Gigue",     "bwv1007-6.mid"),
]


def main() -> None:
    print(f"\nBWV 1007 — beats axis — Coh_pi at p in {{2, 3}}\n")
    print(f"{'Piece':<12} {'p':>3} {'n':>3}  {'Coh_pi':>10}")
    print("-" * 36)
    for name, midi_name in PIECES:
        midi_path = DATA / midi_name
        for p in (2, 3):
            res = run_hierarchical_from_midi(str(midi_path), p=p, axis="beats")
            for row in res["coherence"]:
                print(f"{name:<12} {p:>3} {row['n']:>3}  {row['Coh_pi']:>10.6f}")


if __name__ == "__main__":
    main()
