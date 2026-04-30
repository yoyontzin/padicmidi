"""
padicmidi.io.midi_pretty — optional MIDI adapter using ``pretty_midi``.

This adapter exists for compatibility with workflows that prefer
``pretty_midi``. It reproduces the same ``(t_on, t_off, pitch, velocity)``
quadruples emitted by :mod:`padicmidi.io.midi_mido`, but with two
caveats:

* Numerical outputs may differ from the gold standard at the 4th–5th
  decimal place because ``pretty_midi`` uses a different tick-to-second
  resolution model under tempo changes.
* This adapter requires the optional dependency ``pretty_midi``;
  install with ``pip install padicmidi[pretty]``.

Use this adapter only when you cannot install ``mido`` or when you want
to cross-validate the parsing layer.
"""

from __future__ import annotations

from typing import List, Tuple

NoteEvent = Tuple[float, float, int, int]


def _require_pretty_midi():
    try:
        import pretty_midi
    except ImportError as exc:  # pragma: no cover - exercised only when pretty_midi missing
        raise ImportError(
            "padicmidi.io.midi_pretty requires the optional dependency 'pretty_midi'. "
            "Install with: pip install padicmidi[pretty]"
        ) from exc
    return pretty_midi


def parse_midi_notes_seconds(path: str) -> List[NoteEvent]:
    """Return ``(t_on, t_off, pitch, velocity)`` in seconds via ``pretty_midi``."""
    pretty_midi = _require_pretty_midi()
    pm = pretty_midi.PrettyMIDI(path)
    events: List[NoteEvent] = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            events.append((float(note.start), float(note.end), int(note.pitch), int(note.velocity)))
    events.sort(key=lambda e: e[0])
    return events


def parse_midi_notes_beats(path: str) -> List[NoteEvent]:
    """Return ``(u_on, u_off, pitch, velocity)`` in beats via ``pretty_midi``.

    Beat-time uses ``pretty_midi.time_to_tick`` divided by ticks per beat,
    therefore it follows the score grid rather than wall-clock time.
    """
    pretty_midi = _require_pretty_midi()
    pm = pretty_midi.PrettyMIDI(path)
    tpb = pm.resolution
    events: List[NoteEvent] = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            u_on = pm.time_to_tick(note.start) / tpb
            u_off = pm.time_to_tick(note.end) / tpb
            events.append((float(u_on), float(u_off), int(note.pitch), int(note.velocity)))
    events.sort(key=lambda e: e[0])
    return events


__all__ = ["parse_midi_notes_seconds", "parse_midi_notes_beats"]
