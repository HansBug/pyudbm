"""
Render a one-clock forward-search walkthrough.
"""

import argparse

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from dbm_plot import save_figure


PANELS = [
    (r"$Z_0$", 0.0, 5.0, "#4c78a8", False),
    (r"$Z_0 \cap g_0$", 2.0, 5.0, "#f58518", False),
    (r"$reset_{\{x\}}$", 0.0, 0.0, "#e45756", True),
    (r"$Z_1$", 0.0, 3.0, "#54a24b", False),
    (r"$Z_1 \cap g_1$", 1.0, 3.0, "#b279a2", False),
    (r"$Z_2$", 0.0, 1.0, "#72b7b2", False),
]


def draw_interval(ax, title: str, left: float, right: float, color: str, point_only: bool) -> None:
    ax.set_xlim(-0.3, 5.3)
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks(range(0, 6))
    ax.set_yticks([])
    ax.grid(axis="x", color="#d9d9d9", linewidth=0.6, alpha=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_linewidth(1.0)
    ax.tick_params(axis="x", labelsize=9, length=3, width=0.8)
    ax.set_title(title, fontsize=11, pad=5)

    y = 0.52
    if point_only:
        ax.scatter([left], [y], s=58, color=color, zorder=3)
    else:
        ax.hlines(y, left, right, color=color, linewidth=5.0, zorder=2)
        ax.scatter([left, right], [y, y], s=42, color=color, zorder=3)


def build_figure():
    fig, axes = plt.subplots(2, 3, figsize=(10.8, 5.4), constrained_layout=True)

    for ax, (title, left, right, color, point_only) in zip(axes.flat, PANELS):
        draw_interval(ax, title, left, right, color, point_only)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    save_figure(build_figure(), args.output)
