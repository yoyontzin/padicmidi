"""
padicmidi.io.midi_mido — default MIDI adapter (re-export from the canonical motor).

This module exists for two reasons:

1. To keep ``padicmidi.io.*`` as a stable public surface for users who
   want to swap implementations.
2. To document explicitly that the gold-standard CSVs in
   ``results/verified/`` were produced with ``mido``.

The actual parsing is implemented in :mod:`padicmidi.core.echo`; this
module simply re-exports the two parsing functions.
"""

from __future__ import annotations

from padicmidi.core.echo import (
    parse_midi_notes_seconds,
    parse_midi_notes_beats,
)

__all__ = ["parse_midi_notes_seconds", "parse_midi_notes_beats"]
