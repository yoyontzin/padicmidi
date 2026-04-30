# `REPORTE-TECNICO/` — documento técnico integral imprimible

Carpeta dedicada al **reporte técnico único** que integra en un solo PDF:

1. Portada institucional (autor, ORCID, web, financiamiento).
2. Resumen ejecutivo de PAdicMIDI.
3. Marco matemático (definiciones, Coh_π, piso 1/p, Corolario de aridez).
4. Arquitectura del software (estructura de directorios, métricas).
5. Instrucciones de instalación y uso (los seis ejecutables CLI + API Python).
6. Descripción detallada del applet web autocontenido.
7. Suite de reproducibilidad y validación (28 tests).
8. Datos del solicitante para registro INDAUTOR.
9. **Apéndice A** — listado completo del código fuente (~3,700 líneas Python).
10. **Apéndice B** — manifiesto SHA-256 de todos los archivos del dossier.
11. **Apéndice C** — instrucciones para subir el software a la página personal.
12. **Apéndice D** — resumen de los archivos del dossier INDAUTOR.

## Archivos en esta carpeta

| Archivo | Descripción |
|---|---|
| `main.tex` | Fuente LaTeX (compilable con `lualatex`) |
| `main.pdf` | PDF generado por `lualatex` (88 páginas, ≈ 850 KB) |
| `REPORTE-TECNICO.pdf` | Copia con nombre canónico para distribución |
| `README.md` | Este archivo |

La copia oficial dentro del dossier INDAUTOR está en
[`../indautor/REPORTE-TECNICO.pdf`](../indautor/REPORTE-TECNICO.pdf).

## Cómo recompilar

Requiere TeX Live (≥ 2023) con `lualatex`, `babel-spanish`, `listings`,
`fontspec`, `hyperref` y la fuente DejaVu Sans Mono (incluida en TeX Live
desde hace años).

```bash
cd REPORTE-TECNICO/
lualatex -interaction=nonstopmode main.tex
lualatex -interaction=nonstopmode main.tex   # segunda pasada para TOC y refs
lualatex -interaction=nonstopmode main.tex   # tercera pasada para LastPage
```

El PDF resultante (`main.pdf`) debe tener exactamente 88 páginas y
≈ 847 KB. Su hash SHA-256 está documentado en
`../indautor/manifiesto-archivos.md`.

## Notas de compilación

- **Compilador**: se requiere `lualatex` (no `pdflatex`) por dos razones:
  1. Soporte UTF-8 nativo, necesario para los caracteres Unicode (π, β,
     ├, ─, └) que aparecen en los listings de código y diagramas.
  2. Acceso directo a fuentes OpenType del sistema vía `fontspec`.
- **Fuentes**: Latin Modern (texto principal y matemáticas) + DejaVu Sans
  Mono (código y diagramas). Ambas se incluyen en una instalación
  completa de TeX Live.
- **Babel español**: se desactivan los caracteres activos de babel
  (`< > . ~`) con `\shorthandoff{<>.~}` para evitar conflictos con math
  mode dentro de tablas y títulos.
- **Listados**: se incluyen los archivos Python directamente con
  `\lstinputlisting`; no se duplica el código en el `.tex` para
  garantizar coherencia bit-equivalente con el código fuente.

## Para imprimir

El PDF está optimizado para impresión a tamaño A4, tinta negra y
sangrías mínimas (2.4 cm). Cualquier impresora estándar produce un
documento legible. Para encuadernación profesional, conviene imprimir
en doble cara (es `oneside` por defecto pero el contenido respeta
márgenes simétricos).
