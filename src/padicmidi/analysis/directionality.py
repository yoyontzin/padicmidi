#!/usr/bin/env python3
"""Directionality report for hierarchical coherence.

This script reports both the raw dense-normalized Coh_pi and the coverage-corrected
conditional score Coh_pi_valid = match / valid_b from audit_table.csv. The latter is
the appropriate statistic when coverage differs by prime (e.g. p=2 with step=2).
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from statistics import mean


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def group_for(piece: str) -> str:
    if piece.startswith(("bwv1049", "bwv1050", "bwv1079")) or piece == "goldberg_aria":
        return "poly"
    return "mono"


def binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    if n == 0:
        return 1.0
    probs = [math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(n + 1)]
    pk = probs[k]
    return min(1.0, sum(x for x in probs if x <= pk + 1e-18))


def clopper_pearson_zero_success(n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    # For k=0, exact upper endpoint is 1 - (alpha/2)^(1/n).
    return (0.0, 1.0 - (alpha / 2.0) ** (1.0 / n))


def classify(values: list[float], floor: float, eps: float) -> tuple[int, int, int]:
    below = sum(v < floor - eps for v in values)
    above = sum(v > floor + eps for v in values)
    at = len(values) - below - above
    return below, at, above


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-table", default="outputs/audit_summary/audit_table.csv")
    ap.add_argument("--out", default="outputs/directionality/directionality_report.txt")
    ap.add_argument("--eps", type=float, default=1e-3)
    args = ap.parse_args()

    rows = [r for r in read_csv(Path(args.audit_table)) if int(r["p"]) == 2]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    by_piece: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_piece.setdefault(row["piece"], []).append(row)

    lines: list[str] = []
    lines.append("# Directionality Report\n")
    lines.append("Important: raw Coh_pi for p=2 is capped by coverage when step=2. ")
    lines.append("The coverage-corrected score Coh_pi_valid = match/valid_b is therefore reported alongside raw Coh_pi.\n\n")

    for group in ("mono", "poly", "all"):
        if group == "all":
            group_rows = rows
        else:
            group_rows = [r for r in rows if group_for(r["piece"]) == group]
        raw_vals = [float(r["coh_pi_reported"]) for r in group_rows]
        valid_vals = [float(r["coh_pi_valid"]) for r in group_rows]
        raw_below, raw_at, raw_above = classify(raw_vals, 0.5, args.eps)
        valid_below, valid_at, valid_above = classify(valid_vals, 1.0, args.eps)
        n_viol = valid_below + valid_above
        one_sided = (0.5 ** n_viol) if valid_above == 0 and n_viol else 1.0
        two_sided = binom_two_sided(valid_above, n_viol) if n_viol else 1.0
        ci = clopper_pearson_zero_success(n_viol) if valid_above == 0 else (float("nan"), float("nan"))
        lines.append(f"## {group}\n\n")
        lines.append(f"- rows: {len(group_rows)}\n")
        lines.append(f"- raw Coh_pi vs 0.5: below={raw_below}, at={raw_at}, above={raw_above}\n")
        lines.append(f"- Coh_pi_valid vs 1.0: below={valid_below}, at={valid_at}, above={valid_above}\n")
        lines.append(f"- exact binomial one-sided p-value (above fewer than half among valid-score violations): {one_sided:.6g}\n")
        lines.append(f"- exact binomial two-sided p-value: {two_sided:.6g}\n")
        if n_viol:
            lines.append(f"- 95% Clopper-Pearson CI for P(above | violation), if above=0: [{ci[0]:.4f}, {ci[1]:.4f}]\n")
        lines.append("\n")

    lines.append("## By piece\n\n")
    lines.append("piece,group,N,raw_below,raw_at,raw_above,valid_below,valid_at,valid_above,mean_raw,mean_valid\n")
    for piece, prs in sorted(by_piece.items()):
        raw_vals = [float(r["coh_pi_reported"]) for r in prs]
        valid_vals = [float(r["coh_pi_valid"]) for r in prs]
        rb, ra, rup = classify(raw_vals, 0.5, args.eps)
        vb, va, vup = classify(valid_vals, 1.0, args.eps)
        lines.append(
            f"{piece},{group_for(piece)},{len(prs)},{rb},{ra},{rup},{vb},{va},{vup},"
            f"{mean(raw_vals):.6f},{mean(valid_vals):.6f}\n"
        )

    out.write_text("".join(lines))


if __name__ == "__main__":
    main()
