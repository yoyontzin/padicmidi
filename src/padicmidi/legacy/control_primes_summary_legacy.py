#!/usr/bin/env python3
"""
build_control_primes_summary.py — Ingest Phase I CSVs for p=2,3,5,7; output
SUMMARY_TABLE_p2357.csv and CONTROL_PRIMES_REPORT.txt.
Contrasts: Δ23 = beta0_p2 - beta0_p3, Δ25, Δ27; same for giant. Negative-control language.
"""
import csv
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
OUT_SECONDS = ROOT / "outputs" / "seconds"
OUT_BEATS = ROOT / "outputs" / "beats"
SUMMARY_DIR = ROOT / "outputs" / "summary"
PRIMES = (2, 3, 5, 7)

# <piece>_<A|B|C>_tower_real_bach_k<k>_p<2|3|5|7>[._beats].csv
RE_FNAME = re.compile(r"^(.+)_(A|B|C)_tower_real_bach_k(\d+)_p([2357])(_beats)?\.csv$")


def load_csv(path: Path) -> dict[int, dict]:
    out = {}
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            n = int(row["n"])
            out[n] = {
                "beta0": int(row["beta0"]),
                "V": int(row["V"]),
                "avg_degree": float(row["avg_degree"]),
                "giant_component_frac": float(row["giant_component_frac"]),
            }
            if "lambda2" in row:
                out[n]["lambda2"] = float(row["lambda2"])
            if "clustering" in row:
                out[n]["clustering"] = float(row["clustering"])
    return out


def collect_quadruplets():
    """Yield (piece, axis, config, k, paths) where paths[p] = path to _p{p}.csv or None."""
    by_key = {}  # (piece, axis, config, k) -> {2: path, 3: path, 5: path, 7: path}
    for axis, base in [("seconds", OUT_SECONDS), ("beats", OUT_BEATS)]:
        if not base.exists():
            continue
        for path in base.glob("*_tower_real_bach_k*_p*.csv"):
            name = path.name
            m = RE_FNAME.match(name)
            if not m:
                continue
            piece, config, k_str, p_str, suffix = m.groups()
            p_val = int(p_str)
            k = int(k_str)
            key = (piece, axis, config, k)
            if key not in by_key:
                by_key[key] = {q: None for q in PRIMES}
            by_key[key][p_val] = path
    for key in sorted(by_key.keys()):
        paths = by_key[key]
        if paths.get(2) and paths.get(3):
            yield (*key, paths)


def main():
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for piece, axis, config, k, paths in collect_quadruplets():
        data = {p: load_csv(paths[p]) if paths.get(p) else {} for p in PRIMES}
        common_n = set(data[2].keys()) & set(data[3].keys())
        if paths.get(5):
            common_n &= set(data[5].keys())
        if paths.get(7):
            common_n &= set(data[7].keys())
        common_n = sorted(common_n)
        for n in common_n:
            r = {}
            for p in PRIMES:
                r[p] = data[p].get(n)
            if not r[2] or not r[3]:
                continue
            row = {
                "piece": piece,
                "axis": axis,
                "config": config,
                "k": k,
                "n": n,
                "beta0_p2": r[2]["beta0"],
                "beta0_p3": r[3]["beta0"],
                "beta0_p5": r[5]["beta0"] if r.get(5) else "",
                "beta0_p7": r[7]["beta0"] if r.get(7) else "",
                "giant_p2": round(r[2]["giant_component_frac"], 6),
                "giant_p3": round(r[3]["giant_component_frac"], 6),
                "giant_p5": round(r[5]["giant_component_frac"], 6) if r.get(5) else "",
                "giant_p7": round(r[7]["giant_component_frac"], 6) if r.get(7) else "",
            }
            row["Delta23"] = r[2]["beta0"] - r[3]["beta0"]
            row["Delta25"] = (r[2]["beta0"] - r[5]["beta0"]) if r.get(5) else ""
            row["Delta27"] = (r[2]["beta0"] - r[7]["beta0"]) if r.get(7) else ""
            row["DeltaG23"] = round(r[2]["giant_component_frac"] - r[3]["giant_component_frac"], 6)
            row["DeltaG25"] = round(r[2]["giant_component_frac"] - r[5]["giant_component_frac"], 6) if r.get(5) else ""
            row["DeltaG27"] = round(r[2]["giant_component_frac"] - r[7]["giant_component_frac"], 6) if r.get(7) else ""
            rows.append(row)

    out_csv = SUMMARY_DIR / "SUMMARY_TABLE_p2357.csv"
    fieldnames = ["piece", "axis", "config", "k", "n", "beta0_p2", "beta0_p3", "beta0_p5", "beta0_p7",
                  "giant_p2", "giant_p3", "giant_p5", "giant_p7", "Delta23", "Delta25", "Delta27",
                  "DeltaG23", "DeltaG25", "DeltaG27"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("Wrote", out_csv, "rows:", len(rows))

    # Text report: per-piece highlights, negative-control language
    report_lines = [
        "CONTROL PRIMES SUMMARY (p=2,3,5,7)",
        "====================================",
        "p=2 and p=3 are the main primes (dyadic/ternary). p=5 and p=7 are pre-registered negative controls.",
        "Expected: separation (e.g. nonzero Delta23) for musically relevant pieces; control primes (p=5,7) may show flatter or different profiles.",
        "",
    ]
    pieces_done = sorted(set(r["piece"] for r in rows))
    for piece in pieces_done:
        sub = [r for r in rows if r["piece"] == piece]
        if not sub:
            continue
        report_lines.append(f"Piece: {piece}")
        report_lines.append(f"  Rows: {len(sub)} (axis/config/k/n combinations).")
        deltas23 = [r["Delta23"] for r in sub if r.get("Delta23") is not None]
        if deltas23:
            report_lines.append(f"  Delta23 (beta0_p2 - beta0_p3): min={min(deltas23)}, max={max(deltas23)}; nonzero count={sum(1 for d in deltas23 if d != 0)}.")
        if any(r.get("Delta25") != "" for r in sub):
            report_lines.append("  Delta25, Delta27 (vs control primes): see SUMMARY_TABLE_p2357.csv.")
        report_lines.append("")
    report_path = SUMMARY_DIR / "CONTROL_PRIMES_REPORT.txt"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print("Wrote", report_path)


if __name__ == "__main__":
    main()
