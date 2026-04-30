# Procedimiento Zenodo — minar DOI para `yoyontzin/padicmidi v1.0.0`

**Repositorio:** https://github.com/yoyontzin/padicmidi
**Release ya creado:** v1.0.0 (29-abr-2026)
**Cuenta Zenodo:** la tuya (ya conectada a GitHub según tu confirmación)

> Resultado esperado al final de este procedimiento: una cita
> permanente del tipo
>
> > J. R. Pérez-Buendía. *PAdicMIDI: A Python Toolkit for Hierarchical,
> > Ultrametric, and p-adic Analysis of Symbolic Music Data.* Versión
> > 1.0.0. Zenodo, 2026. **DOI:** 10.5281/zenodo.XXXXXXX

---

## Paso 0 — Verificación previa (1 minuto)

1. Entra a https://zenodo.org y haz login.
2. Arriba a la derecha, abre tu menú de usuario → **GitHub**.
3. Confirma que aparece tu cuenta `yoyontzin` y que está marcada como
   **Connected**. Si no, haz clic en *Connect* y autoriza la app de
   Zenodo en GitHub.

---

## Paso 1 — Activar el repositorio en Zenodo (2 minutos)

> Esto es **necesario para que Zenodo "vea" futuros releases** y mine
> DOI automáticamente. Solo se hace una vez.

1. Una vez en https://zenodo.org/account/settings/github/ verás la lista
   de tus repositorios.
2. Si no ves `yoyontzin/padicmidi`, pulsa el botón **Sync now** (arriba
   a la derecha) y espera ~30 s. Vuelve a buscarlo.
3. Junto al repositorio `yoyontzin/padicmidi`, **mueve el toggle a "On"**
   (icono verde con un check).

   Esto instala automáticamente un *webhook* de Zenodo en GitHub. A
   partir de ahora, cada **GitHub Release** del repo dispara
   automáticamente la creación de un depósito en Zenodo y el minado de
   un nuevo DOI.

---

## Paso 2 — Disparar el primer DOI para v1.0.0 (3 minutos)

El release v1.0.0 **ya existe** en GitHub:
https://github.com/yoyontzin/padicmidi/releases/tag/v1.0.0

Pero como Zenodo se "enchufó" *después* de crearlo, tienes que
re-disparar el webhook. Hay dos formas; elige una:

### Opción A — Borrar y re-crear el release (recomendada, más limpia)

```bash
cd "/Users/yoyonzin/Documents/Paper CODA-\bwv1007/padicmidi"

# 1) Borra el release (NO el tag) en GitHub
gh release delete v1.0.0 --yes

# 2) Vuelve a crearlo con los mismos assets y notas
gh release create v1.0.0 \
  "indautor/padicmidi-v1.0.0-source.zip#padicmidi-v1.0.0-source.zip (source bundle)" \
  "indautor/REPORTE-TECNICO.pdf#REPORTE-TECNICO.pdf (technical report, 90 pp)" \
  --title "PAdicMIDI v1.0.0 — initial public release" \
  --notes-from-tag
```

### Opción B — Crear un release v1.0.0.1 vacío para disparar el webhook

```bash
git tag -a v1.0.0.1 -m "Re-tag to trigger Zenodo DOI minting (no code changes)."
git push origin v1.0.0.1
gh release create v1.0.0.1 --title "v1.0.0.1 — DOI registration" \
  --notes "Identical to v1.0.0; new tag exists only to trigger Zenodo."
```

> Si eliges B y luego notas que el DOI principal queda asociado a
> v1.0.0.1 en lugar de a v1.0.0, simplemente edita el registro Zenodo
> manualmente en el siguiente paso para que el "version label" diga
> *v1.0.0*.

---

## Paso 3 — Editar el metadato Zenodo (5 minutos)

1. En https://zenodo.org/account/settings/github/ pulsa sobre
   `yoyontzin/padicmidi` para entrar a la página del repo en Zenodo.
2. Verás el depósito recién creado. Pulsa **Edit**.
3. **Rellena estos campos** (algunos vendrán autodetectados de
   `CITATION.cff`; verifica):

   | Campo Zenodo | Valor recomendado |
   |---|---|
   | Resource type | **Software** |
   | Title | *PAdicMIDI: A Python Toolkit for Hierarchical, Ultrametric, and p-adic Analysis of Symbolic Music Data* |
   | Authors | **Pérez-Buendía, Jesús Rogelio** — afiliación: *SECIHTI – CIMAT, Unidad Mérida* — ORCID: `0000-0002-7739-4779` |
   | Description | *Copiar el contenido del README.md (resumen + highlights). HTML básico permitido.* |
   | Version | `v1.0.0` |
   | Publication date | 2026-04-29 |
   | Languages | English (primary), Spanish, French |
   | Keywords | `p-adic analysis`, `symbolic music`, `MIDI`, `hierarchical clustering`, `arithmetic-topological data analysis`, `music information retrieval`, `inverse system`, `ultrametric` |
   | License | **MIT License** (para el depósito) — anotar en *Additional notes* que la documentación está bajo CC-BY 4.0 |
   | Funding | **SECIHTI** (México), grant `CF-2019/217367` |
   | Related identifiers | (ver siguiente paso) |
   | Communities | Opcional: añadir *Mathematical Software*, *MIR / Music Information Retrieval* si aparecen |

4. **Related identifiers** (esto vincula el DOI con tus artículos):

   | Relation | Identifier |
   |---|---|
   | *isSupplementTo* | DOI o arXiv ID del primer artículo (Pérez-Buendía 2026, JMM) cuando lo tengas |
   | *isSupplementTo* | DOI o arXiv ID del segundo artículo cuando lo tengas |
   | *isSupplementTo* | `https://github.com/yoyontzin/padicmidi/tree/v1.0.0` (URL del tag) |
   | *isCompiledBy* | `https://orcid.org/0000-0002-7739-4779` |

5. Pulsa **Save** (no *Publish* todavía si quieres revisar).

---

## Paso 4 — Publicar y obtener el DOI (1 minuto)

1. Una vez revisado el formulario, pulsa **Publish**.
2. Zenodo asigna **dos DOIs**:
   - **Concept DOI** (estable, siempre apunta a la "última versión" del
     software): por ejemplo `10.5281/zenodo.NNNNNN`.
   - **Version DOI** (este release específico v1.0.0): por ejemplo
     `10.5281/zenodo.NNNNNN+1`.
3. Cópialos. **Recomendación:** cita *siempre* el Concept DOI en
   artículos y CV; usa el Version DOI cuando necesites trazabilidad
   exacta.

---

## Paso 5 — Cerrar el lazo (10 minutos)

### 5.1 Actualizar el README con el DOI badge

```bash
cd "/Users/yoyonzin/Documents/Paper CODA-\bwv1007/padicmidi"
# Edita README.md y README-ES.md y agrega al inicio (después del título):
#
#   [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.NNNNNNN.svg)](https://doi.org/10.5281/zenodo.NNNNNNN)
#
# (sustituye NNNNNNN por tu Concept DOI)
git add README.md README-ES.md
git commit -m "Add Zenodo DOI badge for v1.0.0"
git push origin main
```

### 5.2 Actualizar `CITATION.cff` con el DOI

Agrega en `CITATION.cff`:

```yaml
identifiers:
  - type: doi
    value: 10.5281/zenodo.NNNNNNN
    description: Concept DOI for all versions of PAdicMIDI
  - type: doi
    value: 10.5281/zenodo.NNNNNNN_VERSION
    description: DOI of release v1.0.0 specifically
```

```bash
git add CITATION.cff
git commit -m "Add Zenodo DOI to CITATION.cff"
git push origin main
```

### 5.3 (Opcional) Actualizar la página personal

Edita `web-site/padicmidi.es.html`, `padicmidi.en.html`,
`padicmidi.fr.html` y agrega un *badge* o un párrafo:

> **Cite as:** Pérez-Buendía, J. R. (2026). *PAdicMIDI v1.0.0*.
> Zenodo. https://doi.org/10.5281/zenodo.NNNNNNN

Vuelve a desplegar como indica `INSTRUCCIONES-AGENTE-WEB.md`.

---

## Paso 6 — Para futuros releases (workflow recurrente)

Cada vez que liberes una versión nueva:

```bash
# 1. Actualiza version en pyproject.toml, src/padicmidi/__init__.py,
#    CITATION.cff, VERSION.md, CHANGELOG.md.
# 2. Commit y push.
git add -A && git commit -m "Bump to v1.1.0" && git push origin main

# 3. Tag y release.
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
gh release create v1.1.0 \
  --title "PAdicMIDI v1.1.0" \
  --notes-file CHANGELOG.md
```

A los 30 segundos, Zenodo automáticamente:
- Crea un nuevo registro Zenodo para v1.1.0.
- Asigna un Version DOI nuevo.
- Mantiene el mismo Concept DOI apuntando a v1.1.0 como "latest".

---

## Notas de cumplimiento

- **No hay conflicto INDAUTOR ↔ Zenodo.** El registro INDAUTOR es
  declarativo de autoría originaria bajo derecho mexicano; el DOI
  Zenodo es identificador persistente para citación académica.
  Coexisten sin tensión.
- **El SHA-256 del ZIP fuente** subido a la GitHub Release v1.0.0
  (`2215e514...8ae`) **es exactamente el que se registró en INDAUTOR**.
  Eso da trazabilidad criptográfica entre el registro autoral mexicano,
  el repo público y el DOI Zenodo: cualquier auditor puede verificar
  que las tres entidades describen el mismo objeto.

---

## Contacto si algo falla

- **Zenodo support:** https://zenodo.org/support
- **GitHub-Zenodo guide:** https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content
- **Tu sysadmin Zenodo personal:** ninguno — Zenodo es self-service.
