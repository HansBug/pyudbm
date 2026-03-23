"""
Render the before/after free comparison figure.
"""

from pyudbm import Context

from dbm_op import render_operation


context = Context(["x", "y"])
x = context.x
y = context.y

if __name__ == "__main__":
    render_operation(
        title=r"$\mathrm{free}(Z, y)$",
        before_zone=(x >= 1) & (x <= 3) & (y >= 1) & (y <= 4) & (y - x <= 3) & (x - y <= 2),
        after_zone=(x >= 1) & (x <= 3) & (y >= 0),
        fill=True,
    )
