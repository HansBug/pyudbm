"""
Render the before/after reset comparison figure.
"""

from pyudbm import Context

from dbm_op import render_operation


context = Context(["x", "y"])
x = context.x
y = context.y

if __name__ == "__main__":
    render_operation(
        title=r"$\mathrm{reset}(Z, x=2)$",
        before_zone=(x >= 1) & (x <= 3) & (y >= 1) & (y <= 4) & (y - x <= 3) & (x - y <= 2),
        after_zone=(x == 2) & (y >= 1) & (y <= 4),
        fill=False,
    )
