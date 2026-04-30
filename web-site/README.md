# `web-site/` — paquete listo para tu sitio personal

Esta carpeta es el **paquete completo** que se sube tal cual a
`http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/`
(o a `www.cimat.mx/~rogelio.perez/desarrollo-tecnologico/` cuando esté
disponible). No requiere servidor dinámico, base de datos ni build step:
es HTML+CSS+JS estático.

## Estructura

```
web-site/
├── index.html             ← splash con auto-detección de idioma + selector
├── index.es.html          ← HUB en español
├── index.en.html          ← HUB en inglés
├── index.fr.html          ← HUB en francés
├── padicmidi.es.html      ← landing detallada de PAdicMIDI (ES)
├── padicmidi.en.html      ← landing detallada de PAdicMIDI (EN)
├── padicmidi.fr.html      ← landing detallada de PAdicMIDI (FR)
├── applet.html            ← applet PAdicMIDI (EN, autocontenido, ≈ 53 KB)
├── applet-es.html         ← applet PAdicMIDI (ES, autocontenido, ≈ 55 KB)
└── README.md              ← este archivo
```

### Flujo de navegación

1. El visitante llega a `index.html`.
2. JavaScript detecta el idioma de su navegador y redirige a
   `index.es.html`, `index.en.html` o `index.fr.html` (default: inglés).
   Si no hay JavaScript, un `<meta refresh>` lo manda a la versión inglesa
   tras dos segundos. En cualquier caso, la pantalla muestra los tres
   idiomas como botones para elegir manualmente.
3. Cada HUB lista los **programas disponibles** en tarjetas con
   indicador de estado (estable / beta / próximamente), versión,
   licencias e idiomas soportados. Hoy contiene una sola tarjeta:
   **PAdicMIDI v1.0.0**.
4. Desde el HUB, **Ver detalles** abre la landing detallada del proyecto
   (`padicmidi.{es,en,fr}.html`), donde se documenta el método, las
   instrucciones de instalación y los artículos asociados.
5. Desde el HUB o desde la landing detallada, los botones **Abrir el
   applet** llevan a `applet.html` (EN) o `applet-es.html` (ES). El applet
   francés está pendiente; mientras tanto se enlaza al inglés con una nota
   en `padicmidi.fr.html`.

### Selector de idioma

El selector está en la barra superior de cada página y siempre incluye
las tres lenguas. La opción activa se distingue con fondo azul claro.
Cambiar de idioma desde la landing detallada conserva el contexto
(PAdicMIDI → PAdicMIDI), no salta al HUB.

## Cómo subirlo a tu servidor

### Opción 1 — `rsync` (recomendado)

```bash
cd "Paper CODA-/bwv1007/padicmidi"
rsync -av --delete web-site/ \
    rogelio.perez@personal.cimat.mx:/home/rogelio.perez/public_html/desarrollo-tecnologico/
```

`--delete` retira archivos remotos que ya no existen localmente, lo cual
mantiene la sincronización limpia. Quita esa bandera la primera vez si
quieres una pasada conservadora.

### Opción 2 — `scp` (más simple, sin sincronización)

```bash
scp web-site/*.html web-site/README.md \
    rogelio.perez@personal.cimat.mx:/home/rogelio.perez/public_html/desarrollo-tecnologico/
```

### Opción 3 — Hugo / Jekyll / WordPress

Copia el contenido de `web-site/` dentro de la carpeta `static/` del
generador estático que uses. Los archivos son completamente
auto-contenidos, no dependen de plantillas externas y los `index.*.html`
no chocan con el `index.html` raíz (sirven como páginas independientes).

## Personalización rápida

| Si quieres cambiar… | Edita estos archivos |
|---|---|
| El correo, ORCID o página personal | `index.{es,en,fr}.html` (sección *Acerca del autor / About / À propos*) y `padicmidi.{es,en,fr}.html` (sección equivalente). |
| El versionado mostrado (`v1.0.0 · 2026-04`) | Texto en `<span class="ver">` dentro de la tarjeta de proyecto en cada `index.*.html`. |
| Los badges (estable / beta / próximamente) | Cambia la clase del `<span class="badge stable">` por `badge beta` o `badge soon`. |
| Añadir un nuevo programa | Duplica el bloque `<article class="project">` dentro de la sección *Programas disponibles* en cada `index.*.html` y crea sus propias páginas `<nombre>.{es,en,fr}.html`. |

## Verificación local

```bash
cd web-site
python3 -m http.server 8765
# abrir http://localhost:8765/index.html en el navegador
```

Con eso simulas exactamente cómo se verá en producción. El splash
redirige según el idioma del navegador; usa `?nolang` para forzar el
selector visible:

```
http://localhost:8765/index.html?nolang
```

## Privacidad

El sitio entero **no usa cookies, no carga recursos externos, no envía
datos a ningún servidor** (incluido Google Analytics, fuentes de Google,
etc.). El único JavaScript es el snippet de detección de idioma en
`index.html` y el motor del applet, que se ejecuta enteramente en el
navegador del visitante.

## Licencia

* Código HTML/CSS/JS: **MIT** (mismo `LICENSE` del paquete).
* Texto y documentación: **CC-BY 4.0**.
* Datos MIDI demo embebidos (BWV 1007): **dominio público de EE. UU.**
  vía Mutopia Project.
