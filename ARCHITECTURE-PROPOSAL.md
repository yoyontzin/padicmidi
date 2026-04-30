# Propuesta de arquitectura — PAdicMIDI

**Skill:** `research-software-builder` (Movimiento 4)
**Fecha:** 2026-04-29
**Estado:** **PENDIENTE DE APROBACIÓN POR EL INVESTIGADOR**
**Modo:** B (refactorización ligera con outputs equivalentes garantizados)

> Antes de implementar nada en `src/`, el skill exige presentar esta propuesta y esperar luz verde explícita.

---

## 1. Estructura propuesta de la carpeta `padicmidi/`

```
padicmidi/                                  ← raíz del producto registrable
├── README.md                               ← descripción + quickstart + DOI/INDAUTOR
├── LICENSE                                 ← MIT (a confirmar) para code; CC-BY 4.0 para data
├── CITATION.cff                            ← metadatos de citación (Zenodo-ready)
├── CHANGELOG.md
├── AUTHORS.md
├── CONTRIBUTION-STATEMENT.md               ← obligatorio para INDAUTOR
├── PROJECT-STATE.md                        ← (ya existe) archivo vivo
├── PRODUCT-DECISION.md                     ← (ya existe) decisión de producto
├── RECONNAISSANCE-REPORT.md                ← (ya existe) inventario
├── MATH-SPEC.md                            ← (ya existe) especificación matemática
├── CODE-AUDIT.md                           ← (ya existe) auditoría de código
├── RELATED-WORK-SOFTWARE.md                ← (ya existe) gap y posicionamiento
├── ARCHITECTURE-PROPOSAL.md                ← (este archivo)
├── REPRODUCIBILITY.md                      ← Movimiento 6
├── pyproject.toml                          ← packaging futuro (rangos)
├── requirements-pinned.txt                 ← reproducción exacta (Python 3.13.3)
├── VERSION.md                              ← versión congelada + checksums
│
├── src/
│   └── padicmidi/                          ← paquete Python instalable
│       ├── __init__.py                     ← `__version__`, `__author__`, exporta API pública
│       ├── core/
│       │   ├── __init__.py
│       │   ├── echo.py                     ← copia limpiada de profinite_echo_midi.py (motor Phase I)
│       │   ├── hierarchical.py             ← copia limpiada de build_hierarchical_maps.py (Coh_π)
│       │   └── config.py                   ← constantes (ALPHA, MAX_WINDOWS_PER_RESIDUE, defaults Nmax)
│       ├── io/
│       │   ├── __init__.py
│       │   ├── midi_mido.py                ← adaptador MIDI usando mido (default)
│       │   └── midi_pretty.py              ← adaptador MIDI usando pretty_midi (opcional)
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── coherence.py                ← Coh_π, Coh_grid (re-export desde core.hierarchical)
│       │   ├── null_model.py               ← null_model_fast.py + null_model_verification.py
│       │   ├── audit.py                    ← aggregate_audit.py
│       │   ├── aggregate.py                ← build_control_primes_summary_nextpp.py
│       │   └── directionality.py           ← directionality_test.py
│       ├── figs/                           ← generadores de figuras
│       │   ├── __init__.py
│       │   ├── hierarchical_figs.py
│       │   ├── padic_balls.py
│       │   ├── padic_tree.py
│       │   ├── ladder_balls.py
│       │   └── spectral_precision.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── run_one.py                  ← driver "un MIDI" (entry point: `padicmidi-run-one`)
│       │   ├── run_suite.py                ← driver suite (entry point: `padicmidi-run-suite`)
│       │   ├── benchmark.py                ← driver benchmark
│       │   ├── job_list.py                 ← generador de manifiestos
│       │   └── mutopia.py                  ← descarga MIDIs Mutopia
│       └── legacy/                         ← scripts mantenidos por compatibilidad
│           ├── __init__.py
│           └── control_primes_summary_legacy.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── smoke/
│   │   └── test_imports.py                 ← `from padicmidi import core; assert core.echo`
│   ├── unit/
│   │   ├── test_chroma.py                  ← parsing → chroma series invariantes
│   │   ├── test_residues.py                ← W_n agregación por residuo
│   │   ├── test_kmeans.py                  ← K-means propio: convergencia, semilla
│   │   └── test_distance.py                ← d(W,W') simétrica, no-negativa, ceros en diagonal
│   ├── regression/
│   │   ├── test_bwv1007_p2_csv.py          ← CSV byte-equivalente al gold standard
│   │   └── test_bwv1007_p3_csv.py
│   └── paper_values/
│       ├── test_floor_p2_bwv1007.py        ← Coh_π(2,n) = 0.500 exacto ∀n
│       ├── test_sarabande_p3_n3.py         ← Coh_π(3,3) ≈ 0.901
│       ├── test_prelude_p3_mismatched.py   ← Coh_π(3,3) ≈ 0.358
│       └── test_null_model_pvals.py        ← p-valores Sarabande
│
├── examples/
│   ├── 01_quickstart.py                    ← análisis de un MIDI en 10 líneas
│   ├── 02_suite_bach.py                    ← reproducir suite BWV1007
│   ├── 03_compare_primes.py                ← Coh_π para p=2,3,5,7
│   └── 04_polyphonic_diagnostic.py         ← BWV1049 vs BWV1007 (textura)
│
├── data/
│   ├── README.md                           ← provenance + licencias por archivo
│   └── midi/
│       ├── bwv1007-1.mid …  bwv1007-6.mid  (Mutopia, CC-BY 4.0)
│       ├── bwv1008-1.mid …  bwv1008-6.mid  (Mutopia, CC-BY 4.0)
│       ├── cellosuite3-1.mid … 5.mid       (Mutopia, CC-BY-SA 3.0)
│       ├── cs1-1pre.mid … 6gig.mid         (Dave's 1997, PD-US)
│       ├── bwv1007_prelude.mid             (autor RPB, CC0)
│       ├── toy_binary.mid                  (autor RPB, CC0)
│       ├── toy_ternary.mid                 (autor RPB, CC0)
│       └── external/                       ← Bach polifónico (incluido con licencia auditada)
│           ├── README.md                   ← licencia archivo por archivo
│           ├── bwv1049_mov1.mid … 3.mid    ← (verificar fuente)
│           ├── bwv1050_mov1.mid … 3.mid    ← (verificar fuente)
│           ├── bwv1079_crab.mid            ← (verificar fuente)
│           └── goldberg_aria.mid           ← (verificar fuente)
│
├── results/
│   └── verified/
│       ├── CHECKSUMS.txt                   ← SHA-256 de cada CSV/figura del gold
│       ├── bwv1007_prelude/p{2,3,5,7}/*.csv
│       ├── cs1_4sar/p{2,3}/*.csv
│       ├── SUMMARY_TABLE.csv               ← (copia desde repro/results/)
│       ├── audit_table.csv
│       └── REPORTS/
│           ├── SUMMARY_REPORT.txt
│           └── NULLMODEL_REPORT.txt
│
├── docs/
│   ├── MANUAL-USUARIO.md                   ← cómo instalar, usar el applet, correr el CLI
│   ├── MANUAL-TECNICO.md                   ← arquitectura interna, MATH-SPEC resumido, mapas de módulos
│   ├── API.md                              ← referencia de funciones públicas
│   └── EXAMPLES.md                         ← walk-through de los 4 ejemplos
│
├── scripts/
│   ├── reproduce.sh                        ← reproduce ambos papers en un comando
│   ├── validate.sh                         ← corre tests + verifica checksums
│   ├── make_indautor_dossier.sh            ← compila el dossier INDAUTOR (PDFs)
│   └── snapshot_version.sh                 ← v1.0.0: tag, checksums, ZIP fuente
│
├── web-demo/
│   ├── applet.html                         ← UN ARCHIVO autocontenido offline
│   ├── README.md                           ← cómo abrirlo, qué hace
│   └── assets/                             ← (vacío — todo va embebido en applet.html)
│
└── indautor/                               ← dossier para registro RPDA-03
    ├── descripcion-funcional.md            ← qué hace, autores, originalidad
    ├── manual-usuario.md                   ← copia del docs/MANUAL-USUARIO.md
    ├── manual-tecnico.md                   ← copia del docs/MANUAL-TECNICO.md
    ├── codigo-fuente/                      ← copia íntegra de src/padicmidi/ (impreso)
    ├── evidencia-corridas/
    │   ├── 01_quickstart_run.log
    │   ├── 02_bwv1007_p2_screenshot.png
    │   ├── 03_applet_screenshot.png
    │   └── 04_test_suite_output.txt
    ├── manifiesto-archivos.md              ← lista SHA-256 de TODO el dossier
    ├── VERSION-REGISTRADA.md               ← v1.0.0, hash del ZIP final
    ├── formato-RPDA-03-prefilled.pdf       ← formato pre-llenado listo para imprimir/firmar
    └── carta-titularidad.md                ← (opcional) documento adicional
```

---

## 2. Justificaciones de diseño

### 2.1 Por qué `src/padicmidi/` y no `padicmidi/` directo

Convención `src/` layout (Hynek Schlawack, ya estándar en Python moderno) — evita imports accidentales del directorio de trabajo durante tests. Más fácil garantizar que tests usan la versión instalada, no la de desarrollo.

### 2.2 Cuatro niveles de tests

Siguiendo el skill (Movimiento 5):
1. **smoke** — el módulo importa.
2. **unit** — funciones individuales dan resultados esperados sobre toys.
3. **regression** — outputs CSV byte-equivalentes a gold guardado.
4. **paper_values** — números reportados en los dos papers se reproducen.

### 2.3 Adaptadores MIDI duales (`mido` + `pretty_midi`)

Decisión 2026-04-29 (opción "both"). `io/midi_mido.py` es default y exclusivo para reproducir el gold standard. `io/midi_pretty.py` se ofrece para alinear con el §Method del Paper 2; sus tests aceptan tolerancia $\pm 0.01$ porque convenciones de quantización pueden diferir.

### 2.4 `experimental/` NO se incluye

Decisión 2026-04-29: `analyze_bwv1007.py` y `continuous_patterns.py` quedan fuera de v1.0. Si en el futuro se registran como obra derivada, se hará en un dossier separado.

### 2.5 Applet HTML único autocontenido

Un solo archivo `web-demo/applet.html`:
- Vanilla JavaScript (sin librerías externas, sin CDN, sin localStorage).
- Parser MIDI mínimo en JS (tomado/portado de `mido` reduciendo a lo necesario).
- Implementación reducida del pipeline: chroma → ventanas → K-means → Coh_π. Sólo $p \in \{2,3\}$ para mantener tamaño pequeño.
- Modo demo: BWV1007-1 embebido como base64.
- Modo file: drag-and-drop o selector de archivo.
- Output: tabla HTML con `Coh_π`, gráfico SVG del árbol p-ádico (escrito a mano), descarga CSV.

Tamaño objetivo: **< 500 KB** para asegurar que abre instantáneamente offline.

### 2.6 `data/midi/external/` con licencia auditada

Decisión 2026-04-29 (opción "include_with_audit"). Los MIDIs polifónicos Bach se incluyen *si* se puede auditar y citar fuente. Si la auditoría falla para algún archivo, se mueve a un script de descarga.

### 2.7 `results/verified/` con checksums

Garantiza que cualquier persona puede correr `bash scripts/reproduce.sh` y comparar bit-equivalentemente con los outputs originales, o ejecutar `scripts/validate.sh` para verificar sin re-correr el pipeline completo.

---

## 3. Política de versionado

- **v0.0.x** — durante construcción (este sprint).
- **v1.0.0** — versión que se registra en INDAUTOR. Tag git, checksums congelados, ZIP fuente.
- **v1.1.x** — fixes y mejoras menores; se actualizaría en CITATION.cff pero NO requiere nuevo INDAUTOR (Ley Federal del Derecho de Autor permite registrar versiones derivadas opcionalmente).
- **v2.0.0** — cambios algorítmicos que rompan el gold standard; SÍ requiere nuevo registro INDAUTOR si se quiere protección legal específica.

---

## 4. Política de licencias (a confirmar)

| Componente | Licencia propuesta |
|---|---|
| Código fuente `src/`, `tests/`, `scripts/`, `examples/`, `web-demo/` | **MIT** (permisiva, máxima difusión) |
| Documentación (`docs/`, READMEs) | **CC-BY 4.0** |
| Datos `data/midi/` | atribución por archivo (CC-BY, CC-BY-SA, PD-US, CC0) |
| Resultados `results/verified/` | **CC-BY 4.0** |
| Dossier `indautor/` | "Todos los derechos reservados" — material legal no se redistribuye |

**Importante:** licencia MIT es **independiente** del registro INDAUTOR. Se puede registrar la titularidad autoral en INDAUTOR y simultáneamente liberar bajo MIT. La titularidad protege la autoría aunque el código sea libre. Confirmar.

---

## 5. Roadmap de implementación (Movimientos 5–8C)

| Movimiento | Tarea | Estimación |
|---|---|---|
| 5.1 | Crear `src/padicmidi/` con estructura vacía y `__init__.py` | 5 min |
| 5.2 | Copiar `profinite_echo_midi.py` → `core/echo.py`; agregar `from padicmidi.core.echo import ...` shim de compatibilidad | 15 min |
| 5.3 | Copiar `build_hierarchical_maps.py` → `core/hierarchical.py`; reemplazar `sys.path.insert` por import limpio | 15 min |
| 5.4 | Crear adaptador `io/midi_mido.py` (re-export de funciones de parsing) | 10 min |
| 5.5 | Crear adaptador `io/midi_pretty.py` (alternativo) | 30 min |
| 5.6 | Mover scripts de `analysis/` y `figs/` con imports limpios | 30 min |
| 5.7 | Crear CLI con `argparse` y entry-points en `pyproject.toml` | 30 min |
| 5.8 | Crear `tests/smoke/` y `tests/unit/` (mínimo viable) | 1 h |
| 5.9 | Crear `tests/regression/` con CSV gold copiados | 30 min |
| 5.10 | Crear `tests/paper_values/` con valores del Paper 2 | 30 min |
| 5.11 | Construir `web-demo/applet.html` (parser MIDI JS + pipeline reducido) | 4–6 h |
| 6.1 | `scripts/reproduce.sh` y `REPRODUCIBILITY.md` | 30 min |
| 6.2 | Generar `results/verified/CHECKSUMS.txt` | 5 min |
| 7.x | Documentación completa (README, manuales, CITATION.cff, AUTHORS, CONTRIBUTION-STATEMENT) | 2 h |
| 8A | Tag `v1.0.0`, checksums, ZIP fuente | 15 min |
| 8C | Dossier INDAUTOR completo (descripción, manuales, código impreso, manifiesto, evidencia, RPDA-03 pre-llenado) | 2 h |

**Total estimado:** ~12–15 horas de trabajo focalizado.

---

## 6. Decisión bloqueante (input requerido del investigador)

Para avanzar al Movimiento 5, necesito tu OK explícito sobre:

1. **¿La estructura de carpetas propuesta arriba es correcta?** Si quieres mover algo, ahora es el momento.
2. **¿Licencia MIT para el código?** (Compatible con el registro INDAUTOR; máxima difusión.)
3. **¿`src/` layout o layout plano?** (Recomiendo `src/` por estándar moderno.)
4. **¿Implemento el applet HTML completo (4–6 h) o un MVP mínimo (1 h)?** (El completo es mejor para INDAUTOR; el mínimo es más rápido.)

Una vez que confirmes esto, paso al Movimiento 5 (implementación) sin más preguntas y produzco código + tests + applet en bloques continuos.
