"""
Render the federation up operation figure.
"""

from pyudbm import Context

from fed_plot import VIEWPORT, build_before_after_figure, parser_and_output, save_figure


context = Context(["x", "y"])
x = context.x
y = context.y

BEFORE = (x >= 1) & (x <= 3) & (y >= 1) & (y <= 4) & (y - x <= 3) & (x - y <= 2)
AFTER = BEFORE.up()


if __name__ == "__main__":
    save_figure(
        build_before_after_figure(BEFORE, AFTER, viewport=VIEWPORT, before_title=r"$F$", after_title=r"$\mathrm{up}(F)$"),
        parser_and_output(),
    )
