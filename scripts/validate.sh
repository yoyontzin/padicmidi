#!/usr/bin/env bash
# scripts/validate.sh — verify reproduced CSVs against gold standard.
# Compares results_local/ (newly produced by scripts/reproduce.sh) with
# results/verified/ (ground truth shipped with v1.0.0).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d "results_local" ]]; then
    echo "[validate] results_local/ not found; run scripts/reproduce.sh first." >&2
    exit 1
fi

mismatches=0
checked=0

while IFS= read -r -d '' gold_csv; do
    rel="${gold_csv#results/verified/}"
    local_csv="results_local/${rel}"
    if [[ ! -f "$local_csv" ]]; then
        echo "[validate] MISSING in results_local: $rel" >&2
        mismatches=$((mismatches + 1))
        continue
    fi
    if diff -q "$gold_csv" "$local_csv" >/dev/null; then
        checked=$((checked + 1))
    else
        echo "[validate] DIFFERS: $rel" >&2
        mismatches=$((mismatches + 1))
    fi
done < <(find results/verified -name 'coherence_hier_p*.csv' -print0)

echo "[validate] checked=$checked mismatches=$mismatches"
exit "$mismatches"
