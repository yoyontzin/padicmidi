# Estado del proyecto — PAdicMIDI

**Última actualización:** 2026-04-29

## Producto objetivo

Software registrable INDAUTOR (RPDA-03) + applet HTML autocontenido como entregable funcional.
Fases posteriores diferidas: paquete pip + Zenodo DOI + Software Heritage SWHID.

## Repositorios y registros

- GitHub: pendiente (post-INDAUTOR)
- Zenodo DOI: pendiente
- Software Heritage SWHID: pendiente
- INDAUTOR: en preparación de dossier (formato RPDA-03 pre-llenado pendiente)

## Artículos asociados

- **Paper 1 (aplicado, Phase I, β₀):** *Prime-power indexed multiscale graph diagnostics for symbolic temporal data: methodological exploration and delimitation via BWV 1007.* Autor: J. Rogelio Pérez-Buendía. Estado: listo para envío a *Journal of Mathematics and Music* (Taylor & Francis). Ruta local: `paper_applied/main.tex`.
- **Paper 2 (jerárquico, torre p-ádica, Coh_π):** *p-adic Towers for Symbolic Music: Hierarchical Coherence and Null Floors* (versión Springer Nature) / *Profinite hierarchical patterns and prime-indexed multiscale invariants in symbolic music* (versión CAM). Autor: J. Rogelio Pérez-Buendía. Estado: enviado / en flujo Springer. Ruta local: `Paper-ZpMusic-20250206/paper/main.tex`.

## Algoritmo central

PAdicMIDI implementa una **torre p-ádica de espacios de patrones** $D_{p,n}$ sobre series de tiempo beat-sincrónicas extraídas de un MIDI. Sobre la torre construye (i) grafos kNN por nivel y reporta β₀ (Paper 1), (ii) un sistema inverso $\pi_{n+1,n}: S_{n+1} \to S_n$ con padre forzado y reporta el invariante de coherencia $\mathrm{Coh}_\pi(p,n)$, comparándolo con el piso nulo arquitectónico $1/p$ bajo hipótesis de separación-hermana (SC) e inclusión-ancestro (AI) (Paper 2).

## Convención crítica

**Bins beat-sincrónicos $\Delta_b = 1/12$** (`--bin-beats 0.083333`); **residuos en base 0** ($i \bmod p^n$ con $i \in \{0,\dots,p^n-1\}$); **K-means con `seed=42` fija**; **biblioteca MIDI `mido`** (no `pretty_midi`, contrariamente a una mención en §Method del Paper 2 que será documentada).

## Valores verificados (gold standard)

| Instancia | Parámetros | Valor esperado | Fuente |
|---|---|---|---|
| BWV1007 Prelude (binario) | $p=2$, $n=1..5$, beats | $\mathrm{Coh}_\pi(2,n) = 0.500$ exacto | Paper 2 §5 |
| BWV1007 Prelude (ternario) | $p=3$, $n=1..3$, beats | $\mathrm{Coh}_\pi(3,n) \in [0.67, 0.999]$ | Paper 2 §5 |
| BWV1007 Sarabande matched | $p=3$, $r=p=3$, $n=3$ | $\approx 0.90$ | Paper 2 §5 |
| BWV1007 Prelude mismatched | $p=3$, $r=2$, $n=3$ | $\approx 0.90 \to 0.36$ al pasar a $r=3$ | Paper 2 §5 |
| Pisos nulos | $r=p$, denso | $1/p$: 0.500, 0.333, 0.200, 0.143 | Paper 2 prop:null_floor |
| Bach polifónico (corpus extendido) | $p=3$ | $\mathrm{Coh}_\pi(3,n) \in [0.34, 0.999]$ | Paper 2 abstract |
| Null model Sarabande | $p=3$, $n=2,3,4$ | $p$-val: 0.030, <0.01, 0.030 | Paper 2 §5 |
| Paper 1 control primes | global | $R_{\mathrm{ctrl}} \le 1$ | Paper 1 §5 |
| Paper 1 toys | binario / ternario | $|\Delta_{23}| \le 5$, β₀ → 1 a $n$ alto | Paper 1 §5 |

## Archivos canónicos

| Componente | Archivo origen | Destino futuro `padicmidi/src/padicmidi/` |
|---|---|---|
| Motor Phase I | `profinite_echo_midi.py` (raíz) | `core/echo.py` |
| Motor jerárquico + Coh_π | `scripts/build_hierarchical_maps.py` | `core/hierarchical.py` |
| Driver de un MIDI | `repro/code/run_one_piece.py` | `cli/run_one.py` |
| Driver de suite | `scripts/run_suite_bwv1007.py` | `cli/run_suite.py` |
| Agregador final | `scripts/build_control_primes_summary_nextpp.py` | `analysis/aggregate.py` |
| Null model | `scripts/null_model_fast.py` | `analysis/null_model.py` |
| Auditoría | `scripts/aggregate_audit.py` | `analysis/audit.py` |
| Mutopia downloader | `repro/code/get_mutopia_midis.py` | `data_io/mutopia.py` |
| Job list | `repro/code/job_list_generator.py` | `cli/job_list.py` |

## Comandos principales (objetivo final)

```bash
# Tras Movimiento 5:
python -m padicmidi.cli.run_one --midi data/midi/bwv1007-1.mid --p 2 --nmax 5 --out results_local/
bash scripts/reproduce.sh                    # reproducir tablas de ambos papers
pytest tests/                                # tests smoke + unit + regression + paper_values
open web-demo/applet.html                    # applet pedagógico autocontenido
```

## Versión actual

**v1.0.0 — congelada 2026-04-29.** Movimientos −1 a 8C completados.
- 27 archivos Python en `src/padicmidi/` (1809 LOC motor + 417 LOC jerárquico + adaptadores + CLI + análisis + figuras).
- 28 tests pasando (smoke + unit + paper_values).
- Applet HTML autocontenido `web-demo/applet.html` (34 KB).
- Dossier INDAUTOR completo en `indautor/` con ZIP fuente, manifiesto SHA-256, RPDA-03 pre-llenado y carta de titularidad.
- ZIP fuente: `indautor/padicmidi-v1.0.0-source.zip`, SHA-256 `7d2092a3bce311a47ff19fb32bd5dfa29147a92ca574be0a04e2c93666228eeb`.

## Decisiones tomadas

| Fecha | Decisión | Razón |
|---|---|---|
| 2026-04-29 | Tipo de producto: software registrable INDAUTOR + applet HTML | Prioridad legal, alcance acotado |
| 2026-04-29 | Nombre: `PAdicMIDI — A Python Toolkit for Hierarchical, Ultrametric, and p-adic Analysis of Symbolic Music Data` | Decisión del autor |
| 2026-04-29 | Modo B (refactorización ligera autorizada) | Hay duplicación clara entre raíz/ y repro/code/ |
| 2026-04-29 | Autoría única: J. Rogelio Pérez-Buendía | Decisión del autor; transmisión patrimonial CIMAT pospuesta |
| 2026-04-29 | Gold standard = ambos papers (Phase I + jerárquico) | Decisión del autor |
| 2026-04-29 | Applet: uno universal HTML offline | Acotar alcance; cumple "automatizar a partir del MIDI" |
| 2026-04-29 | `analyze_bwv1007.py` + `continuous_patterns.py` EXCLUIDOS de v1.0; candidatos a registro INDAUTOR separado en el futuro | Son experimentos ultramétricos no alimentan los dos papers |
| 2026-04-29 | Soporte DUAL `mido` + `pretty_midi` como adaptadores intercambiables; default `mido` | Compatibilidad con ambos papers + flexibilidad |
| 2026-04-29 | `data/external_midis/` (Bach polifónico) SE INCLUYE con README de licencia por archivo (auditoría manual previa) | Estos MIDIs sí están en los papers |
| 2026-04-29 | DOS archivos de dependencias: `requirements-pinned.txt` (exacto, reproducción bit-equivalente) + `pyproject.toml` (rangos para distribución futura) | Mejor de ambos mundos |
| 2026-04-29 | Applet con DOS modos: botón "Cargar demo BWV1007" (precargado base64) + selector de archivo MIDI | Demo inmediato + uso real |

## Decisiones pendientes (bloquean Movimiento 4)

Ninguna que bloquee Movimientos 1–3.
La próxima decisión bloqueante es la APROBACIÓN de `ARCHITECTURE-PROPOSAL.md` (Movimiento 4) antes de implementar `src/`.

## Riesgos pendientes

| Tipo | Descripción | Prioridad |
|---|---|---|
| Matemático | Discrepancia `mido`/`pretty_midi` documental | Media |
| Matemático | Reproducción exacta de `Coh_π(3,n)` depende de seed=42 | Alta |
| Técnico | Doble montaje macOS (`Paper CODA-/...` vs `Paper CODA-\...`) | Baja (ya documentado) |
| Técnico | OOM con $p=5, N_{\max}=4$ | Baja (ya documentado, motor advierte) |
| Legal | MIDIs de `data/external_midis/` sin licencia auditada por archivo | Alta |
| Legal | Titularidad patrimonial CIMAT/SECIHTI | Media (no bloquea v1.0) |
| Documental | Tres copias desincronizadas del README en `repro/` | Baja |

## Próximo paso

Resolver las 5 decisiones pendientes y avanzar a Movimiento 1 (`MATH-SPEC.md`): especificación matemática completa con pseudocódigo, invariantes y ejemplos verificables a mano.
