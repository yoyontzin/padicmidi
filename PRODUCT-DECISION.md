# Decisión de producto — PAdicMIDI

**Fecha:** 2026-04-29
**Skill aplicado:** `research-software-builder` (Movimiento −1)
**Decisor:** J. Rogelio Pérez-Buendía (CIMAT–Mérida)

---

## Tipo de producto seleccionado

- [x] **Software registrable (INDAUTOR)** — producto principal
- [x] **Applet pedagógico HTML** — un único applet universal incluido como entregable del software
- [ ] Paquete científico Python (pip) — **fuera de alcance en esta iteración**
- [ ] Repositorio citable Zenodo — **diferido a v1.1.0** (la base ya existe en `repro/`)
- [ ] Demo web con servidor — descartado (el applet HTML offline cubre el caso)

**Producto único:** un dossier de software (código fuente + applet HTML autocontenido + manual + descripción funcional) listo para someterse al Instituto Nacional del Derecho de Autor (INDAUTOR, México) usando el formato **RPDA-03** (Solicitud de Registro de Programa de Computación).

---

## Nombre oficial

**PAdicMIDI** — *A Python Toolkit for Hierarchical, Ultrametric, and p-adic Analysis of Symbolic Music Data*

(Esta cadena es la que se inscribirá en INDAUTOR como título de la obra y la que aparece en `CITATION.cff`, `README.md` y portada del manual.)

---

## Modo de intervención sobre el código existente

**Modo B — Refactorización ligera (autorizado).**

- Se permite separar funciones, eliminar duplicación entre `raíz/` y `repro/code/`, y reorganizar en `padicmidi/src/`.
- Se exige que **outputs numéricos** (CSVs de coherencia, valores `Coh_π`, β₀) sean **bit-equivalentes** o equivalentes hasta tolerancia de punto flotante respecto a la versión actual.
- Tests de regresión obligatorios contra `outputs/paper_profinite_hier/bwv1007_prelude/beats/p2/coherence_by_level.csv` y similares.

---

## Justificación

1. **El triángulo está cerrado.** Los dos papers (JMM aplicado, Springer-Nature jerárquico) tienen valores numéricos verificados, el código existe y reproduce esos valores; falta sólo la capa de producto.
2. **INDAUTOR como prioridad legal.** Registro autoral rápido y barato (≈ MXN $313, RPDA-03), no exige distribución libre — protege la titularidad sin atarla a una licencia. Compatible con liberar después bajo MIT vía Zenodo.
3. **Un solo applet HTML autocontenido** es la forma más limpia de cumplir "automatizar el análisis de un MIDI" sin abrir el alcance a una webapp con servidor. Evita dependencias de red y es evidencia directa de la funcionalidad para el dossier.
4. **Modo B y no A** porque el código actual tiene duplicación documentada (`profinite_echo_midi.py` aparece en raíz y en `repro/code/`, idem `run_one_piece.py`, `analyze_bwv1007.py`, etc.). Para un dossier defendible conviene una versión canónica única, no doce copias.

---

## Qué SÍ se construirá en esta iteración

| Componente | Ubicación | Estado al final |
|---|---|---|
| `PRODUCT-DECISION.md` | `padicmidi/` | ✅ este archivo |
| `RECONNAISSANCE-REPORT.md` | `padicmidi/` | ✅ Movimiento 0 |
| `PROJECT-STATE.md` | `padicmidi/` | vivo, actualizado en cada sesión |
| `MATH-SPEC.md` | `padicmidi/` | Movimiento 1 |
| `CODE-AUDIT.md` | `padicmidi/` | Movimiento 2 |
| `RELATED-WORK-SOFTWARE.md` | `padicmidi/` | Movimiento 3 |
| `ARCHITECTURE-PROPOSAL.md` | `padicmidi/` | Movimiento 4 (esperar OK) |
| Código canónico `src/padicmidi/` | `padicmidi/src/` | Movimiento 5 |
| Tests `tests/` (smoke, unit, regression, paper_values) | `padicmidi/tests/` | Movimiento 5 |
| `applet.html` autocontenido | `padicmidi/web-demo/applet.html` | Movimiento 5 |
| `REPRODUCIBILITY.md` + `scripts/reproduce.sh` | `padicmidi/` | Movimiento 6 |
| `README.md`, `MANUAL-USUARIO.md`, `MANUAL-TECNICO.md`, `LICENSE`, `CITATION.cff`, `AUTHORS.md`, `CONTRIBUTION-STATEMENT.md`, `CHANGELOG.md` | `padicmidi/` | Movimiento 7 |
| Versión congelada `v1.0.0` + `CHECKSUMS-SHA256.txt` | `padicmidi/` | Movimiento 8A |
| Dossier INDAUTOR completo (`indautor/`) con descripción funcional, manual, código impreso, manifiesto, evidencia, formato RPDA-03 pre-llenado | `padicmidi/indautor/` | Movimiento 8C |

---

## Qué NO se construirá en esta iteración

- Empaquetado `pip install padicmidi` con `pyproject.toml` y publicación en PyPI.
- Subida a Zenodo y obtención de DOI permanente.
- Subida a Software Heritage.
- GUI nativa (PyQt6 / Tkinter).
- Versión web con servidor (Streamlit / FastAPI).
- Migración del motor a `pretty_midi` (se mantiene `mido` como en `requirements.txt`; ver discrepancia documentada en RECONNAISSANCE).
- Análisis de Mozart / Handel (queda como "in preparation" igual que en los papers).

Estos quedan agendados para versiones derivadas (v1.1.0+).

---

## Riesgos identificados

### Matemáticos
- **Discrepancia código vs paper en biblioteca MIDI:** el §Method del Paper 2 menciona `pretty_midi`; `requirements.txt` y el código usan `mido`. **Decisión pendiente:** mantener `mido` y corregir el paper en revisión menor, o documentar como elección de implementación equivalente. Será documentada en `MATH-SPEC.md` y `CODE-AUDIT.md`.
- **Tolerancia numérica de K-means:** el invariante `Coh_π(2,n)=0.500` exacto en BWV1007 es estructural (separación binaria), pero `Coh_π(3,n)` depende del clustering K-means con semilla. Tests deben fijar `seed=42` (ya documentado en `CLAUDE.md`).

### Técnicos
- **Doble montaje macOS** (`Paper CODA-/bwv1007/` vs `Paper CODA-\bwv1007/`): trabajaremos exclusivamente en el segundo (con backslash literal), donde están los archivos reales. El primero se ignora.
- **Outputs pesados** (`outputs/**` ≈ 5.3 GB) se EXCLUYEN del paquete; sólo entran los CSVs agregados.

### Legales
- **Datos de terceros:** `data/external_midis/` (Mozart, Handel) puede tener archivos sin licencia auditada por archivo. **Decisión:** no se incluyen MIDIs de terceros en `padicmidi/`; el paquete trae sólo `bwv1007_prelude.mid` (CC0 propio) más toys (CC0 propios). Resto se descarga vía script.
- **Materiales Mutopia:** ya licenciados CC-BY/CC-BY-SA, atribuidos en `repro/data/midi/README.md`. Se replicará la atribución en `padicmidi/data/`.
- **Titularidad CIMAT/SECIHTI:** registro a nombre de RPB autor único. Si CIMAT eventualmente reclama derechos patrimoniales por convenio interno, se hará una transmisión posterior (no bloquea esta iteración).

### Documentales
- **Versionado de scripts**: existen tres variantes de `build_control_primes_summary*.py` (legacy, `_nextplus`, `_nextpp`) que apuntan a layouts distintos de `outputs/`. Se elige `_nextpp` como canónico (es el más reciente y el que alimenta las tablas finales del Paper 1).

---

## Cronograma estimado (en sesiones de agente)

| Sesión | Movimientos | Entregables |
|---|---|---|
| Hoy (sesión actual) | −1, 0 | PRODUCT-DECISION, RECONNAISSANCE, PROJECT-STATE |
| Sesión 2 | 1, 2, 3 | MATH-SPEC, CODE-AUDIT, RELATED-WORK |
| Sesión 3 | 4 (esperar OK), 5 inicio | ARCHITECTURE-PROPOSAL aprobada; `src/` poblado |
| Sesión 4 | 5 fin, 6 | Tests pasando; applet.html funcional; REPRODUCIBILITY.md |
| Sesión 5 | 7 | Documentación completa |
| Sesión 6 | 8A, 8C | v1.0.0 congelada, dossier INDAUTOR listo para imprimir/firmar |

Total estimado: 6 sesiones de trabajo focalizado.

---

## Aprobaciones

- [x] Tipo de producto confirmado por el usuario (sesión 2026-04-29)
- [x] Nombre confirmado (`PAdicMIDI` + subtítulo)
- [x] Modo B autorizado
- [x] Autoría única RPB confirmada
- [x] Gold standard = ambos papers confirmado
- [ ] `ARCHITECTURE-PROPOSAL.md` (Movimiento 4) — pendiente
