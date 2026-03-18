"""
Shared helpers for individual DBM operation comparison plots.
"""

import argparse
from typing import Dict, Optional, Tuple

from matplotlib import pyplot as plt

from plot_common import add_polygon, add_segment, save_figure, style_axes, zone_polygon


VIEWPORT = (0.0, 6.0, 0.0, 6.0)

BASE_CANON = [
    (-1.0, 0.0, -1.0),  # x >= 1
    (1.0, 0.0, 3.0),    # x <= 3
    (0.0, -1.0, -1.0),  # y >= 1
    (0.0, 1.0, 4.0),    # y <= 4
    (-1.0, 1.0, 3.0),   # y - x <= 3
    (1.0, -1.0, 2.0),   # x - y <= 2
]

BASE_POLYGON = zone_polygon(BASE_CANON, VIEWPORT)

OperationSpec = Dict[str, Optional[object]]

OPERATIONS = {
    "constrain": {
        "title": r"$\mathrm{and}(Z, y \geq 2)$",
        "polygon": zone_polygon(BASE_CANON + [(0.0, -1.0, -2.0)], VIEWPORT),
        "segment": None,
    },
    "up": {
        "title": r"$\mathrm{up}(Z)$",
        "polygon": zone_polygon(
            [
                (-1.0, 0.0, -1.0),  # x >= 1
                (0.0, -1.0, -1.0),  # y >= 1
                (-1.0, 1.0, 3.0),   # y - x <= 3
                (1.0, -1.0, 2.0),   # x - y <= 2
            ],
            VIEWPORT,
        ),
        "segment": None,
    },
    "down": {
        "title": r"$\mathrm{down}(Z)$",
        "polygon": zone_polygon(
            [
                (-1.0, 0.0, 0.0),   # x >= 0
                (1.0, 0.0, 3.0),    # x <= 3
                (0.0, -1.0, 0.0),   # y >= 0
                (0.0, 1.0, 4.0),    # y <= 4
                (-1.0, 1.0, 3.0),   # y - x <= 3
                (1.0, -1.0, 2.0),   # x - y <= 2
            ],
            VIEWPORT,
        ),
        "segment": None,
    },
    "reset": {
        "title": r"$\mathrm{reset}(Z, x=2)$",
        "polygon": None,
        "segment": ((2.0, 1.0), (2.0, 4.0)),
    },
    "free": {
        "title": r"$\mathrm{free}(Z, y)$",
        "polygon": zone_polygon(
            [
                (-1.0, 0.0, -1.0),  # x >= 1
                (1.0, 0.0, 3.0),    # x <= 3
                (0.0, -1.0, 0.0),   # y >= 0
            ],
            VIEWPORT,
        ),
        "segment": None,
    },
}  # type: Dict[str, OperationSpec]


def draw_before_panel(ax) -> None:
    """
    Draw the common before-panel zone.
    """
    style_axes(ax, VIEWPORT)
    add_polygon(ax, BASE_POLYGON, facecolor="#9ecae1", edgecolor="#2b6cb0", alpha=0.45)
    ax.set_title(r"$Z$", fontsize=12, pad=6)


def draw_after_panel(ax, title, polygon, segment) -> None:
    """
    Draw the transformed zone and keep the original outline for comparison.
    """
    style_axes(ax, VIEWPORT)
    add_polygon(
        ax,
        BASE_POLYGON,
        facecolor="#ffffff",
        edgecolor="#777777",
        fill=False,
        linewidth=1.4,
        linestyle=(0, (4, 3)),
        zorder=1,
    )

    if polygon is not None:
        add_polygon(ax, polygon, facecolor="#a1d99b", edgecolor="#2f855a", alpha=0.42, zorder=2)
    if segment is not None:
        add_segment(ax, segment[0], segment[1], color="#2f855a", linewidth=3.2, zorder=3)

    ax.set_title(title, fontsize=12, pad=6)


def build_operation_figure(name: str):
    """
    Build one before/after comparison figure.
    """
    spec = OPERATIONS[name]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.7), constrained_layout=True)
    draw_before_panel(axes[0])
    draw_after_panel(axes[1], spec["title"], spec["polygon"], spec["segment"])
    return fig


def render_operation(name: str) -> None:
    """
    CLI entry point for one operation plot.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    save_figure(build_operation_figure(name), args.output)
