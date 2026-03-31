"""
Render a schematic successor-cost comparison.
"""

import argparse

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from dbm_plot import save_figure


LABELS = [r"$g \cap$", r"$reset$", r"$up$", r"$I \cap$", r"$Extra$", r"$close$"]
DENSE_COSTS = [2.1, 0.8, 0.4, 1.9, 1.0, 3.7]
LU_COSTS = [2.1, 0.8, 0.4, 1.9, 1.0, 2.0]


def build_figure():
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.8), constrained_layout=True, sharey=True)

    for ax, values, title, color in [
        (axes[0], DENSE_COSTS, "Dense canonical pipeline", "#4c78a8"),
        (axes[1], LU_COSTS, "LU-aware pipeline", "#54a24b"),
    ]:
        ax.bar(LABELS, values, color=color, alpha=0.82, width=0.72)
        ax.set_ylim(0.0, 4.2)
        ax.set_ylabel("schematic relative cost", fontsize=10)
        ax.set_title(title, fontsize=12, pad=6)
        ax.grid(axis="y", color="#d9d9d9", linewidth=0.6, alpha=0.7)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=10)
        ax.tick_params(axis="y", labelsize=9)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    save_figure(build_figure(), args.output)
