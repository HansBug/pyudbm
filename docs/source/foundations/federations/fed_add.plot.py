"""
Render the convex-union figure for federation addition.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes
from fed_plot import VIEWPORT, parser_and_output


context = Context(["x", "y"])
x = context.x
y = context.y

A = (x >= 1) & (x <= 2) & (y >= 1) & (y <= 4)
B = (x >= 4) & (x <= 5) & (y >= 1) & (y <= 4)
EXACT = A | B
ADDED = A + B


def build_figure():
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.7), constrained_layout=True)

    plot_region(
        axes[0],
        EXACT,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.45,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"$A \mid B$", fontsize=12, pad=6)

    plot_region(
        axes[1],
        EXACT,
        VIEWPORT,
        facecolor="none",
        edgecolor="#777777",
        alpha=1.0,
        linewidth=1.4,
        linestyle=(0, (4, 3)),
        zorder=1,
        show_unbounded=False,
    )
    plot_region(
        axes[1],
        ADDED,
        VIEWPORT,
        facecolor="#fdd49e",
        edgecolor="#d94801",
        alpha=0.45,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$A + B$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
