"""
Shared helpers for DBM-basics plots.
"""

import math
from typing import Any, Iterable, Optional, Tuple

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

VIEWPORT2D = Tuple[float, float, float, float]


def style_axes(ax, viewport: VIEWPORT2D) -> None:
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


def plot_region(
    ax: Any,
    region: Any,
    viewport: VIEWPORT2D,
    *,
    facecolor: Optional[Any],
    edgecolor: Any,
    alpha: float = 0.28,
    linewidth: float = 2.0,
    linestyle: Any = "-",
    zorder: int = 2,
    show_unbounded: bool = False,
    hide_markers: bool = False,
    solid_capstyle: Optional[str] = None,
) -> Any:
    """
    Plot one DBM / federation region with the shared pyudbm visualization API.
    """
    xmin, xmax, ymin, ymax = viewport
    result = region.plot(
        ax=ax,
        limits=((xmin, xmax), (ymin, ymax)),
        facecolor=facecolor,
        edgecolor=edgecolor,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        zorder=zorder,
        show_unbounded=show_unbounded,
        annotate=False,
        label="_nolegend_",
    )

    if hide_markers:
        for marker in result.markers:
            marker.set_visible(False)

    if solid_capstyle is not None:
        for boundary in result.boundaries:
            boundary.set_solid_capstyle(solid_capstyle)

    return result


def save_figure(fig, output: str) -> None:
    """
    Save a figure as SVG.
    """
    fig.savefig(output, format="svg", bbox_inches="tight")
    plt.close(fig)
