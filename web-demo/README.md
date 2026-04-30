# `web-demo/` — offline applet

> Léelo en [español](README-ES.md).

This folder contains two self-contained HTML files that run the PAdicMIDI
analysis end-to-end inside any modern browser, with **no network
dependencies whatsoever**:

- [`applet.html`](applet.html) — English version.
- [`applet-es.html`](applet-es.html) — Spanish version.

## How to use

1. Open `applet.html` by double-clicking it (works on macOS, Linux, Windows).
2. Either click **Load BWV 1007 demo** to use the bundled prelude, or drag
   any Standard MIDI file into the drop zone.
3. Choose the prime *p* (2 or 3) and the maximum tower level *N<sub>max</sub>*.
4. Click **Run analysis**.
5. Read off the table of $\mathrm{Coh}_\pi(p,n)$ values, compare with the
   floor $1/p$, and explore the four musical visualisations (see below).

## Musical visualisations (section 4 of the applet)

Starting from v1.0.0, instead of a single abstract tree the applet provides
**four chained views** that show what the method is actually looking at
inside the piece. A level selector ($n=1,2,\dots,N_\text{max}$) refreshes
all four simultaneously:

1. **4.1 The piece coloured by prototype** — chromagram across time
   (12 pitch classes $\times$ time, blue intensity) with a bottom band
   coloured by which prototype quantises each window of length $p^n$. This
   is the *temporal fingerprint* of the level: colour changes mark
   musically meaningful transitions (modulations, sectional breaks).

2. **4.2 Catalogue of prototypes** — each prototype is rendered as a mini
   chromagram of size $12 \times p^n$ that shows its actual chromatic
   content (which pitch classes define it). The card colour matches the
   bottom band of 4.1, so the user can read where each pattern occurs in
   the piece. Each card also reports how many windows were assigned to it
   and who its $\pi$-parent is.

3. **4.3 Inverse system $\pi$** — Sankey-like diagram of the mapping
   $\pi_{n+1,n}: S_{n+1} \to S_n$. Parent-level prototypes on top, child
   prototypes below, and curves showing which child inherits from which
   parent. The footer reports the computed value of
   $\mathrm{Coh}_\pi(p,n)$ and the floor $1/p$.

4. **4.4 Full p-adic tree** — the tower
   $S_1 \to S_2 \to \dots \to S_{N_\text{max}}$ with nodes coloured by
   inheritance from their root, so the "branches" of the tree are
   visually consistent with the bands in the previous views.

## What the applet implements

* A minimal Standard MIDI File parser (formats 0/1, multi-track merging,
  tempo map; SMPTE division not supported).
* Beat-axis chroma series with bin $\Delta_b = 1/12$.
* Hierarchical p-adic motor with K-means quantisation and forced inverse
  system $\pi_{n+1,n}$.
* Coherence invariant $\mathrm{Coh}_\pi(p,n)$ with comparison against the
  floor $1/p$.
* Four musical visualisations (described above) using SVG and canvas, and
  CSV download of the coherence table.

## Limitations relative to the Python package

* Only primes $p \in \{2, 3\}$ are exposed.
* The seconds axis is not implemented (beats axis only).
* The K-means RNG uses Mulberry32, while the Python package uses NumPy's
  PCG64 — values may differ at the 5th decimal place. Structural floors
  (e.g. $\mathrm{Coh}_\pi(2,n) = 0.500$ on monophonic Bach) are reproduced
  exactly.

For full reproducibility use the CLI command `padicmidi-run-one` or the
Python API `padicmidi.run_hierarchical_from_midi`.

## Privacy

The applet does not send any data anywhere. There are no network requests,
no cookies, no localStorage, no telemetry. The only file accessed is the
MIDI you upload, and that file never leaves your computer.
