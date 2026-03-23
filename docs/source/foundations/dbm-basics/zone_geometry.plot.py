"""
Render the running DBM zone as a language-neutral SVG figure.
"""

import argparse

from matplotlib import pyplot as plt

from dbm_basics_plot_common import DOC_CONTEXT, plot_region, save_figure, style_axes


x = DOC_CONTEXT.x
y = DOC_CONTEXT.y

RUNNING_ZONE = (x >= 0) & (x <= 5) & (y >= 0) & (y <= 3) & (x - y <= 2)

VIEWPORT = (0.0, 6.0, 0.0, 4.0)


def draw_boundary_lines(ax) -> None:
    """
    Draw the key boundary lines of the running zone.
    """
    ax.axvline(5.0, color="#6f6f6f", linestyle="--", linewidth=1.2, zorder=1)
    ax.axhline(3.0, color="#6f6f6f", linestyle="--", linewidth=1.2, zorder=1)
    ax.plot([0.0, 6.0], [-2.0, 4.0], color="#6f6f6f", linestyle="--", linewidth=1.2, zorder=1)

    ax.text(5.05, 0.22, r"$x=5$", fontsize=10, color="#555555")
    ax.text(0.16, 3.08, r"$y=3$", fontsize=10, color="#555555")
    ax.text(3.05, 0.75, r"$x-y=2$", fontsize=10, color="#555555", rotation=33)


def build_figure():
    """
    Build the zone geometry figure.
    """
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    plot_region(
        ax,
        RUNNING_ZONE,
        VIEWPORT,
        facecolor="#9ecae1",
        edgecolor="#2b6cb0",
        alpha=0.45,
        linewidth=2.0,
        zorder=2,
        show_unbounded=False,
    )
    draw_boundary_lines(ax)
    style_axes(ax, VIEWPORT)
    ax.set_title(r"$Z$", fontsize=12, pad=8)
    return fig


def main() -> None:
    """
    Render the figure to the requested path.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    save_figure(build_figure(), args.output)


if __name__ == "__main__":
    main()
