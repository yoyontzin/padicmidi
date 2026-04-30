"""Compare ``Coh_pi`` against the architectural null floor 1/p for p in {2, 3, 5, 7}.

For BWV 1007 prelude (binary), the floor 1/2 = 0.500 is reached EXACTLY
because the structure of the piece satisfies the hypotheses (SC) and (AI) of
the null-floor proposition. For p in {3, 5, 7} the value is significantly
higher than the floor 1/p.
"""

from __future__ import annotations

from pathlib import Path

from padicmidi import run_hierarchical_from_midi

HERE = Path(__file__).resolve().parent
MIDI = HERE.parent / "data" / "midi" / "bwv1007-1.mid"


def main() -> None:
    print("\nBWV 1007 (Prelude) — beats axis — Coh_pi vs null floor 1/p\n")
    print(f"{'p':>3} {'1/p':>8} {'n':>3}  {'Coh_pi':>10}  {'gap':>10}")
    print("-" * 45)
    for p in (2, 3, 5, 7):
        floor = 1.0 / p
        res = run_hierarchical_from_midi(str(MIDI), p=p, axis="beats")
        for row in res["coherence"]:
            gap = row["Coh_pi"] - floor
            print(f"{p:>3} {floor:>8.4f} {row['n']:>3}  {row['Coh_pi']:>10.6f}  {gap:>+10.6f}")


if __name__ == "__main__":
    main()
