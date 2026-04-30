"""MIDI input/output adapters.

The default backend is :mod:`padicmidi.io.midi_mido`, used to reproduce
the gold-standard CSVs of the companion papers. An optional adapter
:mod:`padicmidi.io.midi_pretty` is provided for users who prefer
``pretty_midi``.
"""

from padicmidi.io.midi_mido import (
    parse_midi_notes_seconds,
    parse_midi_notes_beats,
)

__all__ = ["parse_midi_notes_seconds", "parse_midi_notes_beats"]
