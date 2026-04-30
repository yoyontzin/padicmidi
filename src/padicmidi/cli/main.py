#!/usr/bin/env python3
"""
padicmidi.cli.main — unified ``padicmidi`` command-line entry point.

Dispatches to the specialised sub-commands (run-one, run-suite, benchmark,
job-list, mutopia). This is the canonical executable advertised by the
manuals: ``padicmidi <subcommand> [options]``.
"""

from __future__ import annotations

import sys

from padicmidi.cli import benchmark, job_list, mutopia, run_one, run_suite

SUBCOMMANDS = {
    "run-one":   run_one.main,
    "run-suite": run_suite.main,
    "benchmark": benchmark.main,
    "job-list":  job_list.main,
    "mutopia":   mutopia.main,
}

USAGE = """\
padicmidi v1.0.0 — p-adic hierarchical analysis of symbolic music
Author: J. Rogelio Pérez-Buendía (CIMAT-Mérida) · ORCID 0000-0002-7739-4779

Usage:
  padicmidi <subcommand> [arguments...]
  padicmidi --help
  padicmidi <subcommand> --help

Sub-commands:
  run-one    Analyse a single MIDI file (one piece, one prime).
  run-suite  Analyse a corpus across multiple primes and axes.
  benchmark  Run the canonical BWV 1007 benchmark.
  job-list   Generate a job list for a corpus.
  mutopia    Download CC-licensed MIDI files from Mutopia.

For details on each sub-command, run:
  padicmidi <subcommand> --help

Web demo (no installation needed):
  Open `web-demo/applet.html` (English) or
       `web-demo/applet-es.html` (Spanish) in any modern browser.
"""


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    sub = argv[0]
    if sub not in SUBCOMMANDS:
        print(f"padicmidi: unknown sub-command '{sub}'\n", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    sys.argv = [f"padicmidi {sub}"] + argv[1:]
    rc = SUBCOMMANDS[sub]()
    return int(rc) if rc is not None else 0


if __name__ == "__main__":
    raise SystemExit(main())
