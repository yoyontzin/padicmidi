# Manual técnico — PAdicMIDI

**Versión:** 1.0.0 · **Autor:** Jesús Rogelio Pérez Buendía — *firma como* J. Rogelio Pérez-Buendía (CIMAT–Mérida).
**ORCID:** [0000-0002-7739-4779](https://orcid.org/0000-0002-7739-4779) · **Web:** [www.cimat.mx/~rogelio.perez](https://www.cimat.mx/~rogelio.perez)

Este manual describe la arquitectura interna del paquete, las decisiones de
diseño, las convenciones matemáticas y el flujo de datos. Para una guía de
uso, consulte [`MANUAL-USUARIO.md`](MANUAL-USUARIO.md). Para la especificación
matemática completa, consulte [`../MATH-SPEC.md`](../MATH-SPEC.md).

---

## 1. Vista panorámica

PAdicMIDI implementa el marco **ATDA** (Arithmetic-Topological Data Analysis)
sobre música simbólica. El núcleo del paquete es una pequeña biblioteca
numérica que (i) parsea un MIDI a una serie multivariada beat- o
seconds-síncrona, (ii) construye una torre p-ádica de espacios de patrones, y
(iii) calcula invariantes de coherencia.

El paquete tiene seis subpaquetes:

| Subpaquete | Propósito |
|---|---|
| `padicmidi.core` | motor numérico (parsing, chroma, K-means, torre, $\pi$, $\mathrm{Coh}_\pi$) |
| `padicmidi.io` | adaptadores MIDI (`mido` default, `pretty_midi` opcional) |
| `padicmidi.analysis` | post-procesos (null model, audit, agregación, direccionalidad) |
| `padicmidi.figs` | generadores de figuras (PDF/PNG) para los artículos |
| `padicmidi.cli` | entry points de línea de comandos |
| `padicmidi.legacy` | scripts mantenidos por compatibilidad |

---

## 2. Mapa de flujo de datos

```
   MIDI bytes ─► padicmidi.io.midi_mido.parse_midi_notes_{seconds,beats}
                                  │
                                  ▼
   eventos (t_on,t_off,pitch,vel)
                                  │
                                  ▼
   padicmidi.core.echo.{chroma_series_duration,onset_density_series}
                                  │
                                  ▼
   H ∈ R^(T×12)   a ∈ R^T
                                  │
                  ┌───────────────┴───────────────┐
                  │  series_with_rhythm(H, a)     │
                  ▼                               ▼
                                X ∈ R^(T×13)
                                  │
                                  ▼
   padicmidi.core.hierarchical.build_W_n  ─► W_n[a] (mediana por residuo)
                                  │
                                  ▼
   padicmidi.core.hierarchical.run_hierarchical
   ├── K-means inicial sobre ventanas p^1
   ├── Para cada n→n+1: parent forzado por truncamiento + K-means por padre
   ├── Cuantizador f_n: residuo → prototipo
   ├── Sistema inverso π_{n+1,n}
   └── Coh_pi(p,n) = #{b : π(f_{n+1}(b)) = f_n(b mod p^n)} / p^{n+1}
                                  │
                                  ▼
   CSVs: prototypes / pi / f / coherence_hier / audit
```

---

## 3. Convenciones críticas

Todas las convenciones están documentadas en
[`../MATH-SPEC.md`](../MATH-SPEC.md) §3. Las más importantes:

| Convención | Valor |
|---|---|
| Indexación de residuos | base 0: $a \in \{0,\dots,p^n-1\}$ |
| Bin beats default | $\Delta_b = 1/12 \approx 0.0833$ |
| Bin seconds default | $\Delta_s = 0.05$ s |
| Distancia entre ventanas | $L^2$ promediada en tiempo: $d(W,W') = \sqrt{(1/N)\sum_i \|W_i-W'_i\|_2^2}$ |
| Agregación por residuo | mediana componente-a-componente |
| K-means | implementación propia, semilla fija (default 42), max 30 iteraciones |
| Hijos por padre | $K_{\mathrm{child}} = 2$ por default |
| Tamaño de muestra K-means | $M = 800$ ventanas equispaciadas |
| Step de ventaneo | $s = 2$ |
| Defaults $N_{\max}$ | $\{2 \to 6, 3 \to 5, 5 \to 4, 7 \to 3\}$ (memoria-aware) |

---

## 4. Funciones públicas principales

### `padicmidi.run_hierarchical_from_midi(midi_path, p, axis="beats", nmax=None, ...)`

Entry point de alto nivel. Devuelve dict con `prototypes_n`, `f_n`,
`pi_maps`, `coherence`, `audit`.

### `padicmidi.core.echo.parse_midi_notes_{seconds,beats}(path)`

Devuelve lista de tuplas `(t_on, t_off, pitch, velocity)`.

### `padicmidi.core.echo.chroma_series_duration[_beats](events, bin_size)`

Devuelve matriz $T \times 12$ con cromograma duración-pesado y
$L^1$-normalizado por fila.

### `padicmidi.core.echo.onset_density_series[_beats](events, bin_size)`

Devuelve vector de densidad de onsets por bin.

### `padicmidi.core.echo.series_with_rhythm(H, a, alpha=1.0)`

Concatenación $X = [H \mid \alpha\, a] \in \mathbb{R}^{T \times 13}$.

### `padicmidi.core.hierarchical.build_W_n(X, p, n_max, step)`

Construye la familia $\{W_{p,n}(a)\}$ por mediana sobre residuos.

### `padicmidi.core.hierarchical.run_hierarchical(X, p, Nmax, step, K, Kchild, M, rng)`

Pipeline completo. Devuelve `(prototypes_n, f_n, pi_maps, coherence_rows, audit_rows)`.

---

## 5. Tests

| Nivel | Cantidad | Cubre |
|---|---:|---|
| `tests/smoke/` | 7 | el paquete y todos los submódulos importan |
| `tests/unit/` | 18 | chroma, residuos, distancia, K-means determinista |
| `tests/regression/` | (placeholder v1.1) | CSVs byte-equivalentes al gold |
| `tests/paper_values/` | 3 | valores reportados en los artículos |

Total: **28 tests pasando** (Python 3.13.3, macOS arm64, 2026-04-29).

Ejecutar: `pytest tests/`.

---

## 6. Empaquetado y distribución

| Archivo | Propósito |
|---|---|
| `pyproject.toml` | metadatos PEP-621, dependencias con rangos, entry points |
| `requirements-pinned.txt` | versiones exactas reproducibles |
| `LICENSE` | MIT |
| `CITATION.cff` | metadatos de citación Zenodo-ready |
| `CHANGELOG.md` | cambios entre versiones |
| `AUTHORS.md` + `CONTRIBUTION-STATEMENT.md` | autoría y atribución (obligatorio para INDAUTOR) |

Build:

```bash
python -m build       # genera dist/padicmidi-1.0.0-py3-none-any.whl + sdist
```

---

## 7. Arquitectura del applet HTML

`web-demo/applet.html` es un único archivo de ~34 KB que reproduce el pipeline
en JavaScript vanilla:

| Componente | Implementación |
|---|---|
| Parser MIDI | `parseMidi(arrayBuffer)` — formatos 0/1, tempo map, multi-track |
| Chroma + onset | `buildChromaBeats(events, binBeats)` |
| Distancia $L^2$ | `dist(a, b)` |
| K-means | `kmeans(samples, K, rng)` con Mulberry32 (seed reproducible) |
| Motor jerárquico | `runHierarchical(X, p, nmax, K, Kchild, M, step, seed)` |
| UI | drag-and-drop + selector de archivo + tabla + SVG |

El applet **no envía datos a ningún servidor**. No usa CDNs, ni cookies, ni
localStorage, ni telemetría.

---

## 8. Limitaciones conocidas

- **Polifonía**: el motor agrega polifonía implícitamente vía la representación
  cromática duración-pesada; análisis voice-by-voice requiere preprocesamiento.
- **Tamaños grandes**: $p=5$, $N_{\max}=4$ requiere ~5 GiB.
- **Reproducibilidad cross-platform**: la bit-equivalencia se garantiza
  únicamente en macOS arm64 con `requirements-pinned.txt`. En otras
  plataformas puede haber drift en el 5°–6° decimal.
- **Eje seconds en applet**: no implementado; el applet usa eje beats.
- **Primos en applet**: sólo $p \in \{2, 3\}$.

---

## 9. Cómo extender

### 9.1 Agregar un nuevo primo

`padicmidi.core.config.SUPPORTED_PRIMES` define los primos válidos. Para
agregar un nuevo primo, actualice esa tupla y agregue una entrada en
`_DEFAULT_NMAX_BY_PRIME` con un valor memory-aware.

### 9.2 Agregar un adaptador MIDI alternativo

Cree `padicmidi/io/midi_<backend>.py` exponiendo
`parse_midi_notes_seconds(path)` y `parse_midi_notes_beats(path)` con la
misma firma del default. Agregue un test en `tests/unit/test_io_<backend>.py`
que verifique que produce los mismos eventos sobre un MIDI conocido.

### 9.3 Agregar una nueva métrica de coherencia

Implemente la función en `padicmidi/analysis/<su_metrica>.py` reusando
`build_W_n`, `kmeans_numpy` y `dist_matrix`. Agregue tests en
`tests/unit/`. Para que aparezca en el CSV principal, modifique
`padicmidi.core.hierarchical.run_hierarchical` y actualice el contrato de
salida documentado en `MATH-SPEC.md`.

---

## 10. Trazabilidad

Cada commit del repositorio es trazable a través de `git log`. La versión
v1.0.0 está congelada por `scripts/snapshot_version.sh`, que produce
`VERSION.md` y `results/verified/CHECKSUMS.txt` con hashes SHA-256 de cada
archivo del paquete. El dossier completo para INDAUTOR se genera con
`scripts/make_indautor_dossier.sh`.
