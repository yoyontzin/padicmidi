#!/usr/bin/env python3
"""
build_padic_tree_fig.py — Árbol p-ádico fractal tipo L-system para el paper.
Estructura ramificada: cada nodo tiene p ramas (como Z_p); gramática tipo Lindenmayer.
Salida (vectorizadas: PDF y SVG):
  padic_tree_p3.pdf/.svg, padic_tree_p5.pdf/.svg  (7 iteraciones)
  padic_tree_p3_10iter.pdf/.svg, padic_tree_p5_10iter.pdf/.svg  (10 iteraciones)
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Paper-ZpMusic-20250206" / "paper" / "figs"
OUT.mkdir(parents=True, exist_ok=True)

# Convención: ramas del mismo nivel (misma profundidad) tienen el mismo color; el color cambia por nivel.
# Nivel 0 = tronco, nivel 1 = primeras ramas, etc. (raíz → puntas).
TREE_COLORS = [
    "#0d47a1",
    "#00695c",
    "#f9a825",
    "#c62828",
    "#6a1b9a",
]


def lsystem_expand(axiom: str, rules: dict, n: int) -> str:
    """Expande el axioma n veces aplicando las reglas."""
    s = axiom
    for _ in range(n):
        s = "".join(rules.get(c, c) for c in s)
    return s


def make_p_ary_rule(p: int) -> str:
    """Regla X -> F [ + X ] [ + + X ] ... (k-ésima rama con k veces '+', ángulo 2π/p entre ramas)."""
    blocks = []
    for k in range(1, p + 1):
        blocks.append("[" + "+" * k + "X]")
    return "F" + "".join(blocks)


def lsystem_draw(
    ax,
    s: str,
    angle_deg: float,
    length0: float,
    scale: float,
    start_angle_deg: float = 90.0,
    start_xy=(0.0, 0.0),
    length_grows_with_depth: bool = False,
    depth_scale_step: float = 0.12,
):
    """
    Interpreta la cadena L-system y dibuja segmentos.
    F = forward (dibuja), [ = push estado, ] = pop, + = gira +angle_deg, - = gira -angle_deg.
    Si length_grows_with_depth=False: longitud = length0 * scale^depth. Usar scale=1/3 para que
    cada nivel sea 1/3 del anterior (primera rama 1, segunda 1/3, tercera 1/9, etc.).
    Si length_grows_with_depth=True: longitud = length0 * (scale + depth * depth_scale_step), así las
    aristas se alargan al subir de nivel y no se amontonan en el centro.
    """
    x, y = start_xy
    angle = np.radians(start_angle_deg)
    stack = []
    segments = []  # list of ((x0,y0),(x1,y1), depth) for coloring
    for c in s:
        depth = len(stack)
        if c == "F":
            if length_grows_with_depth:
                # Aristas más largas en niveles más profundos para evitar solapamiento
                length = length0 * (scale + depth * depth_scale_step)
            else:
                length = length0 * (scale ** depth)
            x1 = x + length * np.cos(angle)
            y1 = y + length * np.sin(angle)
            segments.append(((x, y), (x1, y1), depth))
            x, y = x1, y1
        elif c == "[":
            stack.append((x, y, angle))
        elif c == "]":
            x, y, angle = stack.pop()
        elif c == "+":
            angle += np.radians(angle_deg)
        elif c == "-":
            angle -= np.radians(angle_deg)
    # Dibujar por niveles: todas las aristas del mismo nivel (depth) con el mismo color.
    max_depth = max((d for (_, _, d) in segments), default=0)
    for depth in range(max_depth + 1):
        segs_at_depth = [((a, b), (c, d)) for (a, b), (c, d), dpt in segments if dpt == depth]
        if not segs_at_depth:
            continue
        color = TREE_COLORS[depth % len(TREE_COLORS)]  # un color por nivel
        lw = 2.0 - 0.3 * depth
        lw = max(0.5, lw)
        lc = LineCollection(segs_at_depth, colors=color, linewidths=lw, capstyle="round")
        ax.add_collection(lc)
    return segments


def _draw_tree(ax, p: int, n_iter: int, scale: float = 1/3):
    """Dibuja el árbol p-ádico: p ramas por nodo, n_iter iteraciones. Longitud por nivel = length0 * scale^depth."""
    angle_deg = 360 / p
    rules = {"X": make_p_ary_rule(p), "F": "F"}
    s = lsystem_expand("X", rules, n_iter)
    lsystem_draw(ax, s, angle_deg, length0=0.85, scale=scale, start_angle_deg=90, start_xy=(0, -0.9))
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.3, 1.3)


def main():
    # Proporción del dibujo: xlim 3.5, ylim 2.6 → ratio 3.5:2.6.
    fig_w, fig_h = 8.0, 8.0 * (2.6 / 3.5)
    figsize_single = (fig_w, fig_h)
    # Salida vectorial: PDF y SVG (sin rasterizar; las líneas son vectores).
    formats = ("pdf", "svg")

    # scale = factor por nivel: longitud siguiente = scale * anterior. p=3: 0.4; p=5: 1/3.
    configs = [
        (3, 10, "padic_tree_p3", 0.4),       # p=3: longitud 0.4 de la anterior
        (5, 7, "padic_tree_p5", 1/3),
        (3, 10, "padic_tree_p3_10iter", 0.4),
        (5, 10, "padic_tree_p5_10iter", 1/3),
    ]
    for p, n_iter, base_name, scale in configs:
        # padic_tree_p3: figura más grande para que llene todo el alto y ancho de la imagen
        if base_name == "padic_tree_p3":
            figsize = (12.0, 12.0 * (2.6 / 3.5))
        else:
            figsize = figsize_single
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        ax.set_aspect("equal")
        ax.axis("off")
        _draw_tree(ax, p, n_iter, scale=scale)
        plt.tight_layout(pad=0.1)
        for fmt in formats:
            out_path = OUT / f"{base_name}.{fmt}"
            plt.savefig(out_path, bbox_inches="tight", format=fmt)
            print("Wrote", out_path)
        plt.close()


if __name__ == "__main__":
    main()
