"""
Minimal DBM visualization examples.

Run:

    python test_dbm_visual.py
"""

from matplotlib import pyplot as plt

from pyudbm import Context


def main():
    context_1d = Context(["x"])
    context_2d = Context(["x", "y"])

    dbm_1d = ((context_1d.x > 0) & (context_1d.x <= 3)).to_dbm_list()[0]
    dbm_1d_2 = ((context_1d.x >= 2) & (context_1d.x < 5)).to_dbm_list()[0]
    dbm_2d = ((context_2d.x < 3) & (context_2d.y <= 2) & (context_2d.x - context_2d.y < 2)).to_dbm_list()[0]
    dbm_2d_overlay = ((context_2d.x >= 2) & (context_2d.y >= 1) & (context_2d.x <= 4)).to_dbm_list()[0]
    dbm_2d_y_unbounded = (context_2d.x <= 2).to_dbm_list()[0]
    dbm_2d_quadrant_unbounded = ((context_2d.x >= 1) & (context_2d.y >= 2)).to_dbm_list()[0]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.reshape(-1)

    dbm_1d.plot(ax=axes[0])
    dbm_1d_2.plot(ax=axes[0])
    axes[0].set_title("DBM 1D: Same Ax Overlay")
    axes[0].grid(True, linestyle="--", alpha=0.3)
    axes[0].legend(loc="upper right")

    dbm_2d.plot(ax=axes[1])
    dbm_2d_overlay.plot(ax=axes[1])
    axes[1].set_title("DBM 2D: Same Ax Overlay")
    axes[1].grid(True, linestyle="--", alpha=0.3)
    axes[1].legend(loc="upper right")

    dbm_2d_y_unbounded.plot(ax=axes[2])
    axes[2].set_title("DBM 2D: Upper Side Unbounded")
    axes[2].grid(True, linestyle="--", alpha=0.3)
    axes[2].legend(loc="upper right")

    dbm_2d_quadrant_unbounded.plot(ax=axes[3])
    axes[3].set_title("DBM 2D: Two-Sided Unbounded")
    axes[3].grid(True, linestyle="--", alpha=0.3)
    axes[3].legend(loc="upper right")

    fig.suptitle("pyudbm DBM Visualization Demo")
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
