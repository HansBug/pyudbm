"""
Render the federation extrapolate_max_bounds figure.
"""

from pyudbm import Context

from fed_plot import WIDE_VIEWPORT, build_before_after_figure, parser_and_output, save_figure


context = Context(["x", "y"])
x = context.x
y = context.y

BEFORE = (x - y <= 10) & (y < 150)
AFTER = BEFORE.extrapolate_max_bounds({"x": 100, "y": 100})


if __name__ == "__main__":
    save_figure(
        build_before_after_figure(
            BEFORE,
            AFTER,
            viewport=WIDE_VIEWPORT,
            before_title=r"$F$",
            after_title=r"$\mathrm{Extra}_M(F)$",
        ),
        parser_and_output(),
    )
