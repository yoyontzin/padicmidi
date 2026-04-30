# Instrucciones para el agente que sube PAdicMIDI a la página personal

**Destinatario:** agente / asistente que despliega los archivos del sitio
personal de Jesús Rogelio Pérez Buendía.
**Fecha de generación de este manifiesto:** 2026-04-29 (revisar `SHA-256`
abajo antes de publicar).
**Origen autoritativo en la Mac de Rogelio:**
`/Users/yoyonzin/Documents/Paper\ CODA-\\bwv1007/padicmidi/web-site/`

---

## 1. URL pública objetivo

El sitio se publica bajo la siguiente URL ya operativa:

```
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/
```

Si la cuenta también está reflejada en el host `www.cimat.mx`, la URL
"limpia" objetivo (que es la que aparece como `homepage` del repo GitHub) es:

```
https://www.cimat.mx/~rogelio.perez/desarrollo-tecnologico/
```

Verificar con el administrador del servidor si:
- la ruta `~rogelio.perez/desarrollo-tecnologico/` está habilitada en
  `www.cimat.mx` (sin el `:8181`),
- los `.html` se sirven con `Content-Type: text/html; charset=utf-8`,
- los archivos pueden ser indexados (no robots.txt restrictivo).

---

## 2. Lista exacta de archivos a publicar (10 archivos + 1 README)

Esta es la **única** carpeta a sincronizar. Es estática, sin dependencias
externas, sin generadores. Cada archivo es autocontenido.

| # | Archivo | Tamaño (bytes) | SHA-256 |
|---|---|---:|---|
| 1 | `index.html` | 4 045 | `545ea5779dce7303f0f5941eba0e162944cc9975e151d43109bb98270e532269` |
| 2 | `index.es.html` | 11 723 | `78d1359810921874dfac786a1f9ad36b43f8ef62da96daa670cf9b50b23208cd` |
| 3 | `index.en.html` | 10 966 | `af55752f2cc4a3c982f77cfcb76076f4fa753cf702a28e8e2dcb1d2620043920` |
| 4 | `index.fr.html` | 11 220 | `f26bf9de1ab5e97ab134d6a26ed4fbdafdb4dbdd75dba157b689ee96e9243fc4` |
| 5 | `padicmidi.es.html` | 14 478 | `cab4edf5b26a9b8b5a75ec35fe2907c008488f9fcee6f5becd62c7312263057f` |
| 6 | `padicmidi.en.html` | 14 031 | `be0b846a40f2660e24d7fad1fb8dc2d1b8eb3d7afb7c62b005d11302a30fb3d2` |
| 7 | `padicmidi.fr.html` | 14 854 | `ded0288b8df584d4f4826b9e6fef3c35c73a7518f5d35d4833f4051abbb04870` |
| 8 | `applet.html` *(EN)* | 124 502 | `7cbd640ceb1bd55bda300589004d2cf03bb69b4b06ff286a0537c988277d7e59` |
| 9 | `applet-es.html` *(ES)* | 132 535 | `1b078d221fe30f66401c214eb8744b1f9102d83276dab3b6b603e76db29afd34` |
| 10 | `README.md` *(opcional, para inspección humana)* | 5 049 | `60bab2bdcf8f942ea99ed8748dc7bcffe97ccf637c9209fb222034783f617138` |

**Tamaño total: aproximadamente 343 KB.**

> **Nota sobre el francés.** No existe `applet-fr.html`: la versión
> francesa del applet está marcada como *coming soon* dentro de
> `padicmidi.fr.html`. La página francesa redirige al usuario al applet
> EN o ES. No subir ningún archivo `applet-fr.html`.

---

## 3. Estructura del directorio remoto

```
~rogelio.perez/desarrollo-tecnologico/
├── index.html                ← redirector con detección de idioma
├── index.es.html             ← hub trilingüe (ES)
├── index.en.html             ← hub trilingüe (EN)
├── index.fr.html             ← hub trilingüe (FR)
├── padicmidi.es.html         ← landing page del proyecto (ES)
├── padicmidi.en.html         ← landing page del proyecto (EN)
├── padicmidi.fr.html         ← landing page del proyecto (FR)
├── applet.html               ← applet interactivo (EN)
├── applet-es.html            ← applet interactivo (ES)
└── README.md                 ← (opcional) lectura humana
```

**No hay subdirectorios. No hay `assets/`, `js/`, `css/` separados.**
Cada HTML es autocontenido (CSS y JS embebidos).

---

## 4. Comandos exactos de sincronización

### 4.1 Si tu agente tiene acceso SSH a `personal.cimat.mx`

```bash
# Desde la Mac de Rogelio (ruta autoritativa):
cd "/Users/yoyonzin/Documents/Paper CODA-\bwv1007/padicmidi/"

# Crear el directorio remoto (idempotente):
ssh rogelio.perez@personal.cimat.mx \
    'mkdir -p ~/public_html/desarrollo-tecnologico'

# Sincronizar (modo seguro, sin borrar otras cosas que ya estén ahí):
rsync -avz --checksum \
    --include='*.html' --include='README.md' --exclude='*' \
    web-site/ \
    rogelio.perez@personal.cimat.mx:~/public_html/desarrollo-tecnologico/
```

> El flag `--checksum` evita re-subir archivos que coincidan en SHA-256.
> El triple `--include`/`--exclude` evita subir basura accidental.

### 4.2 Si en el servidor el `public_html` se llama `www_html` o similar

Pregunta al administrador la ruta canónica equivalente a
`~rogelio.perez/desarrollo-tecnologico/`. Sustituye en `rsync` arriba.

### 4.3 Si solo dispones de `scp`

```bash
cd "/Users/yoyonzin/Documents/Paper CODA-\bwv1007/padicmidi/web-site"
scp index.html index.es.html index.en.html index.fr.html \
    padicmidi.es.html padicmidi.en.html padicmidi.fr.html \
    applet.html applet-es.html README.md \
    rogelio.perez@personal.cimat.mx:~/public_html/desarrollo-tecnologico/
```

### 4.4 Si tu agente solo opera por panel web / FTP

Subir los 10 archivos listados en la sección 2, conservando
exactamente sus nombres y respetando que se almacenen en una sola
carpeta plana llamada `desarrollo-tecnologico`.

---

## 5. Permisos y propietario en el servidor

```bash
ssh rogelio.perez@personal.cimat.mx '
  cd ~/public_html/desarrollo-tecnologico &&
  chmod 644 *.html *.md &&
  chmod 755 . &&
  ls -la
'
```

Verifica que el usuario propietario sea `rogelio.perez` y que el grupo
herede del `public_html`. Los `.html` deben ser legibles por el grupo
`www` o equivalente para que Apache/Nginx los sirva.

---

## 6. Verificación post-deploy (obligatoria)

Después de subir, abrir en un navegador limpio (modo incógnito) **cada
URL** y comprobar que carga sin advertencias:

```
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/index.es.html
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/index.en.html
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/index.fr.html
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/padicmidi.es.html
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/padicmidi.en.html
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/padicmidi.fr.html
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/applet.html
http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico/applet-es.html
```

**Pruebas funcionales del applet** (basta hacerlas con `applet.html`):

1. Cargar la página: la sección "0. Before you start" debe abrir sin
   pulsar nada.
2. Pulsar **Demo BWV 1007** y luego **Run analysis**.
3. Esperar ~5 s. Debe mostrar tabla con `Coh_pi(2,n) = 0.500` para todos
   los niveles, y todas las visualizaciones 4.0 a 4.5 deben renderizar.
4. Pulsar el botón ▶ Play del reproductor 4.0 y comprobar que se oye el
   preludio sintetizado y que el cursor rojo avanza sobre el cromograma.

Si alguna falla, el problema casi siempre es:
- política de `file://` vs `http://` (el applet ya está pensado para
  ambos, no debería fallar);
- algún navegador antiguo sin WebAudio (probar Firefox actualizado);
- algún antivirus de servidor que reescribe `.html`.

---

## 7. Verificación de integridad SHA-256 después del despliegue

Desde tu máquina local, después de subir, ejecuta:

```bash
URL_BASE="http://personal.cimat.mx:8181/~rogelio.perez/desarrollo-tecnologico"
for f in index.html index.es.html index.en.html index.fr.html \
         padicmidi.es.html padicmidi.en.html padicmidi.fr.html \
         applet.html applet-es.html README.md; do
  remote_sha=$(curl -s "$URL_BASE/$f" | shasum -a 256 | awk '{print $1}')
  echo "$remote_sha  $f"
done
```

Compara la salida contra la tabla de la sección 2. **Cada SHA-256 debe
coincidir bit-a-bit.** Si alguno difiere, el archivo se subió mal o el
servidor está añadiendo cabeceras / reescribiendo contenido.

---

## 8. Cabeceras HTTP recomendadas (si tienes acceso a configurar)

Para que el applet funcione siempre con caché controlada:

```
applet.html, applet-es.html:
    Cache-Control: public, max-age=3600

index*.html, padicmidi*.html:
    Cache-Control: public, max-age=86400
```

Y para el correcto soporte de Unicode:

```
Content-Type: text/html; charset=utf-8
```

---

## 9. ¿Qué NO subir?

**No subir nada de las siguientes carpetas / archivos** del proyecto
local de Rogelio:

- `padicmidi/indautor/` — datos personales (RFC, CURP, dirección,
  teléfono); este material va exclusivamente al USB que entrega el
  colega en INDAUTOR.
- `padicmidi/USB-PAdicMIDI-INDAUTOR-v1.0.0/` y
  `padicmidi/USB-PAdicMIDI-INDAUTOR-v1.0.0.zip` — destinado al USB.
- `padicmidi/.venv/`, `padicmidi/.pytest_cache/`,
  `padicmidi/results_local/` — basura local.
- `padicmidi/REPORTE-TECNICO/main.aux` y similares — artefactos LaTeX.
- Cualquier `.DS_Store`.

---

## 10. Resumen ejecutivo (1 oración por paso)

1. Sincronizar **solo** la carpeta `padicmidi/web-site/` a
   `~/public_html/desarrollo-tecnologico/` con `rsync --checksum`.
2. Ajustar permisos a `644` para archivos y `755` para la carpeta.
3. Abrir en navegador las 9 URLs listadas en §6 y validar el applet.
4. Verificar SHA-256 remotos contra la tabla §2.
5. Avisar a Rogelio (`rogelio@cimat.mx`) cuando todo esté en línea.
