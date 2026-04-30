#!/usr/bin/env python3
"""
build_padic_balls_fig.py — Genera la figura de bolas p-ádicas anidadas para el paper.
Estructura fractal de Z_p: círculo de radio 1 → p círculos con centros en anillo de radio 1/3,
ángulos 2π/p; recursión 3–4 niveles. Un color por nivel; los más pequeños se dibujan encima.
Salida: Paper-ZpMusic-20250206/paper/figs/padic_nested_balls.pdf
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Paper-ZpMusic-20250206" / "paper" / "figs"
OUT.mkdir(parents=True, exist_ok=True)

# Colores por nivel (nivel 0 = exterior; último nivel = más pequeño y visible)
COLORS = [
    "#0d47a1",  # azul oscuro
    "#00838f",  # teal
    "#f9a825",  # ámbar
    "#c62828",  # rojo
    "#6a1b9a",  # púrpura
]
# Grosor de línea por nivel (los pequeños más gruesos para que se vean)
LINEWIDTHS = [1.2, 1.0, 1.1, 1.3, 1.5]


def draw_nested_balls_recursive(ax, cx, cy, r, level, max_level, p, colors, lws):
    """
    Dibuja un círculo de centro (cx, cy) y radio r; luego p hijos con centros
    sobre un círculo de radio r/3, separados 2π/p, con radios suficientemente
    pequeños para que sean ajenos; recursión hasta max_level.
    Orden: primero se dibujan los hijos (recursión), luego el círculo actual,
    para que el nivel actual quede debajo y los pequeños encima y visibles.
    """
    # Hijos: centros en círculo de radio r/3, ángulo 2π*k/p
    ring_r = r / 3.0
    # Radio hijo para que p círculos en ese anillo sean ajenos:
    # distancia entre centros adyacentes = 2*ring_r*sin(π/p) → radio hijo <= ring_r*sin(π/p)
    child_r = ring_r * np.sin(np.pi / p) * 0.86
    # Dibujar este círculo primero (nivel actual); luego hijos encima para que los pequeños se vean
    color = colors[level] if level < len(colors) else colors[-1]
    lw = lws[level] if level < len(lws) else lws[-1]
    circle = plt.Circle((cx, cy), r, fill=False, ec=color, lw=lw)
    ax.add_patch(circle)
    # Recursión: hijos se dibujan después y quedan encima (más pequeños = más visibles)
    if level < max_level:
        for k in range(p):
            angle = 2 * np.pi * k / p
            nx = cx + ring_r * np.cos(angle)
            ny = cy + ring_r * np.sin(angle)
            draw_nested_balls_recursive(ax, nx, ny, child_r, level + 1, max_level, p, colors, lws)


def draw_nested_balls(ax, cx, cy, p, n_max=4, r0=1.0, colors=None, linewidths=None):
    """
    Dibuja la estructura de bolas p-ádicas: círculo exterior de radio r0,
    luego recursión con centros en anillo r/3 y ángulo 2π/p.
    """
    colors = colors or COLORS
    linewidths = linewidths or LINEWIDTHS
    draw_nested_balls_recursive(ax, cx, cy, r0, 0, n_max, p, colors, linewidths)
    ax.text(cx, cy - r0 - 0.08, rf'$n=0$: 1; $n=1$: ${p}$; ... $n={n_max}$: ${p**n_max}$', ha='center', fontsize=8)


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))
    for ax in (ax1, ax2):
        ax.set_aspect("equal")
        ax.axis("off")
    # Escalar para abajo: r0 < 1 para que los círculos queden enteros dentro del marco
    r0 = 0.78
    margin = 0.35
    # Cada panel tiene su propio rango; círculo centrado en 0 dentro del panel
    # Panel izquierdo: datos en [-1-r0-margin, -1+r0+margin] x [-r0-margin, r0+margin] → normalizamos a centro 0
    cx1, cy1 = 0.0, 0.0
    cx2, cy2 = 0.0, 0.0
    ax1.set_xlim(-r0 - margin, r0 + margin)
    ax1.set_ylim(-r0 - margin, r0 + margin)
    ax2.set_xlim(-r0 - margin, r0 + margin)
    ax2.set_ylim(-r0 - margin, r0 + margin)
    draw_nested_balls(ax1, cx1, cy1, 3, n_max=4, r0=r0)
    ax1.set_title(r"$p=3$: $\mathbb{Z}_3$", fontsize=12)
    draw_nested_balls(ax2, cx2, cy2, 5, n_max=4, r0=r0)
    ax2.set_title(r"$p=5$: $\mathbb{Z}_5$", fontsize=12)
    fig.suptitle(
        r"Estructura fractal de $\mathbb{Z}_p$: cada bola contiene $p$ bolas (clases residuales mod $p^n$)",
        fontsize=10,
        y=1.02,
    )
    plt.tight_layout(pad=0.8)
    out_path = OUT / "padic_nested_balls.pdf"
    plt.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close()
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
