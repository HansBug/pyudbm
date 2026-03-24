"""
Render representative set-relation examples for federation comparisons.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes
from fed_plot import VIEWPORT, parser_and_output


context = Context(["x", "y"])
x = context.x
y = context.y

DASH = (0, (4, 3))

EQ_A = (x >= 1) & (x <= 4) & (y >= 1) & (y <= 4)
EQ_B = (x >= 1) & (x <= 4) & (y >= 1) & (y <= 4)

NE_A = (x >= 1) & (x <= 3) & (y >= 1) & (y <= 3)
NE_B = (x >= 2) & (x <= 5) & (y >= 2) & (y <= 5)

LE_A = (x >= 2) & (x <= 3) & (y >= 2) & (y <= 3)
LE_B = (x >= 1) & (x <= 4) & (y >= 1) & (y <= 4)

GE_A = (x >= 1) & (x <= 4) & (y >= 1) & (y <= 4)
GE_B = (x >= 2) & (x <= 3) & (y >= 2) & (y <= 3)

LT_A = (x >= 2) & (x <= 3) & (y >= 2) & (y <= 4)
LT_B = (x >= 1) & (x <= 5) & (y >= 1) & (y <= 5)

GT_A = (x >= 1) & (x <= 5) & (y >= 1) & (y <= 5)
GT_B = (x >= 2) & (x <= 4) & (y >= 2) & (y <= 3)

PANELS = [
    (EQ_A, EQ_B, r"$A == B$"),
    (NE_A, NE_B, r"$A \neq B$"),
    (LE_A, LE_B, r"$A \leq B$"),
    (GE_A, GE_B, r"$A \geq B$"),
    (LT_A, LT_B, r"$A < B$"),
    (GT_A, GT_B, r"$A > B$"),
]


def draw_pair(ax, left, right, title):
    plot_region(
        ax,
        right,
        VIEWPORT,
        facecolor="#fdd49e",
        edgecolor="#c26d1f",
        alpha=0.35,
        linewidth=2.0,
        zorder=1,
        show_unbounded=False,
    )
    plot_region(
        ax,
        left,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.48,
        linewidth=2.0,
        zorder=2,
        show_unbounded=False,
    )
    plot_region(
        ax,
        right,
        VIEWPORT,
        facecolor="none",
        edgecolor="#c26d1f",
        alpha=1.0,
        linewidth=1.4,
        linestyle=DASH,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(ax, VIEWPORT)
    ax.set_title(title, fontsize=12, pad=6)
    ax.text(0.18, 5.45, r"$A$", fontsize=10, color="#2b6cb0")
    ax.text(0.72, 5.45, r"$B$", fontsize=10, color="#c26d1f")


def build_figure():
    fig, axes = plt.subplots(2, 3, figsize=(11.6, 7.0), constrained_layout=True)

    for ax, (left, right, title) in zip(axes.ravel(), PANELS):
        draw_pair(ax, left, right, title)

    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
