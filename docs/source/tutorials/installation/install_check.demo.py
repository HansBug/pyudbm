from pyudbm import Context, IntValuation, __version__

print(__version__)

context = Context(["x", "y"], name="c")
zone = (context.x < 10) & (context.x - context.y <= 1)

valuation = IntValuation(context)
valuation["x"] = 3
valuation["y"] = 2

print(zone.contains(valuation))
