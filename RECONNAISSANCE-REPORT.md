# Reporte de reconocimiento — PAdicMIDI

**Fecha:** 2026-04-29
**Skill aplicado:** `research-software-builder` (Movimiento 0)
**Modo:** lectura exclusiva, sin modificaciones
**Alcance:** `/Users/yoyonzin/Documents/Paper CODA-\bwv1007/` (carpeta de trabajo real con backslash literal en el nombre)

---

## Resumen ejecutivo

- **Motor numérico canónico:** `profinite_echo_midi.py` (≈ 1809 LOC) — implementa Phase I (parseo MIDI → series → torres $N=p^n$ → grafos kNN → β₀).
- **Motor de torre jerárquica:** `scripts/build_hierarchical_maps.py` (≈ 417 LOC) — importa `profinite_echo_midi`, añade el sistema inverso $\pi_{n+1,n}$ y calcula `Coh_π(p,n)`.
- **Driver canónico de un MIDI:** `repro/code/run_one_piece.py` (≈ 59 LOC) — invoca `build_hierarchical_maps.py` con parámetros estándar.
- **Drivers Phase I:** `scripts/run_benchmark.py`, `scripts/run_suite_bwv1007.py`.
- **Versionado de agregadores:** tres variantes `_legacy / _nextplus / _nextpp` para `build_control_primes_summary*.py` — la canónica para los papers actuales es `_nextpp`.
- **Duplicación masiva detectada:** 7 scripts existen en `raíz/` y en `repro/code/` con LOC idéntico. Modo B nos permite consolidar en `padicmidi/src/` y dejar las copias originales intactas.
- **MIDIs con licencia documentada:** `repro/data/midi/README.md` registra Mutopia (CC-BY/CC-BY-SA), 1997 PD-US, y CC0 propios.
- **MIDIs sin licencia auditada:** `data/external_midis/` (Bach polifónico, Mozart, Handel) — exclusión propuesta del paquete público.
- **Outputs reproducibles ya generados:** estructura `outputs/paper_profinite_hier/<piece>/<axis>/p{2,3,5,7}/coherence_by_level.csv` para BWV1007, BWV1008, BWV1009, BWV1049, BWV1050, BWV1079, Goldberg.

---

## Inventario de archivos (scripts Python clave)

| Archivo (relativo a `Paper CODA-\bwv1007/`) | Categoría | LOC | Notas |
|---|---|---:|---|
| `profinite_echo_midi.py` | motor Phase I + CLI | 1809 | Parseo MIDI, series, torres, grafos kNN, β₀, figuras. Motor canónico. |
| `repro/code/profinite_echo_midi.py` | copia idéntica | 1809 | Pequeña diferencia en docstring (apunta a `exact_commands.sh`). Obsoletar. |
| `scripts/build_hierarchical_maps.py` | motor torre + Coh_π | 417 | Importa de raíz `profinite_echo_midi`. Calcula `Coh_π`, `Coh_π^valid`, escribe `coherence_by_level.csv`. |
| `repro/code/run_one_piece.py` | driver batch jerárquico | 59 | `subprocess` → `build_hierarchical_maps.py`. Canónico. |
| `run_one_piece.py` (raíz) | duplicado | 59 | Obsoletar. |
| `scripts/run_benchmark.py` | driver Phase I (suites toy) | 98 | Llama `profinite_echo_midi` para `cs1-*.mid` + toys. |
| `scripts/run_suite_bwv1007.py` | driver Phase I BWV1007 | 66 | Outputs en `outputs/seconds`, `outputs/beats`. |
| `analyze_bwv1007.py` (raíz) | experimento ultramétrico distinto | 177 | Torre de particiones p-ádicas + tensión tonal. NO es el pipeline de los papers principales. Excluir del paquete o marcar como `experimental/`. |
| `repro/code/analyze_bwv1007.py` | duplicado | 177 | Obsoletar. |
| `continuous_patterns.py` (raíz) | experimento patterns continuos | 72 | Soporte. |
| `repro/code/continuous_patterns.py` | duplicado | 72 | Obsoletar. |
| `job_list_generator.py` (raíz) | utilidad corpus | 86 | Lista 25 MIDIs + reglas. |
| `repro/code/job_list_generator.py` | duplicado | 86 | Obsoletar. |
| `get_mutopia_midis.py` (raíz) | adaptador descarga datos | ~50 | Descarga ZIPs Mutopia. |
| `repro/code/get_mutopia_midis.py` | duplicado | ~50 | Obsoletar. |
| `scripts/build_control_primes_summary.py` | agregador legacy | 143 | Lee `outputs/seconds`, `outputs/beats`. |
| `scripts/build_control_primes_summary_nextplus.py` | agregador Phase I+ | 153 | Lee `outputs/phaseI_nextplus/raw/`. |
| `scripts/build_control_primes_summary_nextpp.py` | agregador Phase I++ (canónico) | 149 | Lee `outputs/phaseI_nextpp/raw/`. Alimenta tablas finales. |
| `scripts/math_findings_nextpp.py` | post-análisis tabla | 99 | Consume `SUMMARY_TABLE_p2357_nextpp.csv`. |
| `scripts/build_summary.py`, `build_continuous_maps.py`, `build_supplement_tables.py`, `build_*_fig*.py`, `build_paper_figures.py`, `aggregate_*.py` | visualización / LaTeX | 50–310 | Generadores de figuras/tablas para los papers. |
| `scripts/nullmodel_*.py`, `run_nullmodel_phaseI.py` | null models | 92–176 | Validación estadística. |
| `scripts/null_model_fast.py`, `null_model_verification.py` | null models (versiones corregidas) | 152, 188 | Recientes (2026-03-10), prefieren a versiones anteriores. |
| `scripts/directionality_test.py` | test direccionalidad | ~110 | Reciente (2026-04-28). |
| `scripts/aggregate_audit.py`, `build_audit_table_tex.py` | auditoría coherencia | 200, 130 | Recientes (2026-04-28). |
| `scripts/debug_parse_latex_log.py` | utilidad LaTeX | ~50 | Soporte editorial. |

---

## Artículos asociados

| Título | Autor | Estado | Ruta principal |
|---|---|---|---|
| *Prime-power indexed multiscale graph diagnostics for symbolic temporal data: methodological exploration and delimitation via BWV 1007* | J. Rogelio Pérez-Buendía | Listo para envío JMM (Taylor & Francis) | `paper_applied/main.tex` |
| *p-adic Towers for Symbolic Music: Hierarchical Coherence and Null Floors* (título Springer-Nature) / equivalente *Profinite hierarchical patterns and prime-indexed multiscale invariants in symbolic music* (versión CAM) | J. Rogelio Pérez-Buendía | Enviado / en flujo Springer | `Paper-ZpMusic-20250206/paper/main.tex` |

PDFs referenciados en raíz:
- `PerezBuendia2026_bwv1007_diagnostics_v1.0.pdf` (paper aplicado)
- `PerezBuendia2026_profinite_music_v1.0.pdf` (paper jerárquico)
- `submission_JMM/prime_power_diagnostics_ANON.pdf` (versión anónima JMM)

---

## Valores verificados identificados (gold standard)

| Cantidad / fenómeno | Valor o rango | Fuente |
|---|---|---|
| Piso nulo arquitectónico (denso, $r=p$) | $\mathrm{Coh}_\pi(p,n) = 1/p$, $\mathrm{Coh}_\pi^{\mathrm{valid}}(p,n) = 1$ | Paper 2 §3 prop:null_floor |
| Pisos numéricos | p=2 → 0.500, p=3 → 0.333, p=5 → 0.200, p=7 → 0.143 | Paper 2 abstract |
| Benchmark BWV1007 binario | $\mathrm{Coh}_\pi(2,n) = 0.500$ exacto $\forall n$, ambos ejes (beats/seconds) | Paper 2 §5 + `CLAUDE.md` |
| BWV1007 ternario | $\mathrm{Coh}_\pi(3,n) \in [0.67, 0.999]$ benchmark | Paper 2 abstract |
| Corpus polifónico Bach (1049/1050/1079/Goldberg) ternario | $\mathrm{Coh}_\pi(3,n) \in [0.34, 0.999]$ | Paper 2 abstract |
| Suites BWV1008, BWV1009 binario | $\mathrm{Coh}_\pi(2,n) = 0.500$ niveles densos (eje beats) | Paper 2 §5 |
| Branching mismatched (Prelude, $r=2 \to r=3$) | $\mathrm{Coh}_\pi(3,3): 0.90 \to 0.36$ (cerca del piso $1/3$) | Paper 2 §5 |
| Branching matched (Sarabande, $r=p=3$) | $\mathrm{Coh}_\pi(3,3) \approx 0.90$ | Paper 2 §5 |
| Null model (ternario Sarabande) | $p$-valores $n=2,3,4$: 0.030, <0.01, 0.030 | Paper 2 §5 |
| Null model (Prelude ternario) | $p$ > 0.30 | Paper 2 §5 |
| Paper 1 — control primes | $R_{\mathrm{ctrl}} \le 1$ | Paper 1 abstract + §5 |
| Paper 1 — toys binario/ternario | $|\Delta_{23}| \le 5$, β₀ → 1 a niveles altos | Paper 1 §5 |

---

## Mapa de dependencias

```
profinite_echo_midi.py (raíz, motor Phase I)
        ▲
        │  imports
        │
scripts/build_hierarchical_maps.py  ──escribe──▶  outputs/paper_profinite_hier/<piece>/<axis>/p{N}/coherence_by_level.csv
        ▲
        │  subprocess
        │
repro/code/run_one_piece.py  ◀── driver batch jerárquico (canónico)

profinite_echo_midi.py
        ▲
        │  subprocess
        │
scripts/run_benchmark.py        ──escribe──▶  outputs/seconds/, outputs/beats/
scripts/run_suite_bwv1007.py    ──escribe──▶  outputs/seconds/, outputs/beats/

outputs/seconds, outputs/beats, outputs/phaseI_nextpp/raw/
        │
        ▼ leen
scripts/build_control_primes_summary*.py
scripts/build_summary.py, aggregate_*.py
        │
        ▼ producen
results/SUMMARY_TABLE*.csv, audit_table.csv, *_REPORT.txt
        │
        ▼ alimentan
scripts/build_*_table_tex.py, build_*_fig*.py
        │
        ▼ producen
paper_applied/sections/TABLE_*.tex,  Paper-ZpMusic-.../paper/figs/*.pdf
```

---

## Duplicados o versiones detectadas

| Grupo | Archivos | Decisión |
|---|---|---|
| Motor Phase I | `profinite_echo_midi.py` (raíz) vs `repro/code/profinite_echo_midi.py` | Canónico: raíz. Copia se elimina del paquete nuevo. |
| Driver jerárquico | `run_one_piece.py` raíz vs `repro/code/run_one_piece.py` | Canónico: `repro/code/run_one_piece.py` (más reciente). |
| Experimentos ultramétricos | `analyze_bwv1007.py` × 2, `continuous_patterns.py` × 2 | NO entran al paquete principal. Mover a `padicmidi/experimental/` opcional. |
| Job list / Mutopia | `job_list_generator.py` × 2, `get_mutopia_midis.py` × 2 | Canónico: `repro/code/`. |
| Control primes (Phase I) | `build_control_primes_summary{,_nextplus,_nextpp}.py` | Canónico: `_nextpp`. Otros como `legacy/`. |
| Null model | `nullmodel_cohpi.py`, `null_model_fast.py`, `null_model_verification.py` | Canónicos: `null_model_fast.py` + `null_model_verification.py` (recientes 2026-03-10). |
| Generadores de figuras paper 2 | varias copias `gen_paridity_fig.py` bajo `paper/`, `submission_CAM/`, `figs/` | Canónica: la del `Paper-ZpMusic-20250206/paper/figs/`. |

---

## Archivos canónicos candidatos

| Componente | Archivo canónico (origen) | Destino en `padicmidi/src/padicmidi/` |
|---|---|---|
| Motor MIDI → series + torres + β₀ | `profinite_echo_midi.py` (raíz) | `core/echo.py` |
| Motor torre jerárquica + Coh_π | `scripts/build_hierarchical_maps.py` | `core/hierarchical.py` |
| Driver de un MIDI | `repro/code/run_one_piece.py` | `cli/run_one.py` |
| Driver de suite | `scripts/run_suite_bwv1007.py` | `cli/run_suite.py` |
| Agregador final Phase I | `scripts/build_control_primes_summary_nextpp.py` | `analysis/aggregate_control_primes.py` |
| Null model | `scripts/null_model_fast.py` + `null_model_verification.py` | `analysis/null_model.py` |
| Auditoría coherencia | `scripts/aggregate_audit.py` + `build_audit_table_tex.py` | `analysis/audit.py` |
| Adaptador Mutopia | `repro/code/get_mutopia_midis.py` | `data_io/mutopia.py` |
| Generador job list | `repro/code/job_list_generator.py` | `cli/job_list.py` |

---

## Datos detectados

| Ubicación | Contenido | Licencia | Inclusión en paquete |
|---|---|---|---|
| `repro/data/midi/` | 26 MIDIs Mutopia + Dave's Bach 1997 + propios | Mutopia CC-BY/CC-BY-SA, PD-US, CC0 | **SÍ** (con `data/midi/README.md` re-emitido) |
| Raíz: `bwv1007*.mid`, `bwv1008*.mid`, `cellosuite3*.mid`, `cs1-*.mid` | Mutopia + Dave's | Mismas | **SÍ** (idénticos a los de `repro/data/midi/`) |
| Raíz: `bwv1007_prelude.mid` | Quantización propia | CC0 | **SÍ** |
| `data/external_midis/` (Bach polifónico, Mozart, Handel) | Externos | Sin auditar archivo por archivo | **NO** — script de descarga + checksums esperados |
| `outputs/**` | ~5.3 GB de CSVs/figuras intermedias | Derivado | **NO** — sólo agregados (`SUMMARY_TABLE*.csv`) |
| `results/` (en `repro/`) | Tablas resumen | CC-BY 4.0 | **SÍ** (vía `padicmidi/results/verified/`) |
| PDFs de papers en raíz | Manuscritos | All rights reserved (autor) | **NO** en código; **SÍ** referenciados en `MANUAL-USUARIO.md` |
| `.venv/`, `__pycache__/` | Entorno | — | **NO** (en `.gitignore`) |
| `JMM_latex_sources.zip`, `KGBN_*.pdf` | Documentos no relacionados | — | **NO** |

---

## Riesgos detectados

### Matemáticos
- **Discrepancia documental `mido` vs `pretty_midi`:** el §Method del Paper 2 menciona `pretty_midi`, pero el código usa `mido`. Decisión a tomar en MATH-SPEC: documentar la elección o emitir errata menor al paper.
- **Convención de bins:** `--bin-beats 0.083333` ↔ $\Delta_b = 1/12$. Documentar explícitamente en MATH-SPEC.
- **Indexado:** residuos $i \bmod p^n$ con $i \in \{0, \dots, p^n - 1\}$ (base 0). Confirmar que todas las funciones siguen esta convención.
- **Semilla aleatoria:** K-means con `seed=42` fija; cambiar la semilla rompería la reproducción exacta de `Coh_π(3,n)`.

### Técnicos
- **Doble montaje macOS:** ignorar `Paper CODA-/bwv1007/` y trabajar exclusivamente con backslash literal `Paper CODA-\bwv1007/`. Documentar al inicio del README.
- **Python 3.13.3 fijo en `repro/requirements.txt`:** versiones pinneadas (numpy 2.4.3, scipy 1.17.1, networkx 3.6.1). Riesgo de fricción en sistemas con Python ≠ 3.13. Mitigación: `MANUAL-TECNICO.md` indica rangos compatibles.
- **OOM con $p=5, N_{\max}=4$:** documentado en `CLAUDE.md` (`shape (625,128,625,13) ≈ 4.84 GiB`). El motor debe rechazar o advertir.

### Legales
- **Datos de terceros sin licencia auditada:** `data/external_midis/` no entra al paquete.
- **`KGBN_...pdf` y `JMM_latex_sources.zip`:** materiales de revisión / PDFs de revistas. NO entran al paquete.
- **Titularidad CIMAT:** se inscribe a nombre de RPB; transmisión patrimonial posterior si CIMAT lo requiere.

### Documentales
- **Versiones derivadas mal documentadas:** los `_nextplus / _nextpp` no tienen `CHANGELOG`. Se generará uno consolidado en `padicmidi/CHANGELOG.md`.
- **Tres copias del README de `repro/`** desincronizadas potencialmente.

---

## Decisiones pendientes (input del investigador requerido antes de Movimiento 1)

1. **¿Incluir `analyze_bwv1007.py` y `continuous_patterns.py` en el paquete como `experimental/`, o excluirlos por completo?** (No alimentan los papers principales.)
2. **¿`mido` o `pretty_midi`?** Recomendación: mantener `mido` y documentar la elección en MATH-SPEC. Confirmar.
3. **¿`data/external_midis/` (Bach polifónico — BWV1049/1050/1079/Goldberg) entra al paquete con su README de licencias propio, o se excluye junto con Mozart/Handel?** Estos sí están en los papers.
4. **Versión pinneada vs flexible:** ¿`requirements.txt` con pins exactos (Python 3.13.3, numpy 2.4.3) o `pyproject.toml` con rangos (`numpy>=2.0,<3.0`)? Recomendación: ambos — `requirements.txt` para reproducción exacta, `pyproject.toml` (post-INDAUTOR) para distribución.
5. **¿El applet HTML universal debe traer BWV1007 precargado como demo?** Recomendación: sí, es evidencia directa para el dossier INDAUTOR.

---

**Fin del Movimiento 0.** Próximo paso: respuesta del investigador a las 5 decisiones pendientes, luego Movimiento 1 (`MATH-SPEC.md`).
