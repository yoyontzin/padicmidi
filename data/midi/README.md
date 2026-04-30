# MIDI inputs — provenance and licensing

All files in this folder are either in the public domain or distributed under permissive Creative Commons licenses.

| File | Piece | Source | License |
|---|---|---|---|
| `bwv1007-1.mid` | J.S. Bach, Cello Suite No. 1, BWV 1007 — Prelude | [Mutopia Project](https://www.mutopiaproject.org/) | CC-BY 4.0 / CC-BY-SA 3.0 |
| `bwv1007-2.mid` | BWV 1007 — Allemande | Mutopia Project | CC-BY 4.0 / CC-BY-SA 3.0 |
| `bwv1007-3.mid` | BWV 1007 — Courante | Mutopia Project | CC-BY 4.0 / CC-BY-SA 3.0 |
| `bwv1007-4.mid` | BWV 1007 — Sarabande | Mutopia Project | CC-BY 4.0 / CC-BY-SA 3.0 |
| `bwv1007-5.mid` | BWV 1007 — Menuet I & II | Mutopia Project | CC-BY 4.0 / CC-BY-SA 3.0 |
| `bwv1007-6.mid` | BWV 1007 — Gigue | Mutopia Project | CC-BY 4.0 / CC-BY-SA 3.0 |
| `bwv1007_prelude.mid` | BWV 1007 — Prelude (author's quantization) | Author-curated | CC0 |
| `bwv1008-*.mid` | J.S. Bach, Cello Suite No. 2, BWV 1008 (six movements) | Mutopia Project | CC-BY 4.0 / CC-BY-SA 3.0 |
| `cellosuite3-*.mid` | J.S. Bach, Cello Suite No. 3, BWV 1009 (five movements) | Mutopia Project | CC-BY 4.0 / CC-BY-SA 3.0 |
| `cs1-1pre.mid` … `cs1-6gig.mid` | BWV 1007 — six movements (older transcription, Feb 1997) | Dave's J.S. Bach MIDI page (1997 web archive) | Public domain (US — pre-1929 work) |
| `toy_binary.mid` | Synthetic toy with binary subdivision (control input) | Author-generated | CC0 |
| `toy_ternary.mid` | Synthetic toy with ternary subdivision (control input) | Author-generated | CC0 |

> **Reproducibility note.** The Mutopia project sometimes updates engravings and quantizations; the files in this bundle are the exact byte sequences used to generate the results in `results/verified/` (see `results/verified/CHECKSUMS.txt` for SHA-256 hashes). To download fresh copies, run `padicmidi-mutopia --out data/midi/`.

The polyphonic Bach corpus (BWV 1049, 1050, 1079, Goldberg) used in the
companion papers is documented separately in `external/README.md` because each
file requires individual licence audit before redistribution.
