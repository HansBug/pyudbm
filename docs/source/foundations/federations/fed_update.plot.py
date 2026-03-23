"""
Render the federation update/reset figure.
"""

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes
from fed_plot import WIDE_VIEWPORT, parser_and_output


context = Context(["x", "y"])
x = context.x
y = context.y

BASE = (x >= 1) & (x <= 3) & (y >= 1) & (y <= 4) & (y - x <= 3) & (x - y <= 2)
UPDATED = BASE.update_value(x, 2)
RESET = BASE.reset_value(x)


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.7), constrained_layout=True)

    for ax, region, title, fill in [
        (axes[0], BASE, r"$F$", True),
        (axes[1], UPDATED, r"$\mathrm{updateValue}(F, x{=}2)$", False),
        (axes[2], RESET, r"$\mathrm{resetValue}(F, x)$", False),
    ]:
        if ax is not axes[0]:
            plot_region(
                ax,
                BASE,
                WIDE_VIEWPORT,
                facecolor="none",
                edgecolor="#777777",
                alpha=1.0,
                linewidth=1.4,
                linestyle=(0, (4, 3)),
                zorder=1,
                show_unbounded=False,
            )
        plot_region(
            ax,
            region,
            WIDE_VIEWPORT,
            facecolor="#9ecae1" if fill else "none",
            edgecolor="#2b6cb0" if fill else "#2f855a",
            alpha=0.45 if fill else 1.0,
            linewidth=2.0 if fill else 3.0,
            zorder=3,
            show_unbounded=False,
            hide_markers=fill,
            solid_capstyle="round" if not fill else None,
        )
        style_axes(ax, WIDE_VIEWPORT)
        ax.set_title(title, fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    save_figure(build_figure(), parser_and_output())
