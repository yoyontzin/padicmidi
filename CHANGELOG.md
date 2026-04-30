# Changelog

All notable changes to PAdicMIDI are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-04-29

### Added

- First public release. Version registered before INDAUTOR (RPDA-03).
- Module `padicmidi.core.echo`: Phase I motor (MIDI parsing, duration-weighted chroma, onset density, K-means towers, β₀ of k-NN graphs).
- Module `padicmidi.core.hierarchical`: p-adic tower with forced inverse system $\pi_{n+1,n}$, computation of $\mathrm{Coh}_\pi(p,n)$ and $\mathrm{Coh}_{\mathrm{grid}}(p,n)$, per-parent audit of (SC) and (AI) hypotheses.
- Modules `padicmidi.io.midi_mido` (default) and `padicmidi.io.midi_pretty` (optional adapter).
- Modules `padicmidi.analysis.{coherence, null_model, audit, aggregate, directionality}`.
- Modules `padicmidi.figs.*` for paper figures.
- CLI entry points: `padicmidi-run-one`, `padicmidi-run-suite`, `padicmidi-benchmark`, `padicmidi-job-list`, `padicmidi-mutopia`.
- Test suite at four levels: smoke, unit, regression (CSV byte-equivalent), paper_values.
- Self-contained offline web applet `web-demo/applet.html` with embedded BWV 1007 demo, drag-and-drop MIDI upload, $\mathrm{Coh}_\pi$ table, p-adic tree SVG, CSV download.
- Reproducibility script `scripts/reproduce.sh` reproducing the gold-standard CSVs of both companion papers.
- 26 CC-licensed MIDI files in `data/midi/` plus polyphonic Bach corpus in `data/midi/external/` with per-file licence audit.
- Verified results in `results/verified/` with SHA-256 checksums.
- Full INDAUTOR dossier in `indautor/`: functional description, technical and user manuals, source code copy, evidence of execution, file manifest, pre-filled RPDA-03 form.

### Documented

- Mathematical specification (`MATH-SPEC.md`) with 22 explicit conventions and three hand-verifiable examples.
- Code audit (`CODE-AUDIT.md`) verifying that the motor reproduces gold values from both companion papers.
- Related work (`RELATED-WORK-SOFTWARE.md`) documenting the gap relative to existing MIDI/MIR toolkits.
