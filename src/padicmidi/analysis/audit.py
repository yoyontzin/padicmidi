#!/usr/bin/env python3
"""Aggregate per-parent SC/AI audits from build_hierarchical_maps.py.

The audit has two parallel diagnostic families:

* *_pi columns recompute the actual Coh_pi numerator.
* *_trunc columns recompute the Coh_grid numerator.

This distinction matters because the current pipeline assigns level-(n+1)
residues globally to child prototypes, so pi(q_{n+1}(.)) can differ from
q_n(trunc(.)).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def parse_context(path: Path) -> tuple[str, str, int]:
    # Expected: outputs/paper_profinite_hier/<piece>/<axis>/p<p>/audit_p<p>.csv
    p_dir = path.parent
    axis_dir = p_dir.parent
    piece_dir = axis_dir.parent
    p = int(p_dir.name.removeprefix("p"))
    return piece_dir.name, axis_dir.name, p


def load_reported(path: Path) -> dict[int, dict[str, float]]:
    p = int(path.parent.name.removeprefix("p"))
    coh_path = path.parent / f"coherence_hier_p{p}.csv"
    out: dict[int, dict[str, float]] = {}
    if not coh_path.exists():
        return out
    for row in read_csv(coh_path):
        n = int(row["n"])
        out[n] = {
            "coh_pi": float(row["Coh_pi"]),
            "coh_grid": float(row["Coh_grid"]),
            "valid_b": float(row["n_samples_nplus1"]),
        }
    return out


def aggregate_one(path: Path) -> list[dict]:
    piece, axis, p = parse_context(path)
    reported = load_reported(path)
    by_n: dict[int, list[dict[str, str]]] = {}
    for row in read_csv(path):
        by_n.setdefault(int(row["n"]), []).append(row)

    rows: list[dict] = []
    for n, items in sorted(by_n.items()):
        counted = [r for r in items if r["coherent_count_pi"] != ""]
        included = [r for r in counted if r["excluded_sparsity"] == "0"]
        excluded = [r for r in items if r["excluded_sparsity"] == "1"]
        denom_dense = p ** (n + 1)
        valid_b = sum(int(r["n_valid_siblings"]) for r in counted)
        sum_pi = sum(int(r["coherent_count_pi"]) for r in counted)
        sum_trunc = sum(int(r["coherent_count_trunc"]) for r in counted)
        coh_pi_recomputed = sum_pi / denom_dense if denom_dense else 0.0
        coh_grid_recomputed = sum_trunc / denom_dense if denom_dense else 0.0
        coh_pi_valid = sum_pi / valid_b if valid_b else 0.0
        coh_grid_valid = sum_trunc / valid_b if valid_b else 0.0
        rep = reported.get(n, {})
        coh_pi_reported = rep.get("coh_pi", float("nan"))
        coh_grid_reported = rep.get("coh_grid", float("nan"))
        if abs(coh_pi_recomputed - coh_pi_reported) > 1e-6:
            raise RuntimeError(
                f"Coh_pi mismatch {path} n={n}: "
                f"recomputed={coh_pi_recomputed} reported={coh_pi_reported}"
            )
        if abs(coh_grid_recomputed - coh_grid_reported) > 1e-6:
            raise RuntimeError(
                f"Coh_grid mismatch {path} n={n}: "
                f"recomputed={coh_grid_recomputed} reported={coh_grid_reported}"
            )
        n_parents = len(included)
        n_sc_pi = sum(int(r["V_SC_pi"]) == p for r in included)
        n_ai_pi = sum(int(r["AI_pi"]) == 1 for r in included)
        n_both_pi = sum(int(r["V_SC_pi"]) == p and int(r["AI_pi"]) == 1 for r in included)
        n_sc_trunc = sum(int(r["V_SC_trunc"]) == p for r in included)
        n_ai_trunc = sum(int(r["AI_trunc"]) == 1 for r in included)
        n_both_trunc = sum(int(r["V_SC_trunc"]) == p and int(r["AI_trunc"]) == 1 for r in included)
        rows.append({
            "piece": piece,
            "axis": axis,
            "p": p,
            "n": n,
            "n_parents_total": len(items),
            "n_parents_included": n_parents,
            "n_parents_excluded_sparsity": len(excluded),
            "n_SC_pi_holds": n_sc_pi,
            "n_AI_pi_holds": n_ai_pi,
            "n_both_pi_hold": n_both_pi,
            "frac_SC_pi": n_sc_pi / n_parents if n_parents else 0.0,
            "frac_AI_pi": n_ai_pi / n_parents if n_parents else 0.0,
            "frac_both_pi": n_both_pi / n_parents if n_parents else 0.0,
            "n_SC_trunc_holds": n_sc_trunc,
            "n_AI_trunc_holds": n_ai_trunc,
            "n_both_trunc_hold": n_both_trunc,
            "frac_SC_trunc": n_sc_trunc / n_parents if n_parents else 0.0,
            "frac_AI_trunc": n_ai_trunc / n_parents if n_parents else 0.0,
            "frac_both_trunc": n_both_trunc / n_parents if n_parents else 0.0,
            "coverage": valid_b / denom_dense if denom_dense else 0.0,
            "coh_pi_recomputed": coh_pi_recomputed,
            "coh_pi_reported": coh_pi_reported,
            "coh_pi_valid": coh_pi_valid,
            "coh_grid_recomputed": coh_grid_recomputed,
            "coh_grid_reported": coh_grid_reported,
            "coh_grid_valid": coh_grid_valid,
        })
    return rows


def group_for(piece: str) -> str:
    if piece.startswith(("bwv1049", "bwv1050", "bwv1079")) or piece == "goldberg_aria":
        return "poly"
    return "mono"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="outputs/paper_profinite_hier")
    ap.add_argument("--out", default="outputs/audit_summary")
    args = ap.parse_args()
    root = Path(args.root)
    out_dir = Path(args.out)
    audit_paths = sorted(root.glob("*/**/p*/audit_p*.csv"))
    if not audit_paths:
        raise SystemExit(f"No audit_p*.csv files found under {root}")

    table: list[dict] = []
    for path in audit_paths:
        table.extend(aggregate_one(path))

    fields = list(table[0].keys())
    write_csv(out_dir / "audit_table.csv", table, fields)

    by_key: dict[tuple[str, str, int], list[dict]] = {}
    for row in table:
        by_key.setdefault((row["piece"], row["axis"], int(row["p"])), []).append(row)

    piece_rows = []
    for (piece, axis, p), rows in sorted(by_key.items()):
        piece_rows.append({
            "piece": piece,
            "texture_group": group_for(piece),
            "axis": axis,
            "p": p,
            "n_levels": len(rows),
            "mean_frac_SC_pi": mean(float(r["frac_SC_pi"]) for r in rows),
            "mean_frac_AI_pi": mean(float(r["frac_AI_pi"]) for r in rows),
            "mean_frac_both_pi": mean(float(r["frac_both_pi"]) for r in rows),
            "mean_frac_SC_trunc": mean(float(r["frac_SC_trunc"]) for r in rows),
            "mean_frac_AI_trunc": mean(float(r["frac_AI_trunc"]) for r in rows),
            "mean_frac_both_trunc": mean(float(r["frac_both_trunc"]) for r in rows),
            "mean_coverage": mean(float(r["coverage"]) for r in rows),
            "mean_coh_pi": mean(float(r["coh_pi_reported"]) for r in rows),
            "mean_coh_pi_valid": mean(float(r["coh_pi_valid"]) for r in rows),
        })
    write_csv(out_dir / "audit_by_piece.csv", piece_rows, list(piece_rows[0].keys()))

    with (out_dir / "SUMMARY.md").open("w") as f:
        f.write("# Audit Summary\n\n")
        f.write(f"Audited files: {len(audit_paths)}\n\n")
        f.write("`coh_pi_recomputed == coh_pi_reported` and `coh_grid_recomputed == coh_grid_reported` for all rows.\n\n")
        for group in ("mono", "poly"):
            group_rows = [r for r in piece_rows if r["texture_group"] == group and int(r["p"]) == 2]
            if not group_rows:
                continue
            f.write(f"## {group} p=2\n\n")
            f.write(f"- mean coverage: {mean(float(r['mean_coverage']) for r in group_rows):.4f}\n")
            f.write(f"- mean frac_SC_pi: {mean(float(r['mean_frac_SC_pi']) for r in group_rows):.4f}\n")
            f.write(f"- mean frac_AI_pi: {mean(float(r['mean_frac_AI_pi']) for r in group_rows):.4f}\n")
            f.write(f"- mean Coh_pi_valid: {mean(float(r['mean_coh_pi_valid']) for r in group_rows):.4f}\n\n")


if __name__ == "__main__":
    main()
