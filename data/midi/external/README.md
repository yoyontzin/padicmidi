# External polyphonic corpus — provenance and licensing

This folder is intended for the polyphonic Bach corpus used in the texture-discriminant
analysis of the companion papers (BWV 1049, 1050, 1079, Goldberg Aria). Each
file requires **individual licence audit** before redistribution; for that
reason, the files are not all included by default in v1.0.0.

| File | Piece | Source | Licence | Included in v1.0.0 |
|---|---|---|---|---|
| `bwv1049_mov1.mid`, `_mov2.mid`, `_mov3.mid` | Brandenburg Concerto No. 4, BWV 1049 (3 movements) | likely Mutopia Project or KernScores; user must verify locally | to be verified by the user | no |
| `bwv1050_mov1.mid`, `_mov2.mid`, `_mov3.mid` | Brandenburg Concerto No. 5, BWV 1050 (3 movements) | likely Mutopia Project or KernScores; user must verify locally | to be verified by the user | no |
| `bwv1079_crab.mid` | The Musical Offering, Crab Canon | likely Mutopia Project or KernScores; user must verify locally | to be verified by the user | no |
| `goldberg_aria.mid` | Goldberg Variations, Aria | likely Mutopia Project or KernScores; user must verify locally | to be verified by the user | no |

## How to populate this folder

If you have already audited the licence of your local copies, simply place
them here using the filenames above and re-run the analysis pipeline.

If you need to obtain CC-licensed copies, two recommended sources:

* **Mutopia Project** — https://www.mutopiaproject.org/ — search by BWV
  number; check per-engraver licence (CC-BY, CC-BY-SA, or CC0).
* **KernScores Humdrum corpus** — http://kern.humdrum.org/ — provides a
  `mkern2midi` exporter; redistribution conditions vary by collection.

## Reproducibility note

The polyphonic comparison in Paper 2 §5 reports
$\mathrm{Coh}_\pi(3,n) \in [0.34, 0.999]$ for the extended corpus, which is
the basis of the texture-discriminant claim. Without these files the test
``tests/paper_values/test_polyphonic_corpus.py`` (if implemented in v1.1)
will be skipped automatically.
