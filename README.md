# PAdicMIDI

> *A Python Toolkit for Hierarchical, Ultrametric, and p-adic Analysis of Symbolic Music Data.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests: 28 passing](https://img.shields.io/badge/tests-28%20passing-brightgreen)](tests/)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Status: v1.0.0](https://img.shields.io/badge/release-v1.0.0-orange)](VERSION.md)

> Léelo en [español](README-ES.md).

PAdicMIDI is a research-software toolkit that implements, for the first time
in publicly available code, the framework of **Arithmetic-Topological Data
Analysis (ATDA)** on symbolic music. Given a Standard MIDI file, the toolkit
constructs a $p$-adic tower of pattern spaces $D_{p,n}$, builds the explicit
inverse system $\pi_{n+1,n}\colon S_{n+1} \to S_n$, and computes the coherence
invariant $\mathrm{Coh}_\pi(p,n)$ together with its architectural null floor
$1/p$.

## Companion papers

The toolkit reproduces, exactly, the numerical claims of two manuscripts:

1. **Pérez-Buendía, J. R.** *Prime-power indexed multiscale graph diagnostics for
   symbolic temporal data: methodological exploration and delimitation via BWV 1007.*
   Submitted to *Journal of Mathematics and Music* (Taylor & Francis), 2026.
2. **Pérez-Buendía, J. R.** *Profinite hierarchical patterns and prime-indexed
   multiscale invariants in symbolic music.* Submitted, 2026.

## Quick start

```bash
git clone https://github.com/yoyontzin/padicmidi.git
cd padicmidi
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Analyse the bundled BWV 1007 prelude with p=2:
padicmidi-run-one data/midi/bwv1007-1.mid bwv1007_pre beats 2 --out results_local/bwv1007/p2
cat results_local/bwv1007/p2/coherence_hier_p2.csv
# n,Coh_pi,Coh_grid,n_samples_n,n_samples_nplus1
# 1,0.5,0.5,1,2
# 2,0.5,0.5,2,4
# ...
```

The exact value $\mathrm{Coh}_\pi(2,n)=1/2$ is the **architectural null floor**
predicted by the proposition `prop:null_floor` of Paper 2.

## Programmatic API

```python
from padicmidi import run_hierarchical_from_midi

result = run_hierarchical_from_midi(
    midi_path="data/midi/bwv1007-1.mid",
    p=2,
    axis="beats",
    nmax=5,
    seed=42,
)
for row in result["coherence"]:
    print(row)
```

## Self-contained offline applet

The folder `web-demo/` contains a single HTML file `applet.html` that runs the
analysis end-to-end inside the browser, with **zero network dependencies**.
Open it with a double-click; load any MIDI file or use the embedded BWV 1007
demo, choose a prime $p$, and read off $\mathrm{Coh}_\pi(p,n)$ together with a
visualisation of the $p$-adic tree of prototypes.

## What is in this repository

```
padicmidi/
├── src/padicmidi/         Python package (motor, IO, analysis, figs, CLI)
├── tests/                 28 tests across smoke, unit, regression, paper_values
├── examples/              minimal scripts to learn the API
├── data/midi/             26 CC-licensed MIDI files (BWV 1007/1008/1009 + toys)
├── results/verified/      gold-standard CSVs from both companion papers
├── docs/                  user manual, technical manual, API reference
├── scripts/               reproduce.sh, validate.sh
└── web-demo/applet.html   self-contained offline applet (≈ 500 KB)
```

## Mathematical highlights

- **Null floor (Proposition 3.1, Paper 2).** Under the structural hypotheses
  (SC) of sibling-coverage and (AI) of ancestor-inclusion, the coherence
  invariant of the forced inverse system equals $\mathrm{Coh}_\pi(p,n) = 1/p$
  exactly.
- **Texture discriminant.** Polyphonic Bach corpora (BWV 1049, 1050, 1079,
  Goldberg) deviate measurably from the floor, providing a quantitative
  diagnostic of musical texture.
- **p-adic aridity filter (Corollary 3.2, Paper 2).** When the branching ratio
  $r$ matches the prime $p$, the differentiation signal is absorbed into the
  branching structure and produces the null floor; mismatched cases let the
  signal escape.

See [`MATH-SPEC.md`](MATH-SPEC.md) for the full mathematical specification with
all conventions, pseudocode and verifiable invariants.

## Reproducibility

```bash
bash scripts/reproduce.sh           # rerun the canonical pipeline
bash scripts/validate.sh            # verify CSV checksums against results/verified
pytest tests/                       # 28 tests, including paper_values/
```

See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for environment, seeds, and
expected values.

## Citation

If you use this software, please cite both this package and the companion
papers. Use the [`CITATION.cff`](CITATION.cff) file or the BibTeX block below:

```bibtex
@software{padicmidi2026,
  author       = {P{\'e}rez-Buend{\'\i}a, J. Rogelio},
  title        = {{PAdicMIDI}: A {P}ython Toolkit for Hierarchical,
                  Ultrametric, and p-adic Analysis of Symbolic Music Data},
  version      = {1.0.0},
  year         = {2026},
  url          = {https://github.com/yoyontzin/padicmidi}
}
```

## Licence

- Source code in `src/`, `tests/`, `scripts/`, `examples/`, `web-demo/`:
  **MIT License** ([`LICENSE`](LICENSE)).
- Documentation, verified results, derived figures: **CC-BY 4.0**.
- MIDI files: per-file attribution in [`data/midi/README.md`](data/midi/README.md);
  predominantly Mutopia (CC-BY 4.0 / CC-BY-SA 3.0), Public-Domain US, and the
  author's own CC0 contributions.

## Author and affiliation

**Jesús Rogelio Pérez Buendía** — *publishes as* **J. Rogelio Pérez-Buendía**.
SECIHTI — Centro de Investigación en Matemáticas (CIMAT), Unidad Mérida.
ORCID: [0000-0002-7739-4779](https://orcid.org/0000-0002-7739-4779).
Web: [www.cimat.mx/~rogelio.perez](https://www.cimat.mx/~rogelio.perez).
Email: rogelio@cimat.mx.
Group: P-ADAGIO (P-adic Arithmetic, Dynamics And Galois-Informed Observations).

Funding: SECIHTI (Mexico), grant CF-2019/217367.

## Authorial registration (México)

The version `v1.0.0` of this software is registered before the
**Instituto Nacional del Derecho de Autor (INDAUTOR)** under format **RPDA-03**.
The dossier (which contains personal data of the author: RFC, CURP, contact
address) is delivered physically to the Mexican Institute and is therefore
not included in this public repository. The MIT licence on the source code
is independent of, and does not affect, the recognition of moral and
patrimonial rights granted by the Mexican Federal Copyright Law (LFDA).
The frozen ZIP whose SHA-256 was registered corresponds exactly to the
contents of this repository at the tagged release `v1.0.0`.
