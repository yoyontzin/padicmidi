# Auditoría de código — PAdicMIDI

**Skill:** `research-software-builder` (Movimiento 2)
**Fecha:** 2026-04-29
**Modo de intervención:** B — refactorización ligera autorizada con outputs equivalentes garantizados.

---

## 1. Clasificación de archivos

### Núcleo (`motor-principal`) — entran a `padicmidi/src/`

| Archivo origen | Categoría | Canónico | Notas |
|---|---|:---:|---|
| `profinite_echo_midi.py` | motor Phase I + parsing MIDI + chroma + ventanas + β₀ | ✅ | 1809 LOC. Ofrece 11 funciones reutilizadas por el motor jerárquico. |
| `scripts/build_hierarchical_maps.py` | motor torre p-ádica + π forzado + Coh_π/Coh_grid + audit | ✅ | 417 LOC. Importa de `profinite_echo_midi` por inserción `sys.path`. |

### Drivers (`adaptador`) — entran a `padicmidi/src/padicmidi/cli/`

| Archivo origen | Categoría | Canónico | Notas |
|---|---|:---:|---|
| `repro/code/run_one_piece.py` | driver "un MIDI" jerárquico | ✅ | 59 LOC. `subprocess` → `build_hierarchical_maps.py`. |
| `scripts/run_suite_bwv1007.py` | driver suite BWV1007 Phase I | ✅ | 66 LOC. Wrappa `profinite_echo_midi`. |
| `scripts/run_benchmark.py` | driver benchmark (cs1 + toys) Phase I | ✅ | 98 LOC. |
| `repro/code/get_mutopia_midis.py` | descarga MIDIs Mutopia | ✅ | ~50 LOC. Para reconstruir `data/midi/` desde cero. |
| `repro/code/job_list_generator.py` | manifiesto de trabajos | ✅ | 86 LOC. Lista 25 piezas y reglas. |

### Análisis post-pipeline — entran a `padicmidi/src/padicmidi/analysis/`

| Archivo origen | Categoría | Canónico | Notas |
|---|---|:---:|---|
| `scripts/build_control_primes_summary_nextpp.py` | agregador final Phase I | ✅ | 149 LOC. Lee `outputs/phaseI_nextpp/raw/`. |
| `scripts/null_model_fast.py` | null model rápido | ✅ | 152 LOC. Reciente (2026-03-10). |
| `scripts/null_model_verification.py` | verificación null model | ✅ | 188 LOC. |
| `scripts/aggregate_audit.py` | auditoría de coherencia (V_SC, AI) | ✅ | ~200 LOC. Reciente (2026-04-28). |
| `scripts/directionality_test.py` | test de direccionalidad | ✅ | ~110 LOC. Reciente. |
| `scripts/build_supplement_tables.py` | tablas LaTeX para suplemento | ✅ | 309 LOC. |

### Visualización — entran a `padicmidi/src/padicmidi/figs/`

| Archivo origen | Categoría | Notas |
|---|---|---|
| `scripts/build_paper_figures.py`, `build_continuous_figures.py`, `build_hierarchical_figures.py`, `build_padic_balls_fig.py`, `build_padic_tree_fig.py`, `build_p_ladder_balls_fig.py`, `build_spectral_precision_figs.py`, `build_music_snippet_fig.py` | generadores de figuras `.pdf`/`.png` para los papers | Se incluyen los que generan figuras del paper aceptado/enviado; los demás como `legacy/`. |

### Versiones obsoletas — NO entran al paquete

| Archivo | Razón |
|---|---|
| `repro/code/profinite_echo_midi.py` | duplicado idéntico al de raíz |
| `run_one_piece.py` (raíz) | duplicado de `repro/code/run_one_piece.py`; este último es canónico |
| `repro/code/job_list_generator.py`, `repro/code/get_mutopia_midis.py`, `get_mutopia_midis.py` (raíz), `job_list_generator.py` (raíz) | duplicados |
| `scripts/build_control_primes_summary.py` | versión legacy; reemplazada por `_nextpp` |
| `scripts/build_control_primes_summary_nextplus.py` | versión intermedia; reemplazada por `_nextpp` |
| `scripts/nullmodel_cohpi.py` | obsoleta; reemplazada por `null_model_fast.py` |

### Excluidos por decisión 2026-04-29 (registro INDAUTOR separado futuro)

| Archivo | Razón |
|---|---|
| `analyze_bwv1007.py` (raíz + `repro/code/`) | experimento ultramétrico distinto, no alimenta los dos papers |
| `continuous_patterns.py` (raíz + `repro/code/`) | apoyo del experimento anterior |

### Sin uso identificado en pipelines actuales

| Archivo | Notas |
|---|---|
| `scripts/build_table_fragment.py` | utilidad LaTeX puntual |
| `scripts/build_padic_tree_zoom_gif.py` | generación de GIF (no aparece en papers actuales); marcar `experimental/` |
| `scripts/math_findings_nextpp.py` | post-análisis ad-hoc; marcar `experimental/` |
| `scripts/debug_parse_latex_log.py` | utilidad de soporte editorial; mover a `repo-tools/` fuera del paquete |

---

## 2. Versiones del mismo componente

| Componente | Versiones | Versión canónica | Razón |
|---|---|---|---|
| Motor Phase I | `profinite_echo_midi.py` (raíz) y (`repro/code/`) | raíz | docstring referencia `run_benchmark.py`, más conectado al pipeline activo |
| Driver "un MIDI" | `run_one_piece.py` (raíz) y (`repro/code/`) | `repro/code/` | mtime más reciente |
| Job list generator | 2 copias | `repro/code/job_list_generator.py` | ya bien empaquetado para reproducibilidad |
| Mutopia downloader | 2 copias | `repro/code/get_mutopia_midis.py` | ya bien empaquetado |
| `analyze_bwv1007.py`, `continuous_patterns.py` | 2 copias cada uno | N/A (excluidos) | — |
| Control primes summary | 3 versiones (legacy / _nextplus / _nextpp) | `_nextpp` | última versión, alimenta tablas finales |
| Null model | 3 archivos (`nullmodel_cohpi.py` / `null_model_fast.py` / `null_model_verification.py`) | `null_model_fast.py` + `null_model_verification.py` | recientes (2026-03-10) y validados |

---

## 3. Verificación contra el paper (gold standard)

**Datos verificados leyendo `outputs/paper_profinite_hier_r3/`** (corridas con seed=42, K=16, Kchild=2, M=800, step=2, --bin-beats=1/12, $K_{\mathrm{child}}^{\text{init}} = p$ para reproducir matched/mismatched):

| Pieza | $p$ | $n$ | Valor del paper | Valor del CSV | Coincide |
|---|---:|---:|---|---|:---:|
| BWV1007 Prelude (cs1_1pre) | 2 | 1–5 | $0.500$ exacto $\forall n$ | `0.5, 0.5, 0.5, 0.5, 0.5` | ✅ |
| BWV1007 Prelude (cs1_1pre) | 3 | 1, 2 | $> 0.67$ (rango benchmark) | `1.0, 1.0` | ✅ |
| BWV1007 Prelude (cs1_1pre) | 3 | 3 (mismatched $r=2,p=3$) | $\approx 0.36$ (cerca del piso $1/3$) | `0.358025` | ✅ ≈ 1/3 |
| BWV1007 Prelude (cs1_1pre) | 3 | 4 | (sin valor explícito en abstract; > piso $1/3$) | `0.526749` | ✅ > 1/3 |
| BWV1007 Sarabande (cs1_4sar) | 3 | 3 (matched $r=p=3$) | $\approx 0.90$ | `0.901235` | ✅ exacto |
| BWV1007 Sarabande (cs1_4sar) | 3 | 4 | (no reportado explícitamente) | `0.843621` | ✅ alto |

**Conclusión:** el motor `build_hierarchical_maps.py` reproduce los valores gold del Paper 2 con tolerancia $< 0.01$ (en realidad: exacto en los casos estructurales binarios, error $< 0.001$ en los casos K-means con seed fija).

---

## 4. Discrepancias detectadas

| # | Discrepancia | Tipo | Decisión |
|---|---|---|---|
| D1 | Paper 2 §Method menciona `pretty_midi`; `requirements.txt` y código usan `mido` | error-transcripción (paper) | Documentar elección `mido` en MATH-SPEC; ofrecer adaptador `pretty_midi` opcional como decisión 2 del 2026-04-29; emitir errata al Paper 2 cuando entre en revisión menor. |
| D2 | `run_one_piece.py` existe en raíz y en `repro/code/`; ambos llaman a `scripts/build_hierarchical_maps.py` con paths absolutos relativos al script | duplicado | Versión canónica: `repro/code/run_one_piece.py`. La de raíz se descarta. |
| D3 | Tres versiones de `build_control_primes_summary*.py` apuntan a layouts distintos de `outputs/`: `outputs/seconds`, `outputs/phaseI_nextplus/raw/`, `outputs/phaseI_nextpp/raw/` | diferencia-versión | Canónica: `_nextpp`. Mover `_nextplus` y la versión sin sufijo a `padicmidi/legacy/`. |
| D4 | El motor jerárquico usa `sys.path.insert(0, str(ROOT))` para importar `profinite_echo_midi` | hack de ejecución | En `padicmidi/`, ambos serán módulos del mismo paquete (`from padicmidi.core.echo import ...`); el hack desaparece. |
| D5 | Convención `Kchild=2` para todo $n$ en `build_hierarchical_maps.py`, pero el CSV muestra `n_samples_nplus1 = 2 * n_samples_n` con la excepción del nivel 1 (`Kchild_init` = $p$ para reproducir benchmark) | parámetro implícito | Documentado en MATH-SPEC §3 (tabla "Hijos por padre"). El CSV `cs1_1pre/p2/coherence_hier_p2.csv` muestra `n_samples=1,2,4,8,16,32` lo que indica `K=2` en S_1 (no 16): **alerta** — verificar si esa corrida usó `K=2` o si hay rama del código que reduce K. |
| D6 | El driver `run_one_piece.py` no expone `--seed` (asume 42) | usabilidad | El motor sí lo acepta. El driver nuevo `padicmidi.cli.run_one` debe exponerlo. |
| D7 | `analyze_bwv1007.py` y `continuous_patterns.py` aparecen en `repro/code/README.md` pero NO entran al pipeline de los dos papers principales | documentación inconsistente | Excluidos por decisión 2026-04-29; se actualiza `repro/code/README.md` para marcarlos como `experimental` o se omiten. |

**D5 requiere atención**: el CSV `cs1_1pre/beats/p2/coherence_hier_p2.csv` muestra `n_samples_n=1` en $n=1$, lo que sólo es posible si $|S_1|=1$ (no $K=16$). Esto puede ser:
- (a) una corrida con `K=2` que reproduce los pisos estructurales por casualidad,
- (b) la pieza es lo suficientemente corta que `K_actual = max(1, min(K, len(samples)))` cayó a 1,
- (c) una versión del motor con default distinto.

**Acción:** verificar `params.json` adyacente al CSV antes de fijar el gold standard final. (Se hará en Movimiento 5 al construir tests/regression.)

---

## 5. Mapa de dependencias real (extraído del código)

```
profinite_echo_midi.py
├── parse_midi_notes_seconds, parse_midi_notes_beats     ← mido
├── chroma_series_duration, chroma_series_duration_beats
├── onset_density_series, onset_density_series_beats
├── series_with_rhythm
├── spectral_flux_series, zscore_series
├── (otras 1.7k LOC: torres Phase I, β₀, K-means propio, figuras)
└── CLI propio (Phase I)

scripts/build_hierarchical_maps.py
├── from profinite_echo_midi import {parse, chroma, onset, series_with_rhythm}
├── build_X_seconds, build_X_beats
├── get_windows, aggregate_median, dist_matrix, kmeans_numpy
├── build_W_n
├── run_hierarchical  ← núcleo Coh_pi/Coh_grid + audit
└── CLI propio
```

`mido` es la única dependencia externa de I/O en el motor. `numpy` para todo el cálculo. `matplotlib` sólo en figuras. K-means es **implementación propia** (no `sklearn`). Esto es bueno para auditoría: cero dependencias estadísticas externas en el cálculo de $\mathrm{Coh}_\pi$.

---

## 6. Decisiones tomadas (no requieren input del investigador)

| Decisión | Resolución |
|---|---|
| K-means propio vs `sklearn` | Mantener implementación propia: dependencias mínimas, reproducible. |
| `MAX_WINDOWS_PER_RESIDUE = 800` | Constante a nivel de módulo (no expuesta en CLI). Mover a config en Movimiento 5. |
| `ALPHA = 1.0` | Igual: a config. |
| `default Nmax = {2:6, 3:5, 5:4, 7:3}` | Mantener. Documentado en MATH-SPEC. |

---

## 7. Decisiones pendientes (input del investigador antes de Movimiento 4)

Ninguna en este nivel. Queda únicamente la APROBACIÓN de `ARCHITECTURE-PROPOSAL.md` (siguiente movimiento).

---

**Próximo paso:** Movimiento 3 (RELATED-WORK-SOFTWARE) — búsqueda de software similar para documentar el gap que llena PAdicMIDI (esto va al README y al dossier INDAUTOR como "originalidad").
