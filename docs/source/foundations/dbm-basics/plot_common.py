"""
Shared helpers for DBM geometry plots.
"""

import math
from typing import Iterable, List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from matplotlib.patches import Polygon


Point = Tuple[float, float]
HalfPlane = Tuple[float, float, float]

EPSILON = 1e-9


def rectangle_polygon(xmin: float, xmax: float, ymin: float, ymax: float) -> List[Point]:
    """
    Create a rectangle polygon.
    """
    return [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]


def clip_polygon_with_half_plane(polygon: Sequence[Point], plane: HalfPlane) -> List[Point]:
    """
    Clip a convex polygon against ``a * x + b * y <= c``.
    """
    if not polygon:
        return []

    a, b, c = plane
    output = []  # type: List[Point]

    def signed_value(point: Point) -> float:
        x, y = point
        return a * x + b * y - c

    def inside(point: Point) -> bool:
        return signed_value(point) <= EPSILON

    def intersection(start: Point, end: Point) -> Point:
        s_value = signed_value(start)
        e_value = signed_value(end)
        denom = s_value - e_value
        if abs(denom) <= EPSILON:
            return end

        ratio = s_value / denom
        return (
            start[0] + ratio * (end[0] - start[0]),
            start[1] + ratio * (end[1] - start[1]),
        )

    points = list(polygon)
    for index, end in enumerate(points):
        start = points[index - 1]
        start_inside = inside(start)
        end_inside = inside(end)

        if start_inside and end_inside:
            output.append(end)
        elif start_inside and not end_inside:
            output.append(intersection(start, end))
        elif not start_inside and end_inside:
            output.append(intersection(start, end))
            output.append(end)

    return output


def zone_polygon(planes: Iterable[HalfPlane], viewport: Tuple[float, float, float, float]) -> List[Point]:
    """
    Build a clipped convex polygon for a zone inside a fixed viewport.
    """
    xmin, xmax, ymin, ymax = viewport
    polygon = rectangle_polygon(xmin, xmax, ymin, ymax)

    for plane in planes:
        polygon = clip_polygon_with_half_plane(polygon, plane)
        if not polygon:
            break

    return polygon


def add_polygon(
    ax,
    polygon: Sequence[Point],
    facecolor: str,
    edgecolor: str,
    alpha: float = 0.28,
    linewidth: float = 2.0,
    linestyle: str = "-",
    fill: bool = True,
    zorder: int = 2,
) -> None:
    """
    Draw a polygon when it is non-empty.
    """
    if not polygon:
        return

    patch = Polygon(
        polygon,
        closed=True,
        facecolor=facecolor if fill else "none",
        edgecolor=edgecolor,
        alpha=alpha if fill else 1.0,
        linewidth=linewidth,
        linestyle=linestyle,
        zorder=zorder,
    )
    ax.add_patch(patch)


def add_segment(
    ax,
    start: Point,
    end: Point,
    color: str,
    linewidth: float = 3.0,
    linestyle: str = "-",
    zorder: int = 3,
) -> None:
    """
    Draw a line segment.
    """
    ax.plot(
        [start[0], end[0]],
        [start[1], end[1]],
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        solid_capstyle="round",
        zorder=zorder,
    )


def style_axes(ax, viewport: Tuple[float, float, float, float]) -> None:
    """
    Apply a consistent language-neutral Cartesian style.
    """
    xmin, xmax, ymin, ymax = viewport
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal", adjustable="box")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(1.0)
    ax.spines["bottom"].set_linewidth(1.0)

    ax.set_xlabel(r"$x$", fontsize=11)
    ax.set_ylabel(r"$y$", fontsize=11, rotation=0, labelpad=8)

    ax.set_xticks(list(integer_ticks(xmin, xmax)))
    ax.set_yticks(list(integer_ticks(ymin, ymax)))
    ax.tick_params(length=3, width=0.8, labelsize=9)
    ax.grid(color="#d9d9d9", linewidth=0.6, alpha=0.7)


def integer_ticks(lower: float, upper: float) -> Iterable[int]:
    """
    Yield integer ticks inside a viewport.
    """
    start = int(math.ceil(lower))
    end = int(math.floor(upper))
    for value in range(start, end + 1):
        yield value


def save_figure(fig, output: str) -> None:
    """
    Save a figure as SVG.
    """
    fig.savefig(output, format="svg", bbox_inches="tight")
    plt.close(fig)
