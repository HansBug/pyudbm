"""
Render the federation predt operation figure.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes
from fed_plot import VIEWPORT, parser_and_output


context = Context(["x", "y"])
x = context.x
y = context.y

GOOD = (x >= 2) & (x <= 4) & (y >= 2) & (y <= 4)
BAD = (x >= 5) & (x <= 6) & (y >= 5) & (y <= 6)
PREDT = GOOD.predt(BAD)


def build_figure():
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.7), constrained_layout=True)

    plot_region(
        axes[0],
        GOOD,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.45,
        linewidth=2.0,
        show_unbounded=False,
    )
    plot_region(
        axes[0],
        BAD,
        VIEWPORT,
        facecolor="#fcbba1",
        edgecolor="#cb181d",
        alpha=0.55,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"$\mathrm{good}$ and $\mathrm{bad}$", fontsize=12, pad=6)

    plot_region(
        axes[1],
        GOOD,
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
        PREDT,
        VIEWPORT,
        facecolor="#a1d99b",
        edgecolor="#2f855a",
        alpha=0.42,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$\mathrm{predt}(\mathrm{good}, \mathrm{bad})$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
