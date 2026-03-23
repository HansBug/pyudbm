"""
Render the federation set_zero operation figure.
"""

from pyudbm import Context

from fed_plot import WIDE_VIEWPORT, build_before_after_figure, parser_and_output, save_figure


context = Context(["x", "y"])
x = context.x
y = context.y

BEFORE = (x >= 1) & (x <= 3) & (y >= 1) & (y <= 4)
AFTER = BEFORE.copy().set_zero()


if __name__ == "__main__":
    save_figure(
        build_before_after_figure(
            BEFORE,
            AFTER,
            viewport=WIDE_VIEWPORT,
            before_title=r"$F$",
            after_title=r"$\mathrm{setZero}(F)$",
            fill_after=False,
        ),
        parser_and_output(),
    )
