"""
Render a collective-cover / contains_dbm illustration for CDDs.
"""

import argparse

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes


VIEWPORT = (-0.2, 6.2, -0.2, 3.2)

context = Context(["x", "y"])
x = context.x
y = context.y

PASSED = (
    ((x >= 0) & (x <= 2) & (y >= 0) & (y <= 2))
    | ((x >= 4) & (x <= 6) & (y >= 0) & (y <= 2))
)
CANDIDATE = (x >= 4) & (x <= 5) & (y >= 0) & (y <= 1)


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.5), constrained_layout=True)

    plot_region(
        axes[0],
        PASSED,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.42,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"$F_{\mathrm{passed}}$", fontsize=12, pad=6)

    plot_region(
        axes[1],
        CANDIDATE,
        VIEWPORT,
        facecolor="#a1d99b",
        edgecolor="#2f855a",
        alpha=0.46,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$D$", fontsize=12, pad=6)

    plot_region(
        axes[2],
        PASSED,
        VIEWPORT,
        facecolor="none",
        edgecolor="#7a7a7a",
        alpha=1.0,
        linewidth=1.4,
        linestyle=(0, (4, 3)),
        zorder=1,
        show_unbounded=False,
    )
    plot_region(
        axes[2],
        CANDIDATE,
        VIEWPORT,
        facecolor="#74c476",
        edgecolor="#1b7837",
        alpha=0.55,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[2], VIEWPORT)
    axes[2].set_title(r"$D \subseteq F_{\mathrm{passed}}$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    save_figure(build_figure(), args.output)
