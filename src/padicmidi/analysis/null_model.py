#!/usr/bin/env python3
"""
Fast null model verification: config A only, parallel processing.
Verifies original values and computes pitch/time-shuffle null models.
"""
import sys, os, csv
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from profinite_echo_midi import (
    parse_midi_notes_seconds,
    parse_midi_notes_beats,
    chroma_series_duration,
    chroma_series_duration_beats,
    onset_density_series,
    onset_density_series_beats,
    build_phase1_patterns,
    build_phase1_patterns_beats,
    knn_graph_phase1,
)
import networkx as nx


def tower_beta0(events, H, a_raw, p, n_max, k, cap, use_beats):
    result = {}
    for n in range(1, n_max + 1):
        N = p ** n
        if use_beats:
            u0 = events[0][0] if events else 0.0
            patterns = build_phase1_patterns_beats(
                events, H, a_raw, 1.0/12.0, u0,
                N=N, step=1, d_ioi=16, Tmax_ioi_beats=2.0)
        else:
            t0 = events[0][0] if events else 0.0
            patterns = build_phase1_patterns(
                events, H, a_raw, 0.05, t0,
                N=N, step=1, d_ioi=16, Tmax_ioi=2.0)
        if len(patterns) > cap:
            idx = np.linspace(0, len(patterns)-1, cap).astype(int)
            patterns = [patterns[i] for i in idx]
        if not patterns:
            result[n] = 0
            continue
        G = knn_graph_phase1(patterns, k, 1.0, 0.0, 0.0)
        result[n] = nx.number_connected_components(G)
    return result


def load_events_and_series(midi_path, axis):
    use_beats = axis == "beats"
    if use_beats:
        events = parse_midi_notes_beats(midi_path)
        H = chroma_series_duration_beats(events, bin_size_beats=1.0/12.0)
        a = onset_density_series_beats(events, bin_size_beats=1.0/12.0)
    else:
        events = parse_midi_notes_seconds(midi_path)
        H = chroma_series_duration(events, bin_size=0.05)
        a = onset_density_series(events, bin_size=0.05)
    return events, H, a, use_beats


def compute_mad_s23(midi_path, axis, ks, cap, shuffle_type="none", seed=42):
    events, H, a, use_beats = load_events_and_series(midi_path, axis)
    if not events:
        return 0.0, 0.0, 0

    rng = np.random.RandomState(seed)
    if shuffle_type == "pitch":
        H_shuf = H.copy()
        rng.shuffle(H_shuf)
        H = H_shuf
    elif shuffle_type == "time":
        a = a.copy()
        win = max(50, len(a) // 20)
        for s in range(0, len(a), win):
            block = a[s:s+win].copy()
            rng.shuffle(block)
            a[s:s+win] = block

    deltas = []
    for k in ks:
        b2 = tower_beta0(events, H, a, 2, 6, k, cap, use_beats)
        b3 = tower_beta0(events, H, a, 3, 5, k, cap, use_beats)
        for n in range(2, 6):
            if n in b2 and n in b3:
                deltas.append(b2[n] - b3[n])

    if not deltas:
        return 0.0, 0.0, 0
    mad = sum(abs(d) for d in deltas) / len(deltas)
    s23 = sum(1 for d in deltas if d != 0) / len(deltas)
    return mad, s23, len(deltas)


def original_from_csvs(prefix, axis, ks, csv_base):
    deltas = []
    sfx = "_beats" if axis == "beats" else ""
    for k in ks:
        p2 = os.path.join(csv_base, axis,
                          f"{prefix}_cap300_A_tower_real_bach_k{k}_p2{sfx}.csv")
        p3 = os.path.join(csv_base, axis,
                          f"{prefix}_cap300_A_tower_real_bach_k{k}_p3{sfx}.csv")
        if not os.path.exists(p2) or not os.path.exists(p3):
            continue
        with open(p2) as f:
            b2 = {int(r["n"]): int(r["beta0"]) for r in csv.DictReader(f)}
        with open(p3) as f:
            b3 = {int(r["n"]): int(r["beta0"]) for r in csv.DictReader(f)}
        for n in range(2, 6):
            if n in b2 and n in b3:
                deltas.append(b2[n] - b3[n])

    if not deltas:
        return 0.0, 0.0, 0
    mad = sum(abs(d) for d in deltas) / len(deltas)
    s23 = sum(1 for d in deltas if d != 0) / len(deltas)
    return mad, s23, len(deltas)


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ext = os.path.join(base, "data", "external_midis")
    out = os.path.join(base, "outputs")
    ks = [8, 10, 12]

    pieces = [
        ("BWV 1049 mov.1", "bwv1049_mov1",
         os.path.join(ext, "bwv1049_brand4_mov1.bachcentral.mid")),
        ("BWV 1050 mov.2", "bwv1050_mov2",
         os.path.join(ext, "bwv1050_brand5_mov2.bachcentral.mid")),
    ]

    fmt = f"{'Piece':<20s} {'Variant':<15s} {'Axis':<8s} {'MAD':>8s} {'S23':>8s} {'N':>4s}"
    print(fmt)
    print("-" * len(fmt))

    for name, pfx, midi in pieces:
        for axis in ["seconds", "beats"]:
            mad, s23, n = original_from_csvs(pfx, axis, ks, out)
            print(f"{name:<20s} {'original':<15s} {axis:<8s} "
                  f"{mad:8.3f} {s23:8.3f} {n:4d}")

        for sh in ["pitch", "time"]:
            for axis in ["seconds", "beats"]:
                print(f"  {name} {sh}-shuffle {axis}...",
                      file=sys.stderr, flush=True)
                mad, s23, n = compute_mad_s23(midi, axis, ks, 300, sh)
                print(f"{name:<20s} {sh+'-shuffle':<15s} {axis:<8s} "
                      f"{mad:8.3f} {s23:8.3f} {n:4d}")
