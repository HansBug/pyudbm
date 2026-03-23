"""
Render property-oriented federation figures.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes
from fed_plot import VIEWPORT, WIDE_VIEWPORT, draw_point, parser_and_output, plot_piecewise


context = Context(["x", "y"])
x = context.x
y = context.y

FED = ((x >= 1) & (x <= 2) & (y >= 1) & (y <= 3)) | ((x >= 4) & (x <= 5) & (y >= 2) & (y <= 4))
ZERO_COVERING = (x >= 0) & (x <= 2) & (y >= 0) & (y <= 2)
ZERO_ONLY = context.get_zero_federation()
EMPTY = (x == 1) & (x != 1)
LEFT = (x >= 2) & (x <= 3) & (y >= 2) & (y <= 3)
RIGHT = (x >= 1) & (x <= 4) & (y >= 1) & (y <= 4)


def build_figure():
    fig, axes = plt.subplots(2, 3, figsize=(11.6, 7.0), constrained_layout=True)
    flat = axes.ravel()

    plot_piecewise(flat[0], FED, VIEWPORT, ["#9ecae1", "#fdd49e"])
    style_axes(flat[0], VIEWPORT)
    flat[0].set_title(r"$F = D_1 \cup D_2$", fontsize=12, pad=6)

    plot_region(
        flat[1],
        RIGHT,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.35,
        linewidth=2.0,
        show_unbounded=False,
    )
    plot_region(
        flat[1],
        LEFT,
        VIEWPORT,
        facecolor="#fdd49e",
        edgecolor="#d94801",
        alpha=0.55,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(flat[1], VIEWPORT)
    flat[1].set_title(r"$A \subset B$", fontsize=12, pad=6)

    plot_region(
        flat[2],
        FED,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.35,
        linewidth=2.0,
        show_unbounded=False,
    )
    draw_point(flat[2], 1.5, 2.0, color="#2f855a", filled=True)
    draw_point(flat[2], 3.0, 2.0, color="#cb181d", filled=False)
    style_axes(flat[2], VIEWPORT)
    flat[2].set_title(r"$\mathrm{contains}$", fontsize=12, pad=6)

    plot_region(
        flat[3],
        ZERO_COVERING,
        WIDE_VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.35,
        linewidth=2.0,
        show_unbounded=False,
    )
    draw_point(flat[3], 0.0, 0.0, color="#2f855a", filled=True)
    style_axes(flat[3], WIDE_VIEWPORT)
    flat[3].set_title(r"$\mathrm{hasZero}(F)$", fontsize=12, pad=6)

    plot_region(
        flat[4],
        ZERO_ONLY,
        WIDE_VIEWPORT,
        facecolor="none",
        edgecolor="#2f855a",
        alpha=1.0,
        linewidth=3.0,
        show_unbounded=False,
        hide_markers=True,
        solid_capstyle="round",
    )
    draw_point(flat[4], 0.0, 0.0, color="#2f855a", filled=True)
    style_axes(flat[4], WIDE_VIEWPORT)
    flat[4].set_title(r"$\mathrm{isZero}(F)$", fontsize=12, pad=6)

    plot_region(
        flat[5],
        EMPTY,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.35,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(flat[5], VIEWPORT)
    flat[5].set_title(r"$\mathrm{isEmpty}(F)$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
