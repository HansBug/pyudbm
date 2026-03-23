"""
Render a non-convex subtraction example for the federations tutorial.
"""

import argparse

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes


VIEWPORT = (0.0, 6.0, 0.0, 6.0)

context = Context(["x", "y"])
x = context.x
y = context.y

OUTER = (x >= 1) & (x <= 5) & (y >= 1) & (y <= 5)
HOLE = (x >= 2) & (x <= 4) & (y >= 2) & (y <= 4)
RESULT = OUTER - HOLE


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.7), constrained_layout=True)

    plot_region(
        axes[0],
        OUTER,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.45,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"$Z$", fontsize=12, pad=6)

    plot_region(
        axes[1],
        OUTER,
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
        HOLE,
        VIEWPORT,
        facecolor="#fcbba1",
        edgecolor="#cb181d",
        alpha=0.55,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$H$", fontsize=12, pad=6)

    plot_region(
        axes[2],
        RESULT,
        VIEWPORT,
        facecolor="#a1d99b",
        edgecolor="#2f855a",
        alpha=0.42,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(axes[2], VIEWPORT)
    axes[2].set_title(r"$Z - H$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    save_figure(build_figure(), args.output)
