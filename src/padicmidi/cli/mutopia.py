#!/usr/bin/env python3
"""
padicmidi.cli.mutopia — download CC-licensed MIDIs from the Mutopia project.

Entry point: ``padicmidi-mutopia``. Downloads ZIPs from
``mutopiaproject.org`` and extracts the BWV 1007/1008/1009 MIDI files
to a destination folder (defaults to the current working directory).
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

from padicmidi import __version__

ZIPS: list[tuple[str, str]] = [
    ("BWV1007", "https://www.mutopiaproject.org/ftp/BachJS/BWV1007/bwv1007/bwv1007-mids.zip"),
    ("BWV1008", "https://www.mutopiaproject.org/ftp/BachJS/BWV1008/bwv1008/bwv1008-mids.zip"),
    ("BWV1009", "https://www.mutopiaproject.org/ftp/BachJS/BWV1009/cellosuite3/cellosuite3-mids.zip"),
]

SKIP = ["viola", "bwv1007.mid", "cellosuite3.mid", "bwv1008.mid"]

USER_AGENT = "Mozilla/5.0 (academic research; padicmidi/{})".format(__version__)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="padicmidi-mutopia",
        description="Download Bach Cello Suites MIDIs from the Mutopia Project (CC-licensed).",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("."),
        help="Destination directory (default: current directory).",
    )
    ap.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds (default 30).")
    ap.add_argument("--version", action="version", version=f"padicmidi {__version__}")
    args = ap.parse_args(argv)

    dest = args.out.expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    print(f"Destination: {dest}\n")

    total = 0
    headers = {"User-Agent": USER_AGENT}
    for label, url in ZIPS:
        print(f"-> {label}: {url.split('/')[-1]}", flush=True)
        try:
            req = urllib.request.Request(url, headers=headers)
            data = urllib.request.urlopen(req, timeout=args.timeout).read()
            print(f"   ZIP downloaded: {len(data) // 1024} KB")
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for name in sorted(zf.namelist()):
                    if not name.lower().endswith(".mid"):
                        continue
                    base = os.path.basename(name)
                    if any(s in base for s in SKIP):
                        print(f"   skip: {base}")
                        continue
                    out_path = dest / base
                    with zf.open(name) as src, open(out_path, "wb") as dst:
                        dst.write(src.read())
                    print(f"   OK: {base} ({out_path.stat().st_size} bytes)")
                    total += 1
        except Exception as exc:
            print(f"   FAILED: {exc}", file=sys.stderr)

    print(f"\nNew MIDIs: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
