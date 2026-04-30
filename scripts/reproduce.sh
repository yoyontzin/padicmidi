#!/usr/bin/env bash
# scripts/reproduce.sh — re-run the canonical pipeline of PAdicMIDI.
# Reproduces the gold-standard CSVs of both companion papers and writes them
# under results_local/. To compare with results/verified/ use scripts/validate.sh.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -d ".venv" ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

PIECES=(
    "bwv1007-1.mid:bwv1007_pre"
    "bwv1007-2.mid:bwv1007_all"
    "bwv1007-3.mid:bwv1007_cou"
    "bwv1007-4.mid:bwv1007_sar"
    "bwv1007-5.mid:bwv1007_men"
    "bwv1007-6.mid:bwv1007_gig"
    "cs1-1pre.mid:cs1_1pre"
    "cs1-4sar.mid:cs1_4sar"
)
PRIMES=(2 3 5 7)

mkdir -p results_local

for spec in "${PIECES[@]}"; do
    midi="${spec%%:*}"
    piece="${spec##*:}"
    midi_path="data/midi/${midi}"
    if [[ ! -f "$midi_path" ]]; then
        echo "[reproduce] missing MIDI: $midi_path (skipping)" >&2
        continue
    fi
    for p in "${PRIMES[@]}"; do
        out_dir="results_local/${piece}/beats/p${p}"
        mkdir -p "$out_dir"
        echo "[reproduce] piece=${piece} p=${p}"
        padicmidi-run-one "$midi_path" "$piece" beats "$p" --out "$out_dir"
    done
done

echo "[reproduce] done. Compare results_local/ with results/verified/ via scripts/validate.sh."
