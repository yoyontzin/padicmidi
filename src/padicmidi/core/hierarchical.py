#!/usr/bin/env python3
"""
padicmidi.core.hierarchical — p-adic tower with forced inverse system.

Hierarchical dictionaries ``S_n`` together with the explicit inverse map
``pi_{n+1,n}: S_{n+1} -> S_n`` that forces each child to inherit a parent
by construction. Computes the coherence invariants
``Coh_pi(p, n)`` and ``Coh_grid(p, n)`` and writes the per-parent audit
table that allows verification of hypotheses (SC) and (AI) of the
null-floor proposition.

Construction summary:
  * ``S_1`` is obtained via K-means on a sample of windows of length p.
  * For every ``n -> n+1`` the parent of an aggregated window
    ``W_{p,n+1}(b)`` is its truncation projected onto ``S_n``; per-parent
    K-means with ``Kchild`` clusters yields ``S_{n+1}``;
    ``pi(child_id) = parent_id`` by construction.

Outputs (one file per CSV):
  * ``params.json``, ``params.txt``
  * ``S_n_prototypes_p{p}_n{n}.csv``
  * ``pi_p{p}_n{n+1}_to_n{n}.csv``
  * ``f_p{p}_n{n}.csv``
  * ``coherence_hier_p{p}.csv``
  * ``audit_p{p}.csv``
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from collections import defaultdict

import numpy as np

from padicmidi.core.echo import (
    parse_midi_notes_seconds,
    parse_midi_notes_beats,
    chroma_series_duration,
    chroma_series_duration_beats,
    onset_density_series,
    onset_density_series_beats,
    series_with_rhythm,
)
from padicmidi.core.config import ALPHA, MAX_WINDOWS_PER_RESIDUE, default_nmax


def build_X_seconds(path: str, bin_size: float = 0.05) -> np.ndarray:
    events = parse_midi_notes_seconds(path)
    if not events:
        return np.zeros((0, 13), dtype=float)
    H = chroma_series_duration(events, bin_size=bin_size)
    a = onset_density_series(events, bin_size=bin_size)
    return series_with_rhythm(H, a, alpha=ALPHA)


def build_X_beats(path: str, bin_size_beats: float = 1.0 / 12.0) -> np.ndarray:
    events = parse_midi_notes_beats(path)
    if not events:
        return np.zeros((0, 13), dtype=float)
    H = chroma_series_duration_beats(events, bin_size_beats=bin_size_beats)
    a = onset_density_series_beats(events, bin_size_beats=bin_size_beats)
    return series_with_rhythm(H, a, alpha=ALPHA)


def get_windows(X: np.ndarray, N: int, step: int) -> list[tuple[int, np.ndarray]]:
    out = []
    for start in range(0, len(X) - N + 1, step):
        out.append((start, X[start : start + N, :].copy()))
    return out


def aggregate_median(windows: list[np.ndarray]) -> np.ndarray:
    """Componentwise median; W_{p,n}(a) = median over windows with i ≡ a (mod p^n)."""
    if not windows:
        return np.full((1, 1), np.nan)
    stack = np.stack(windows, axis=0)
    return np.median(stack, axis=0).astype(np.float64)


def dist_matrix(windows: np.ndarray, prototypes: np.ndarray) -> np.ndarray:
    """windows (W, N, 13), prototypes (P, N, 13) -> (W, P)."""
    diff = windows[:, None, :, :] - prototypes[None, :, :, :]
    return np.sqrt(np.mean(np.sum(diff ** 2, axis=3), axis=2))


def kmeans_numpy(samples: np.ndarray, K: int, rng: np.random.Generator, max_iter: int = 30) -> np.ndarray:
    """samples (N, D). Returns centers (K_eff, D) with K_eff = max(1, min(K, len(samples)))."""
    if len(samples) == 0:
        return np.zeros((K, samples.shape[1]) if samples.size else (K, 0))
    K_actual = max(1, min(K, len(samples)))
    idx = np.arange(len(samples))
    rng.shuffle(idx)
    centers = samples[idx[:K_actual]].copy()
    if K_actual < K:
        centers = np.vstack([centers, np.tile(centers[-1], (K - K_actual, 1))])
    for _ in range(max_iter):
        dists = np.linalg.norm(samples[:, None, :] - centers[None, :, :], axis=2)
        labels = np.argmin(dists, axis=1)
        new_centers = centers.copy()
        for j in range(K_actual):
            mask = labels == j
            if np.any(mask):
                new_centers[j] = samples[mask].mean(axis=0)
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return centers[:K_actual]


def build_W_n(X: np.ndarray, p: int, n_max: int, step: int) -> dict[int, dict[int, np.ndarray]]:
    """W_n[n][a] = aggregated window (p^n, 13) for residue a. Median over { P_{n,i} : i ≡ a (mod p^n) }."""
    W_n = {}
    for n in range(1, n_max + 1):
        N = p ** n
        windows_with_start = get_windows(X, N, step)
        if not windows_with_start:
            W_n[n] = {}
            continue
        by_residue = defaultdict(list)
        for start, w in windows_with_start:
            a = start % (p ** n)
            if len(by_residue[a]) < MAX_WINDOWS_PER_RESIDUE:
                by_residue[a].append(w)
        W_n[n] = {}
        for a, wlist in by_residue.items():
            W_n[n][a] = aggregate_median(wlist)
    return W_n


def run_hierarchical(
    X: np.ndarray,
    p: int,
    Nmax: int,
    step: int,
    K: int,
    Kchild: int,
    M: int,
    rng: np.random.Generator,
) -> tuple[dict, dict, dict, list[dict], list[dict]]:
    """
    Returns:
      prototypes_n: n -> (|S_n|, p^n, 13)
      f_n: n -> dict residue a -> prototype_id
      pi_maps: n -> list of length |S_{n+1}|, pi_maps[n][child_id] = parent_id
      coherence_rows: list of {n, Coh_pi, Coh_grid, n_samples_n, n_samples_nplus1}
      audit_rows: per-parent diagnostics for the quantities underlying Coh_pi
        (pi columns) and Coh_grid (trunc columns).
    """
    W_n = build_W_n(X, p, Nmax, step)
    prototypes_n = {}
    f_n = {}
    pi_maps = {}

    N1 = p
    win1 = get_windows(X, N1, step)
    if not win1:
        return prototypes_n, f_n, pi_maps, [], []

    indices = np.arange(len(win1))
    if len(indices) > M:
        indices = np.linspace(0, len(indices) - 1, M).astype(int)
    sample1 = np.array([win1[i][1].flatten() for i in indices])
    K1 = max(1, min(K, len(sample1)))
    centers1 = kmeans_numpy(sample1, K1, rng)
    prototypes_n[1] = centers1.reshape(-1, N1, 13)
    f_n[1] = {}
    if W_n.get(1):
        keys, wstack = zip(*[(a, w) for a, w in W_n[1].items() if not np.any(np.isnan(w))])
        if keys:
            wstack = np.stack(wstack)
            d = dist_matrix(wstack, prototypes_n[1])
            for i, a in enumerate(keys):
                f_n[1][a] = int(np.argmin(d[i]))

    for n in range(1, Nmax):
        pn = p ** n
        pn1 = p ** (n + 1)
        if n + 1 not in W_n or not W_n[n + 1]:
            continue
        b_list, w_list = zip(*[(b, w) for b, w in W_n[n + 1].items() if not np.any(np.isnan(w))])
        if not b_list:
            continue
        w_list = np.stack(w_list)
        trunc_list = w_list[:, :pn, :]
        d_parent = dist_matrix(trunc_list, prototypes_n[n])
        parent_of_b = {b: int(np.argmin(d_parent[i])) for i, b in enumerate(b_list)}

        by_parent = defaultdict(list)
        for b, w in W_n[n + 1].items():
            if b not in parent_of_b or np.any(np.isnan(w)):
                continue
            by_parent[parent_of_b[b]].append(w)

        n_parents = len(prototypes_n[n])
        all_children = []
        pi_list = []
        for j in range(n_parents):
            wlist = by_parent.get(j, [])
            K_eff = max(1, min(Kchild, len(wlist))) if wlist else 1
            if len(wlist) < 2:
                c = wlist[0].copy() if len(wlist) == 1 else np.repeat(
                    prototypes_n[n][j], (pn1 + pn - 1) // pn, axis=0
                )[:pn1, :].copy()
                for _ in range(K_eff):
                    all_children.append(c.copy())
                    pi_list.append(j)
                for _ in range(Kchild - K_eff):
                    all_children.append(all_children[-1].copy())
                    pi_list.append(j)
            else:
                flat = np.array([x.flatten() for x in wlist])
                centers_child = kmeans_numpy(flat, K_eff, rng)
                for k in range(len(centers_child)):
                    all_children.append(centers_child[k].reshape(pn1, 13))
                    pi_list.append(j)
                for _ in range(Kchild - len(centers_child)):
                    all_children.append(all_children[-1].copy())
                    pi_list.append(j)
        if not all_children:
            continue
        prototypes_n[n + 1] = np.stack(all_children, axis=0)
        pi_maps[n] = pi_list
        keys_n1, w_n1 = zip(*[(a, w) for a, w in W_n[n + 1].items() if not np.any(np.isnan(w))])
        if keys_n1:
            f_n[n + 1] = {}
            w_stack_n1 = np.stack(w_n1)
            d_n1 = dist_matrix(w_stack_n1, prototypes_n[n + 1])
            for i, a in enumerate(keys_n1):
                f_n[n + 1][a] = int(np.argmin(d_n1[i]))

    coherence_rows = []
    audit_rows = []
    for n in range(1, Nmax):
        if n not in pi_maps or n + 1 not in f_n or n not in f_n:
            continue
        pn = p ** n
        pn1 = p ** (n + 1)
        valid_b_list = [
            b for b in range(pn1)
            if b in W_n.get(n + 1, {}) and not np.any(np.isnan(W_n[n + 1][b]))
            and f_n[n + 1].get(b) is not None and (b % pn) in f_n[n]
        ]
        if not valid_b_list:
            coherence_rows.append({
                "n": n, "Coh_pi": 0.0, "Coh_grid": 0.0,
                "n_samples_n": len(W_n.get(n, {})), "n_samples_nplus1": 0,
            })
            continue
        w_stack = np.stack([W_n[n + 1][b] for b in valid_b_list])
        trunc_stack = w_stack[:, :pn, :]
        d_trunc = dist_matrix(trunc_stack, prototypes_n[n])
        q_n_trunc = np.argmin(d_trunc, axis=1)
        q_n1_arr = np.array([f_n[n + 1][b] for b in valid_b_list], dtype=int)
        parent_via_pi = np.array([pi_maps[n][j] for j in q_n1_arr])
        f_n_r_b = np.array([f_n[n][b % pn] for b in valid_b_list], dtype=int)
        match_pi = int((parent_via_pi == f_n_r_b).sum())
        match_grid = int((q_n_trunc == f_n_r_b).sum())
        coh_pi = match_pi / pn1 if pn1 > 0 else 0.0
        coh_grid = match_grid / pn1 if pn1 > 0 else 0.0
        coherence_rows.append({
            "n": n,
            "Coh_pi": round(coh_pi, 6),
            "Coh_grid": round(coh_grid, 6),
            "n_samples_n": len(W_n.get(n, {})),
            "n_samples_nplus1": len(valid_b_list),
        })

        valid_index = {b: i for i, b in enumerate(valid_b_list)}
        for a in range(pn):
            siblings = [a + k * pn for k in range(p)]
            valid_siblings = [b for b in siblings if b in valid_index]
            if not valid_siblings or a not in f_n[n]:
                audit_rows.append({
                    "n": n,
                    "parent_class": a,
                    "n_valid_siblings": len(valid_siblings),
                    "excluded_sparsity": 1,
                    "V_SC_pi": "",
                    "AI_pi": "",
                    "coherent_count_pi": "",
                    "V_SC_trunc": "",
                    "AI_trunc": "",
                    "coherent_count_trunc": "",
                    "parent_prototype": f_n[n].get(a, ""),
                })
                continue

            idx = [valid_index[b] for b in valid_siblings]
            parent_proto = int(f_n[n][a])
            pi_vals = [int(parent_via_pi[i]) for i in idx]
            trunc_vals = [int(q_n_trunc[i]) for i in idx]
            audit_rows.append({
                "n": n,
                "parent_class": a,
                "n_valid_siblings": len(valid_siblings),
                "excluded_sparsity": int(len(valid_siblings) < p),
                "V_SC_pi": len(set(pi_vals)),
                "AI_pi": int(parent_proto in set(pi_vals)),
                "coherent_count_pi": sum(1 for x in pi_vals if x == parent_proto),
                "V_SC_trunc": len(set(trunc_vals)),
                "AI_trunc": int(parent_proto in set(trunc_vals)),
                "coherent_count_trunc": sum(1 for x in trunc_vals if x == parent_proto),
                "parent_prototype": parent_proto,
            })
    return prototypes_n, f_n, pi_maps, coherence_rows, audit_rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Hierarchical profinite maps with π_{n+1,n}")
    ap.add_argument("midi", help="Path to MIDI file")
    ap.add_argument("--axis", choices=["seconds", "beats"], default="beats")
    ap.add_argument("--bin", type=float, default=0.05, help="Bin size (seconds axis)")
    ap.add_argument("--bin-beats", type=float, default=1.0 / 12.0, help="Bin size (beats)")
    ap.add_argument("--p", type=int, required=True, help="Prime (2,3,5,7)")
    ap.add_argument("--Nmax", type=int, default=None)
    ap.add_argument("--K", type=int, default=16)
    ap.add_argument("--Kchild", type=int, default=2, help="Children per parent")
    ap.add_argument("--M", type=int, default=800)
    ap.add_argument("--step", type=int, default=2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True, help="Output directory (e.g. .../p2/)")
    ap.add_argument("--audit-only", action="store_true", help="Only write audit_p{p}.csv; leave existing coherence/prototype files untouched")
    ap.add_argument("--force", action="store_true", help="Overwrite audit_p{p}.csv when --audit-only is used")
    args = ap.parse_args()

    if args.p not in (2, 3, 5, 7):
        raise SystemExit("--p must be 2, 3, 5, or 7")
    Nmax = args.Nmax if args.Nmax is not None else default_nmax(args.p)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_path = out_dir / f"audit_p{args.p}.csv"
    if args.audit_only and audit_path.exists() and not args.force:
        print(f"Audit exists, skipping (use --force to overwrite): {audit_path}", file=sys.stderr)
        return

    if args.axis == "seconds":
        X = build_X_seconds(args.midi, bin_size=args.bin)
    else:
        X = build_X_beats(args.midi, bin_size_beats=args.bin_beats)

    if len(X) < 2:
        raise SystemExit("Series too short")

    rng = np.random.default_rng(args.seed)
    prototypes_n, f_n, pi_maps, coherence_rows, audit_rows = run_hierarchical(
        X, args.p, Nmax, args.step, args.K, args.Kchild, args.M, rng
    )

    p = args.p
    # params
    params = {
        "piece": str(Path(args.midi).name),
        "axis": args.axis,
        "p": p,
        "Nmax": Nmax,
        "K": args.K,
        "Kchild": args.Kchild,
        "M": args.M,
        "step": args.step,
        "seed": args.seed,
        "bin_seconds": args.bin,
        "bin_beats": args.bin_beats,
    }
    if not args.audit_only:
        with open(out_dir / "params.json", "w") as f:
            json.dump(params, f, indent=2)
        with open(out_dir / "params.txt", "w") as f:
            f.write(f"piece={params['piece']} axis={args.axis} p={p} Nmax={Nmax} K={args.K} Kchild={args.Kchild} M={args.M} step={args.step} seed={args.seed}\n")

        # S_n_prototypes_p{p}_n{n}.csv (rows = prototypes, flattened)
        for n, prot in prototypes_n.items():
            flat = prot.reshape(prot.shape[0], -1)
            path = out_dir / f"S_n_prototypes_p{p}_n{n}.csv"
            np.savetxt(path, flat, delimiter=",")
        # pi_p{p}_n{n+1}_to_n{n}.csv
        for n, pi_list in pi_maps.items():
            path = out_dir / f"pi_p{p}_n{n+1}_to_n{n}.csv"
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["child_id", "parent_id"])
                for cid, pid in enumerate(pi_list):
                    w.writerow([cid, pid])
        # f_p{p}_n{n}.csv
        for n, fn in f_n.items():
            path = out_dir / f"f_p{p}_n{n}.csv"
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["residue", "prototype_id"])
                for a in sorted(fn.keys()):
                    w.writerow([a, fn[a]])

        # coherence_hier_p{p}.csv
        coh_path = out_dir / f"coherence_hier_p{p}.csv"
        with open(coh_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["n", "Coh_pi", "Coh_grid", "n_samples_n", "n_samples_nplus1"])
            w.writeheader()
            w.writerows(coherence_rows)
    else:
        coh_path = out_dir / f"coherence_hier_p{p}.csv"

    # audit_p{p}.csv stores per-parent diagnostics for both quantities:
    # pi-columns recompute Coh_pi, trunc-columns recompute Coh_grid.
    audit_fields = [
        "n",
        "parent_class",
        "n_valid_siblings",
        "excluded_sparsity",
        "V_SC_pi",
        "AI_pi",
        "coherent_count_pi",
        "V_SC_trunc",
        "AI_trunc",
        "coherent_count_trunc",
        "parent_prototype",
    ]
    with open(audit_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=audit_fields)
        w.writeheader()
        w.writerows(audit_rows)

    print(f"Wrote {coh_path} ({len(coherence_rows)} rows), {audit_path} ({len(audit_rows)} rows), params, prototypes, pi, f")


if __name__ == "__main__":
    main()
