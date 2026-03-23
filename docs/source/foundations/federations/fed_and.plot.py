"""
Render the federation intersection figure.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes
from fed_plot import VIEWPORT, parser_and_output


context = Context(["x", "y"])
x = context.x
y = context.y

LEFT = (x >= 1) & (x <= 4) & (y >= 1) & (y <= 4)
RIGHT = (x >= 3) & (x <= 5) & (y >= 2) & (y <= 5)
INTERSECTION = LEFT & RIGHT


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.7), constrained_layout=True)

    for ax, region, color, title in [
        (axes[0], LEFT, "#9ecae1", r"$A$"),
        (axes[1], RIGHT, "#fdd49e", r"$B$"),
        (axes[2], INTERSECTION, "#a1d99b", r"$A \cap B$"),
    ]:
        plot_region(
            ax,
            region,
            VIEWPORT,
            facecolor=color,
            edgecolor="#333333",
            alpha=0.45,
            linewidth=2.0,
            show_unbounded=False,
        )
        style_axes(ax, VIEWPORT)
        ax.set_title(title, fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
