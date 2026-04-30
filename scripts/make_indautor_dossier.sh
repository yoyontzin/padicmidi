#!/usr/bin/env bash
# scripts/make_indautor_dossier.sh — assemble the INDAUTOR dossier.
# Copies source code into indautor/codigo-fuente/, runs the test suite, captures
# the output, and writes the manifest.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p indautor/codigo-fuente indautor/evidencia-corridas

echo "[dossier] copying source code…"
rsync -a --delete --exclude '__pycache__' src/padicmidi/ indautor/codigo-fuente/

if [[ -d ".venv" ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

echo "[dossier] running tests and capturing output…"
{
    echo "PAdicMIDI test suite — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Python: $(python --version 2>&1)"
    echo
    pytest tests/ -v
} > indautor/evidencia-corridas/04_test_suite_output.txt

echo "[dossier] running quickstart on BWV 1007 prelude…"
{
    echo "Quickstart: padicmidi-run-one data/midi/bwv1007-1.mid bwv1007_pre beats 2"
    echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo
    padicmidi-run-one data/midi/bwv1007-1.mid bwv1007_pre beats 2 \
        --out indautor/evidencia-corridas/quickstart_p2 2>&1
    echo
    echo "Resulting CSV:"
    cat indautor/evidencia-corridas/quickstart_p2/coherence_hier_p2.csv
} > indautor/evidencia-corridas/01_quickstart_run.log

echo "[dossier] writing manifest…"
{
    echo "# Manifest of files in the INDAUTOR dossier — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo
    find indautor -type f ! -name '.DS_Store' -print0 \
        | LC_ALL=C sort -z \
        | xargs -0 shasum -a 256
} > indautor/manifiesto-archivos.md

echo "[dossier] done. See indautor/."
