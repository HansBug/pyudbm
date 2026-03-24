"""
Render backward transition and backward-time examples for CDDs.
"""

import argparse

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes


VIEWPORT = (-0.2, 4.2, -0.2, 4.2)

base = Context(["x", "y"])
ctx = base.to_cdd_context()

POST = (ctx.x == 0) & (ctx.y >= 2) & (ctx.y <= 3)
GUARD = (ctx.x <= 2) & (ctx.y <= 3)
UPDATE = ctx.x == 0
BACK = POST.transition_back(guard=GUARD, update=UPDATE, clock_resets=["x"]).reduce().to_federation()
BACK_PAST = POST.transition_back_past(guard=GUARD, update=UPDATE, clock_resets=["x"]).reduce().to_federation()


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.5), constrained_layout=True)

    plot_region(
        axes[0],
        POST.to_federation(),
        VIEWPORT,
        facecolor="#fcbba1",
        edgecolor="#cb181d",
        alpha=0.6,
        linewidth=2.0,
        show_unbounded=False,
    )
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"$S'$", fontsize=12, pad=6)

    plot_region(
        axes[1],
        POST.to_federation(),
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
        BACK,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.42,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$\mathrm{transition\_back}(S')$", fontsize=12, pad=6)

    plot_region(
        axes[2],
        BACK,
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
        BACK_PAST,
        VIEWPORT,
        facecolor="#a1d99b",
        edgecolor="#2f855a",
        alpha=0.42,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[2], VIEWPORT)
    axes[2].set_title(r"$\mathrm{transition\_back\_past}(S')$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    save_figure(build_figure(), args.output)
