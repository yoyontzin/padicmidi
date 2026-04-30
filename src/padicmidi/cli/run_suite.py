#!/usr/bin/env python3
"""
padicmidi.cli.run_suite — Phase I run on a suite of MIDIs (entry point: ``padicmidi-run-suite``).

Runs the Phase I (echo) motor on each MIDI in a folder and writes
results under a configurable output directory. By default analyses the
six BWV 1007 movements bundled in ``data/midi/`` of the package.

This is a thin orchestration wrapper around :mod:`padicmidi.core.echo`,
invoking it as a subprocess to keep CLI argument parsing isolated.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from padicmidi import __version__

DEFAULT_PIECES: list[tuple[str, str]] = [
    ("1pre", "cs1-1pre.mid"),
    ("2all", "cs1-2all.mid"),
    ("3cou", "cs1-3cou.mid"),
    ("4sar", "cs1-4sar.mid"),
    ("5men", "cs1-5men.mid"),
    ("6gig", "cs1-6gig.mid"),
]


def _build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="padicmidi-run-suite",
        description="Run Phase I on a suite of MIDI files (defaults to the BWV 1007 movements).",
    )
    ap.add_argument(
        "--midi-dir",
        type=Path,
        required=True,
        help="Directory containing the MIDI files referenced by --pieces (or default cs1-* set).",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Output directory; subfolders 'seconds/' and 'beats/' will be created.",
    )
    ap.add_argument(
        "--pieces",
        nargs="*",
        metavar="SHORTNAME=FILENAME",
        help="Override the default list (e.g. 1pre=cs1-1pre.mid 2all=cs1-2all.mid). Default uses the BWV 1007 set.",
    )
    ap.add_argument("--cap", type=int, default=300, help="Window cap (default 300, paper default).")
    ap.add_argument("--bin-beats", type=float, default=0.083333)
    ap.add_argument("--axes", nargs="+", choices=["seconds", "beats"], default=["seconds", "beats"])
    ap.add_argument("--version", action="version", version=f"padicmidi {__version__}")
    return ap


def _parse_pieces(spec: list[str] | None) -> list[tuple[str, str]]:
    if not spec:
        return DEFAULT_PIECES
    out: list[tuple[str, str]] = []
    for item in spec:
        if "=" not in item:
            raise SystemExit(f"--pieces entry must be SHORTNAME=FILENAME; got {item!r}")
        short, name = item.split("=", 1)
        out.append((short.strip(), name.strip()))
    return out


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    pieces = _parse_pieces(args.pieces)

    midi_dir = args.midi_dir.expanduser().resolve()
    if not midi_dir.is_dir():
        print(f"error: --midi-dir does not exist: {midi_dir}", file=sys.stderr)
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_seconds = args.out_dir / "seconds"
    out_beats = args.out_dir / "beats"
    out_seconds.mkdir(exist_ok=True)
    out_beats.mkdir(exist_ok=True)

    for short, name in pieces:
        midi_path = midi_dir / name
        if not midi_path.exists():
            print(f"[run-suite] skipping missing MIDI: {midi_path}", file=sys.stderr)
            continue
        for axis in args.axes:
            out_dir = out_seconds if axis == "seconds" else out_beats
            prefix = str(out_dir) + f"/cs1_{short}_cap{args.cap}_"
            cmd = [
                sys.executable,
                "-m", "padicmidi.core.echo",
                str(midi_path),
                "--phase1-only",
                "--save", prefix,
                "--cap", str(args.cap),
            ]
            if axis == "beats":
                cmd += ["--time-axis", "beats", "--bin-beats", str(args.bin_beats)]
            print("[run-suite]", " ".join(cmd))
            ret = subprocess.run(cmd)
            if ret.returncode != 0:
                print(f"[run-suite] failed on {short}/{axis}", file=sys.stderr)
                return ret.returncode
    print("[run-suite] finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
