"""
Render the federation decomposition / size figure.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from fed_plot import VIEWPORT, parser_and_output, plot_piecewise, save_figure, style_axes


context = Context(["x", "y"])
x = context.x
y = context.y

FEDERATION = ((x >= 1) & (x <= 2) & (y >= 1) & (y <= 3)) | ((x >= 4) & (x <= 5) & (y >= 2) & (y <= 4))


def build_figure():
    fig, ax = plt.subplots(figsize=(4.4, 3.7), constrained_layout=True)
    plot_piecewise(ax, FEDERATION, VIEWPORT, ["#9ecae1", "#fdd49e"])
    style_axes(ax, VIEWPORT)
    ax.text(
        1.5,
        2.0,
        r"$D_1$",
        fontsize=11,
        ha="center",
        va="center",
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "#666666", "alpha": 0.9},
    )
    ax.text(
        4.5,
        3.0,
        r"$D_2$",
        fontsize=11,
        ha="center",
        va="center",
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "#666666", "alpha": 0.9},
    )
    ax.set_title(r"$F = D_1 \cup D_2$", fontsize=12, pad=6)
    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
