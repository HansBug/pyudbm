"""
Render representation-maintenance figures for reduce and intern.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region
from fed_plot import VIEWPORT, parser_and_output, plot_piecewise, save_figure, style_axes


context = Context(["x", "y"])
x = context.x
y = context.y

BEFORE = (x <= 1) | (x >= 1)
AFTER = (x <= 1) | (x >= 1)
AFTER.reduce()
INTERN = (x <= 1) | (x >= 1)
INTERN.reduce()
INTERN.intern()


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.7), constrained_layout=True)

    plot_piecewise(axes[0], BEFORE, VIEWPORT, ["#9ecae1", "#fdd49e"])
    style_axes(axes[0], VIEWPORT)
    axes[0].text(0.45, 5.45, r"$x \leq 1$", fontsize=10, color="#2b6cb0")
    axes[0].text(3.65, 5.45, r"$x \geq 1$", fontsize=10, color="#c26d1f")
    axes[0].set_title(r"$F$ before $\mathrm{reduce}$", fontsize=12, pad=6)

    plot_region(
        axes[1],
        AFTER,
        VIEWPORT,
        facecolor="#a1d99b",
        edgecolor="#2f855a",
        alpha=0.42,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$\mathrm{reduce}(F)$", fontsize=12, pad=6)

    plot_region(
        axes[2],
        AFTER,
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
        axes[2],
        INTERN,
        VIEWPORT,
        facecolor="#a1d99b",
        edgecolor="#2f855a",
        alpha=0.42,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[2], VIEWPORT)
    axes[2].set_title(r"$\mathrm{intern}(\mathrm{reduce}(F))$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
