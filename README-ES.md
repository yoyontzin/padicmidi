# PAdicMIDI

> *Conjunto de herramientas en Python para el análisis jerárquico, ultramétrico y p-ádico de datos musicales simbólicos.*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19909665.svg)](https://doi.org/10.5281/zenodo.19909665)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-blue.svg)](LICENSE)
[![Tests: 28 pasan](https://img.shields.io/badge/tests-28%20pasan-brightgreen)](tests/)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Estado: v1.0.0](https://img.shields.io/badge/release-v1.0.0-orange)](VERSION.md)

> Read this in [English](README.md).

PAdicMIDI es un programa de cómputo de investigación que implementa, por
primera vez en software de uso público, el marco del **Análisis
Aritmético-Topológico de Datos (ATDA)** sobre música simbólica. Dado un
archivo MIDI estándar, el programa construye una *torre p-ádica de espacios
de patrones* $D_{p,n}$, define explícitamente el sistema inverso
$\pi_{n+1,n}\colon S_{n+1} \to S_n$ y calcula el invariante de coherencia
$\mathrm{Coh}_\pi(p,n)$ junto con su *piso nulo arquitectónico* $1/p$.

## Artículos asociados

El programa reproduce, exactamente, las afirmaciones numéricas de dos manuscritos:

1. **Pérez-Buendía, J. R.** *Prime-power indexed multiscale graph diagnostics for
   symbolic temporal data: methodological exploration and delimitation via BWV 1007.*
   Sometido a *Journal of Mathematics and Music* (Taylor & Francis), 2026.
2. **Pérez-Buendía, J. R.** *Profinite hierarchical patterns and prime-indexed
   multiscale invariants in symbolic music.* Sometido, 2026.

## Inicio rápido

```bash
git clone https://github.com/yoyontzin/padicmidi.git
cd padicmidi
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Analizar el preludio de BWV 1007 con p=2:
padicmidi-run-one data/midi/bwv1007-1.mid bwv1007_pre beats 2 --out resultados/bwv1007/p2
cat resultados/bwv1007/p2/coherence_hier_p2.csv
# n,Coh_pi,Coh_grid,n_samples_n,n_samples_nplus1
# 1,0.5,0.5,1,2
# 2,0.5,0.5,2,4
# ...
```

El valor exacto $\mathrm{Coh}_\pi(2,n)=1/2$ es el **piso nulo arquitectónico**
predicho por la Proposición `prop:null_floor` del Artículo 2.

## API programática

```python
from padicmidi import run_hierarchical_from_midi

resultado = run_hierarchical_from_midi(
    midi_path="data/midi/bwv1007-1.mid",
    p=2,
    axis="beats",
    nmax=5,
    seed=42,
)
for fila in resultado["coherence"]:
    print(fila)
```

## Applet sin conexión, autocontenido

La carpeta `web-demo/` contiene un único archivo HTML (`applet-es.html`) que
ejecuta el análisis de extremo a extremo dentro del navegador, **sin
dependencias de red**. Ábrelo con doble clic; carga cualquier archivo MIDI o
usa la demostración embebida BWV 1007, elige un primo $p$, y lee
$\mathrm{Coh}_\pi(p,n)$ junto con una visualización del árbol p-ádico de
prototipos.

## Qué contiene este repositorio

```
padicmidi/
├── src/padicmidi/         Paquete Python (motor, IO, análisis, figuras, CLI)
├── tests/                 28 tests: smoke, unit, regresión, paper_values
├── examples/              scripts mínimos para aprender la API
├── data/midi/             26 MIDIs con licencia CC (BWV 1007/1008/1009 + toys)
├── results/verified/      CSVs de referencia de ambos artículos
├── docs/                  manuales de usuario y técnico, referencia API
├── scripts/               reproduce.sh, validate.sh
└── web-demo/applet-es.html   applet sin conexión autocontenido (~35 KB)
```

## Aspectos matemáticos centrales

- **Piso nulo (Proposición 3.1, Artículo 2).** Bajo las hipótesis estructurales
  (SC) de cobertura entre hermanos y (AI) de inclusión-ancestro, el invariante
  de coherencia del sistema inverso forzado iguala
  $\mathrm{Coh}_\pi(p,n) = 1/p$ exactamente.
- **Discriminante de textura.** Los corpus polifónicos de Bach (BWV 1049, 1050,
  1079, Goldberg) se desvían medibles del piso, lo cual da un diagnóstico
  cuantitativo de textura musical.
- **Filtro de aridez p-ádica (Corolario 3.2, Artículo 2).** Cuando el cociente
  de ramificación $r$ coincide con el primo $p$, la señal de diferenciación
  queda absorbida en la estructura de ramificación y produce el piso nulo;
  los casos discordantes dejan escapar la señal.

Ver [`MATH-SPEC.md`](MATH-SPEC.md) para la especificación matemática completa
con todas las convenciones, pseudocódigo e invariantes verificables.

## Reproducibilidad

```bash
bash scripts/reproduce.sh           # vuelve a correr el pipeline canónico
bash scripts/validate.sh            # verifica los hashes de CSV contra results/verified
pytest tests/                       # 28 tests, incluidos paper_values/
```

Ver [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) para entorno, semillas y
valores esperados.

## Cómo citar

Si usa este software, por favor cite tanto este paquete como los artículos
asociados. Use el archivo [`CITATION.cff`](CITATION.cff) o el bloque BibTeX
siguiente:

```bibtex
@software{padicmidi2026,
  author       = {P{\'e}rez-Buend{\'\i}a, J. Rogelio},
  title        = {{PAdicMIDI}: A {P}ython Toolkit for Hierarchical,
                  Ultrametric, and p-adic Analysis of Symbolic Music Data},
  version      = {1.0.0},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19909665},
  url          = {https://doi.org/10.5281/zenodo.19909665}
}
```

## Licencia

- Código fuente en `src/`, `tests/`, `scripts/`, `examples/`, `web-demo/`:
  **Licencia MIT** ([`LICENSE`](LICENSE)).
- Documentación, resultados verificados, figuras derivadas: **CC-BY 4.0**.
- Archivos MIDI: atribución por archivo en
  [`data/midi/README.md`](data/midi/README.md); predominantemente Mutopia
  (CC-BY 4.0 / CC-BY-SA 3.0), Dominio Público de EUA, y aportaciones propias
  del autor en CC0.

## Autor y afiliación

**Jesús Rogelio Pérez Buendía** — *publica académicamente como* **J. Rogelio Pérez-Buendía**.
SECIHTI — Centro de Investigación en Matemáticas (CIMAT), Unidad Mérida.
ORCID: [0000-0002-7739-4779](https://orcid.org/0000-0002-7739-4779).
Página web: [www.cimat.mx/~rogelio.perez](https://www.cimat.mx/~rogelio.perez).
Correo: rogelio@cimat.mx.
Grupo de investigación: P-ADAGIO (P-adic Arithmetic, Dynamics And
Galois-Informed Observations).

Financiamiento: SECIHTI (México), proyecto CF-2019/217367.

## Registro autoral en México

La versión `v1.0.0` de este software está registrada ante el **Instituto
Nacional del Derecho de Autor (INDAUTOR)** con el formato **RPDA-03**. El
dossier (que incluye datos personales del autor: RFC, CURP, domicilio) se
entrega físicamente al Instituto y por ello no forma parte de este
repositorio público. La licencia MIT del código fuente es independiente de,
y no afecta, el reconocimiento de los derechos morales y patrimoniales que
otorga la Ley Federal del Derecho de Autor (LFDA). El ZIP cuyo SHA-256 se
registró corresponde exactamente al contenido de este repositorio en el
release etiquetado `v1.0.0`.
