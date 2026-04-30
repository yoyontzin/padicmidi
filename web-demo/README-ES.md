# `web-demo/` — applet sin conexión

> Read this in [English](README.md).

Esta carpeta contiene dos archivos HTML autocontenidos que ejecutan el
análisis de PAdicMIDI de extremo a extremo dentro de cualquier navegador
moderno, **sin dependencias de red**:

- [`applet.html`](applet.html) — versión en inglés.
- [`applet-es.html`](applet-es.html) — versión en español.

Ambos comparten el mismo motor JavaScript y el mismo MIDI de demostración
embebido (BWV 1007 codificado en base64).

## Cómo usar

1. Abre `applet-es.html` con doble clic (funciona en macOS, Linux y Windows).
2. Pulsa **Cargar demo BWV 1007** para usar el preludio precargado, o
   arrastra cualquier archivo MIDI estándar a la zona indicada.
3. Elige el primo *p* (2 o 3) y el nivel máximo *N<sub>máx</sub>*.
4. Pulsa **Ejecutar análisis**.
5. Lee la tabla de valores $\mathrm{Coh}_\pi(p,n)$, compárala con el piso
   $1/p$ y explora las cuatro vistas musicales (ver más abajo).

## Vistas musicales del applet (sección 4)

A partir de v1.0.0, en lugar de un único árbol abstracto el applet ofrece
**cuatro visualizaciones encadenadas** que muestran qué está mirando el
método dentro de la pieza. Un selector de nivel ($n=1,2,\dots,N_\text{máx}$)
las refresca todas simultáneamente:

1. **4.1 La pieza coloreada por prototipo** — cromograma a lo largo del
   tiempo (12 clases de altura $\times$ tiempo, intensidad azul) con una
   franja inferior coloreada según qué prototipo cuantiza cada ventana de
   longitud $p^n$. Es la *huella temporal* del nivel: los cambios de color
   marcan transiciones musicalmente relevantes (modulaciones, secciones).

2. **4.2 Catálogo de prototipos** — cada prototipo se renderiza como un
   mini-cromograma $12 \times p^n$ que enseña su contenido cromático real
   (qué clases de altura define). El recuadro coloreado coincide con la
   franja temporal de 4.1, así se puede leer dónde aparece cada patrón en
   la pieza. Cada tarjeta indica además cuántas ventanas se le asignaron y
   quién es su padre $\pi$.

3. **4.3 Sistema inverso $\pi$** — diagrama tipo Sankey del mapeo
   $\pi_{n+1,n}: S_{n+1} \to S_n$. Arriba los prototipos del nivel padre,
   abajo los del hijo, y curvas que muestran qué hijo hereda de qué padre.
   El pie del diagrama muestra el valor calculado de $\mathrm{Coh}_\pi(p,n)$
   y el piso $1/p$.

4. **4.4 Árbol p-ádico completo** — la torre $S_1 \to S_2 \to \dots \to
   S_{N_\text{máx}}$ con nodos coloreados según la herencia de su raíz, de
   modo que las "ramas" del árbol son visualmente coherentes con las
   franjas de las vistas anteriores.

## Qué implementa el applet

- Un parser mínimo de archivos MIDI estándar (formatos 0/1, fusión de pistas
  múltiples, mapa de tempo; división SMPTE no soportada).
- Serie cromática con eje en pulsos (beats) y bin $\Delta_b = 1/12$.
- Motor jerárquico p-ádico con cuantización K-means y sistema inverso
  $\pi_{n+1,n}$ forzado.
- Cálculo del invariante $\mathrm{Coh}_\pi(p,n)$ con comparación contra el
  piso $1/p$.
- Cuatro visualizaciones musicales (descritas arriba) en SVG y canvas, y
  descarga del CSV con la tabla.

## Limitaciones respecto al paquete Python

- Sólo se exponen los primos $p \in \{2, 3\}$.
- El eje en segundos no está implementado (sólo eje en pulsos).
- El generador pseudoaleatorio del K-means usa Mulberry32, mientras que el
  paquete Python usa PCG64 de NumPy — los valores pueden diferir en el
  quinto decimal. Los pisos estructurales (por ejemplo,
  $\mathrm{Coh}_\pi(2,n) = 0{,}500$ exacto en BWV 1007 monofónico) se
  reproducen exactamente.

Para reproducibilidad completa use la línea de comandos
`padicmidi-run-one` o la API Python `padicmidi.run_hierarchical_from_midi`.

## Privacidad

El applet **no envía datos a ningún servidor**. No realiza peticiones de
red, no usa cookies, no usa localStorage y no genera telemetría. El único
archivo al que accede es el MIDI que tú cargas, y ese archivo nunca sale de
tu computadora.
