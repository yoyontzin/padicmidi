"""Smoke tests: the package and all submodules import without error."""

from __future__ import annotations


def test_import_top_level():
    import padicmidi

    assert padicmidi.__version__ == "1.0.0"
    assert padicmidi.__author__ == "J. Rogelio Pérez-Buendía"
    assert padicmidi.__license__ == "MIT"


def test_import_core():
    from padicmidi.core import (
        ALPHA,
        DEFAULT_BIN_BEATS,
        DEFAULT_K,
        DEFAULT_KCHILD,
        DEFAULT_M,
        DEFAULT_SEED,
        DEFAULT_STEP,
        MAX_WINDOWS_PER_RESIDUE,
        SUPPORTED_PRIMES,
        default_nmax,
    )

    assert ALPHA == 1.0
    assert DEFAULT_K == 16
    assert DEFAULT_KCHILD == 2
    assert DEFAULT_M == 800
    assert DEFAULT_STEP == 2
    assert DEFAULT_SEED == 42
    assert DEFAULT_BIN_BEATS == 1.0 / 12.0
    assert MAX_WINDOWS_PER_RESIDUE == 800
    assert SUPPORTED_PRIMES == (2, 3, 5, 7)
    assert default_nmax(2) == 6
    assert default_nmax(3) == 5
    assert default_nmax(5) == 4
    assert default_nmax(7) == 3


def test_import_motor():
    from padicmidi.core.echo import (
        parse_midi_notes_seconds,
        parse_midi_notes_beats,
        chroma_series_duration,
        chroma_series_duration_beats,
        onset_density_series,
        onset_density_series_beats,
        series_with_rhythm,
    )
    from padicmidi.core.hierarchical import (
        build_X_seconds,
        build_X_beats,
        build_W_n,
        run_hierarchical,
        kmeans_numpy,
        dist_matrix,
        aggregate_median,
        get_windows,
    )

    assert callable(parse_midi_notes_seconds)
    assert callable(parse_midi_notes_beats)
    assert callable(chroma_series_duration)
    assert callable(chroma_series_duration_beats)
    assert callable(onset_density_series)
    assert callable(onset_density_series_beats)
    assert callable(series_with_rhythm)
    assert callable(build_X_seconds)
    assert callable(build_X_beats)
    assert callable(build_W_n)
    assert callable(run_hierarchical)
    assert callable(kmeans_numpy)
    assert callable(dist_matrix)
    assert callable(aggregate_median)
    assert callable(get_windows)


def test_import_io_default():
    from padicmidi.io.midi_mido import (
        parse_midi_notes_seconds,
        parse_midi_notes_beats,
    )

    assert callable(parse_midi_notes_seconds)
    assert callable(parse_midi_notes_beats)


def test_import_io_pretty_module_loads():
    """``midi_pretty`` module must import even if pretty_midi is missing."""
    from padicmidi.io import midi_pretty

    assert hasattr(midi_pretty, "parse_midi_notes_seconds")
    assert hasattr(midi_pretty, "parse_midi_notes_beats")


def test_import_cli():
    from padicmidi.cli import run_one, run_suite, benchmark, job_list, mutopia

    for mod in (run_one, run_suite, benchmark, job_list, mutopia):
        assert hasattr(mod, "main"), f"missing main() in {mod.__name__}"


def test_high_level_entry_point_exists():
    from padicmidi import run_hierarchical_from_midi

    assert callable(run_hierarchical_from_midi)
