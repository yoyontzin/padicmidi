#!/usr/bin/env python3
"""
padicmidi.cli.benchmark — Phase I benchmark across the bundled benchmark set.

Entry point: ``padicmidi-benchmark``. Runs the Phase I motor for each
piece in the benchmark set (BWV 1007 movements + binary/ternary toys)
and writes prefixed outputs under the user-supplied output directory.

Defaults reproduce the gold-standard runs of the companion papers.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from padicmidi import __version__

BENCHMARK_PIECES: list[tuple[str, str]] = [
    ("cs1_1pre", "cs1-1pre.mid"),
    ("cs1_2all", "cs1-2all.mid"),
    ("cs1_3cou", "cs1-3cou.mid"),
    ("cs1_4sar", "cs1-4sar.mid"),
    ("cs1_5men", "cs1-5men.mid"),
    ("cs1_6gig", "cs1-6gig.mid"),
    ("toy_binary", "toy_binary.mid"),
    ("toy_ternary", "toy_ternary.mid"),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="padicmidi-benchmark",
        description="Run the Phase I benchmark for all pieces in the BWV 1007 + toys set.",
    )
    ap.add_argument(
        "--midi-dir",
        type=Path,
        required=True,
        help="Directory containing the benchmark MIDI files.",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Output directory; subfolders 'seconds/' and 'beats/' will be created.",
    )
    ap.add_argument("--seconds-only", action="store_true", help="Only run seconds axis.")
    ap.add_argument("--beats-only", action="store_true", help="Only run beats axis.")
    ap.add_argument("--dry-run", action="store_true", help="Print commands only.")
    ap.add_argument("--version", action="version", version=f"padicmidi {__version__}")
    args = ap.parse_args(argv)

    midi_dir = args.midi_dir.expanduser().resolve()
    if not midi_dir.is_dir():
        print(f"error: --midi-dir does not exist: {midi_dir}", file=sys.stderr)
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_seconds = args.out_dir / "seconds"
    out_beats = args.out_dir / "beats"

    run_seconds = not args.beats_only
    run_beats = not args.seconds_only

    for piece, midi_name in BENCHMARK_PIECES:
        midi_path = midi_dir / midi_name
        if not midi_path.exists():
            print(f"[benchmark] skip (missing): {midi_name}", file=sys.stderr)
            continue

        if run_seconds:
            out_seconds.mkdir(parents=True, exist_ok=True)
            prefix = str(out_seconds) + f"/{piece}_"
            cmd = [
                sys.executable, "-m", "padicmidi.core.echo",
                str(midi_path),
                "--phase1-only",
                "--save", prefix,
            ]
            print(" ".join(cmd))
            if not args.dry_run:
                ret = subprocess.run(cmd)
                if ret.returncode != 0:
                    print(f"[benchmark] failed on {piece}/seconds", file=sys.stderr)
                    return ret.returncode

        if run_beats:
            out_beats.mkdir(parents=True, exist_ok=True)
            prefix = str(out_beats) + f"/{piece}_"
            cmd = [
                sys.executable, "-m", "padicmidi.core.echo",
                str(midi_path),
                "--phase1-only",
                "--save", prefix,
                "--time-axis", "beats",
                "--bin-beats", "0.083333",
            ]
            print(" ".join(cmd))
            if not args.dry_run:
                ret = subprocess.run(cmd)
                if ret.returncode != 0:
                    print(f"[benchmark] failed on {piece}/beats", file=sys.stderr)
                    return ret.returncode

    print("[benchmark] finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
