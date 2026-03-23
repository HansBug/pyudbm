"""
Shared helpers for federations tutorial plots.
"""

import argparse
from typing import Any, Iterable, Optional, Sequence, Tuple

from matplotlib import pyplot as plt

from dbm_plot import plot_region, save_figure, style_axes

VIEWPORT = (0.0, 6.0, 0.0, 6.0)
WIDE_VIEWPORT = (-0.5, 6.0, -0.5, 6.0)


def parser_and_output() -> str:
    """
    Parse the common ``-o/--output`` argument.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    return parser.parse_args().output


def draw_point(ax: Any, x: float, y: float, *, color: str, filled: bool = True, size: float = 48.0) -> None:
    """
    Draw one test point.
    """
    ax.scatter(
        [x],
        [y],
        s=size,
        facecolors=color if filled else "white",
        edgecolors=color,
        linewidths=1.5,
        zorder=6,
    )


def plot_piecewise(ax: Any, federation: Any, viewport: Tuple[float, float, float, float], colors: Sequence[str]) -> None:
    """
    Plot each DBM piece of one federation with a dedicated color.
    """
    for dbm, color in zip(federation.to_dbm_list(), colors):
        plot_region(
            ax,
            dbm,
            viewport,
            facecolor=color,
            edgecolor=color,
            alpha=0.28,
            linewidth=1.8,
            zorder=2,
            show_unbounded=False,
        )

    plot_region(
        ax,
        federation,
        viewport,
        facecolor="none",
        edgecolor="#333333",
        alpha=1.0,
        linewidth=2.0,
        zorder=5,
        show_unbounded=False,
    )


def build_before_after_figure(
    before: Any,
    after: Any,
    *,
    viewport: Tuple[float, float, float, float] = VIEWPORT,
    before_title: str = r"$F$",
    after_title: str = r"$T(F)$",
    fill_after: bool = True,
) -> Any:
    """
    Build a common before/after comparison figure.
    """
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.7), constrained_layout=True)

    plot_region(
        axes[0],
        before,
        viewport,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.45,
        linewidth=2.0,
        zorder=2,
        show_unbounded=False,
    )
    style_axes(axes[0], viewport)
    axes[0].set_title(before_title, fontsize=12, pad=6)

    plot_region(
        axes[1],
        before,
        viewport,
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
        after,
        viewport,
        facecolor="#a1d99b" if fill_after else "none",
        edgecolor="#2f855a",
        alpha=0.42 if fill_after else 1.0,
        linewidth=2.0 if fill_after else 3.0,
        zorder=3,
        show_unbounded=True,
        hide_markers=not fill_after,
        solid_capstyle="round" if not fill_after else None,
    )
    style_axes(axes[1], viewport)
    axes[1].set_title(after_title, fontsize=12, pad=6)

    return fig
