"""
Render an exact-family / extrapolation / cover-check figure.
"""

import argparse

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes


VIEWPORT = (-0.4, 8.4, -0.2, 2.2)
COLORS = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#b279a2"]

context = Context(["x", "y"])
x = context.x
y = context.y


def exact_zone(shift: int):
    return (x - y <= shift) & (y - x <= -shift) & (y >= 0) & (y <= 1) & (x <= shift + 1)


EXACT_FAMILY = [exact_zone(shift) for shift in range(6)]
COLLAPSED = exact_zone(5).extrapolate_max_bounds({"x": 2, "y": 1})
CANDIDATE = exact_zone(6)


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.7), constrained_layout=True)

    for zone, color in zip(EXACT_FAMILY, COLORS):
        plot_region(
            axes[0],
            zone,
            VIEWPORT,
            facecolor=color,
            edgecolor=color,
            alpha=0.42,
            linewidth=2.0,
            zorder=3,
            show_unbounded=False,
        )
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"Exact $Z_k$ family", fontsize=12, pad=6)

    for zone in EXACT_FAMILY:
        plot_region(
            axes[1],
            zone,
            VIEWPORT,
            facecolor="none",
            edgecolor="#b0b0b0",
            alpha=1.0,
            linewidth=1.0,
            linestyle=(0, (3, 3)),
            zorder=1,
            show_unbounded=False,
        )
    plot_region(
        axes[1],
        COLLAPSED,
        VIEWPORT,
        facecolor="#a1d99b",
        edgecolor="#2f855a",
        alpha=0.40,
        linewidth=2.2,
        zorder=3,
        show_unbounded=True,
    )
    style_axes(axes[1], VIEWPORT)
    axes[1].set_title(r"$\mathrm{Extra}_M(Z_k)$ for large $k$", fontsize=12, pad=6)

    plot_region(
        axes[2],
        COLLAPSED,
        VIEWPORT,
        facecolor="none",
        edgecolor="#2f855a",
        alpha=1.0,
        linewidth=2.1,
        linestyle=(0, (4, 3)),
        zorder=1,
        show_unbounded=True,
    )
    plot_region(
        axes[2],
        CANDIDATE,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.55,
        linewidth=2.0,
        zorder=3,
        show_unbounded=False,
    )
    style_axes(axes[2], VIEWPORT)
    axes[2].set_title(r"$Z_{6} \subseteq F_{\mathrm{passed}}$", fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    save_figure(build_figure(), args.output)
