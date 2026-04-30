# API reference — PAdicMIDI

Stable across the v1.x series.

## Top-level

```python
import padicmidi
padicmidi.__version__              # "1.0.0"
padicmidi.run_hierarchical_from_midi(...)
```

### `run_hierarchical_from_midi(midi_path, p, axis="beats", nmax=None, K=16, Kchild=2, M=800, step=2, seed=42, bin_seconds=0.05, bin_beats=1/12) -> dict`

Returns a dict with keys `prototypes_n`, `f_n`, `pi_maps`, `coherence`, `audit`.

## Constants (`padicmidi.core.config`)

| Name | Default | Meaning |
|---|---|---|
| `ALPHA` | 1.0 | Weight of onset density when concatenating with chroma |
| `MAX_WINDOWS_PER_RESIDUE` | 800 | Cap on windows per residue class |
| `DEFAULT_K` | 16 | Initial K-means K |
| `DEFAULT_KCHILD` | 2 | Children per parent in the tower |
| `DEFAULT_M` | 800 | Sample size for K-means |
| `DEFAULT_STEP` | 2 | Window step |
| `DEFAULT_SEED` | 42 | RNG seed |
| `DEFAULT_BIN_BEATS` | 1/12 | Bin size on beat axis |
| `DEFAULT_BIN_SECONDS` | 0.05 | Bin size on seconds axis |
| `SUPPORTED_PRIMES` | (2,3,5,7) | Allowed primes |
| `default_nmax(p)` | callable | Memory-aware default Nmax |

## I/O (`padicmidi.io.midi_mido`, `.midi_pretty`)

Both expose:

- `parse_midi_notes_seconds(path) -> List[(t_on, t_off, pitch, vel)]`
- `parse_midi_notes_beats(path) -> List[(u_on, u_off, pitch, vel)]`

The `_pretty` variant requires `pip install padicmidi[pretty]`.

## Motor (`padicmidi.core.echo`)

- `parse_midi_notes_seconds(path)`
- `parse_midi_notes_beats(path)`
- `chroma_series_duration(events, bin_size) -> ndarray (T, 12)`
- `chroma_series_duration_beats(events, bin_size_beats) -> ndarray (T, 12)`
- `onset_density_series(events, bin_size) -> ndarray (T,)`
- `onset_density_series_beats(events, bin_size_beats) -> ndarray (T,)`
- `series_with_rhythm(H, a, alpha=1.0) -> ndarray (T, 13)`
- `spectral_flux_series(H) -> ndarray (T,)`
- `zscore_series(x) -> ndarray`

## Hierarchical motor (`padicmidi.core.hierarchical`)

- `build_X_seconds(path, bin_size=0.05) -> ndarray (T, 13)`
- `build_X_beats(path, bin_size_beats=1/12) -> ndarray (T, 13)`
- `get_windows(X, N, step) -> List[(start, ndarray (N, 13))]`
- `aggregate_median(windows) -> ndarray (N, 13)`
- `dist_matrix(windows, prototypes) -> ndarray (W, P)`
- `kmeans_numpy(samples, K, rng, max_iter=30) -> ndarray (K_eff, D)`
- `build_W_n(X, p, n_max, step) -> dict[n -> dict[a -> ndarray (p^n, 13)]]`
- `run_hierarchical(X, p, Nmax, step, K, Kchild, M, rng) -> tuple`

## CLI entry points

| Command | Module |
|---|---|
| `padicmidi-run-one` | `padicmidi.cli.run_one` |
| `padicmidi-run-suite` | `padicmidi.cli.run_suite` |
| `padicmidi-benchmark` | `padicmidi.cli.benchmark` |
| `padicmidi-job-list` | `padicmidi.cli.job_list` |
| `padicmidi-mutopia` | `padicmidi.cli.mutopia` |
