"""
Minimal federation visualization examples.

Run:

    python test_fed_visual.py
"""

from matplotlib import pyplot as plt

from pyudbm import Context


def main():
    context_1d = Context(["x"])
    context_2d = Context(["x", "y"])

    fed_1d = ((context_1d.x > 0) & (context_1d.x < 1)) | ((context_1d.x >= 1) & (context_1d.x <= 2))
    fed_1d_2 = ((context_1d.x >= 3) & (context_1d.x <= 4)) | ((context_1d.x > 4) & (context_1d.x < 5))

    ring_parts = [
        (context_2d.x >= 0) & (context_2d.x <= 3) & (context_2d.y >= 0) & (context_2d.y <= 1),
        (context_2d.x >= 0) & (context_2d.x <= 3) & (context_2d.y >= 2) & (context_2d.y <= 3),
        (context_2d.x >= 0) & (context_2d.x <= 1) & (context_2d.y >= 1) & (context_2d.y <= 2),
        (context_2d.x >= 2) & (context_2d.x <= 3) & (context_2d.y >= 1) & (context_2d.y <= 2),
    ]
    fed_2d = ring_parts[0]
    for part in ring_parts[1:]:
        fed_2d = fed_2d | part

    l_parts = [
        (context_2d.x >= 4) & (context_2d.x <= 6) & (context_2d.y >= 0) & (context_2d.y <= 1),
        (context_2d.x >= 4) & (context_2d.x <= 5) & (context_2d.y >= 1) & (context_2d.y <= 3),
    ]
    fed_2d_2 = l_parts[0] | l_parts[1]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    fed_1d.plot(ax=axes[0])
    fed_1d_2.plot(ax=axes[0])
    axes[0].set_title("Federation 1D: Same Ax Overlay")
    axes[0].grid(True, linestyle="--", alpha=0.3)
    axes[0].legend(loc="upper right")

    fed_2d.plot(ax=axes[1])
    fed_2d_2.plot(ax=axes[1])
    axes[1].set_title("Federation 2D: Same Ax Overlay")
    axes[1].grid(True, linestyle="--", alpha=0.3)
    axes[1].legend(loc="upper right")

    fig.suptitle("pyudbm Federation Visualization Demo")
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
