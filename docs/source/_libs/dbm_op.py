"""
Shared helpers for individual DBM operation comparison plots.
"""

import argparse

from matplotlib import pyplot as plt

from dbm_plot import plot_region, save_figure, style_axes


VIEWPORT = (0.0, 6.0, 0.0, 6.0)


def draw_before_panel(ax, before_zone) -> None:
    """
    Draw the common before-panel zone.
    """
    plot_region(
        ax,
        before_zone,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.45,
        linewidth=2.0,
        zorder=2,
        show_unbounded=False,
    )
    style_axes(ax, VIEWPORT)
    ax.set_title(r"$Z$", fontsize=12, pad=6)


def draw_after_panel(ax, title, before_zone, after_zone, fill) -> None:
    """
    Draw the transformed zone and keep the original outline for comparison.
    """
    plot_region(
        ax,
        before_zone,
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
        ax,
        after_zone,
        VIEWPORT,
        facecolor="#a1d99b" if fill else "none",
        edgecolor="#2f855a",
        alpha=0.42 if fill else 1.0,
        linewidth=2.0 if fill else 3.2,
        zorder=3 if fill else 2,
        show_unbounded=False,
        hide_markers=not fill,
        solid_capstyle="round" if not fill else None,
    )

    style_axes(ax, VIEWPORT)
    ax.set_title(title, fontsize=12, pad=6)


def build_operation_figure(title, before_zone, after_zone, fill):
    """
    Build one before/after comparison figure.
    """
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.7), constrained_layout=True)
    draw_before_panel(axes[0], before_zone)
    draw_after_panel(axes[1], title, before_zone, after_zone, fill)
    return fig


def render_operation(title, before_zone, after_zone, fill) -> None:
    """
    CLI entry point for one operation plot.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    save_figure(build_operation_figure(title, before_zone, after_zone, fill), args.output)
