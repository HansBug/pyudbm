"""
Render the federation exact-union figure.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes
from fed_plot import parser_and_output


VIEWPORT = (0.0, 6.0, 0.0, 5.0)
DASH = (0, (4, 3))

context = Context(["x", "y"])
x = context.x
y = context.y

A = (x >= 1) & (x <= 2) & (y >= 1) & (y <= 4)
B = (x >= 4) & (x <= 5) & (y >= 1) & (y <= 4)
EXACT = A | B


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.7), constrained_layout=True)

    plot_region(
        axes[0],
        B,
        VIEWPORT,
        facecolor="none",
        edgecolor="#c26d1f",
        alpha=1.0,
        linewidth=1.4,
        linestyle=DASH,
        zorder=1,
        show_unbounded=False,
    )
    plot_region(
        axes[0],
        A,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.45,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"$A$", fontsize=12, pad=6)

    plot_region(
        axes[1],
        A,
        VIEWPORT,
        facecolor="none",
        edgecolor="#2b6cb0",
        alpha=1.0,
        linewidth=1.4,
        linestyle=DASH,
        zorder=1,
        show_unbounded=False,
    )
    plot_region(
        axes[1],
        B,
        VIEWPORT,
        facecolor="#fdd49e",
        edgecolor="#c26d1f",
        alpha=0.48,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$B$", fontsize=12, pad=6)

    plot_region(
        axes[2],
        A,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.45,
        linewidth=2.0,
        zorder=2,
        show_unbounded=False,
    )
    plot_region(
        axes[2],
        B,
        VIEWPORT,
        facecolor="#fdd49e",
        edgecolor="#c26d1f",
        alpha=0.48,
        linewidth=2.0,
        zorder=2,
        show_unbounded=False,
    )
    plot_region(
        axes[2],
        A,
        VIEWPORT,
        facecolor="none",
        edgecolor="#2b6cb0",
        alpha=1.0,
        linewidth=1.4,
        linestyle=DASH,
        zorder=4,
        show_unbounded=False,
    )
    plot_region(
        axes[2],
        B,
        VIEWPORT,
        facecolor="none",
        edgecolor="#c26d1f",
        alpha=1.0,
        linewidth=1.4,
        linestyle=DASH,
        zorder=4,
        show_unbounded=False,
    )
    plot_region(
        axes[2],
        EXACT,
        VIEWPORT,
        facecolor="none",
        edgecolor="#333333",
        alpha=1.0,
        linewidth=2.0,
        zorder=5,
        show_unbounded=False,
    )
    style_axes(axes[2], VIEWPORT)
    axes[2].set_title(r"$A \mid B$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
