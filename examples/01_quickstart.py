"""Quickstart: analyse the BWV 1007 prelude with p=2 and print the coherences."""

from __future__ import annotations

from pathlib import Path

from padicmidi import run_hierarchical_from_midi

HERE = Path(__file__).resolve().parent
MIDI = HERE.parent / "data" / "midi" / "bwv1007-1.mid"


def main() -> None:
    result = run_hierarchical_from_midi(
        midi_path=str(MIDI),
        p=2,
        axis="beats",
        nmax=5,
    )
    print(f"\nBWV 1007 (Prelude) — beats axis — p=2 — Nmax=5\n")
    print(f"{'n':>3}  {'Coh_pi':>10}  {'Coh_grid':>10}  {'samples_n':>10}  {'samples_n+1':>12}")
    for row in result["coherence"]:
        print(
            f"{row['n']:>3}  {row['Coh_pi']:>10.6f}  {row['Coh_grid']:>10.6f}  "
            f"{row['n_samples_n']:>10}  {row['n_samples_nplus1']:>12}"
        )
    print(
        "\nThe constant value 0.500000 illustrates the architectural null floor "
        "Coh_pi(p, n) = 1/p predicted by Proposition 3.1 of the companion paper."
    )


if __name__ == "__main__":
    main()
