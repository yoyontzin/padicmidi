#!/usr/bin/env python3
"""
padicmidi.cli.run_one — analyse a single MIDI file (entry point: ``padicmidi-run-one``).

Wrapper around :mod:`padicmidi.core.hierarchical` that mirrors the
historical ``run_one_piece.py`` script but with two improvements:

* Calls the motor in-process (no ``subprocess``).
* Exposes the random seed and all hyper-parameters via the CLI.

Examples
--------
::

    padicmidi-run-one bwv1007-1.mid bwv1007_pre beats 2 5 \\
        --out results_local/bwv1007_pre/beats/p2

    padicmidi-run-one bwv1007-1.mid bwv1007_pre beats 3 4 \\
        --K 16 --Kchild 2 --M 800 --step 2 --seed 42 \\
        --out results_local/bwv1007_pre/beats/p3
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

from padicmidi import __version__
from padicmidi.core.config import (
    DEFAULT_BIN_BEATS,
    DEFAULT_BIN_SECONDS,
    DEFAULT_K,
    DEFAULT_KCHILD,
    DEFAULT_M,
    DEFAULT_SEED,
    DEFAULT_STEP,
    SUPPORTED_PRIMES,
    default_nmax,
)
from padicmidi.core.hierarchical import (
    build_X_beats,
    build_X_seconds,
    run_hierarchical,
)


def _build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="padicmidi-run-one",
        description=(
            "Analyse a single MIDI file with the p-adic hierarchical motor "
            "and write coherence/audit/prototype CSVs to an output folder."
        ),
    )
    ap.add_argument("midi", help="Path to the MIDI file (absolute or relative).")
    ap.add_argument("piece", help="Short identifier for the piece (used in output folder name).")
    ap.add_argument("axis", choices=["beats", "seconds"], help="Time axis.")
    ap.add_argument("p", type=int, help=f"Prime in {SUPPORTED_PRIMES}.")
    ap.add_argument("Nmax", type=int, nargs="?", default=None, help="Maximum tower level (default depends on p).")
    ap.add_argument("--out", required=True, help="Output directory.")
    ap.add_argument("--K", type=int, default=DEFAULT_K, help=f"K for K-means (default {DEFAULT_K}).")
    ap.add_argument("--Kchild", type=int, default=DEFAULT_KCHILD, help=f"Children per parent (default {DEFAULT_KCHILD}).")
    ap.add_argument("--M", type=int, default=DEFAULT_M, help=f"Subsample size for K-means (default {DEFAULT_M}).")
    ap.add_argument("--step", type=int, default=DEFAULT_STEP, help=f"Window step (default {DEFAULT_STEP}).")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"Random seed (default {DEFAULT_SEED}).")
    ap.add_argument("--bin-beats", type=float, default=DEFAULT_BIN_BEATS, help=f"Bin size (beats axis, default {DEFAULT_BIN_BEATS:.6f}).")
    ap.add_argument("--bin", type=float, default=DEFAULT_BIN_SECONDS, help=f"Bin size (seconds axis, default {DEFAULT_BIN_SECONDS}).")
    ap.add_argument("--version", action="version", version=f"padicmidi {__version__}")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)

    if args.p not in SUPPORTED_PRIMES:
        print(f"error: --p must be one of {SUPPORTED_PRIMES}; got {args.p!r}", file=sys.stderr)
        return 2
    Nmax = args.Nmax if args.Nmax is not None else default_nmax(args.p)

    midi_path = Path(args.midi).expanduser().resolve()
    if not midi_path.exists():
        print(f"error: MIDI file not found: {midi_path}", file=sys.stderr)
        return 2

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.axis == "seconds":
        X = build_X_seconds(str(midi_path), bin_size=args.bin)
    else:
        X = build_X_beats(str(midi_path), bin_size_beats=args.bin_beats)

    if len(X) < 2:
        print("error: series too short (less than 2 bins)", file=sys.stderr)
        return 1

    rng = np.random.default_rng(args.seed)
    prototypes_n, f_n, pi_maps, coherence_rows, audit_rows = run_hierarchical(
        X, args.p, Nmax, args.step, args.K, args.Kchild, args.M, rng
    )

    p = args.p
    params = {
        "piece": args.piece,
        "midi": str(midi_path),
        "axis": args.axis,
        "p": p,
        "Nmax": Nmax,
        "K": args.K,
        "Kchild": args.Kchild,
        "M": args.M,
        "step": args.step,
        "seed": args.seed,
        "bin_seconds": args.bin,
        "bin_beats": args.bin_beats,
        "padicmidi_version": __version__,
    }
    (out_dir / "params.json").write_text(json.dumps(params, indent=2))
    (out_dir / "params.txt").write_text(
        " ".join(f"{k}={v}" for k, v in params.items()) + "\n"
    )

    for n, prot in prototypes_n.items():
        flat = prot.reshape(prot.shape[0], -1)
        np.savetxt(out_dir / f"S_n_prototypes_p{p}_n{n}.csv", flat, delimiter=",")
    for n, pi_list in pi_maps.items():
        with open(out_dir / f"pi_p{p}_n{n+1}_to_n{n}.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["child_id", "parent_id"])
            for cid, pid in enumerate(pi_list):
                w.writerow([cid, pid])
    for n, fn in f_n.items():
        with open(out_dir / f"f_p{p}_n{n}.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["residue", "prototype_id"])
            for a in sorted(fn.keys()):
                w.writerow([a, fn[a]])

    with open(out_dir / f"coherence_hier_p{p}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["n", "Coh_pi", "Coh_grid", "n_samples_n", "n_samples_nplus1"])
        w.writeheader()
        w.writerows(coherence_rows)

    audit_fields = [
        "n", "parent_class", "n_valid_siblings", "excluded_sparsity",
        "V_SC_pi", "AI_pi", "coherent_count_pi",
        "V_SC_trunc", "AI_trunc", "coherent_count_trunc",
        "parent_prototype",
    ]
    with open(out_dir / f"audit_p{p}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=audit_fields)
        w.writeheader()
        w.writerows(audit_rows)

    print(
        f"[padicmidi-run-one] piece={args.piece} axis={args.axis} p={p} Nmax={Nmax}: "
        f"wrote {out_dir} ({len(coherence_rows)} coherence rows, {len(audit_rows)} audit rows).",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
