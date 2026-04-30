# Software relacionado y posicionamiento — PAdicMIDI

**Versión:** 1.0.0
**Fecha:** 2026-04-29
**Propósito:** documentar el hueco que llena PAdicMIDI en el ecosistema de
software para música simbólica; este texto se reutiliza en `README.md` y en
el dossier INDAUTOR (sección "originalidad").

---

## 1. Software comparable identificado

Búsqueda en PyPI, GitHub y literatura MIR. Categorías exhaustivas de toolkits Python para música simbólica (MIDI / MusicXML / ABC):

| Software | Mantenedor | Licencia | Categoría | URL |
|---|---|---|---|---|
| `mido` | Ole Martin Bjørndalen | MIT | I/O MIDI bajo nivel (eventos) | mido.readthedocs.io |
| `pretty_midi` | C. Raffel et al. | MIT | I/O MIDI alto nivel + piano-roll | github.com/craffel/pretty-midi |
| `music21` | M. S. Cuthbert / MIT | BSD | análisis musicológico amplio (intervalos, tonalidad, set theory) | web.mit.edu/music21 |
| `muspy` | H.-W. Dong et al. | MIT | toolkit MIR para generación + datasets + I/O multi-formato | muspy.readthedocs.io |
| `miditok` | N. Fradet (LBDs ISMIR 2021) | MIT | tokenización para Transformers (REMI, CPWord, etc.) | pypi.org/project/miditok |
| `symusic` | Y. Liao | MIT | parsing C++ ultrarrápido (200×–500× faster que `mido`) | yikai-liao.github.io/symusic |
| `pyAMPACT` | Pyampact team | BSD | alineación score↔audio + descriptores performance | pyampact.github.io |
| `pytakt` | S. Nishimura, A. Marui (JNMR 2025) | MIT | descripción + generación + MIDI realtime con MML | github.com/snisim/pytakt |
| `pypianoroll` | H.-W. Dong | MIT | piano-roll para deep learning | salu133445.github.io/pypianoroll |
| `partitura` | Marchini, Cancino-Chacón et al. | Apache-2.0 | parsing MusicXML + alineación performance | github.com/CPJKU/partitura |
| `librosa` (no MIDI) | McFee et al. | ISC | análisis audio | librosa.org |

**Bibliotecas matemáticas relacionadas (no específicas de música):**
- `gudhi`, `ripser`, `giotto-tda` — análisis topológico de datos (TDA) clásico (Vietoris-Rips, persistencia). No tienen torres p-ádicas.
- `sage.padics` — aritmética $p$-ádica como objeto algebraico (no aplicada a series de tiempo).
- `pyhomology` — homología persistente clásica.

---

## 2. Gap identificado

Ninguno de los toolkits anteriores implementa **análisis aritmético-topológico p-ádico (ATDA)** sobre series de tiempo extraídas de música simbólica. Específicamente, ninguno provee:

| Funcionalidad PAdicMIDI | Disponible en otros |
|---|---|
| Construcción de **torre de espacios de patrones** $D_{p,n}$ con $N = p^n$ a partir de un MIDI | no — exclusivo de PAdicMIDI |
| Cuantizadores $f_n$ vía K-means jerárquico forzado por $\pi_{n+1,n}$ | no |
| Cómputo del invariante $\mathrm{Coh}_\pi(p,n)$ y comparación contra el piso nulo $1/p$ | no |
| Diagnóstico de hipótesis estructurales (Sibling-Coverage, Ancestor-Inclusion) | no |
| $\beta_0$ del grafo $k$-NN sobre $S_n$ por nivel y por primo de control | no — los toolkits TDA calculan $\beta_0$ pero no sobre esta torre p-ádica |
| Pipeline en lote para una suite de MIDIs con ejes en segundos y en beats | parcial (existen drivers ad-hoc en otros artículos) |
| Auditoría de coherencia mediante CSV `audit_p{p}.csv` | no |

Los toolkits citados (especialmente `music21`, `muspy`, `partitura`) son **complementarios**: se podrían usar como front-end de I/O alternativo. PAdicMIDI usa `mido` directamente para minimizar dependencias y porque la información necesaria para los algoritmos (tiempos en beats vs seconds, pitch class, velocity) es un subconjunto pequeño del API completo de `mido`.

---

## 3. Originalidad metodológica (resumen para INDAUTOR)

PAdicMIDI implementa por primera vez en software de uso público el marco teórico desarrollado por J. Rogelio Pérez-Buendía en dos artículos enviados a revistas indexadas (JMM y Springer-Nature, 2026):

1. **Torre p-ádica de patrones** — construcción algorítmica de $D_{p,n}$ con sistema inverso $\pi_{n+1,n}$ forzado por construcción (no inducido).
2. **Invariante $\mathrm{Coh}_\pi(p,n)$** — primera definición operacional con cota inferior arquitectónica $1/p$ y proposición de "piso nulo" bajo hipótesis (SC) e (AI).
3. **Discriminante de textura** — desviación del piso nulo como diagnóstico cuantitativo de polifonía vs monofonía.
4. **Filtro de aridez p-ádica** — el caso $r = p$ (aridad coincidente) absorbe la señal de diferenciación; el caso $r \neq p$ la deja escapar (Corolario `cor:aridity`).
5. **Auditoría algorítmica de hipótesis matemáticas** — verificación en tiempo de cómputo de las condiciones (SC) y (AI) de la Proposición prop:null_floor.

Ningún software previo conocido implementa estas construcciones.

---

## 4. Posicionamiento de mercado / nicho académico

PAdicMIDI no compite con `miditok` (deep learning) ni con `music21` (musicología clásica). Su nicho es:

- **Investigadores de teoría matemática de la música** (categoría: Mazzola, Mannone, Tymoczko, Lewin, Forte) que necesiten un instrumento computacional para análisis estructural más allá de pitch-class set theory.
- **Investigadores de TDA** que quieran extender análisis topológico clásico (homología persistente Vietoris-Rips) a torres p-ádicas inducidas por la estructura métrica del tiempo.
- **MIR investigators** que quieran un descriptor de textura (mono/poli-fónico) basado en propiedades aritméticas, complementario a descriptores espectrales y rítmicos.
- **Comunidad p-ádica computacional** (entorno SAGE, Magma) interesada en aplicaciones aplicadas de la aritmética p-ádica a series de tiempo reales.

---

## 5. Documentación de la diferencia para el dossier INDAUTOR

Parráfo redactado para `descripcion-funcional.md`:

> *PAdicMIDI es un programa de cómputo en lenguaje Python que implementa por primera vez en software de uso público el marco teórico de Análisis Aritmético-Topológico p-ádico (ATDA) aplicado a música simbólica. A diferencia de bibliotecas existentes para procesamiento MIDI (mido, music21, muspy, miditok, symusic, partitura, pretty_midi, pypianoroll, pyAMPACT, pytakt), que se especializan en entrada/salida, tokenización para aprendizaje profundo, análisis musicológico clásico o alineación score-audio, PAdicMIDI construye torres p-ádicas de espacios de patrones $D_{p,n}$ inducidas por la estructura beat-síncrona o segundo-síncrona de un archivo MIDI, calcula el invariante de coherencia $\mathrm{Coh}_\pi(p,n)$ del sistema inverso $\pi_{n+1,n}$ asociado, lo compara con el piso nulo arquitectónico $1/p$, y produce un diagnóstico cuantitativo de textura musical (aridez, polifonía, jerarquía métrica). El programa se acompaña de un applet HTML autocontenido que automatiza el análisis a partir de un archivo MIDI proporcionado por el usuario.*

El texto anterior es el utilizado en `indautor/descripcion-funcional.md`
para documentar la originalidad del programa frente al estado del arte.
