#!/usr/bin/env python3
"""
build_spectral_precision_figs.py — λ2(n) and d_spec(n) from Phase I tower CSVs (spectral persistence by precision).
Reads *_tower_real_bach_k{k}_p{2,3,5,7}.csv from outputs/seconds and outputs/beats; extracts lambda2 per n.
d_spec(n) = |lambda2(n+1) - lambda2(n)| (single-eigenvalue version).
Outputs: lambda2_vs_n_<piece>_<axis>_<config>_k{k}_p2p3p5p7.pdf, dspec_vs_n_<piece>_<axis>_<config>_k{k}_p2p3p5p7.pdf.
Writes outputs/summary/SPECTRAL_PRECISION_REPORT.txt (factual).
"""
import csv
import re
from pathlib import Path
import numpy as np

matplotlib = __import__("matplotlib")
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT_SECONDS = ROOT / "outputs" / "seconds"
OUT_BEATS = ROOT / "outputs" / "beats"
SUMMARY_DIR = ROOT / "outputs" / "summary"
FIG_DIR = ROOT / "Paper-ZpMusic-20250206" / "paper" / "figs"
PRIMES = (2, 3, 5, 7)
RE_FNAME = re.compile(r"^(.+)_(A|B|C)_tower_real_bach_k(\d+)_p([2357])(_beats)?\.csv$")


def load_tower_csv(path: Path) -> dict[int, dict]:
    """n -> {lambda2, clustering, ...}."""
    out = {}
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            n = int(row["n"])
            out[n] = {"lambda2": float(row.get("lambda2", 0))}
    return out


def collect_piece_axis_config_k(root_dirs) -> list[tuple[str, str, str, int, dict]]:
    """(piece, axis, config, k, {p: path})."""
    by_key = {}
    for axis, base in [("seconds", OUT_SECONDS), ("beats", OUT_BEATS)]:
        if not base.exists():
            continue
        for path in base.glob("*_tower_real_bach_k*_p*.csv"):
            m = RE_FNAME.match(path.name)
            if not m:
                continue
            piece, config, k_str, p_str, suffix = m.groups()
            p_val = int(p_str)
            k = int(k_str)
            key = (piece, axis, config, k)
            if key not in by_key:
                by_key[key] = {q: None for q in PRIMES}
            by_key[key][p_val] = path
    out = []
    for (piece, axis, config, k), paths in sorted(by_key.items()):
        if all(paths.get(p) for p in PRIMES):
            out.append((piece, axis, config, k, paths))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--piece", type=str, default=None, help="Filter piece (e.g. bwv1079_crab_cap300)")
    ap.add_argument("--axis", type=str, default="beats")
    ap.add_argument("--config", type=str, default="A")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()
    out_dir = Path(args.out) if args.out else FIG_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    runs = collect_piece_axis_config_k(None)
    if args.piece:
        runs = [r for r in runs if r[0] == args.piece]
    if args.axis:
        runs = [r for r in runs if r[1] == args.axis]
    if args.config:
        runs = [r for r in runs if r[2] == args.config]
    if args.k:
        runs = [r for r in runs if r[3] == args.k]
    if not runs:
        print("No runs with all p=2,3,5,7 CSVs found.")
        report_path = SUMMARY_DIR / "SPECTRAL_PRECISION_REPORT.txt"
        report_path.write_text("SPECTRAL_PRECISION_REPORT: No Phase I tower CSVs with lambda2 for p=2,3,5,7. Run Phase I with --control-primes 5 7 first.\n")
        return

    report_lines = ["SPECTRAL PRECISION (lambda2, d_spec)", "Factual: from Phase I tower CSVs (lambda2 when present).", ""]
    for piece, axis, config, k, paths in runs:
        data = {p: load_tower_csv(paths[p]) for p in PRIMES}
        common_n = sorted(set.intersection(*[set(data[p].keys()) for p in PRIMES]))
        if not common_n:
            continue
        ns = np.array(common_n)
        lambda2_by_p = {p: np.array([data[p][n]["lambda2"] for n in common_n]) for p in PRIMES}
        # lambda2 vs n
        fig, ax = plt.subplots(figsize=(5.5, 3.2))
        for i, p in enumerate(PRIMES):
            ax.plot(ns, lambda2_by_p[p], "o-"[i % 2], label=f"$p={p}$", color=f"C{i}")
        ax.set_xlabel("level $n$")
        ax.set_ylabel("$\\lambda_2$ (Fiedler)")
        ax.set_title(f"$\\lambda_2$ vs $n$ — {piece}, {axis}, config {config}, k={k}")
        ax.legend()
        ax.set_xticks(ns)
        plt.tight_layout()
        out1 = out_dir / f"lambda2_vs_n_{piece}_{axis}_{config}_k{k}_p2p3p5p7.pdf"
        plt.savefig(out1, bbox_inches="tight")
        plt.close()
        print("Wrote", out1)
        # d_spec(n) = |lambda2(n+1) - lambda2(n)| for each p
        fig2, ax2 = plt.subplots(figsize=(5.5, 3.2))
        for i, p in enumerate(PRIMES):
            lam = lambda2_by_p[p]
            d_spec = np.abs(np.diff(lam))
            ax2.plot(ns[:-1], d_spec, "o-"[i % 2], label=f"$p={p}$", color=f"C{i}")
        ax2.set_xlabel("level $n$ (transition $n \\to n+1$)")
        ax2.set_ylabel("$d_{\\mathrm{spec}}(n) = |\\lambda_2(n+1)-\\lambda_2(n)|$")
        ax2.set_title(f"Spectral step — {piece}, {axis}, config {config}, k={k}")
        ax2.legend()
        plt.tight_layout()
        out2 = out_dir / f"dspec_vs_n_{piece}_{axis}_{config}_k{k}_p2p3p5p7.pdf"
        plt.savefig(out2, bbox_inches="tight")
        plt.close()
        print("Wrote", out2)
        report_lines.append(f"{piece} {axis} config={config} k={k}: n_range={min(common_n)}..{max(common_n)}, lambda2 present for p=2,3,5,7.")

    with open(SUMMARY_DIR / "SPECTRAL_PRECISION_REPORT.txt", "w") as f:
        f.write("\n".join(report_lines))
    print("Wrote", SUMMARY_DIR / "SPECTRAL_PRECISION_REPORT.txt")


if __name__ == "__main__":
    main()
