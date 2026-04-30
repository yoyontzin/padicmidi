#!/usr/bin/env python3
"""
padicmidi.core.echo — Phase I motor of PAdicMIDI.

Verbatim copy of the canonical file ``profinite_echo_midi.py`` from the
research project repository. Outputs are bit-equivalent to the original
under macOS arm64 with Python 3.13.3 and the dependencies listed in
``requirements-pinned.txt``.

The historical docstring follows.

Profinite Echo / p-adic Precision Tower for MIDI (with harmonic context).

Core objects (see docstrings):
  - bin_size Δ (seconds); MIDI → events (t_on, t_off, pitch, velocity).
  - Duration-weighted chroma series H[t_bin] ∈ R^12, L1-normalized per bin.
  - For prime p and level n: N = p^n; patterns D_n = windows of H of length N.
  - d_n(a,b) = sqrt(mean_i ||a[i]-b[i]||_2^2).
  - G_n(δ): vertices = patterns; edge if d_n <= δ.
  - Invariants: |D_n| (windows sampled), beta0(n) = #connected components in G_n(δ).

Hypothesis: p=2 aligns with binary subdivision, p=3 with ternary; compare n -> beta0(n), n -> |D_n|.

Script: Phase I: --phase1-only --save <prefix>; beats: --time-axis beats --bin-beats 0.083333.
Multi-piece: use scripts/run_benchmark.py. Use out_seconds_<piece>_ and out_beats_<piece>_ (do not mix).
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from mido import MidiFile, MidiTrack, MetaMessage, Message, bpm2tempo

# ---------------------------------------------------------------------------
# 1) Synthetic MIDI generator (binary vs ternary subdivision)
# ---------------------------------------------------------------------------


def write_synthetic_midi(
    path: str,
    tempo_bpm: int = 120,
    ticks_per_beat: int = 480,
    pattern: str = "binary",
    bars: int = 8,
) -> None:
    """
    Binary: Cmaj/G7 por barra, subdiv 2, sustain 0.30.
    Ternary: Cmaj/Fmaj/G7 por barra, subdiv 3, sustain corto (staccato), velocities por subdivisión.
    """
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(tempo_bpm), time=0))

    Cmaj = [60, 64, 67]
    Fmaj = [65, 69, 72]
    G7 = [67, 71, 74, 77]

    if pattern == "binary":
        subdiv = 2
        chords = [Cmaj, G7]
        dur_beats = 0.30
        vel_base = 70
    elif pattern == "ternary":
        subdiv = 3
        chords = [Cmaj, Fmaj, G7]  # 3 acordes por barra
        dur_beats = 0.08  # sustain corto (staccato), sin solapamiento
        vel_base = 60  # variación por k abajo
    else:
        raise ValueError("pattern must be 'binary' or 'ternary'")

    def ticks(beats: float) -> int:
        return int(round(beats * ticks_per_beat))

    beats_per_bar = 4
    total_beats = bars * beats_per_bar

    abs_events = []
    for beat in range(total_beats):
        bar = beat // beats_per_bar
        chord = chords[bar % len(chords)]
        for k in range(subdiv):
            onset_beats = beat + k / subdiv
            on_tick = ticks(onset_beats)
            off_tick = ticks(onset_beats + dur_beats)
            if pattern == "ternary":
                vel = vel_base + k * 22  # 60, 82, 104 por subdivisión
            else:
                vel = vel_base
            for note in chord:
                abs_events.append((on_tick, Message("note_on", note=note, velocity=vel)))
                abs_events.append((off_tick, Message("note_off", note=note, velocity=0)))

    abs_events.sort(key=lambda x: x[0])

    last = 0
    for t, msg in abs_events:
        msg.time = t - last
        track.append(msg)
        last = t

    mid.save(path)


# ---------------------------------------------------------------------------
# 2) MIDI parsing → note events in seconds
# ---------------------------------------------------------------------------

NoteEvent = Tuple[float, float, int, int]  # (t_on, t_off, pitch, velocity)


def parse_midi_notes_seconds(path: str) -> List[NoteEvent]:
    """
    Parse MIDI to (t_on, t_off, pitch, vel) in seconds.
    Uses mido's iterator, which yields msg.time already in seconds.
    """
    mid = MidiFile(path)
    current_sec = 0.0
    on: Dict[Tuple[int, int], Tuple[float, int]] = {}  # (ch, note) -> (t_on_sec, vel)
    events: List[NoteEvent] = []

    for msg in mid:
        current_sec += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            ch = getattr(msg, "channel", 0)
            on[(ch, msg.note)] = (current_sec, msg.velocity)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            ch = getattr(msg, "channel", 0)
            key = (ch, msg.note)
            if key in on:
                t_on_sec, vel = on.pop(key)
                events.append((t_on_sec, current_sec, msg.note, vel))

    events.sort(key=lambda e: e[0])
    return events


NoteEventBeats = Tuple[float, float, int, int]  # (u_on, u_off, pitch, velocity) in beats


def parse_midi_notes_beats(path: str) -> List[NoteEventBeats]:
    """
    Parse MIDI to (u_on, u_off, pitch, vel) in beat-time u (beats).
    Uses ticks_per_beat and delta times in ticks per track; merges tracks, then u = tick / ticks_per_beat.
    Beat-time is independent of tempo: tempo changes do not affect u (beats follow the score grid, not real time).
    """
    mid = MidiFile(path)
    tpb = mid.ticks_per_beat
    # Collect (absolute_tick, msg) from all tracks
    tick_events: List[Tuple[int, object]] = []
    for track in mid.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            tick_events.append((abs_tick, msg))
    tick_events.sort(key=lambda x: x[0])

    on: Dict[Tuple[int, int], Tuple[int, int]] = {}  # (ch, note) -> (tick_on, vel)
    events_beats: List[NoteEventBeats] = []
    for (tick, msg) in tick_events:
        if not hasattr(msg, "type"):
            continue
        if msg.type == "note_on" and msg.velocity > 0:
            ch = getattr(msg, "channel", 0)
            on[(ch, msg.note)] = (tick, msg.velocity)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            ch = getattr(msg, "channel", 0)
            key = (ch, msg.note)
            if key in on:
                tick_on, vel = on.pop(key)
                u_on = tick_on / tpb
                u_off = tick / tpb
                events_beats.append((u_on, u_off, msg.note, vel))

    events_beats.sort(key=lambda e: e[0])
    return events_beats


def chroma_series_duration_beats(
    events: List[NoteEventBeats], bin_size_beats: float
) -> np.ndarray:
    """
    Duration-weighted chroma H(u) with bins in beat space. Same logic as chroma_series_duration.
    """
    if not events:
        return np.zeros((0, 12), dtype=float)
    u0 = events[0][0]
    u1 = max(e[1] for e in events)
    U = u1 - u0
    nbins = max(1, int(U / bin_size_beats) + 1)
    H = np.zeros((nbins, 12), dtype=float)
    for (u_on, u_off, pitch, vel) in events:
        if u_off <= u_on:
            continue
        pc = pitch % 12
        b0 = int((u_on - u0) / bin_size_beats)
        b1 = int((u_off - u0) / bin_size_beats)
        for b in range(b0, min(b1 + 1, nbins)):
            left = u0 + b * bin_size_beats
            right = u0 + (b + 1) * bin_size_beats
            overlap = max(0.0, min(u_off, right) - max(u_on, left))
            if overlap > 0:
                H[b, pc] += overlap * (vel / 127.0)
    row_sums = H.sum(axis=1)
    nz = row_sums > 0
    H[nz] = H[nz] / row_sums[nz][:, None]
    return H


def onset_density_series_beats(
    events: List[NoteEventBeats], bin_size_beats: float
) -> np.ndarray:
    """Onset density a(u) per beat-bin: sum of velocity/127 for note_on in that bin."""
    if not events:
        return np.zeros(0, dtype=float)
    u0 = events[0][0]
    u1 = max(e[1] for e in events)
    U = u1 - u0
    nbins = max(1, int(U / bin_size_beats) + 1)
    a = np.zeros(nbins, dtype=float)
    for (u_on, u_off, pitch, vel) in events:
        if vel <= 0 or u_off <= u_on:
            continue
        b = int((u_on - u0) / bin_size_beats)
        if 0 <= b < nbins:
            a[b] += vel / 127.0
    return a


# ---------------------------------------------------------------------------
# 3) Harmonic context: duration-weighted chroma (12D) per bin
# ---------------------------------------------------------------------------


def chroma_series_duration(events: List[NoteEvent], bin_size: float) -> np.ndarray:
    """
    Build duration-weighted chroma series H with shape (nbins, 12).
    Each row L1-normalized (sum=1) if nonzero.
    Weight per bin = overlap_length * (velocity/127).
    """
    if not events:
        return np.zeros((0, 12), dtype=float)

    t0 = events[0][0]
    t1 = max(e[1] for e in events)
    ev = [(a - t0, b - t0, p, v) for (a, b, p, v) in events]
    T = t1 - t0

    nbins = max(1, int(T / bin_size) + 1)
    H = np.zeros((nbins, 12), dtype=float)

    for (t_on, t_off, pitch, vel) in ev:
        if t_off <= t_on:
            continue
        pc = pitch % 12
        b0 = int(t_on / bin_size)
        b1 = int(t_off / bin_size)
        for b in range(b0, min(b1 + 1, nbins)):
            left = b * bin_size
            right = (b + 1) * bin_size
            overlap = max(0.0, min(t_off, right) - max(t_on, left))
            if overlap > 0:
                H[b, pc] += overlap * (vel / 127.0)

    row_sums = H.sum(axis=1)
    nz = row_sums > 0
    H[nz] = H[nz] / row_sums[nz][:, None]
    return H


def onset_density_series(events: List[NoteEvent], bin_size: float) -> np.ndarray:
    """
    Onset density a(t) por bin: suma de velocity/127 para note_on (vel>0) cuyo t_on cae en el bin.
    a(t) ∈ R, shape (nbins,).
    """
    if not events:
        return np.zeros(0, dtype=float)
    t0 = events[0][0]
    t1 = max(e[1] for e in events)
    T = t1 - t0
    nbins = max(1, int(T / bin_size) + 1)
    a = np.zeros(nbins, dtype=float)
    for (t_on, t_off, pitch, vel) in events:
        if vel <= 0 or t_off <= t_on:
            continue
        b = int((t_on - t0) / bin_size)
        if 0 <= b < nbins:
            a[b] += vel / 127.0
    return a


def series_with_rhythm(
    H: np.ndarray, a: np.ndarray, alpha: float = 1.0
) -> np.ndarray:
    """
    Patrón por bin: X(t) = [H(t); alpha*a(t)], dim 13.
    H (nbins, 12), a (nbins,) -> X (nbins, 13).
    """
    nbins = min(len(H), len(a))
    if nbins == 0:
        return np.zeros((0, 13), dtype=float)
    a_col = (alpha * a[:nbins]).reshape(-1, 1)
    return np.hstack([H[:nbins], a_col])


def spectral_flux_series(H: np.ndarray) -> np.ndarray:
    """f(t) = ||H(t)-H(t-1)||_2 per bin; f(0)=0."""
    nbins = len(H)
    f = np.zeros(nbins, dtype=float)
    for i in range(1, nbins):
        f[i] = float(np.linalg.norm(H[i] - H[i - 1]))
    return f


def zscore_series(x: np.ndarray) -> np.ndarray:
    """Z-score over the whole series; if std=0 return zeros."""
    out = np.asarray(x, dtype=float).copy()
    m, s = np.mean(out), np.std(out)
    if s > 1e-12:
        out = (out - m) / s
    else:
        out[:] = 0.0
    return out


def ioi_histogram_for_window(
    onset_times: np.ndarray,
    t_start: float,
    t_end: float,
    d: int = 16,
    Tmax: float = 2.0,
) -> np.ndarray:
    """
    IOI histogram for onsets in [t_start, t_end). d bins, max IOI = Tmax s.
    Onset_times: sorted array of onset times (e.g. t_on from events).
    Returns histogram (d,) normalized to sum 1; if no IOIs, return uniform 1/d.
    """
    in_window = (onset_times >= t_start) & (onset_times < t_end)
    times = np.sort(onset_times[in_window])
    if len(times) < 2:
        h = np.ones(d, dtype=float) / d
        return h
    iois = np.diff(times)
    iois = iois[iois < Tmax]
    if len(iois) == 0:
        return np.ones(d, dtype=float) / d
    edges = np.linspace(0, Tmax, d + 1)
    h, _ = np.histogram(iois, bins=edges)
    h = h.astype(float)
    if h.sum() > 0:
        h = h / h.sum()
    else:
        h = np.ones(d) / d
    return h


def ioi_histogram_for_window_beats(
    onset_times_u: np.ndarray,
    u_start: float,
    u_end: float,
    d: int = 16,
    Tmax_beats: float = 2.0,
) -> np.ndarray:
    """
    IOI histogram for onsets in [u_start, u_end) in beat-time. d bins, max IOI = Tmax_beats (beats). Default 2.0 beats.
    Returns histogram (d,) normalized to sum 1; if no IOIs, return uniform 1/d.
    """
    in_window = (onset_times_u >= u_start) & (onset_times_u < u_end)
    times = np.sort(onset_times_u[in_window])
    if len(times) < 2:
        return np.ones(d, dtype=float) / d
    iois = np.diff(times)
    iois = iois[iois < Tmax_beats]
    if len(iois) == 0:
        return np.ones(d, dtype=float) / d
    edges = np.linspace(0, Tmax_beats, d + 1)
    h, _ = np.histogram(iois, bins=edges)
    h = h.astype(float)
    if h.sum() > 0:
        h = h / h.sum()
    else:
        h = np.ones(d) / d
    return h


def plot_chroma_heatmap(
    H: np.ndarray,
    title: str = "Chroma heatmap",
    save_path: str | None = None,
) -> None:
    """Heatmap 12 x timebins for chroma (duration-weighted)."""
    plt.figure(figsize=(12, 4))
    plt.imshow(H.T, aspect="auto", origin="lower")
    plt.yticks(range(12), [str(k) for k in range(12)])
    plt.xlabel("time bin")
    plt.ylabel("pitch class")
    plt.title(title)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120)
        plt.close()
    else:
        plt.show()


# ---------------------------------------------------------------------------
# 4) Patterns D_n: windows of length N = p^n over chroma series
# ---------------------------------------------------------------------------


def build_patterns_from_series(
    X: np.ndarray, N: int, step: int = 1
) -> List[np.ndarray]:
    """Windows a: Z/(p^n)Z -> X as arrays of shape (N, D). D=12 (chroma) or 13 (chroma+rhythm). step = window slide."""
    if len(X) < N:
        return []
    patterns = []
    for start in range(0, len(X) - N + 1, step):
        patterns.append(X[start : start + N, :].copy())
    return patterns


# ---------------------------------------------------------------------------
# 5) Metric and proximity graph
# ---------------------------------------------------------------------------


def pattern_dist(a: np.ndarray, b: np.ndarray) -> float:
    """d_n(a,b) = sqrt( mean_i ||a[i]-b[i]||_2^2 )."""
    return float(np.sqrt(np.mean(np.sum((a - b) ** 2, axis=1))))


def proximity_graph(patterns: List[np.ndarray], delta: float) -> nx.Graph:
    """G_n(δ): vertices = patterns; edge if d_n(a,b) <= δ."""
    G = nx.Graph()
    m = len(patterns)
    G.add_nodes_from(range(m))
    for i in range(m):
        for j in range(i + 1, m):
            if pattern_dist(patterns[i], patterns[j]) <= delta:
                G.add_edge(i, j)
    return G


def adaptive_delta_from_patterns(
    patterns: List[np.ndarray],
    q: float = 0.05,
    sample_size: int = 5000,
    rng: np.random.Generator | None = None,
) -> float:
    """
    (A) Umbral adaptativo: muestra de distancias pairwise (sample_size pares),
    delta_n = cuantil q. Evita colapso del grafo en niveles finos.
    """
    m = len(patterns)
    if m < 2:
        return 0.0
    rng = rng or np.random.default_rng()
    max_pairs = m * (m - 1) // 2
    n_sample = min(sample_size, max_pairs)
    if n_sample == 0:
        return 0.0
    if n_sample >= max_pairs:
        dists = []
        for i in range(m):
            for j in range(i + 1, m):
                dists.append(pattern_dist(patterns[i], patterns[j]))
        dists = np.array(dists)
    else:
        dists = []
        seen = set()
        while len(dists) < n_sample:
            i, j = rng.integers(0, m, size=2)
            if i == j or (i, j) in seen or (j, i) in seen:
                continue
            seen.add((i, j))
            dists.append(pattern_dist(patterns[i], patterns[j]))
        dists = np.array(dists)
    return float(np.quantile(dists, q))


def knn_graph(patterns: List[np.ndarray], k: int = 10) -> nx.Graph:
    """
    (B) Grafo kNN: cada nodo se conecta con sus k vecinos más cercanos; grafo no dirigido (simetrizado).
    Evita colapso por delta fijo; k configurable (default 10).
    """
    G = nx.Graph()
    m = len(patterns)
    G.add_nodes_from(range(m))
    k_actual = min(k, m - 1)
    if k_actual < 1:
        return G
    for i in range(m):
        dists = [(pattern_dist(patterns[i], patterns[j]), j) for j in range(m) if j != i]
        dists.sort(key=lambda x: x[0])
        for _, j in dists[:k_actual]:
            G.add_edge(i, j)
    return G


# ---------------------------------------------------------------------------
# 5b) Phase I: multi-observable distance (H, a, f, g_W)
# ---------------------------------------------------------------------------

Phase1Pattern = Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]  # (H_block, a_block, f_block, g_W)


def pattern_dist_phase1(
    p: Phase1Pattern,
    q: Phase1Pattern,
    alpha: float,
    beta: float,
    gamma: float,
) -> float:
    """
    d^2 = mean_i ||H_i-H'_i||^2 + alpha^2 mean_i |a_i-a'_i|^2
        + beta^2 mean_i |f_i-f'_i|^2 + gamma^2 ||g_W-g'_W||^2
    """
    H1, a1, f1, g1 = p
    H2, a2, f2, g2 = q
    N = len(H1)
    term_H = np.mean(np.sum((H1 - H2) ** 2, axis=1))
    term_a = np.mean((a1 - a2) ** 2)
    term_f = np.mean((f1 - f2) ** 2)
    term_g = np.sum((g1 - g2) ** 2)
    d2 = term_H + (alpha ** 2) * term_a + (beta ** 2) * term_f + (gamma ** 2) * term_g
    return float(np.sqrt(max(0.0, d2)))


def knn_graph_phase1(
    patterns: List[Phase1Pattern],
    k: int,
    alpha: float,
    beta: float,
    gamma: float,
) -> nx.Graph:
    """kNN sobre patrones Phase1 con distancia ponderada."""
    G = nx.Graph()
    m = len(patterns)
    G.add_nodes_from(range(m))
    k_actual = min(k, m - 1)
    if k_actual < 1:
        return G
    for i in range(m):
        dists = [
            (pattern_dist_phase1(patterns[i], patterns[j], alpha, beta, gamma), j)
            for j in range(m)
            if j != i
        ]
        dists.sort(key=lambda x: x[0])
        for _, j in dists[:k_actual]:
            G.add_edge(i, j)
    return G


def build_phase1_patterns(
    events: List[NoteEvent],
    H: np.ndarray,
    a_raw: np.ndarray,
    bin_size: float,
    t0: float,
    N: int,
    step: int,
    d_ioi: int = 16,
    Tmax_ioi: float = 2.0,
) -> List[Phase1Pattern]:
    """
    Build list of Phase1 patterns for window length N.
    a and f z-scored over the piece; g_W per window (IOI histogram), normalized sum=1.
    """
    nbins = len(H)
    f = spectral_flux_series(H)
    a = zscore_series(a_raw)
    f = zscore_series(f)
    onset_times = np.array([e[0] for e in events], dtype=float)

    patterns: List[Phase1Pattern] = []
    for start in range(0, nbins - N + 1, step):
        H_block = H[start : start + N, :].copy()
        a_block = a[start : start + N].copy()
        f_block = f[start : start + N].copy()
        t_start = t0 + start * bin_size
        t_end = t0 + (start + N) * bin_size
        g_W = ioi_histogram_for_window(onset_times, t_start, t_end, d=d_ioi, Tmax=Tmax_ioi)
        patterns.append((H_block, a_block, f_block, g_W))
    return patterns


def build_phase1_patterns_beats(
    events: List[NoteEventBeats],
    H: np.ndarray,
    a_raw: np.ndarray,
    bin_size_beats: float,
    u0: float,
    N: int,
    step: int,
    d_ioi: int = 16,
    Tmax_ioi_beats: float = 2.0,
) -> List[Phase1Pattern]:
    """
    Phase1 patterns in beat-time: H(u), a(u), f(u) z-scored; g_W = IOI histogram in beats. Tmax_ioi_beats default 2.0.
    """
    nbins = len(H)
    f = spectral_flux_series(H)
    a = zscore_series(a_raw)
    f = zscore_series(f)
    onset_times_u = np.array([e[0] for e in events], dtype=float)

    patterns: List[Phase1Pattern] = []
    for start in range(0, nbins - N + 1, step):
        H_block = H[start : start + N, :].copy()
        a_block = a[start : start + N].copy()
        f_block = f[start : start + N].copy()
        u_start = u0 + start * bin_size_beats
        u_end = u0 + (start + N) * bin_size_beats
        g_W = ioi_histogram_for_window_beats(
            onset_times_u, u_start, u_end, d=d_ioi, Tmax_beats=Tmax_ioi_beats
        )
        patterns.append((H_block, a_block, f_block, g_W))
    return patterns


# ---------------------------------------------------------------------------
# 6) Tower runner and profile plots
# ---------------------------------------------------------------------------


def _spectral_invariants(G: nx.Graph) -> Tuple[float, float, float, float, float]:
    """Fiedler (lambda2) of normalized Laplacian, average clustering, degree percentiles p25,p50,p75. Returns (lambda2, clustering, p25, p50, p75)."""
    if G.number_of_nodes() == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    try:
        L = nx.normalized_laplacian_matrix(G)
        ev = np.linalg.eigvalsh(L.toarray())
        ev = np.sort(ev)
        lambda2 = float(ev[1]) if len(ev) > 1 else 0.0
    except Exception:
        lambda2 = 0.0
    try:
        clustering = nx.average_clustering(G)
    except Exception:
        clustering = 0.0
    degs = [d for _, d in G.degree()]
    p25 = float(np.percentile(degs, 25)) if degs else 0.0
    p50 = float(np.percentile(degs, 50)) if degs else 0.0
    p75 = float(np.percentile(degs, 75)) if degs else 0.0
    return lambda2, clustering, p25, p50, p75


@dataclass
class LevelResult:
    n: int
    N: int
    num_patterns: int
    num_edges: int
    avg_degree: float
    beta0: int
    delta_used: float  # delta (quantile/fixed) o -1 si kNN
    giant_component_frac: float  # |C_max|/V
    lambda2: float = 0.0  # Fiedler (normalized Laplacian)
    clustering: float = 0.0  # average clustering
    degree_p25: float = 0.0
    degree_p50: float = 0.0
    degree_p75: float = 0.0


def run_tower_on_midi(
    path: str,
    p: int,
    n_min: int,
    n_max: int,
    bin_size: float,
    step: int,
    delta: float,
    cap: int = 300,
    threshold_mode: str = "quantile",
    quantile_q: float = 0.05,
    sample_size: int = 5000,
    knn_k: int = 10,
    alpha: float = 1.0,
    show_heatmap: bool = True,
    save_heatmap: str | None = None,
    rng: np.random.Generator | None = None,
) -> List[LevelResult]:
    """
    Build chroma H(t) + onset density a(t); X(t)=[H(t); alpha*a(t)] dim 13.
    At each level n build G_n by (A) quantile or (B) kNN. Report V, E, avg_degree, beta0, giant_component_frac.
    """
    events = parse_midi_notes_seconds(path)
    H = chroma_series_duration(events, bin_size=bin_size)
    a = onset_density_series(events, bin_size=bin_size)
    X = series_with_rhythm(H, a, alpha=alpha)

    if show_heatmap or save_heatmap:
        plot_chroma_heatmap(
            H,
            title=f"{Path(path).name} | chroma (duration-weighted), bin={bin_size}",
            save_path=save_heatmap,
        )

    rng = rng or np.random.default_rng()
    results: List[LevelResult] = []
    for n in range(n_min, n_max + 1):
        N = p**n
        patterns = build_patterns_from_series(X, N=N, step=step)

        if len(patterns) > cap:
            idx = np.linspace(0, len(patterns) - 1, cap).astype(int)
            patterns = [patterns[i] for i in idx]

        if not patterns:
            results.append(
                LevelResult(
                    n=n,
                    N=N,
                    num_patterns=0,
                    num_edges=0,
                    avg_degree=0.0,
                    beta0=0,
                    delta_used=delta,
                    giant_component_frac=0.0,
                )
            )
            continue

        if threshold_mode == "quantile":
            delta_n = adaptive_delta_from_patterns(
                patterns, q=quantile_q, sample_size=sample_size, rng=rng
            )
            G = proximity_graph(patterns, delta=delta_n)
        elif threshold_mode == "knn":
            G = knn_graph(patterns, k=knn_k)
            delta_n = -1.0  # sentinel: kNN
        else:
            delta_n = delta
            G = proximity_graph(patterns, delta=delta)

        V = len(patterns)
        E = G.number_of_edges()
        avg_deg = (2.0 * E / V) if V > 0 else 0.0
        comps = list(nx.connected_components(G))
        max_comp_size = max(len(c) for c in comps) if comps else 0
        giant_frac = (max_comp_size / V) if V > 0 else 0.0
        results.append(
            LevelResult(
                n=n,
                N=N,
                num_patterns=V,
                num_edges=E,
                avg_degree=avg_deg,
                beta0=len(comps),
                delta_used=delta_n,
                giant_component_frac=giant_frac,
            )
        )
    return results


def run_tower_phase1(
    path: str,
    p: int,
    n_min: int,
    n_max: int,
    bin_size: float,
    step: int,
    cap: int,
    knn_k: int,
    alpha: float,
    beta: float,
    gamma: float,
    d_ioi: int = 16,
    Tmax_ioi: float = 2.0,
    time_axis: str = "seconds",
    bin_size_beats: float = 1.0 / 12.0,
    Tmax_ioi_beats: float = 2.0,
) -> List[LevelResult]:
    """
    Phase I: H, a (z-score), f (spectral flux z-score), g_W (IOI hist per window).
    Distance d^2 = mean||H-H'||^2 + alpha^2 mean|a-a'|^2 + beta^2 mean|f-f'|^2 + gamma^2 ||g_W-g'_W||^2.
    kNN graph only.
    time_axis: 'seconds' (default) or 'beats'. If beats, bin_size_beats and Tmax_ioi_beats (default 2.0 beats) used.
    """
    if time_axis == "beats":
        events_beats = parse_midi_notes_beats(path)
        if not events_beats:
            return []
        H = chroma_series_duration_beats(events_beats, bin_size_beats=bin_size_beats)
        a_raw = onset_density_series_beats(events_beats, bin_size_beats=bin_size_beats)
        u0 = events_beats[0][0]
        results: List[LevelResult] = []
        for n in range(n_min, n_max + 1):
            N = p**n
            patterns = build_phase1_patterns_beats(
                events_beats,
                H,
                a_raw,
                bin_size_beats,
                u0,
                N=N,
                step=step,
                d_ioi=d_ioi,
                Tmax_ioi_beats=Tmax_ioi_beats,
            )
            if len(patterns) > cap:
                idx = np.linspace(0, len(patterns) - 1, cap).astype(int)
                patterns = [patterns[i] for i in idx]
            if not patterns:
                results.append(
                    LevelResult(
                        n=n, N=N, num_patterns=0, num_edges=0, avg_degree=0.0,
                        beta0=0, delta_used=-1.0, giant_component_frac=0.0,
                    )
                )
                continue
            G = knn_graph_phase1(patterns, knn_k, alpha, beta, gamma)
            V = len(patterns)
            E = G.number_of_edges()
            avg_deg = (2.0 * E / V) if V > 0 else 0.0
            comps = list(nx.connected_components(G))
            max_comp = max(len(c) for c in comps) if comps else 0
            giant_frac = (max_comp / V) if V > 0 else 0.0
            lam2, clust, dp25, dp50, dp75 = _spectral_invariants(G)
            results.append(
                LevelResult(
                    n=n, N=N, num_patterns=V, num_edges=E, avg_degree=avg_deg,
                    beta0=len(comps), delta_used=-1.0, giant_component_frac=giant_frac,
                    lambda2=lam2, clustering=clust, degree_p25=dp25, degree_p50=dp50, degree_p75=dp75,
                )
            )
        return results

    events = parse_midi_notes_seconds(path)
    H = chroma_series_duration(events, bin_size=bin_size)
    a_raw = onset_density_series(events, bin_size=bin_size)
    t0 = events[0][0] if events else 0.0

    results = []
    for n in range(n_min, n_max + 1):
        N = p**n
        patterns = build_phase1_patterns(
            events, H, a_raw, bin_size, t0, N=N, step=step, d_ioi=d_ioi, Tmax_ioi=Tmax_ioi
        )
        if len(patterns) > cap:
            idx = np.linspace(0, len(patterns) - 1, cap).astype(int)
            patterns = [patterns[i] for i in idx]
        if not patterns:
            results.append(
                LevelResult(
                    n=n, N=N, num_patterns=0, num_edges=0, avg_degree=0.0,
                    beta0=0, delta_used=-1.0, giant_component_frac=0.0,
                )
            )
            continue
        G = knn_graph_phase1(patterns, knn_k, alpha, beta, gamma)
        V = len(patterns)
        E = G.number_of_edges()
        avg_deg = (2.0 * E / V) if V > 0 else 0.0
        comps = list(nx.connected_components(G))
        max_comp = max(len(c) for c in comps) if comps else 0
        giant_frac = (max_comp / V) if V > 0 else 0.0
        lam2, clust, dp25, dp50, dp75 = _spectral_invariants(G)
        results.append(
            LevelResult(
                n=n, N=N, num_patterns=V, num_edges=E, avg_degree=avg_deg,
                beta0=len(comps), delta_used=-1.0, giant_component_frac=giant_frac,
                lambda2=lam2, clustering=clust, degree_p25=dp25, degree_p50=dp50, degree_p75=dp75,
            )
        )
    return results


def run_tower_on_beats(
    path: str,
    p: int,
    n_min: int,
    n_max: int,
    bin_size_beats: float,
    step: int,
    cap: int,
    knn_k: int,
    alpha: float,
) -> List[LevelResult]:
    """
    Beat-based binning: H(u) and a(u) with bin_size_beats; X(u)=[H(u); alpha*a(u)].
    kNN only. Same tower as baseline (pattern_dist, knn_graph).
    """
    events = parse_midi_notes_beats(path)
    if not events:
        return []
    H = chroma_series_duration_beats(events, bin_size_beats=bin_size_beats)
    a = onset_density_series_beats(events, bin_size_beats=bin_size_beats)
    X = series_with_rhythm(H, a, alpha=alpha)

    results: List[LevelResult] = []
    for n in range(n_min, n_max + 1):
        N = p**n
        patterns = build_patterns_from_series(X, N=N, step=step)
        if len(patterns) > cap:
            idx = np.linspace(0, len(patterns) - 1, cap).astype(int)
            patterns = [patterns[i] for i in idx]
        if not patterns:
            results.append(
                LevelResult(
                    n=n, N=N, num_patterns=0, num_edges=0, avg_degree=0.0,
                    beta0=0, delta_used=-1.0, giant_component_frac=0.0,
                )
            )
            continue
        G = knn_graph(patterns, k=knn_k)
        V = len(patterns)
        E = G.number_of_edges()
        avg_deg = (2.0 * E / V) if V > 0 else 0.0
        comps = list(nx.connected_components(G))
        max_comp = max(len(c) for c in comps) if comps else 0
        giant_frac = (max_comp / V) if V > 0 else 0.0
        results.append(
            LevelResult(
                n=n, N=N, num_patterns=V, num_edges=E, avg_degree=avg_deg,
                beta0=len(comps), delta_used=-1.0, giant_component_frac=giant_frac,
            )
        )
    return results


def save_results_csv(
    results: List[LevelResult],
    filepath: str,
    source: str,
    p: int,
    threshold_mode: str = "quantile",
) -> None:
    """CSV: n, N, V, E, avg_degree, beta0, delta_used, giant_component_frac [, lambda2, clustering, degree_p25, degree_p50, degree_p75]."""
    with open(filepath, "w", newline="") as f:
        w = csv.writer(f)
        has_spectral = getattr(results[0], "lambda2", None) is not None if results else False
        row0 = ["n", "N", "V", "E", "avg_degree", "beta0", "delta_used", "giant_component_frac"]
        if has_spectral:
            row0 += ["lambda2", "clustering", "degree_p25", "degree_p50", "degree_p75"]
        w.writerow(row0)
        for r in results:
            du = r.delta_used if (threshold_mode == "quantile" or r.delta_used >= 0) else -1
            row = [r.n, r.N, r.num_patterns, r.num_edges, round(r.avg_degree, 6), r.beta0, du, round(r.giant_component_frac, 6)]
            if has_spectral:
                row += [round(getattr(r, "lambda2", 0), 6), round(getattr(r, "clustering", 0), 6),
                        round(getattr(r, "degree_p25", 0), 4), round(getattr(r, "degree_p50", 0), 4), round(getattr(r, "degree_p75", 0), 4)]
            w.writerow(row)


def save_results_csv_phase2(
    results: List[LevelResult],
    filepath: str,
    knn_k: int,
    k_over_V_threshold: float = 0.15,
) -> None:
    """CSV Phase II: n, N, V, E, avg_degree, beta0, giant_component_frac, k_over_V, no_informativo."""
    with open(filepath, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "N", "V", "E", "avg_degree", "beta0", "giant_component_frac", "k_over_V", "no_informativo"])
        for r in results:
            V = r.num_patterns
            k_over_V = (knn_k / V) if V > 0 else 0.0
            no_inf = "yes" if k_over_V > k_over_V_threshold else "no"
            w.writerow([
                r.n, r.N, V, r.num_edges, round(r.avg_degree, 6), r.beta0,
                round(r.giant_component_frac, 6), round(k_over_V, 6), no_inf,
            ])


def plot_profile(
    results: List[LevelResult],
    title: str,
    save_prefix: str | None = None,
    run_label: str = "",
) -> None:
    """Plot |D_n|, beta0 y avg_degree vs n. Si save_prefix y run_label, guarda con nombre único."""
    ns = [r.n for r in results]
    sizes = [r.num_patterns for r in results]
    b0 = [r.beta0 for r in results]
    avg_deg = [r.avg_degree for r in results]
    tag = f"{save_prefix}{run_label}_" if (save_prefix and run_label) else (save_prefix or "")

    plt.figure()
    plt.plot(ns, sizes, marker="o")
    plt.xlabel("n")
    plt.ylabel("|D_n| (windows sampled)")
    plt.title(title + " : |D_n|")
    plt.tight_layout()
    if save_prefix:
        plt.savefig(f"{tag}Dn.png", dpi=120)
        plt.close()
    else:
        plt.show()

    plt.figure()
    plt.plot(ns, b0, marker="o")
    plt.xlabel("n")
    plt.ylabel("beta0 (#components)")
    plt.title(title + " : beta0")
    plt.tight_layout()
    if save_prefix:
        plt.savefig(f"{tag}beta0.png", dpi=120)
        plt.close()
    else:
        plt.show()

    plt.figure()
    plt.plot(ns, avg_deg, marker="o")
    plt.xlabel("n")
    plt.ylabel("avg_degree (2|E|/|V|)")
    plt.title(title + " : avg_degree")
    plt.tight_layout()
    if save_prefix:
        plt.savefig(f"{tag}avg_degree.png", dpi=120)
        plt.close()
    else:
        plt.show()

    plt.figure()
    gcf = [r.giant_component_frac for r in results]
    plt.plot(ns, gcf, marker="o")
    plt.xlabel("n")
    plt.ylabel("giant_component_frac (|C_max|/V)")
    plt.title(title + " : giant_component_frac")
    plt.tight_layout()
    if save_prefix:
        plt.savefig(f"{tag}giant_component_frac.png", dpi=120)
        plt.close()
    else:
        plt.show()


def plot_profile_compare(
    res_p2: List[LevelResult],
    res_p3: List[LevelResult],
    title_prefix: str,
    save_prefix: str,
    run_label: str,
) -> None:
    """Cuatro figuras: |D_n|(n), avg_degree(n), beta0(n), giant_component_frac(n) con curvas p=2 y p=3."""
    ns2 = [r.n for r in res_p2]
    ns3 = [r.n for r in res_p3]
    tag = f"{save_prefix}{run_label}_"
    plt.figure()
    plt.plot(ns2, [r.num_patterns for r in res_p2], marker="o", label="p=2")
    plt.plot(ns3, [r.num_patterns for r in res_p3], marker="s", label="p=3")
    plt.xlabel("n")
    plt.ylabel("|D_n| (V)")
    plt.title(f"{title_prefix} : |D_n| (p=2 vs p=3)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{tag}Dn.png", dpi=120)
    plt.close()

    plt.figure()
    plt.plot(ns2, [r.avg_degree for r in res_p2], marker="o", label="p=2")
    plt.plot(ns3, [r.avg_degree for r in res_p3], marker="s", label="p=3")
    plt.xlabel("n")
    plt.ylabel("avg_degree")
    plt.title(f"{title_prefix} : avg_degree (p=2 vs p=3)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{tag}avg_degree.png", dpi=120)
    plt.close()

    plt.figure()
    plt.plot(ns2, [r.beta0 for r in res_p2], marker="o", label="p=2")
    plt.plot(ns3, [r.beta0 for r in res_p3], marker="s", label="p=3")
    plt.xlabel("n")
    plt.ylabel("beta0")
    plt.title(f"{title_prefix} : beta0 (p=2 vs p=3)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{tag}beta0.png", dpi=120)
    plt.close()

    plt.figure()
    plt.plot(ns2, [r.giant_component_frac for r in res_p2], marker="o", label="p=2")
    plt.plot(ns3, [r.giant_component_frac for r in res_p3], marker="s", label="p=3")
    plt.xlabel("n")
    plt.ylabel("giant_component_frac")
    plt.title(f"{title_prefix} : giant_component_frac (p=2 vs p=3)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{tag}giant_component_frac.png", dpi=120)
    plt.close()

    if getattr(res_p2[0], "lambda2", 0) != 0 or getattr(res_p3[0], "lambda2", 0) != 0:
        plt.figure()
        plt.plot(ns2, [getattr(r, "lambda2", 0) for r in res_p2], marker="o", label="p=2")
        plt.plot(ns3, [getattr(r, "lambda2", 0) for r in res_p3], marker="s", label="p=3")
        plt.xlabel("n")
        plt.ylabel("lambda2 (Fiedler)")
        plt.title(f"{title_prefix} : lambda2 (p=2 vs p=3)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{tag}lambda2.png", dpi=120)
        plt.close()
    if getattr(res_p2[0], "clustering", 0) != 0 or getattr(res_p3[0], "clustering", 0) != 0:
        plt.figure()
        plt.plot(ns2, [getattr(r, "clustering", 0) for r in res_p2], marker="o", label="p=2")
        plt.plot(ns3, [getattr(r, "clustering", 0) for r in res_p3], marker="s", label="p=3")
        plt.xlabel("n")
        plt.ylabel("clustering")
        plt.title(f"{title_prefix} : clustering (p=2 vs p=3)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{tag}clustering.png", dpi=120)
        plt.close()


# ---------------------------------------------------------------------------
# 6b) Phase I Bach: multi-observable (H, a, f, g_W), configs A/B/C, reporte Delta, Delta_G, ÉXITO
# ---------------------------------------------------------------------------


def _n_max_for_prime(p: int, max_window: int = 2000) -> int:
    """Max level n such that p^n <= max_window (for control primes)."""
    n = 1
    while n < 20 and p ** n <= max_window:
        n += 1
    return max(1, n - 1)


def run_phase1_bach_report(
    real_path: str,
    save_prefix: str,
    bin_size: float = 0.05,
    step: int = 2,
    cap: int = 300,
    knn_k_list: Optional[List[int]] = None,
    n_max_p2: int = 6,
    n_max_p3: int = 5,
    time_axis: str = "seconds",
    bin_size_beats: float = 1.0 / 12.0,
    Tmax_ioi_beats: float = 2.0,
    k_over_V_threshold: float = 0.15,
    control_primes: Optional[List[int]] = None,
) -> None:
    """
    Phase I solo para Bach: configs (A) alpha=1,beta=0,gamma=0; (B) 1,1,0; (C) 1,1,1.
    k=8,10,12; p=2 n_max=6, p=3 n_max=5. Reporta Delta(n)=beta0_p2(n)-beta0_p3(n),
    giant_component_frac p=2/p=3, Delta_G(n); ÉXITO=1 si (existe n con Delta≠0 en ≥2 k) o (|Delta_G|≥0.10 en algún n).
    time_axis='seconds' (default) o 'beats'; si beats, salidas con sufijo _beats y reporte en phase2_beats_report.txt.
    """
    if knn_k_list is None:
        knn_k_list = [8, 10, 12]
    configs: List[Tuple[str, float, float, float]] = [
        ("A", 1.0, 0.0, 0.0),
        ("B", 1.0, 1.0, 0.0),
        ("C", 1.0, 1.0, 1.0),
    ]
    common_n_max = min(n_max_p3, n_max_p2)
    use_beats = time_axis == "beats"
    suffix = "_beats" if use_beats else ""
    report_filename = f"{save_prefix}phase2_beats_report.txt" if use_beats else f"{save_prefix}phase1_bach_report.txt"

    all_delta_nonzero_count: Dict[Tuple[str, int], List[int]] = {}
    any_delta_G_ge_010 = False
    config_any_delta_G_ge_010: Dict[str, bool] = {c[0]: False for c in configs}
    report_lines: List[str] = []

    for config_name, alpha, beta, gamma in configs:
        for k in knn_k_list:
            if use_beats:
                res_p2 = run_tower_phase1(
                    real_path,
                    p=2,
                    n_min=1,
                    n_max=n_max_p2,
                    bin_size=bin_size,
                    step=step,
                    cap=cap,
                    knn_k=k,
                    alpha=alpha,
                    beta=beta,
                    gamma=gamma,
                    time_axis="beats",
                    bin_size_beats=bin_size_beats,
                    Tmax_ioi_beats=Tmax_ioi_beats,
                )
                res_p3 = run_tower_phase1(
                    real_path,
                    p=3,
                    n_min=1,
                    n_max=n_max_p3,
                    bin_size=bin_size,
                    step=step,
                    cap=cap,
                    knn_k=k,
                    alpha=alpha,
                    beta=beta,
                    gamma=gamma,
                    time_axis="beats",
                    bin_size_beats=bin_size_beats,
                    Tmax_ioi_beats=Tmax_ioi_beats,
                )
            else:
                res_p2 = run_tower_phase1(
                    real_path,
                    p=2, n_min=1, n_max=n_max_p2,
                    bin_size=bin_size, step=step, cap=cap,
                    knn_k=k, alpha=alpha, beta=beta, gamma=gamma,
                )
                res_p3 = run_tower_phase1(
                    real_path,
                    p=3, n_min=1, n_max=n_max_p3,
                    bin_size=bin_size, step=step, cap=cap,
                    knn_k=k, alpha=alpha, beta=beta, gamma=gamma,
                )
            if save_prefix:
                save_results_csv(
                    res_p2,
                    f"{save_prefix}{config_name}_tower_real_bach_k{k}_p2{suffix}.csv",
                    real_path,
                    2,
                    "kNN",
                )
                save_results_csv(
                    res_p3,
                    f"{save_prefix}{config_name}_tower_real_bach_k{k}_p3{suffix}.csv",
                    real_path,
                    3,
                    "kNN",
                )
                plot_profile_compare(
                    res_p2,
                    res_p3,
                    f"Phase1 {config_name} Bach k={k}" + (" (beats)" if use_beats else ""),
                    save_prefix,
                    f"{config_name}_real_bach_k{k}{suffix}",
                )
                # Control primes (e.g. p=5,7): run tower and save CSV; no plot.
                if control_primes:
                    for p_val in control_primes:
                        n_max_p = _n_max_for_prime(p_val)
                        if use_beats:
                            res_cp = run_tower_phase1(
                                real_path,
                                p=p_val, n_min=1, n_max=n_max_p,
                                bin_size=bin_size, step=step, cap=cap,
                                knn_k=k, alpha=alpha, beta=beta, gamma=gamma,
                                time_axis="beats",
                                bin_size_beats=bin_size_beats,
                                Tmax_ioi_beats=Tmax_ioi_beats,
                            )
                        else:
                            res_cp = run_tower_phase1(
                                real_path,
                                p=p_val, n_min=1, n_max=n_max_p,
                                bin_size=bin_size, step=step, cap=cap,
                                knn_k=k, alpha=alpha, beta=beta, gamma=gamma,
                            )
                        save_results_csv(
                            res_cp,
                            f"{save_prefix}{config_name}_tower_real_bach_k{k}_p{p_val}{suffix}.csv",
                            real_path,
                            p_val,
                            "kNN",
                        )

            beta0_p2_by_n = {r.n: r.beta0 for r in res_p2}
            beta0_p3_by_n = {r.n: r.beta0 for r in res_p3}
            giant_p2_by_n = {r.n: r.giant_component_frac for r in res_p2}
            giant_p3_by_n = {r.n: r.giant_component_frac for r in res_p3}
            delta_vec = []
            delta_G_vec = []
            ns_common = []
            for n in range(1, common_n_max + 1):
                if n in beta0_p2_by_n and n in beta0_p3_by_n:
                    ns_common.append(n)
                    delta_vec.append(beta0_p2_by_n[n] - beta0_p3_by_n[n])
                    dg = giant_p2_by_n.get(n, 0) - giant_p3_by_n.get(n, 0)
                    delta_G_vec.append(dg)
                    if abs(dg) >= 0.10:
                        any_delta_G_ge_010 = True
                        config_any_delta_G_ge_010[config_name] = True
            for nn in range(1, common_n_max + 1):
                all_delta_nonzero_count.setdefault((config_name, nn), []).append(
                    1 if (nn <= len(delta_vec) and delta_vec[nn - 1] != 0) else 0
                )

            print(f"--- Phase1 Bach config={config_name} k={k}" + (" (beats)" if use_beats else "") + " ---")
            print("Delta(n) = beta0_p2(n)-beta0_p3(n):", delta_vec, "(n =", ns_common, ")")
            print("giant_component_frac p=2:", [round(giant_p2_by_n.get(n, 0), 4) for n in ns_common])
            print("giant_component_frac p=3:", [round(giant_p3_by_n.get(n, 0), 4) for n in ns_common])
            print("Delta_G(n):", [round(x, 4) for x in delta_G_vec])

            if use_beats:
                report_lines.append(f"--- config={config_name} k={k} ---")
                report_lines.append("Delta(n): " + str(delta_vec))
                report_lines.append("Delta_G(n): " + str([round(x, 4) for x in delta_G_vec]))
                for r in res_p2:
                    V = r.num_patterns
                    kv = (k / V) if V > 0 else 0.0
                    no_inf = "no_informativo" if kv > k_over_V_threshold else "ok"
                    report_lines.append(f"  p=2 n={r.n} V={V} k/V={round(kv, 4)} {no_inf}")
                for r in res_p3:
                    V = r.num_patterns
                    kv = (k / V) if V > 0 else 0.0
                    no_inf = "no_informativo" if kv > k_over_V_threshold else "ok"
                    report_lines.append(f"  p=3 n={r.n} V={V} k/V={round(kv, 4)} {no_inf}")

        if use_beats:
            config_success = 0
            for (cfg, n), counts in all_delta_nonzero_count.items():
                if cfg == config_name and sum(counts) >= 2:
                    config_success = 1
                    break
            if config_success == 0 and config_any_delta_G_ge_010.get(config_name, False):
                config_success = 1
            report_lines.append(f"ÉXITO config {config_name} = {config_success}")
            report_lines.append("")

    success = 0
    for (config_name, n), counts in all_delta_nonzero_count.items():
        if sum(counts) >= 2:
            success = 1
            break
    if not success and any_delta_G_ge_010:
        success = 1
    print("========== Phase I Bach ÉXITO =" if not use_beats else "========== Phase I Bach (beats) ÉXITO =", success, "==========")
    if save_prefix:
        with open(report_filename, "w") as f:
            if use_beats:
                f.write("Phase I Bach time-axis=beats: Delta(n), Delta_G(n) por (config,k); k/V por nivel; no_informativo si k/V>0.15.\n\n")
                f.write("\n".join(report_lines))
                f.write(f"\nÉXITO global = {success}\n")
            else:
                f.write("Phase I Bach: Delta(n), Delta_G(n), ÉXITO (see stdout for full vectors).\n")
                f.write(f"ÉXITO = {success}\n")


# ---------------------------------------------------------------------------
# 6c) Phase II Bach: beat-based binning, alpha sweep, criterio binario, k/V
# ---------------------------------------------------------------------------


def run_phase2_bach_report(
    real_path: str,
    save_prefix: str,
    bin_size_beats: float = 1.0 / 12.0,
    step: int = 2,
    cap: int = 300,
    knn_k_list: Optional[List[int]] = None,
    alpha_list: Optional[List[float]] = None,
    n_max_p2: int = 6,
    n_max_p3: int = 5,
    n_min_report: int = 2,
    k_over_V_threshold: float = 0.15,
) -> None:
    """
    Phase II: beat-based binning H(u), a(u); baseline kNN for BWV1007.
    k=8,10,12; alpha in {0, 0.5, 1, 2, 4}; p=2 (n_max=6), p=3 (n_max=5).
    Report: Delta(n)=beta0_p2-beta0_p3, Delta_G(n) for n>=n_min_report; tables with k/V, no informativo if k/V>0.15.
    ÉXITO=1 si (existe n>=2 con Delta(n)≠0 en al menos 2 k) o (|Delta_G(n)|>=0.10 en algún n>=2).
    """
    if knn_k_list is None:
        knn_k_list = [8, 10, 12]
    if alpha_list is None:
        alpha_list = [0.0, 0.5, 1.0, 2.0, 4.0]
    common_n_max = min(n_max_p3, n_max_p2)

    all_delta_nonzero_count: Dict[Tuple[float, int], List[int]] = {}  # (alpha, n) -> count of k with Delta(n)!=0
    any_delta_G_ge_010 = False

    for alpha in alpha_list:
        for k in knn_k_list:
            res_p2 = run_tower_on_beats(
                real_path,
                p=2,
                n_min=1,
                n_max=n_max_p2,
                bin_size_beats=bin_size_beats,
                step=step,
                cap=cap,
                knn_k=k,
                alpha=alpha,
            )
            res_p3 = run_tower_on_beats(
                real_path,
                p=3,
                n_min=1,
                n_max=n_max_p3,
                bin_size_beats=bin_size_beats,
                step=step,
                cap=cap,
                knn_k=k,
                alpha=alpha,
            )
            if save_prefix:
                alpha_tag = str(alpha).replace(".", "p")
                save_results_csv_phase2(
                    res_p2,
                    f"{save_prefix}phase2_bach_k{k}_a{alpha_tag}_p2.csv",
                    knn_k=k,
                    k_over_V_threshold=k_over_V_threshold,
                )
                save_results_csv_phase2(
                    res_p3,
                    f"{save_prefix}phase2_bach_k{k}_a{alpha_tag}_p3.csv",
                    knn_k=k,
                    k_over_V_threshold=k_over_V_threshold,
                )

            beta0_p2_by_n = {r.n: r.beta0 for r in res_p2}
            beta0_p3_by_n = {r.n: r.beta0 for r in res_p3}
            giant_p2_by_n = {r.n: r.giant_component_frac for r in res_p2}
            giant_p3_by_n = {r.n: r.giant_component_frac for r in res_p3}
            delta_vec = []
            delta_G_vec = []
            ns_common = []
            for n in range(1, common_n_max + 1):
                if n in beta0_p2_by_n and n in beta0_p3_by_n:
                    ns_common.append(n)
                    d = beta0_p2_by_n[n] - beta0_p3_by_n[n]
                    dg = giant_p2_by_n.get(n, 0) - giant_p3_by_n.get(n, 0)
                    delta_vec.append(d)
                    delta_G_vec.append(dg)
                    if n >= n_min_report and abs(dg) >= 0.10:
                        any_delta_G_ge_010 = True
            for nn in range(1, common_n_max + 1):
                idx = nn - 1
                delta_val = delta_vec[idx] if idx < len(delta_vec) else 0
                all_delta_nonzero_count.setdefault((alpha, nn), []).append(
                    1 if (idx < len(delta_vec) and delta_val != 0) else 0
                )

            print(f"--- Phase II Bach k={k} alpha={alpha} ---")
            print("Delta(n) = beta0_p2(n)-beta0_p3(n):", delta_vec, "(n =", ns_common, ")")
            print("Delta_G(n):", [round(x, 4) for x in delta_G_vec])
            # Table with k/V and no informativo for n>=1
            print("n\tN\tV\tbeta0\tgiant_frac\tk/V\tno_informativo")
            for r in res_p2:
                V = r.num_patterns
                k_over_V = (k / V) if V > 0 else 0.0
                no_inf = "yes" if k_over_V > k_over_V_threshold else "no"
                print(f"p=2  {r.n}\t{r.N}\t{V}\t{r.beta0}\t{r.giant_component_frac:.4f}\t{k_over_V:.4f}\t{no_inf}")
            for r in res_p3:
                V = r.num_patterns
                k_over_V = (k / V) if V > 0 else 0.0
                no_inf = "yes" if k_over_V > k_over_V_threshold else "no"
                print(f"p=3  {r.n}\t{r.N}\t{V}\t{r.beta0}\t{r.giant_component_frac:.4f}\t{k_over_V:.4f}\t{no_inf}")

    success = 0
    for (alpha, n), counts in all_delta_nonzero_count.items():
        if n >= n_min_report and sum(counts) >= 2:
            success = 1
            break
    if not success and any_delta_G_ge_010:
        success = 1
    print("========== Phase II Bach ÉXITO =", success, "==========")
    if save_prefix:
        with open(f"{save_prefix}phase2_bach_report.txt", "w") as f:
            f.write("Phase II Bach (beat-based): Delta(n), Delta_G(n), k/V, no informativo (k/V>0.15).\n")
            f.write(f"ÉXITO = {success}\n")


# ---------------------------------------------------------------------------
# 7) Reporte final: tablas + 3 bullets (sin interpretación musical fuerte)
# ---------------------------------------------------------------------------


def report_baseline_final(
    baseline_runs: List[Tuple[str, int, List[LevelResult], List[LevelResult]]],
    threshold_mode: str,
    quantile_q: float,
    knn_k_list: List[int],
    alpha: float = 1.0,
) -> List[str]:
    """Reporte solo hechos cuantitativos: estabilidad en k, separación p=2 vs p=3 en toys, Bach."""
    lines = [
        "========== REPORTE BASELINE (solo hechos cuantitativos) ==========",
        f"Threshold: {threshold_mode}; k values: {knn_k_list}; alpha (onset density): {alpha}.",
        "",
    ]
    # Tablas resumidas por (source, k): p=2 y p=3
    for source_label, k, res_p2, res_p3 in baseline_runs:
        lines.append(f"--- {source_label} k={k} ---")
        lines.append("p=2: n\tN\tV\tE\tavg_degree\tbeta0\tgiant_component_frac")
        for r in res_p2:
            lines.append(f"  {r.n}\t{r.N}\t{r.num_patterns}\t{r.num_edges}\t{r.avg_degree:.4f}\t{r.beta0}\t{r.giant_component_frac:.4f}")
        lines.append("p=3: n\tN\tV\tE\tavg_degree\tbeta0\tgiant_component_frac")
        for r in res_p3:
            lines.append(f"  {r.n}\t{r.N}\t{r.num_patterns}\t{r.num_edges}\t{r.avg_degree:.4f}\t{r.beta0}\t{r.giant_component_frac:.4f}")
        lines.append("")

    lines.append("--- Hechos cuantitativos ---")
    # 1) Estabilidad respecto a k
    by_source: Dict[str, List[Tuple[int, List[LevelResult], List[LevelResult]]]] = {}
    for source_label, k, res_p2, res_p3 in baseline_runs:
        by_source.setdefault(source_label, []).append((k, res_p2, res_p3))
    stab = []
    for source_label, k_runs in by_source.items():
        if len(k_runs) < 2:
            stab.append(f"• {source_label}: solo un k, no se evalúa estabilidad.")
            continue
        ns = [r.n for r in k_runs[0][1]]
        b0_curves = [[r.beta0 for r in res_p2] for _, res_p2, _ in k_runs]
        same_shape = all(len(c) == len(ns) for c in b0_curves)
        b0_range = [max(b0_curves[i][j] for i in range(len(k_runs))) - min(b0_curves[i][j] for i in range(len(k_runs))) for j in range(len(ns))]
        max_diff = max(b0_range) if b0_range else 0
        stab.append(f"• {source_label}: curvas beta0(n) para k={[x[0] for x in k_runs]}; max diferencia entre k en algún n = {max_diff}. {'Curvas similares.' if max_diff <= 2 else 'Curvas difieren.'}")
    lines.extend(stab)

    # 2) Separación p=2 vs p=3 en toys (esperado: toy_binary favorece p=2; toy_ternary favorece p=3)
    for source_label, k_runs in by_source.items():
        if source_label not in ("toy_binary", "toy_ternary"):
            continue
        _, res_p2, res_p3 = k_runs[0]
        b0_p2 = [r.beta0 for r in res_p2]
        b0_p3 = [r.beta0 for r in res_p3]
        # toy_binary "favorece" p=2 si en algún nivel p=2 tiene menos componentes que p=3 (más conectado)
        p2_menos = sum(1 for i in range(min(len(b0_p2), len(b0_p3))) if b0_p2[i] < b0_p3[i])
        p3_menos = sum(1 for i in range(min(len(b0_p2), len(b0_p3))) if b0_p2[i] > b0_p3[i])
        if source_label == "toy_binary":
            lines.append(f"• toy_binary: en {p2_menos} niveles beta0(p=2)<beta0(p=3), en {p3_menos} niveles beta0(p=2)>beta0(p=3). Esperado: más niveles con p=2 más conectado (p=2 favorecido).")
        else:
            lines.append(f"• toy_ternary: en {p2_menos} niveles beta0(p=2)<beta0(p=3), en {p3_menos} niveles beta0(p=2)>beta0(p=3). Esperado: más niveles con p=3 más conectado (p=3 favorecido).")

    # 3) Bach: diferencia consistente entre p=2 y p=3
    bach_runs = [(k, r2, r3) for src, k, r2, r3 in baseline_runs if src == "real_bach"]
    if bach_runs:
        _, res_p2, res_p3 = bach_runs[0]
        b0_2 = [r.beta0 for r in res_p2]
        b0_3 = [r.beta0 for r in res_p3]
        diff = [b0_2[i] - b0_3[i] for i in range(min(len(b0_2), len(b0_3)))]
        lines.append(f"• Bach real: diferencia beta0(p=2)-beta0(p=3) por nivel n: {diff}. Diferencia consistente (mismo signo en todos los niveles): {'sí' if all(d >= 0 for d in diff) or all(d <= 0 for d in diff) else 'no'}.")
    else:
        lines.append("• Bach real: no ejecutado.")
    return lines


# ---------------------------------------------------------------------------
# 8) Main: synthetic tests, optional real MIDI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Profinite Echo: precision tower on MIDI chroma (p=2 vs p=3)"
    )
    parser.add_argument(
        "midi",
        nargs="?",
        default="",
        help="Optional: path to real MIDI (if omitted, only synthetic runs)",
    )
    parser.add_argument(
        "--no-synthetic",
        action="store_true",
        help="Skip synthetic MIDI generation and tests",
    )
    parser.add_argument(
        "--phase1-only",
        action="store_true",
        help="Run only Phase I (Bach, configs A/B/C) and skip baseline tower",
    )
    parser.add_argument(
        "--phase2-only",
        action="store_true",
        help="Run only Phase II (Bach, beat-based binning, alpha sweep)",
    )
    parser.add_argument(
        "--bin-size",
        type=float,
        default=0.05,
        help="Chroma bin size in seconds (default 0.05)",
    )
    parser.add_argument(
        "--time-axis",
        type=str,
        choices=["seconds", "beats"],
        default="seconds",
        help="Time axis for binning: seconds (default) or beats",
    )
    parser.add_argument(
        "--bin-beats",
        type=float,
        default=1.0 / 12.0,
        help="Bin size in beats, only if --time-axis=beats (default 1/12)",
    )
    parser.add_argument(
        "--bin-size-beats",
        type=float,
        default=1.0 / 12.0,
        help="Phase II: bin size in beats (default 1/12)",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=2,
        help="Window slide step (default 2)",
    )
    parser.add_argument(
        "--delta",
        type=float,
        default=0.35,
        help="Proximity threshold only when --threshold=fixed (default 0.35)",
    )
    parser.add_argument(
        "--threshold",
        type=str,
        choices=["quantile", "knn", "fixed"],
        default="knn",
        help="knn (default): kNN graph; quantile: delta_n=Q_q; fixed: delta fijo",
    )
    parser.add_argument(
        "--quantile",
        type=float,
        default=0.05,
        help="Quantile q for --threshold=quantile (default 0.05)",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=5000,
        help="Max random pairs for quantile sampling (default 5000)",
    )
    parser.add_argument(
        "--knn-k",
        type=int,
        nargs="+",
        default=[8, 10, 12],
        help="k values for --threshold=knn (default: 8 10 12)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=1.0,
        help="Weight for onset density in X(t)=[H(t); alpha*a(t)] (default 1.0)",
    )
    parser.add_argument(
        "--n-max",
        type=int,
        default=6,
        help="Max tower level n (default 6)",
    )
    parser.add_argument(
        "--cap",
        type=int,
        default=300,
        help="Cap number of patterns per level for graph build (default 300)",
    )
    parser.add_argument(
        "--control-primes",
        type=int,
        nargs="*",
        default=[],
        help="Additional primes for Phase I (e.g. 5 7) as negative controls; default p=2,3 unchanged",
    )
    parser.add_argument(
        "--save",
        type=str,
        default="",
        help="Save plots and CSV to this prefix (e.g. out_) instead of showing",
    )
    args = parser.parse_args()

    n_min, n_max = 1, args.n_max
    bin_size = args.bin_size
    step = args.step
    delta = args.delta
    cap = args.cap
    threshold_mode = args.threshold
    quantile_q = args.quantile
    sample_size = args.sample_size
    knn_k_list = args.knn_k if isinstance(args.knn_k, list) else [args.knn_k]
    if threshold_mode != "knn":
        knn_k_list = [knn_k_list[0]]
    alpha = getattr(args, "alpha", 1.0)
    save_prefix = args.save.strip() or None
    real_path = args.midi.strip()
    if not real_path and Path("bwv1007_prelude.mid").exists():
        real_path = "bwv1007_prelude.mid"

    # Baseline: (source_label, k, res_p2, res_p3) para reporte
    baseline_runs: List[Tuple[str, int, List[LevelResult], List[LevelResult]]] = []

    if args.phase1_only:
        if real_path and Path(real_path).exists():
            run_phase1_bach_report(
                real_path,
                save_prefix or "",
                bin_size=bin_size,
                step=step,
                cap=cap,
                knn_k_list=knn_k_list,
                n_max_p2=n_max,
                n_max_p3=min(5, n_max),
                time_axis=args.time_axis,
                bin_size_beats=args.bin_beats,
                control_primes=getattr(args, "control_primes", None) or [],
            )
        else:
            print("Phase I requires a valid MIDI path (e.g. bwv1007_prelude.mid).")
        return

    if args.phase2_only:
        if real_path and Path(real_path).exists():
            run_phase2_bach_report(
                real_path,
                save_prefix or "",
                bin_size_beats=args.bin_size_beats,
                step=step,
                cap=cap,
                knn_k_list=knn_k_list,
                alpha_list=[0.0, 0.5, 1.0, 2.0, 4.0],
                n_max_p2=n_max,
                n_max_p3=min(5, n_max),
            )
        else:
            print("Phase II requires a valid MIDI path (e.g. bwv1007_prelude.mid).")
        return

    if not args.no_synthetic:
        write_synthetic_midi("toy_binary.mid", pattern="binary", bars=8)
        write_synthetic_midi("toy_ternary.mid", pattern="ternary", bars=8)

    sources: List[Tuple[str, str, bool]] = []  # (path, label, show_heatmap)
    if not args.no_synthetic:
        sources.append(("toy_binary.mid", "toy_binary", True))
        sources.append(("toy_ternary.mid", "toy_ternary", True))
    if real_path and Path(real_path).exists():
        sources.append((real_path, "real_bach", not args.no_synthetic))

    for ki, k in enumerate(knn_k_list):
        for path, source_label, show_heatmap in sources:
            save_heat = save_prefix and ki == 0
            res_p2 = run_tower_on_midi(
                path,
                p=2,
                n_min=n_min,
                n_max=n_max,
                bin_size=bin_size,
                step=step,
                delta=delta,
                cap=cap,
                threshold_mode=threshold_mode,
                quantile_q=quantile_q,
                sample_size=sample_size,
                knn_k=k,
                alpha=alpha,
                show_heatmap=show_heatmap and save_prefix is None,
                save_heatmap=f"{save_prefix}chroma_{source_label}.png" if save_heat else None,
            )
            res_p3 = run_tower_on_midi(
                path,
                p=3,
                n_min=1,
                n_max=min(5, n_max),
                bin_size=bin_size,
                step=step,
                delta=delta,
                cap=cap,
                threshold_mode=threshold_mode,
                quantile_q=quantile_q,
                sample_size=sample_size,
                knn_k=k,
                alpha=alpha,
                show_heatmap=False,
            )
            baseline_runs.append((source_label, k, res_p2, res_p3))
            if save_prefix:
                save_results_csv(res_p2, f"{save_prefix}tower_{source_label}_k{k}_p2.csv", path, 2, threshold_mode)
                save_results_csv(res_p3, f"{save_prefix}tower_{source_label}_k{k}_p3.csv", path, 3, threshold_mode)
                plot_profile_compare(res_p2, res_p3, f"{source_label} k={k}", save_prefix, f"{source_label}_k{k}")
            print(f"--- {source_label} k={k} ---")
            print("p=2:", [f"n={r.n} |V|={r.num_patterns} beta0={r.beta0} avg_deg={r.avg_degree:.2f} giant_frac={r.giant_component_frac:.3f}" for r in res_p2])
            print("p=3:", [f"n={r.n} beta0={r.beta0} avg_deg={r.avg_degree:.2f} giant_frac={r.giant_component_frac:.3f}" for r in res_p3])

    if not sources:
        print("No sources to run (use --no-synthetic only if you provide a MIDI path).")
        if real_path:
            print("Real MIDI path not found:", real_path)

    report_lines = report_baseline_final(baseline_runs, threshold_mode, quantile_q, knn_k_list, alpha)
    for line in report_lines:
        print(line)
    if save_prefix:
        with open(f"{save_prefix}report.txt", "w") as f:
            f.write("\n".join(report_lines))

    # Phase I (multi-observable): solo Bach, configs A/B/C, reporte Delta, Delta_G, ÉXITO
    if real_path and Path(real_path).exists():
        run_phase1_bach_report(
            real_path,
            save_prefix or "",
            bin_size=bin_size,
            step=step,
            cap=cap,
            knn_k_list=knn_k_list,
            n_max_p2=n_max,
            n_max_p3=min(5, n_max),
            control_primes=getattr(args, "control_primes", None) or [],
        )
        # Phase II (beat-based): Bach, alpha sweep, reporte Delta/Delta_G, k/V, ÉXITO
        run_phase2_bach_report(
            real_path,
            save_prefix or "",
            bin_size_beats=args.bin_size_beats,
            step=step,
            cap=cap,
            knn_k_list=knn_k_list,
            alpha_list=[0.0, 0.5, 1.0, 2.0, 4.0],
            n_max_p2=n_max,
            n_max_p3=min(5, n_max),
        )


if __name__ == "__main__":
    main()
