# Especificación matemática — PAdicMIDI

**Skill aplicado:** `research-software-builder` (Movimiento 1)
**Fecha:** 2026-04-29
**Fuente primaria:**
- Paper 2 (jerárquico): `Paper-ZpMusic-20250206/paper/sections/03_method.tex`
- Código canónico: `profinite_echo_midi.py` (raíz) + `scripts/build_hierarchical_maps.py`
**Convención editorial:** notación matemática en LaTeX inline; código y archivos en backticks.

---

## 0. Objetos matemáticos centrales

| Notación | Tipo | Significado |
|---|---|---|
| $p \in \{2,3,5,7\}$ | primo | Aridad de la torre p-ádica. |
| $\Delta_b = 1/12$ | beat | Tamaño de bin beat-síncrono (default; equivale a `--bin-beats 0.083333`). |
| $\Delta_s = 0.05$ s | segundo | Tamaño de bin seconds-síncrono (default; equivale a `--bin 0.05`). |
| $H \in \mathbb{R}^{T \times 12}$ | matriz | Cromograma duración-pesado, $L^1$-normalizado por fila. |
| $a \in \mathbb{R}^T$ | vector | Densidad de onsets por bin. |
| $X \in \mathbb{R}^{T \times 13}$ | matriz | Serie unificada $X = [H \mid \alpha\, a]$, con $\alpha = 1$ por default. |
| $N = p^n$ | entero | Longitud de ventana en el nivel $n$. |
| $W_{n,i} \in \mathbb{R}^{N \times 13}$ | tensor | Ventana cruda: $X[i:i+N, :]$ con `step` $s$ (default $s=2$). |
| $W_{p,n}(a) \in \mathbb{R}^{N \times 13}$ | tensor | Ventana agregada por residuo $a \bmod p^n$: mediana componente-a-componente. |
| $D_{p,n}$ | espacio | Espacio de patrones de longitud $p^n$ (clase de equivalencia tras agregación). |
| $S_n$ | conjunto finito | Diccionario de prototipos (centroides K-means) en el nivel $n$. |
| $f_n: \{0,\dots,p^n-1\} \to S_n$ | función | Cuantizador residuo $\to$ prototipo (asignación por mínima distancia). |
| $\pi_{n+1,n}: S_{n+1} \to S_n$ | función | Sistema inverso forzado: cada hijo hereda padre por construcción. |
| $q_n^{\mathrm{trunc}}: S_{n+1} \to S_n$ | función | Cuantizador alternativo: trunca al prefijo de longitud $p^n$ y proyecta. |
| $\mathrm{Coh}_\pi(p,n)$ | escalar $\in [0,1]$ | Coherencia del sistema inverso $\pi$. |
| $\mathrm{Coh}_{\mathrm{grid}}(p,n)$ | escalar $\in [0,1]$ | Coherencia de la cuantización por truncamiento (control). |
| $\beta_0(G_n)$ | entero | Componentes conexas del grafo $k$-NN sobre $S_n$. (Paper 1) |

---

## 1. Input

- **Tipo:** archivo MIDI Standard (formato 0 o 1).
- **Formato:** ruta absoluta a un `.mid` accesible en sistema de ficheros.
- **Restricciones:**
  - Debe contener al menos un `note_on` con `velocity > 0`.
  - Para eje `beats` se requiere `ticks_per_beat` válido en el header.
  - El motor descarta polifonía implícita: cada `(channel, pitch)` se mantiene como evento individual hasta `note_off`.
  - Pitch range MIDI estándar (0–127), velocity 0–127.

---

## 2. Output

### Para cada combinación (pieza, eje, $p$):

```
out_dir/
├── params.json, params.txt           ← parámetros de la corrida
├── S_n_prototypes_p{p}_n{n}.csv      ← prototipos de S_n (uno por fila, flatten p^n × 13)
├── pi_p{p}_n{n+1}_to_n{n}.csv        ← mapa π: child_id, parent_id
├── f_p{p}_n{n}.csv                   ← cuantizador f_n: residue, prototype_id
├── coherence_hier_p{p}.csv           ← n, Coh_pi, Coh_grid, n_samples_n, n_samples_nplus1
└── audit_p{p}.csv                    ← diagnóstico por padre (V_SC, AI, coherent_count)
```

### Propiedades garantizadas

1. `coherence_hier_p{p}.csv` tiene exactamente $N_{\max} - 1$ filas (una por nivel de transición $n \to n+1$).
2. `Coh_pi`, `Coh_grid` son números racionales $k / p^{n+1}$ con $0 \le k \le p^{n+1}$.
3. `pi_p{p}_n{n+1}_to_n{n}.csv` define una función total: cada `child_id $\in \{0,\dots,|S_{n+1}|-1\}$` aparece exactamente una vez.
4. Para BWV1007 con seed=42: el archivo `coherence_hier_p2.csv` reporta `Coh_pi = 0.500000` para todo $n$ (verificado en gold standard).

---

## 3. Convenciones críticas

| Convención | Valor elegido | Alternativa rechazada | Razón |
|---|---|---|---|
| Indexación de residuos | base 0: $a \in \{0,\dots,p^n-1\}$ | base 1 | Coherente con `numpy` y `i % p**n` en Python. |
| Indexación de niveles $n$ | $n = 1, 2, \dots, N_{\max}$ | $n = 0, \dots, N_{\max}-1$ | $S_1$ tiene ventanas de tamaño $p^1 = p$, no de tamaño 1. |
| Bin beats default | $\Delta_b = 1/12$ ≈ 0.0833 | $\Delta_b = 1/24$ o $1/8$ | $1/12$ resuelve tresillos y semicorcheas; usado en ambos papers. |
| Bin seconds default | $\Delta_s = 0.05$ s | $0.01$ s | Compromiso ruido/resolución; usado en Paper 1. |
| Normalización chroma | $L^1$ por fila si $\sum > 0$, ceros si silencio | $L^2$ | Interpretación probabilística directa. |
| Peso de chroma | $\text{overlap}(t_{\text{on}}, t_{\text{off}}, \text{bin}) \times \text{vel}/127$ | conteo binario | Conserva duración real de las notas. |
| Densidad de onsets $a(t)$ | $\sum_{\text{onsets}} \text{vel}/127$ por bin | conteo simple | Pondera articulación. |
| Concatenación H + a | $X = [H \mid \alpha a]$ con $\alpha = 1$ | escalado adaptativo | Misma magnitud que probabilidades cromáticas. |
| Distancia entre ventanas | $L^2$ promediada en tiempo: $d(W,W') = \sqrt{\frac{1}{N}\sum_{i=0}^{N-1} \|W_i - W'_i\|_2^2}$ | $L^2$ no-promediada | Discretización del producto interno en $L^2(\mathbb{Z}_p, \mu_p)$ (Paper 2 §3, Serre Ch.1 §3). |
| Agregación por residuo | mediana componente-a-componente | promedio | Robusta a outliers; coincide con definición de $W_{p,n}(a)$ en Paper 2. |
| Tope de ventanas por residuo | `MAX_WINDOWS_PER_RESIDUE = 800` | sin tope | Control de memoria; suficientemente grande para todos los corpus probados. |
| Step de ventaneo | `step = 2` (default) | `step = 1` | Reduce redundancia de ventanas casi-idénticas. |
| K-means inicial | $K = 16$ centros, semilla `seed = 42` fija | k-means++ adaptativo | Reproducibilidad bit-equivalente. |
| Hijos por padre $K_{\text{child}}$ | 2 por default | $p$ o $p^n$ | Mantiene $|S_n|$ moderado; se permite override CLI. |
| Tamaño de muestra K-means | $M = 800$ ventanas | todas las ventanas | Velocidad sin pérdida estadística. |
| Biblioteca MIDI | `mido` (default) | `pretty_midi` | Discrepancia documental con §Method del Paper 2; se ofrecerá adaptador `pretty_midi` opcional. |
| Time-axis "beats" | $u = \text{tick} / \text{ticks\_per\_beat}$ | $u = \text{seconds} \times \text{tempo}/60$ | Independiente de cambios de tempo. |
| Iteraciones K-means | máximo 30, parada temprana si $\|c_{k+1}-c_k\| < 10^{-12}$ | sin tope | Convergencia rápida en estos espacios. |
| Sub-muestreo K-means $S_1$ | $M = 800$ ventanas equiespaciadas (`np.linspace`) | aleatorio | Reproducible. |

---

## 4. Algoritmo (pseudocódigo)

### 4.1 Pipeline completo

```
INPUT: archivo MIDI, primo p, axis ∈ {seconds, beats}, Nmax, K, Kchild, M, step, seed

PASO 1 — Parsing:
    eventos ← parse_midi_notes_{seconds,beats}(MIDI)
    H ← chroma_series_duration(eventos, Δ)        # (T, 12)
    a ← onset_density_series(eventos, Δ)          # (T,)
    X ← [H | α·a]                                 # (T, 13), α=1

PASO 2 — Construcción de la torre de ventanas agregadas W_n:
    Para n = 1, …, Nmax:
        N ← p^n
        ventanas ← {(start, X[start:start+N, :]) | start = 0, step, 2·step, …}
        para cada residuo a ∈ {0, …, p^n-1}:
            ventanas_a ← primeras MAX_WINDOWS_PER_RESIDUE con start ≡ a (mod p^n)
            W_{p,n}(a) ← mediana componente-a-componente de ventanas_a

PASO 3 — Diccionario inicial S_1 (K-means):
    muestra ← M ventanas de tamaño p, equiespaciadas
    centros ← K-means(muestra, K, seed)
    S_1 ← {centros}                              # (|S_1|, p, 13)
    f_1: a ↦ argmin_j d(W_{p,1}(a), S_1[j])

PASO 4 — Construcción jerárquica con π forzado:
    Para n = 1, …, Nmax-1:
        Para cada residuo b ∈ {0,…,p^{n+1}-1}:
            trunc_b ← W_{p,n+1}(b)[:p^n, :]
            parent(b) ← argmin_j d(trunc_b, S_n[j])
        Agrupar W_{p,n+1}(b) por parent(b).
        Para cada padre j ∈ S_n:
            niños_j ← K-means(ventanas con parent=j, Kchild, seed)
            agregar niños_j a S_{n+1}
            π[child_id] ← j  para cada child de niños_j.

PASO 5 — Cuantización completa:
    f_{n+1}: b ↦ argmin_j d(W_{p,n+1}(b), S_{n+1}[j])

PASO 6 — Coherencias:
    Para n = 1, …, Nmax-1:
        valid_b ← {b ∈ {0,…,p^{n+1}-1} : W_{p,n+1}(b) y W_{p,n}(b mod p^n) son válidos}
        match_pi   ← #{b ∈ valid_b : π(f_{n+1}(b)) == f_n(b mod p^n)}
        match_grid ← #{b ∈ valid_b : q_n^trunc(W_{p,n+1}(b)[:p^n]) == f_n(b mod p^n)}
        Coh_pi(n)   ← match_pi   / p^{n+1}
        Coh_grid(n) ← match_grid / p^{n+1}

PASO 7 — Auditoría por padre:
    Para cada n y cada clase padre a ∈ {0, …, p^n-1}:
        siblings ← {a, a+p^n, a+2·p^n, …, a+(p-1)·p^n}
        valid_siblings ← siblings ∩ valid_b
        V_SC_pi   ← |{π(f_{n+1}(b)) : b ∈ valid_siblings}|
        AI_pi     ← f_n(a) ∈ {π(f_{n+1}(b)) : b ∈ valid_siblings}
        coherent_count_pi ← #{b ∈ valid_siblings : π(f_{n+1}(b)) == f_n(a)}
        análogo para trunc.

OUTPUT: prototypes S_n, mapas f_n, π, Coh_pi/Coh_grid por nivel, audit por padre.
```

### 4.2 Definiciones formales (ver Paper 2 §3)

$$
\mathrm{Coh}_\pi(p,n) \;=\; \frac{1}{p^{n+1}}\;\#\bigl\{\, b \in \{0,\dots,p^{n+1}-1\} \;:\; \pi_{n+1,n}\!\bigl(f_{n+1}(b)\bigr) \;=\; f_n(b \bmod p^n) \,\bigr\}.
$$

$$
\mathrm{Coh}_\pi^{\mathrm{valid}}(p,n) \;=\; \frac{\#\{\text{coherentes}\}}{\#\{b : W_{p,n+1}(b)\text{ y }W_{p,n}(b \bmod p^n)\text{ existen}\}}.
$$

---

## 5. Invariantes verificables

| # | Invariante | Verificación |
|---|---|---|
| I1 | $\mathrm{Coh}_\pi(p,n) \in \{k/p^{n+1} : k \in \mathbb{Z}, 0 \le k \le p^{n+1}\}$ | `numerador * p**(n+1)` debe ser entero. |
| I2 | $\pi_{n+1,n}$ es total: cada `child_id` aparece exactamente una vez en `pi_p{p}_n{n+1}_to_n{n}.csv`. | Comparar `set(pi['child_id']) == range(|S_{n+1}|)`. |
| I3 | $|S_n| \le K \cdot K_{\text{child}}^{n-1}$ con $|S_1| \le K$. | `nrows(prototypes_n) ≤ ...`. |
| I4 | Si la pieza es estructuralmente $p$-aria con (SC) y (AI) densas, entonces $\mathrm{Coh}_\pi(p,n) = 1/p$ y $\mathrm{Coh}_\pi^{\mathrm{valid}}(p,n) = 1$ (Proposición prop:null_floor del Paper 2). | Para BWV1007 + $p=2$: `Coh_pi = 0.500` exacto. |
| I5 | El diccionario $S_1$ es invariante bajo permutación de etiquetas inicial (`np.random.shuffle(idx)` con `seed=42`). | Reproducir con seed=42 dos veces ⇒ misma matriz. |
| I6 | Para semilla fija y mismo input MIDI, los CSV de salida son bit-equivalentes en macOS arm64 / Python 3.13.3. | `sha256sum coherence_hier_p2.csv` debe coincidir con el manifiesto. |
| I7 | $\mathrm{Coh}_{\mathrm{grid}} \le \mathrm{Coh}_\pi$ no se exige; ambos son métricas independientes. (Falsable por las suites Bach polifónicas.) | Documental. |

---

## 6. Ejemplos mínimos verificados

### Ejemplo 1 — Toy binario perfecto (verificable a mano)

**Input:** Serie sintética $X \in \mathbb{R}^{16 \times 13}$ donde $X_i = e_{i \bmod 2}$ (vector canónico alternado en las dos primeras coordenadas, resto cero).
- $p = 2$, $N_{\max} = 2$, $K = 2$, $K_{\text{child}} = 2$, $M = 16$, $\text{step} = 1$, seed=42.

**Cálculo manual:**
- $W_{2,1}(0) = e_0$, $W_{2,1}(1) = e_1$ (mediana sobre las 8 ventanas pares e impares).
- $S_1 = \{e_0, e_1\}$ (K-means con $K=2$ converge en 1 iteración).
- $f_1(0) = 0$, $f_1(1) = 1$.
- Para $n=1 \to 2$: cada $W_{2,2}(b)$ es una ventana de tamaño 2; los 4 residuos $b=0,1,2,3$ tienen padres por truncamiento $b \bmod 2$, así $\pi$ está perfectamente alineado con $f$.
- $\mathrm{Coh}_\pi(2,1) = 4/4 = 1$. $\mathrm{Coh}_\pi^{\mathrm{valid}}(2,1) = 1$.

**Output esperado:** `coherence_hier_p2.csv` con fila `n=1, Coh_pi=1.000000, Coh_grid=1.000000, n_samples_n=2, n_samples_nplus1=4`.

### Ejemplo 2 — BWV1007 Prelude binario (gold standard del Paper 2)

**Input:** `data/midi/bwv1007_prelude.mid`, $p=2$, axis=beats, $N_{\max} = 5$, $K=16$, $K_{\text{child}}=2$, $M=800$, step=2, seed=42.

**Output esperado** (verificado en `outputs/paper_profinite_hier/bwv1007_prelude/beats/p2/coherence_hier_p2.csv`):

| $n$ | `Coh_pi` | `Coh_grid` |
|---:|---:|---:|
| 1 | 0.500000 | (variable) |
| 2 | 0.500000 | (variable) |
| 3 | 0.500000 | (variable) |
| 4 | 0.500000 | (variable) |

**Tolerancia:** `Coh_pi` exacto (1/2). `Coh_grid` puede variar por seed pero debe quedar en $[0.3, 0.7]$.

### Ejemplo 3 — BWV1007 ternario (rango)

Mismos parámetros, $p=3$, $N_{\max}=4$.

**Output esperado:**

| $n$ | `Coh_pi` |
|---:|---:|
| 1 | $\in [0.67, 0.999]$ |
| 2 | $\in [0.67, 0.999]$ |
| 3 | $\in [0.67, 0.999]$ |

(Rango establecido por Paper 2 abstract para benchmark binario+ternario; tolerancia operativa $\pm 0.01$ por variabilidad K-means.)

---

## 7. Valores de referencia (gold standard) — ambos papers

### Paper 2 — torre jerárquica

| Pieza | Eje | $p$ | $n$ | `Coh_pi` esperado | Tolerancia |
|---|---|---:|---:|---:|---|
| BWV1007-1 (Prelude) | beats | 2 | 1–4 | 0.500000 exacto | $0$ (estructural) |
| BWV1007-1 | beats | 3 | 1–3 | $\in [0.67, 0.999]$ | $\pm 0.01$ |
| BWV1007-1 | beats | 5 | 1–2 | $\in [0.67, 0.999]$ | $\pm 0.01$ |
| BWV1007-1 | beats | 7 | 1 | $\ge 1/7 = 0.143$ | $\pm 0.01$ |
| BWV1008-1 | beats | 2 | 1–4 | 0.500000 exacto (denso) | $0$ |
| BWV1009-1 | beats | 2 | 1–4 | 0.500000 exacto (denso) | $0$ |
| Sarabande BWV1007 | beats | 3 | $r=p=3$, $n=3$ | $\approx 0.90$ | $\pm 0.05$ |
| Prelude BWV1007 mismatched | beats | 3 | $r=2, n=3$ → $r=3$ | $0.90 \to 0.36$ | $\pm 0.05$ |
| BWV1049, BWV1050, BWV1079, Goldberg | beats | 3 | varios | $\in [0.34, 0.999]$ | $\pm 0.05$ |

### Paper 2 — null model

| Pieza | $p$ | $n$ | $p$-valor esperado |
|---|---:|---:|---:|
| Sarabande BWV1007 | 3 | 2 | 0.030 |
| Sarabande BWV1007 | 3 | 3 | $< 0.01$ |
| Sarabande BWV1007 | 3 | 4 | 0.030 |
| Prelude BWV1007 | 3 | 2–4 | $> 0.30$ |

### Paper 1 — Phase I (multiscale, β₀)

| Cantidad | Valor esperado | Fuente |
|---|---|---|
| $R_{\mathrm{ctrl}}$ (ratio control primes 5,7 vs 2,3) | $\le 1$ globalmente | abstract |
| $\beta_0(G_n) \to 1$ en niveles altos para suites monofónicas | sí | §5 |
| $|\Delta_{23}|$ en toys | $\le 5$ | §5 |

### Pisos arquitectónicos

| $p$ | piso $1/p$ |
|---:|---:|
| 2 | 0.500 |
| 3 | 0.333... |
| 5 | 0.200 |
| 7 | 0.143 |

---

## 8. Hipótesis estructurales (Paper 2, prop:null_floor)

Para que el piso $\mathrm{Coh}_\pi(p,n) = 1/p$ se alcance EXACTAMENTE:

- **(SC) Sibling-Coverage:** para cada clase-padre $a \in \{0,\dots,p^n-1\}$, los $p$ hijos siblings $\{a, a+p^n, \dots, a+(p-1)p^n\}$ están todos presentes en `valid_b` (i.e. `n_valid_siblings == p`).
- **(AI) Ancestor-Inclusion:** el prototipo padre $f_n(a)$ aparece en el conjunto $\{\pi(f_{n+1}(b)) : b \in \text{siblings}\}$ (i.e. al menos uno de los hijos identificados con padre coincide).

Estas hipótesis se verifican vía las columnas `V_SC_pi`, `AI_pi` del archivo `audit_p{p}.csv`.

---

## 9. Salida del Movimiento 1

Este `MATH-SPEC.md` fija la convención. Cualquier modificación al algoritmo o a los parámetros default debe:

1. Versionar (`v1.0.0` actual; bump a `v1.1.0` si cambian pisos numéricos esperados).
2. Re-ejecutar tests `tests/paper_values/` y actualizar gold standard.
3. Documentar la decisión en `CHANGELOG.md` y `PROJECT-STATE.md`.

**Próximo movimiento:** Movimiento 2 (`CODE-AUDIT.md`) — clasificar cada archivo Python, verificar reproducción de los valores arriba, identificar discrepancias.
