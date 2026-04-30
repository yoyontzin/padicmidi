#!/usr/bin/env python3
"""
build_hierarchical_figures.py — Figures from hierarchical coherence outputs.

Reads coherence_hier_p2.csv, coherence_hier_p3.csv from <root>/<piece>/<axis>/p2/ and p3/.
Writes to --out (default paper/figs/): cohpi_vs_n_<piece>_<axis>.pdf,
delta_cohpi_vs_n_<piece>_<axis>.pdf, optional stab/coh_grid; pi_bipartite_<piece>_<axis>_p{p}_n{n}.pdf.
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "Paper-ZpMusic-20250206" / "paper" / "figs"


def load_coherence(path: Path) -> dict[int, dict]:
    """n -> {Coh_pi, Coh_grid, n_samples_n, n_samples_nplus1}."""
    out = {}
    if not path.exists():
        return out
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            n = int(row["n"])
            out[n] = {
                "Coh_pi": float(row.get("Coh_pi", 0)),
                "Coh_grid": float(row.get("Coh_grid", 0)),
                "n_samples_n": int(row.get("n_samples_n", 0)),
                "n_samples_nplus1": int(row.get("n_samples_nplus1", 0)),
            }
    return out


def discover_piece_axis(root: Path) -> list[tuple[str, str]]:
    """List (piece, axis) such that root/piece/axis/p2 and p3 have coherence_hier_p*.csv."""
    out = []
    for piece_dir in sorted(root.iterdir()):
        if not piece_dir.is_dir():
            continue
        for axis_dir in sorted(piece_dir.iterdir()):
            if not axis_dir.is_dir():
                continue
            p2 = axis_dir / "p2" / "coherence_hier_p2.csv"
            p3 = axis_dir / "p3" / "coherence_hier_p3.csv"
            if p2.exists() and p3.exists():
                out.append((piece_dir.name, axis_dir.name))
    return out


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, default=None, help="Root of paper_profinite_hier (default: ROOT/outputs/paper_profinite_hier)")
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--piece", type=str, default=None, help="If set, only this piece (with --axis)")
    ap.add_argument("--axis", type=str, default=None)
    ap.add_argument("--pi-n", type=int, default=2, help="Level n for pi_bipartite (n -> n+1)")
    args = ap.parse_args()

    root = Path(args.root) if args.root else ROOT / "outputs" / "paper_profinite_hier"
    out_dir = Path(args.out) if args.out else FIG_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.piece and args.axis:
        pairs = [(args.piece, args.axis)]
    else:
        pairs = discover_piece_axis(root)
    if not pairs:
        print("No (piece, axis) with both p2 and p3 coherence CSVs under", root)
        return

    for piece, axis in pairs:
        p2_dir = root / piece / axis / "p2"
        p3_dir = root / piece / axis / "p3"
        c2 = load_coherence(p2_dir / "coherence_hier_p2.csv")
        c3 = load_coherence(p3_dir / "coherence_hier_p3.csv")
        ns = sorted(set(c2.keys()) & set(c3.keys()))
        if not ns:
            continue
        y2_pi = np.array([c2[n]["Coh_pi"] for n in ns])
        y3_pi = np.array([c3[n]["Coh_pi"] for n in ns])
        y2_grid = np.array([c2[n]["Coh_grid"] for n in ns])
        y3_grid = np.array([c3[n]["Coh_grid"] for n in ns])
        delta_pi = y2_pi - y3_pi
        delta_grid = y2_grid - y3_grid
        x = np.array(ns)

        # cohpi_vs_n
        fig, ax = plt.subplots(figsize=(5, 3.2))
        ax.plot(x, y2_pi, "o-", label="$p=2$ Coh$_\\pi$", color="C0")
        ax.plot(x, y3_pi, "s--", label="$p=3$ Coh$_\\pi$", color="C1")
        ax.plot(x, y2_grid, "^-", alpha=0.7, label="$p=2$ Coh_grid", color="C0", linestyle=":")
        ax.plot(x, y3_grid, "v--", alpha=0.7, label="$p=3$ Coh_grid", color="C1", linestyle=":")
        ax.set_xlabel("level $n$")
        ax.set_ylabel("coherence")
        ax.set_title(f"Hierarchical coherence — {piece}, {axis}")
        ax.legend(fontsize=7)
        ax.set_xticks(x)
        plt.tight_layout()
        out1 = out_dir / f"cohpi_vs_n_{piece}_{axis}.pdf"
        plt.savefig(out1, bbox_inches="tight")
        plt.close()
        print(f"Wrote {out1}")

        # delta_cohpi_vs_n
        fig, ax = plt.subplots(figsize=(5, 3.2))
        ax.bar(x - 0.15, delta_pi, width=0.3, label="$\\Delta$Coh$_\\pi$", color="C0", alpha=0.8)
        ax.bar(x + 0.15, delta_grid, width=0.3, label="$\\Delta$Coh_grid", color="C1", alpha=0.8)
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_xlabel("level $n$")
        ax.set_ylabel("$\\Delta$")
        ax.set_title(f"$p=2$ vs $p=3$ — {piece}, {axis}")
        ax.legend()
        ax.set_xticks(x)
        plt.tight_layout()
        out2 = out_dir / f"delta_cohpi_vs_n_{piece}_{axis}.pdf"
        plt.savefig(out2, bbox_inches="tight")
        plt.close()
        print(f"Wrote {out2}")

        # Optional: p5, p7 for control primes -> cohpi_vs_n_*_p2p3p5p7.pdf and delta_cohpi_*_p2p3p5p7.pdf
        p5_dir = root / piece / axis / "p5"
        p7_dir = root / piece / axis / "p7"
        if (p5_dir / "coherence_hier_p5.csv").exists() and (p7_dir / "coherence_hier_p7.csv").exists():
            c5 = load_coherence(p5_dir / "coherence_hier_p5.csv")
            c7 = load_coherence(p7_dir / "coherence_hier_p7.csv")
            ns_all = sorted(set(c2.keys()) & set(c3.keys()) & set(c5.keys()) & set(c7.keys()))
            if ns_all:
                x4 = np.array(ns_all)
                y5_pi = np.array([c5[n]["Coh_pi"] for n in ns_all])
                y7_pi = np.array([c7[n]["Coh_pi"] for n in ns_all])
                fig4, ax4 = plt.subplots(figsize=(5.5, 3.2))
                ax4.plot(x4, [c2[n]["Coh_pi"] for n in ns_all], "o-", label="$p=2$ Coh$_\\pi$", color="C0")
                ax4.plot(x4, [c3[n]["Coh_pi"] for n in ns_all], "s--", label="$p=3$ Coh$_\\pi$", color="C1")
                ax4.plot(x4, y5_pi, "^-.", label="$p=5$ Coh$_\\pi$", color="C2")
                ax4.plot(x4, y7_pi, "v-.", label="$p=7$ Coh$_\\pi$", color="C3")
                ax4.set_xlabel("level $n$")
                ax4.set_ylabel("Coh$_\\pi$")
                ax4.set_title(f"Hierarchical coherence (incl. control primes) — {piece}, {axis}")
                ax4.legend(fontsize=7)
                ax4.set_xticks(x4)
                plt.tight_layout()
                out4 = out_dir / f"cohpi_vs_n_{piece}_{axis}_p2p3p5p7.pdf"
                plt.savefig(out4, bbox_inches="tight")
                plt.close()
                print(f"Wrote {out4}")
                fig5, ax5 = plt.subplots(figsize=(5.5, 3.2))
                y2_all = np.array([c2[n]["Coh_pi"] for n in ns_all])
                ax5.bar(x4 - 0.3, y2_all - np.array([c3[n]["Coh_pi"] for n in ns_all]), width=0.2, label="$\\Delta_{23}$", color="C0", alpha=0.8)
                ax5.bar(x4 - 0.1, y2_all - y5_pi, width=0.2, label="$\\Delta_{25}$", color="C2", alpha=0.8)
                ax5.bar(x4 + 0.1, y2_all - y7_pi, width=0.2, label="$\\Delta_{27}$", color="C3", alpha=0.8)
                ax5.axhline(0, color="k", linewidth=0.5)
                ax5.set_xlabel("level $n$")
                ax5.set_ylabel("$\\Delta$")
                ax5.set_title(f"Contrasts vs $p=2$ (control primes) — {piece}, {axis}")
                ax5.legend(fontsize=7)
                ax5.set_xticks(x4)
                plt.tight_layout()
                out5 = out_dir / f"delta_cohpi_vs_n_{piece}_{axis}_p2p3p5p7.pdf"
                plt.savefig(out5, bbox_inches="tight")
                plt.close()
                print(f"Wrote {out5}")

        # pi_bipartite for p=2 and p=3, level args.pi_n
        n_rep = args.pi_n
        for p, pdir in [(2, p2_dir), (3, p3_dir)]:
            pi_path = pdir / f"pi_p{p}_n{n_rep+1}_to_n{n_rep}.csv"
            if not pi_path.exists():
                continue
            with open(pi_path, newline="") as f:
                r = list(csv.DictReader(f))
            if not r:
                continue
            child_id = [int(row["child_id"]) for row in r]
            parent_id = [int(row["parent_id"]) for row in r]
            parents = sorted(set(parent_id))
            children = list(range(len(child_id)))
            fig, ax = plt.subplots(figsize=(4, 3))
            for i, (c, pa) in enumerate(zip(child_id, parent_id)):
                ax.plot([0, 1], [c, pa], "k-", alpha=0.5, linewidth=0.8)
            ax.scatter([0] * len(children), children, s=15, c="C0", label="child")
            ax.scatter([1] * len(parents), parents, s=25, c="C1", label="parent")
            ax.set_xticks([0, 1])
            ax.set_xticklabels(["$S_{n+1}$", "$S_n$"])
            ax.set_ylabel("index")
            ax.set_title(f"$\\pi_{{n+1,n}}$ $p={p}$, $n={n_rep}$ — {piece}, {axis}")
            ax.legend(loc="upper right", fontsize=7)
            plt.tight_layout()
            out3 = out_dir / f"pi_bipartite_{piece}_{axis}_p{p}_n{n_rep}.pdf"
            plt.savefig(out3, bbox_inches="tight")
            plt.close()
            print(f"Wrote {out3}")


if __name__ == "__main__":
    main()
