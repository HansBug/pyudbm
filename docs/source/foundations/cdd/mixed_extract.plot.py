"""
Render extraction of boolean guards plus DBM fragments from a mixed CDD.
"""

import argparse

from matplotlib import pyplot as plt

from pyudbm import Context

from dbm_plot import plot_region, save_figure, style_axes


VIEWPORT = (0.0, 6.2, 0.0, 5.0)

base = Context(["x", "y"], name="c")
ctx = base.to_cdd_context(bools=["door_open"])

STATE = (
    ((ctx.x >= 1) & (ctx.x <= 2) & (ctx.y >= 1) & (ctx.y <= 3) & ctx.door_open)
    | ((ctx.x >= 4) & (ctx.x <= 5) & (ctx.y >= 2) & (ctx.y <= 4) & ~ctx.door_open)
).reduce()

EXTRACTED = []
pending = STATE
while not pending.is_false():
    extraction = pending.extract_bdd_and_dbm()
    guard_dict = extraction.bdd_part.bdd_traces().to_dicts(sparse=False)[0]
    EXTRACTED.append((guard_dict, extraction.dbm.to_cdd().to_federation()))
    pending = extraction.remainder


def _guard_label(guard_dict):
    parts = []
    for key, value in guard_dict.items():
        if value is None:
            continue
        parts.append("{0}={1}".format(key, "T" if value else "F"))
    return ", ".join(parts) if parts else "True"


def build_figure():
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.6), constrained_layout=True)

    colors = [
        ("#9ecae1", "#2b6cb0"),
        ("#fdd0a2", "#d94801"),
    ]
    for (guard_dict, fragment), (face, edge) in zip(EXTRACTED, colors):
        plot_region(
            axes[0],
            fragment,
            VIEWPORT,
            facecolor=face,
            edgecolor=edge,
            alpha=0.42,
            linewidth=2.0,
            show_unbounded=False,
        )
    style_axes(axes[0], VIEWPORT)
    axes[0].set_title(r"$\bigvee_i (B_i \wedge D_i)$", fontsize=12, pad=6)
    axes[0].text(0.18, 4.55, "door_open=T", fontsize=10, color="#2b6cb0")
    axes[0].text(3.55, 4.55, "door_open=F", fontsize=10, color="#d94801")

    for axis, (guard_dict, fragment), (face, edge) in zip(axes[1:], EXTRACTED, colors):
        plot_region(
            axis,
            fragment,
            VIEWPORT,
            facecolor=face,
            edgecolor=edge,
            alpha=0.48,
            linewidth=2.0,
            show_unbounded=False,
        )
        style_axes(axis, VIEWPORT)
        axis.set_title(_guard_label(guard_dict), fontsize=12, pad=6)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    save_figure(build_figure(), args.output)
