"""
Shared helpers for individual DBM operation comparison plots.
"""

import argparse
from typing import Any, Dict

from matplotlib import pyplot as plt

from dbm_basics_plot_common import DOC_CONTEXT, plot_region, save_figure, style_axes


VIEWPORT = (0.0, 6.0, 0.0, 6.0)

x = DOC_CONTEXT.x
y = DOC_CONTEXT.y

BASE_ZONE = (x >= 1) & (x <= 3) & (y >= 1) & (y <= 4) & (y - x <= 3) & (x - y <= 2)

OperationSpec = Dict[str, Any]

OPERATIONS = {
    "constrain": {
        "title": r"$\mathrm{and}(Z, y \geq 2)$",
        "zone": BASE_ZONE & (y >= 2),
        "fill": True,
    },
    "up": {
        "title": r"$\mathrm{up}(Z)$",
        "zone": (x >= 1) & (y >= 1) & (y - x <= 3) & (x - y <= 2),
        "fill": True,
    },
    "down": {
        "title": r"$\mathrm{down}(Z)$",
        "zone": (x >= 0) & (x <= 3) & (y >= 0) & (y <= 4) & (y - x <= 3) & (x - y <= 2),
        "fill": True,
    },
    "reset": {
        "title": r"$\mathrm{reset}(Z, x=2)$",
        "zone": (x == 2) & (y >= 1) & (y <= 4),
        "fill": False,
    },
    "free": {
        "title": r"$\mathrm{free}(Z, y)$",
        "zone": (x >= 1) & (x <= 3) & (y >= 0),
        "fill": True,
    },
}  # type: Dict[str, OperationSpec]


def draw_before_panel(ax) -> None:
    """
    Draw the common before-panel zone.
    """
    plot_region(
        ax,
        BASE_ZONE,
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


def draw_after_panel(ax, title, zone, fill) -> None:
    """
    Draw the transformed zone and keep the original outline for comparison.
    """
    plot_region(
        ax,
        BASE_ZONE,
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
        zone,
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


def build_operation_figure(name: str):
    """
    Build one before/after comparison figure.
    """
    spec = OPERATIONS[name]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.7), constrained_layout=True)
    draw_before_panel(axes[0])
    draw_after_panel(axes[1], spec["title"], spec["zone"], spec["fill"])
    return fig


def render_operation(name: str) -> None:
    """
    CLI entry point for one operation plot.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    save_figure(build_operation_figure(name), args.output)
