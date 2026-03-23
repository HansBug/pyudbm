"""
Render the federation free_clock operation figure.
"""

from pyudbm import Context

from fed_plot import WIDE_VIEWPORT, build_before_after_figure, parser_and_output, save_figure


context = Context(["x", "y"])
x = context.x
y = context.y

BEFORE = (x >= 1) & (x <= 3) & (y >= 1) & (y <= 4) & (y - x <= 3) & (x - y <= 2)
AFTER = BEFORE.free_clock(y)


if __name__ == "__main__":
    save_figure(
        build_before_after_figure(
            BEFORE,
            AFTER,
            viewport=WIDE_VIEWPORT,
            before_title=r"$F$",
            after_title=r"$\mathrm{freeClock}(F, y)$",
        ),
        parser_and_output(),
    )
