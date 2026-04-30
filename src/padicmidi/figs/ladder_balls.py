#!/usr/bin/env python3
"""
build_p_ladder_balls_fig.py — Genera la figura p_ladder_balls.pdf para el paper.
Misma geometría que padic_nested_balls: bolas disjuntas, repartidas simétricamente
en el interior de cada círculo (centros en anillo de radio r/3, ángulos 2π/p;
radio hijo = (r/3)*sin(π/p)*0.92 para garantizar que no se traslapen).
Salida: Paper-ZpMusic-20250206/paper/figs/p_ladder_balls.pdf
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Paper-ZpMusic-20250206" / "paper" / "figs"
OUT.mkdir(parents=True, exist_ok=True)

# Colores por nivel (igual que padic_nested_balls)
COLORS = [
    "#0d47a1",  # azul oscuro
    "#00838f",  # teal
    "#f9a825",  # ámbar
    "#c62828",  # rojo
    "#6a1b9a",  # púrpura
]
LINEWIDTHS = [1.2, 1.0, 1.1, 1.3, 1.5]


def draw_nested_balls_recursive(ax, cx, cy, r, level, max_level, p, colors, lws):
    """
    Dibuja un círculo (cx, cy, r) y p hijos con centros en anillo de radio r/3,
    ángulos 2π*k/p; radio hijo = ring_r*sin(π/p)*0.92 para que sean ajenos.
    """
    ring_r = r / 3.0
    child_r = ring_r * np.sin(np.pi / p) * 0.86
    color = colors[level] if level < len(colors) else colors[-1]
    lw = lws[level] if level < len(lws) else lws[-1]
    ax.add_patch(plt.Circle((cx, cy), r, fill=False, ec=color, lw=lw))
    if level < max_level:
        for k in range(p):
            angle = 2 * np.pi * k / p
            nx = cx + ring_r * np.cos(angle)
            ny = cy + ring_r * np.sin(angle)
            draw_nested_balls_recursive(ax, nx, ny, child_r, level + 1, max_level, p, colors, lws)


def draw_nested_balls(ax, cx, cy, p, n_max=4, r0=1.0):
    """Dibuja la estructura de bolas p-ádicas disjuntas con colores por nivel."""
    draw_nested_balls_recursive(ax, cx, cy, r0, 0, n_max, p, COLORS, LINEWIDTHS)
    ax.text(
        cx, cy - r0 - 0.08,
        rf"$n=0$: 1; $n=1$: ${p}$; ... $n={n_max}$: ${p**n_max}$",
        ha="center", fontsize=8,
    )


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.2))
    for ax in (ax1, ax2):
        ax.set_aspect("equal")
        ax.axis("off")
    r0 = 1.0
    margin = 0.25
    # p=3 (izquierda)
    ax1.set_xlim(-2.2 - margin, -margin)
    ax1.set_ylim(-r0 - margin - 0.1, r0 + margin + 0.1)
    draw_nested_balls(ax1, -1.1, 0, 3, n_max=4, r0=r0)
    ax1.set_title(r"$p=3$: $\mathbb{Z}_3$", fontsize=12)
    # p=5 (derecha)
    ax2.set_xlim(margin, 2.2 + margin)
    ax2.set_ylim(-r0 - margin - 0.1, r0 + margin + 0.1)
    draw_nested_balls(ax2, 1.1, 0, 5, n_max=4, r0=r0)
    ax2.set_title(r"$p=5$: $\mathbb{Z}_5$", fontsize=12)
    fig.suptitle(
        r"Estructura fractal de $\mathbb{Z}_p$: cada bola contiene $p$ bolas (clases residuales mod $p^n$); anidamiento hasta $n=4$.",
        fontsize=9,
        y=1.02,
    )
    plt.tight_layout()
    out_path = OUT / "p_ladder_balls.pdf"
    plt.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close()
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
