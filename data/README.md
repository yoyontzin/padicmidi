# `data/` — bundled corpora

This folder contains all data that ships with PAdicMIDI v1.0.0.

```
data/
├── README.md         (this file)
└── midi/
    ├── README.md     (per-file licence and provenance)
    ├── bwv1007-*.mid (Mutopia, CC-BY 4.0)
    ├── bwv1008-*.mid (Mutopia, CC-BY 4.0)
    ├── cellosuite3-*.mid (Mutopia / BWV 1009, CC-BY-SA 3.0)
    ├── cs1-*.mid     (Dave's J.S. Bach MIDI page 1997, Public Domain US)
    ├── bwv1007_prelude.mid (author's own quantisation, CC0)
    ├── toy_binary.mid, toy_ternary.mid (author's own toys, CC0)
    └── external/
        └── README.md (audited per-file provenance for polyphonic Bach corpus)
```

All MIDIs in `data/midi/` (excluding `external/`) are either in the public
domain or under permissive Creative Commons licences. See
[`midi/README.md`](midi/README.md) for the per-file table.

The polyphonic Bach corpus in `data/midi/external/` (BWV 1049, 1050, 1079,
Goldberg) is included only after per-file licence audit; see
[`midi/external/README.md`](midi/external/README.md). When licence audit is
incomplete, files are absent and a download script is provided instead.
