"""
Render forward delay and reset examples for CDD-backed symbolic states.
"""

import argparse

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes


VIEWPORT = (-0.2, 4.8, -0.2, 4.2)

base = Context(["x", "y"])
ctx = base.to_cdd_context()

SOURCE = (ctx.x >= 1) & (ctx.x <= 2) & (ctx.y >= 0) & (ctx.y <= 1)
DELAYED = SOURCE.delay().to_federation()
RESET = SOURCE.apply_reset({"x": 0}).to_federation()


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.5), constrained_layout=True)

    plot_region(
        axes[0],
        SOURCE.to_federation(),
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.42,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"$S$", fontsize=12, pad=6)

    plot_region(
        axes[1],
        SOURCE.to_federation(),
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
        DELAYED,
        VIEWPORT,
        facecolor="#a1d99b",
        edgecolor="#2f855a",
        alpha=0.42,
        linewidth=2.0,
        zorder=3,
        show_unbounded=True,
    )
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$\mathrm{delay}(S)$", fontsize=12, pad=6)

    plot_region(
        axes[2],
        SOURCE.to_federation(),
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
        RESET,
        VIEWPORT,
        facecolor="#fdd0a2",
        edgecolor="#d94801",
        alpha=0.52,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[2], VIEWPORT)
    axes[2].set_title(r"$\mathrm{reset}_x(S)$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    save_figure(build_figure(), args.output)
