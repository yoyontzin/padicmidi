#!/usr/bin/env bash
# scripts/snapshot_version.sh — produce VERSION.md and CHECKSUMS.txt for v1.0.0.
# Should be run AFTER all source code, tests, data and verified results are
# settled. Generates SHA-256 hashes for everything that must be byte-stable.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VERSION="$(grep -E '^version =' pyproject.toml | head -1 | awk -F'"' '{print $2}')"
DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
COMMIT="unknown"
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    COMMIT="$(git rev-parse HEAD)"
fi

cat > VERSION.md <<EOF
# Frozen version

| Field    | Value                                  |
|----------|----------------------------------------|
| Version  | v${VERSION}                            |
| Date     | ${DATE}                                |
| Commit   | ${COMMIT}                              |
| Author   | J. Rogelio Pérez-Buendía               |
| Licence  | MIT (code) / CC-BY 4.0 (docs, results) |

## Files included in this snapshot

See \`results/verified/CHECKSUMS.txt\` and \`indautor/manifiesto-archivos.md\`.
EOF

# Hash the canonical files (data/midi, src/, results/verified, web-demo).
{
    echo "# SHA-256 manifest for PAdicMIDI v${VERSION} (${DATE})"
    echo
    find data/midi src results/verified web-demo \( -type f \) ! -name '.DS_Store' -print0 \
        | LC_ALL=C sort -z \
        | xargs -0 shasum -a 256
} > results/verified/CHECKSUMS.txt

echo "[snapshot] wrote VERSION.md and results/verified/CHECKSUMS.txt"
echo "[snapshot] $(wc -l < results/verified/CHECKSUMS.txt) lines hashed."
