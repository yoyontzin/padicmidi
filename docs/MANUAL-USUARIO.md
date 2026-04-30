# Manual de usuario — PAdicMIDI

**Versión:** 1.0.0
**Autor:** Jesús Rogelio Pérez Buendía — *firma como* J. Rogelio Pérez-Buendía (CIMAT–Mérida).
**ORCID:** [0000-0002-7739-4779](https://orcid.org/0000-0002-7739-4779) · **Web:** [www.cimat.mx/~rogelio.perez](https://www.cimat.mx/~rogelio.perez)
**Idioma:** este manual está en español; los mensajes del software y la API están en inglés.

---

## 1. Instalación

### 1.1 Instalación rápida (entorno virtual)

```bash
git clone https://github.com/yoyontzin/padicmidi.git
cd padicmidi
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verificación:

```bash
python -c "import padicmidi; print(padicmidi.__version__)"
# 1.0.0
```

### 1.2 Instalación con dependencias bit-equivalentes

Si necesita reproducir exactamente las tablas de los artículos:

```bash
pip install -r requirements-pinned.txt
pip install -e .
```

### 1.3 Adaptador opcional `pretty_midi`

```bash
pip install padicmidi[pretty]
```

Esto habilita un parser MIDI alternativo basado en `pretty_midi`. El default
sigue siendo `mido`.

---

## 2. Uso desde la línea de comandos

### 2.1 Analizar un MIDI individual

```bash
padicmidi-run-one <ruta_midi> <nombre_pieza> <eje> <p> [Nmax] --out <directorio>
```

Ejemplo:

```bash
padicmidi-run-one data/midi/bwv1007-1.mid bwv1007_pre beats 2 \
    --out resultados/bwv1007/p2
```

Esto produce:

```
resultados/bwv1007/p2/
├── params.json
├── params.txt
├── S_n_prototypes_p2_n1.csv … S_n_prototypes_p2_n6.csv
├── pi_p2_n2_to_n1.csv … pi_p2_n6_to_n5.csv
├── f_p2_n1.csv … f_p2_n6.csv
├── coherence_hier_p2.csv      ← TABLA PRINCIPAL
└── audit_p2.csv               ← diagnóstico (SC, AI)
```

### 2.2 Suite completa BWV 1007

```bash
padicmidi-run-suite --midi-dir data/midi --out-dir resultados/suite
```

### 2.3 Benchmark (BWV 1007 movements + toys)

```bash
padicmidi-benchmark --midi-dir data/midi --out-dir resultados/benchmark
```

### 2.4 Generar lista de jobs

```bash
padicmidi-job-list --out resultados/job_list.txt
```

### 2.5 Descargar MIDIs de Mutopia

```bash
padicmidi-mutopia --out data/midi/
```

---

## 3. Uso desde Python

### 3.1 Análisis simple

```python
from padicmidi import run_hierarchical_from_midi

result = run_hierarchical_from_midi(
    midi_path="data/midi/bwv1007-1.mid",
    p=2,
    axis="beats",
    nmax=5,
)

for row in result["coherence"]:
    print(f"n={row['n']}  Coh_pi={row['Coh_pi']:.6f}")
```

### 3.2 Acceso al motor de bajo nivel

```python
import numpy as np
from padicmidi.core.echo import (
    parse_midi_notes_beats, chroma_series_duration_beats,
    onset_density_series_beats, series_with_rhythm,
)
from padicmidi.core.hierarchical import run_hierarchical

events = parse_midi_notes_beats("data/midi/bwv1007-1.mid")
H = chroma_series_duration_beats(events, bin_size_beats=1/12)
a = onset_density_series_beats(events, bin_size_beats=1/12)
X = series_with_rhythm(H, a, alpha=1.0)

rng = np.random.default_rng(42)
prototypes_n, f_n, pi_maps, coh, audit = run_hierarchical(
    X, p=2, Nmax=5, step=2, K=16, Kchild=2, M=800, rng=rng
)
```

---

## 4. El applet HTML offline

1. Abra `web-demo/applet.html` con doble clic.
2. Cargue la demo precargada (BWV 1007) o arrastre un archivo MIDI.
3. Seleccione el primo *p* y el N<sub>max</sub>.
4. Pulse **Run analysis**.
5. Lea la tabla, descargue el CSV, examine el árbol p-ádico SVG.

El applet **no envía datos a ningún servidor**.

---

## 5. Salidas

### 5.1 `coherence_hier_p{p}.csv`

| Columna | Significado |
|---|---|
| `n` | Nivel de la torre |
| `Coh_pi` | Coherencia del sistema inverso $\pi_{n+1,n}$ |
| `Coh_grid` | Coherencia del cuantizador alternativo (control) |
| `n_samples_n` | Tamaño efectivo de $S_n$ |
| `n_samples_nplus1` | Cantidad de residuos válidos en $S_{n+1}$ |

### 5.2 `audit_p{p}.csv`

Diagnóstico por padre del cumplimiento de las hipótesis (SC) sibling-coverage
y (AI) ancestor-inclusion (Proposición 3.1 del Paper 2).

| Columna | Significado |
|---|---|
| `parent_class` | Clase padre $a \in \{0, \dots, p^n - 1\}$ |
| `n_valid_siblings` | # de siblings válidos (debe ser $p$ para que (SC) se cumpla) |
| `V_SC_pi` | # de prototipos distintos visitados por $\pi$ entre los siblings |
| `AI_pi` | 1 si el prototipo padre aparece en la lista; 0 si no |
| `coherent_count_pi` | # de siblings cuyo $\pi$-padre coincide con el cuantizador |

---

## 6. Resolución de problemas

### 6.1 "Series too short"

El MIDI no tiene suficientes bins para construir ventanas del nivel
solicitado. Reduzca `--Nmax` o use un MIDI más largo.

### 6.2 OOM con `p=5, Nmax=4`

Documentado: requiere ~5 GiB. Use `--Nmax 3` para `p=5` en piezas largas.

### 6.3 Resultados ligeramente distintos al gold standard

La reproducción bit-equivalente requiere macOS arm64 con Python 3.13.3 y
las versiones pinneadas en `requirements-pinned.txt`. En otras plataformas
puede haber drift en el 5°–6° decimal de `Coh_pi`. La estructura
`Coh_pi(p,n) = 1/p` exacta para BWV 1007 binario es estructural y se mantiene.

### 6.4 El applet no abre

Algunos navegadores bloquean `file://`. Use Firefox o Safari, o sirva el
archivo localmente con `python3 -m http.server -d web-demo` y abra
`http://localhost:8000/applet.html`.

---

## 7. Soporte y contacto

Bug reports y preguntas: GitHub Issues en el repositorio del proyecto.
Contacto académico: J. Rogelio Pérez-Buendía, CIMAT-Mérida ([rogelio@cimat.mx](mailto:rogelio@cimat.mx)) ·
[www.cimat.mx/~rogelio.perez](https://www.cimat.mx/~rogelio.perez) ·
ORCID [0000-0002-7739-4779](https://orcid.org/0000-0002-7739-4779).
