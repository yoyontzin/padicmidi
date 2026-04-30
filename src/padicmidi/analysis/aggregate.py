#!/usr/bin/env python3
"""
build_control_primes_summary_nextpp.py — Ingest Phase I Next++ CSVs from
outputs/phaseI_nextpp/raw/<piece>/<condition>/ e.g. seconds_cap300, beats_bin12_cap300.
Filename: <prefix>_<A|B|C>_tower_real_bach_k<k>_p<2|3|5|7>(_beats)?.csv
Piece and condition taken from directory path; axis/bin/cap parsed from condition name.
Output: outputs/phaseI_nextpp/summary/SUMMARY_TABLE_p2357_nextpp.csv, CONTROL_PRIMES_REPORT_nextpp.txt
"""
import csv
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
RAW_BASE = ROOT / "outputs" / "phaseI_nextpp" / "raw"
SUMMARY_DIR = ROOT / "outputs" / "phaseI_nextpp" / "summary"
PRIMES = (2, 3, 5, 7)

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
    return out


def parse_condition(cond_name: str) -> tuple[str, str, str]:
    """Return (axis, bin_beats_str, cap_str)."""
    axis = "seconds" if cond_name.startswith("seconds") else "beats"
    cap_str = "500" if "cap500" in cond_name else "300"
    bin_str = "16" if "bin16" in cond_name else ("12" if "bin12" in cond_name else "")
    return axis, bin_str, cap_str


def collect_quadruplets():
    """Yield (piece, condition, axis, bin_beats, cap, config, k, paths). piece/condition from dir path."""
    by_key = {}
    if not RAW_BASE.exists():
        return
    for piece_dir in sorted(RAW_BASE.iterdir()):
        if not piece_dir.is_dir():
            continue
        piece = piece_dir.name
        for cond_dir in sorted(piece_dir.iterdir()):
            if not cond_dir.is_dir():
                continue
            cond_name = cond_dir.name
            axis, bin_str, cap_str = parse_condition(cond_name)
            for path in cond_dir.glob("*_tower_real_bach_k*_p*.csv"):
                name = path.name
                m = RE_FNAME.match(name)
                if not m:
                    continue
                _, config, k_str, p_str, suffix = m.groups()
                p_val = int(p_str)
                k = int(k_str)
                key = (piece, cond_name, axis, bin_str, cap_str, config, k)
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
    for piece, condition, axis, bin_beats, cap, config, k, paths in collect_quadruplets():
        data = {p: load_csv(paths[p]) if paths.get(p) else {} for p in PRIMES}
        common_n = set(data[2].keys()) & set(data[3].keys())
        if paths.get(5):
            common_n &= set(data[5].keys())
        if paths.get(7):
            common_n &= set(data[7].keys())
        common_n = sorted(common_n)
        for n in common_n:
            r = {p: data[p].get(n) for p in PRIMES}
            if not r[2] or not r[3]:
                continue
            row = {
                "piece": piece,
                "condition": condition,
                "axis": axis,
                "bin_beats": bin_beats,
                "cap": cap,
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

    fieldnames = ["piece", "condition", "axis", "bin_beats", "cap", "config", "k", "n",
                  "beta0_p2", "beta0_p3", "beta0_p5", "beta0_p7",
                  "giant_p2", "giant_p3", "giant_p5", "giant_p7",
                  "Delta23", "Delta25", "Delta27", "DeltaG23", "DeltaG25", "DeltaG27"]
    out_csv = SUMMARY_DIR / "SUMMARY_TABLE_p2357_nextpp.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("Wrote", out_csv, "rows:", len(rows))

    report_lines = [
        "CONTROL PRIMES SUMMARY (Phase I Next++)",
        "========================================",
        "Conditions: seconds_cap300/500, beats_bin12/16_cap300/500.",
        "",
    ]
    for (piece, condition) in sorted(set((r["piece"], r["condition"]) for r in rows)):
        sub = [r for r in rows if r["piece"] == piece and r["condition"] == condition]
        if not sub:
            continue
        report_lines.append(f"Piece: {piece}  Condition: {condition}")
        report_lines.append(f"  Rows: {len(sub)}. Delta23 nonzero: {sum(1 for r in sub if r.get('Delta23') != 0)}.")
        report_lines.append("")
    report_path = SUMMARY_DIR / "CONTROL_PRIMES_REPORT_nextpp.txt"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print("Wrote", report_path)


if __name__ == "__main__":
    main()
