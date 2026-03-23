"""
Render representation-maintenance figures for reduce and intern.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from fed_plot import VIEWPORT, parser_and_output, plot_piecewise, save_figure, style_axes


context = Context(["x", "y"])
x = context.x
y = context.y

BEFORE = ((x >= 1) & (x <= 3) & (y >= 1) & (y <= 2)) | ((x >= 2) & (x <= 4) & (y >= 1) & (y <= 2))
AFTER = BEFORE.copy().reduce()
INTERN = BEFORE.copy()
INTERN.intern()


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.7), constrained_layout=True)

    plot_piecewise(axes[0], BEFORE, VIEWPORT, ["#9ecae1", "#fdd49e"])
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"$F$ before $\mathrm{reduce}$", fontsize=12, pad=6)

    plot_piecewise(axes[1], AFTER, VIEWPORT, ["#a1d99b"])
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$\mathrm{reduce}(F)$", fontsize=12, pad=6)

    plot_piecewise(axes[2], INTERN, VIEWPORT, ["#9ecae1", "#fdd49e"])
    style_axes(axes[2], VIEWPORT)
    axes[2].set_title(r"$\mathrm{intern}(F)$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
