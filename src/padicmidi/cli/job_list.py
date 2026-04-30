#!/usr/bin/env python3
"""
padicmidi.cli.job_list — generate a job manifest for the bundled corpus.

Entry point: ``padicmidi-job-list``. Writes a file ``job_list.txt`` in
the current working directory with one line per job in the form

    <midi> <piece_id> <axis> <p> <Nmax>

ready to be consumed by SLURM array jobs, GNU parallel, or hand
piped through ``padicmidi-run-one``.
"""

import argparse
import sys

from padicmidi import __version__

# Movimientos por suite:
#  1=Prelude, 2=Allemande, 3=Courante, 4=Sarabande, 5=Menuet/Gavotte, 6=Gigue

PIECES = [
    # ── BWV 1007 Mutopia (LilyPond 2018, Public Domain) ──────────────────
    # Fuente canónica: un solo tempo por movimiento, sin artefactos
    ("bwv1007-1.mid", "bwv1007_pre"),   # Prelude   2/2  70 BPM
    ("bwv1007-2.mid", "bwv1007_all"),   # Allemande 3/4  80 BPM
    ("bwv1007-3.mid", "bwv1007_cou"),   # Courante  3/4  60 BPM
    ("bwv1007-4.mid", "bwv1007_sar"),   # Sarabande 3/4 120 BPM
    ("bwv1007-5.mid", "bwv1007_men"),   # Menuet    3/4 120 BPM
    ("bwv1007-6.mid", "bwv1007_gig"),   # Gigue     6/8 120 BPM ← experimento clave p=2 vs p=3

    # ── BWV 1007 Grossman 1997 (beats-axis only) ─────────────────────────
    # Incluir para replicabilidad; NO usar eje de segundos (artefactos de tempo)
    ("cs1-1pre.mid", "cs1_pre"),
    ("cs1-2all.mid", "cs1_all"),
    ("cs1-3cou.mid", "cs1_cou"),
    ("cs1-4sar.mid", "cs1_sar"),
    ("cs1-5men.mid", "cs1_men"),
    ("cs1-6gig.mid", "cs1_gig"),

    # ── BWV 1008 Mutopia (Suite 2 Re menor, CC-BY-SA 3.0) ─────────────────
    ("bwv1008-1.mid", "bwv1008_pre"),   # Prelude
    ("bwv1008-2.mid", "bwv1008_all"),   # Allemande
    ("bwv1008-3.mid", "bwv1008_cou"),   # Courante
    ("bwv1008-4.mid", "bwv1008_sar"),   # Sarabande
    ("bwv1008-5.mid", "bwv1008_men"),   # Menuet
    ("bwv1008-6.mid", "bwv1008_gig"),   # Gigue

    # ── BWV 1009 Mutopia (Suite 3 Do mayor, cellosuite3) ──────────────────
    # ZIP contiene 5 movimientos (sin Gigue separado)
    ("cellosuite3-1.mid", "bwv1009_pre"),
    ("cellosuite3-2.mid", "bwv1009_all"),
    ("cellosuite3-3.mid", "bwv1009_cou"),
    ("cellosuite3-4.mid", "bwv1009_sar"),
    ("cellosuite3-5.mid", "bwv1009_men"),

    # ── Toys ──────────────────────────────────────────────────────────────
    ("toy_binary.mid",  "toy_binary"),
    ("toy_ternary.mid", "toy_ternary"),
]

# Ejes y primos
AXES = ["beats", "seconds"]
PRIMES = {2: 6, 3: 5, 5: 4, 7: 3}  # prime: Nmax

# Para cs1_* restringir a beats (artefacto de tempo en seconds)
CS1_PIECES = {p for _, p in PIECES if p.startswith("cs1_")}

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="padicmidi-job-list",
        description="Generate a job manifest (job_list.txt) for the bundled MIDI corpus.",
    )
    ap.add_argument("--out", default="job_list.txt", help="Output file (default job_list.txt).")
    ap.add_argument("--version", action="version", version=f"padicmidi {__version__}")
    args = ap.parse_args(argv)

    jobs = []
    for midi, piece in PIECES:
        axes = ["beats"] if piece in CS1_PIECES else AXES
        for axis in axes:
            for p, Nmax in PRIMES.items():
                jobs.append(f"{midi} {piece} {axis} {p} {Nmax}")

    with open(args.out, "w") as f:
        f.write("\n".join(jobs) + "\n")

    print(f"{len(jobs)} jobs written to {args.out}")
    print(f"  BWV1007 Mutopia (2 axes): 6 × 2 × 4 = {6*2*4} jobs")
    print(f"  BWV1007 Grossman (beats): 6 × 1 × 4 = {6*1*4} jobs")
    print(f"  BWV1008 Mutopia (2 axes): 6 × 2 × 4 = {6*2*4} jobs")
    print(f"  BWV1009 Mutopia (2 axes): 5 × 2 × 4 = {5*2*4} jobs")
    print(f"  Toys (2 axes):            2 × 2 × 4 = {2*2*4} jobs")
    print(f"  TOTAL: {len(jobs)}")
    print(f"\nFirst jobs:")
    for j in jobs[:6]:
        print(f"  {j}")
    print("  ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
