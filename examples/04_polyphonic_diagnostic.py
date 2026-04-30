"""Demonstrate the texture discriminant on a hand-picked monophonic vs polyphonic pair.

Compare ``Coh_pi(2, n)`` between BWV 1007 (monophonic cello suite, expected to
SATISFY the floor 0.500 exactly) and a hypothetical polyphonic counterpart
(deviates from the floor). The full polyphonic Bach corpus is in
``data/midi/external/`` if available; this example uses BWV 1008 as a proxy.
"""

from __future__ import annotations

from pathlib import Path

from padicmidi import run_hierarchical_from_midi

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "midi"

PAIRS = [
    ("BWV 1007 Prelude (cello solo)", "bwv1007-1.mid"),
    ("BWV 1008 Prelude (cello solo)", "bwv1008-1.mid"),
]


def main() -> None:
    print("\nTexture diagnostic — Coh_pi(2, n) for monophonic Bach Cello Suites\n")
    print(f"{'Piece':<35} {'n':>3}  {'Coh_pi':>10}  {'deviation from 0.5':>22}")
    print("-" * 76)
    for label, midi_name in PAIRS:
        midi_path = DATA / midi_name
        if not midi_path.exists():
            print(f"{label:<35}  (missing: {midi_name})")
            continue
        res = run_hierarchical_from_midi(str(midi_path), p=2, axis="beats")
        for row in res["coherence"]:
            dev = abs(row["Coh_pi"] - 0.5)
            marker = "  <-- deviates" if dev > 0.01 else ""
            print(f"{label:<35} {row['n']:>3}  {row['Coh_pi']:>10.6f}  {dev:>22.6f}{marker}")


if __name__ == "__main__":
    main()
