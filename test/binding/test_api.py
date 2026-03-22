import pytest

import pyudbm
import pyudbm.binding
from pyudbm.binding import Constraint, Context, Federation, FloatValuation, IntValuation, Valuation, VariableDifference


@pytest.mark.unittest
class TestBindingApi:
    def setup_method(self):
        self.c = Context(["x", "y", "z"], name="c")

    def test_binding_exports(self):
        assert Context is pyudbm.binding.Context
        assert Federation is pyudbm.binding.Federation
        assert IntValuation is pyudbm.binding.IntValuation
        assert FloatValuation is pyudbm.binding.FloatValuation
        assert pyudbm.binding.Clock is not None
        assert pyudbm.binding.Context is not None
        assert pyudbm.binding.Federation is not None
        assert pyudbm.binding.IntValuation is not None
        assert pyudbm.binding.FloatValuation is not None

    def test_root_exports(self):
        assert pyudbm.Clock is pyudbm.binding.Clock
        assert pyudbm.Context is pyudbm.binding.Context
        assert pyudbm.Federation is pyudbm.binding.Federation
        assert pyudbm.IntValuation is pyudbm.binding.IntValuation
        assert pyudbm.FloatValuation is pyudbm.binding.FloatValuation

    def test_int_valuation(self):
        c = self.c
        valuation = IntValuation(c)

        with pytest.raises(KeyError):
            _ = valuation["not_in_federation"]

        with pytest.raises(TypeError):
            valuation["x"] = 0.1

        valuation["x"] = 1
        valuation["y"] = 1
        valuation["z"] = 1

        assert ((c.x == 1) & (c.y == 1) & (c.z == 1)).contains(valuation)
        assert not ((c.x == 2) & (c.y == 1) & (c.z == 1)).contains(valuation)

    def test_float_valuation(self):
        c = self.c
        valuation = FloatValuation(c)

        with pytest.raises(KeyError):
            _ = valuation["not_in_federation"]

        valuation["x"] = 1.0
        valuation["y"] = 1.01
        valuation["z"] = 1

        assert not ((c.x == 1) & (c.y == 1) & (c.z == 1)).contains(valuation)
        assert ((c.x == 1) & (c.y < 2) & (c.y > 1) & (c.z == 1)).contains(valuation)

    def test_set_operations(self):
        c = self.c

        assert (c.x == 1) == ((c.x >= 1) & (c.x <= 1))
        assert (c.x != 1) == ((c.x > 1) | (c.x < 1))
        assert (c.x == 1) & (c.y == 1) == (c.y == 1) & (c.x == 1)
        assert (c.x == 1) | (c.y == 1) == (c.y == 1) | (c.x == 1)
        assert (c.x == 1) & ((c.y == 1) | (c.z == 1)) == ((c.x == 1) & (c.y == 1)) | ((c.x == 1) & (c.z == 1))
        assert (c.x - c.y <= 1) == (c.y - c.x >= -1)
        assert ((c.x - c.y == 1) & (c.x == 1)) == ((c.x == 1) & (c.y == 0))
        assert (c.x - c.y != 1) == ((c.x - c.y > 1) | (c.x - c.y < 1))

    def test_zero(self):
        c = self.c

        assert not (c.x == 1).has_zero()
        assert not (c.x > 1).has_zero()
        assert (c.x < 1).has_zero()
        assert ((c.x == 1) & (c.z == 2)).set_zero() == ((c.x == 0) & (c.y == 0) & (c.z == 0))
        assert ((c.x == 1) & (c.z == 2)).set_zero().has_zero()

    def test_update_clocks(self):
        c = self.c

        assert ((c.x == 1) | (c.z == 2)).update_value(c.x, 2) == (c.x == 2)
        assert ((c.x == 1) & (c.z == 2)).reset_value(c.x) == ((c.x == 0) & (c.z == 2))

    def test_str(self):
        c = self.c
        assert str((c.x == 1) & (c.y == 1)) == "(c.x==1 & c.x==c.y & c.y==1)"

    def test_copy(self):
        c = self.c
        original = (c.x - c.y) == 1
        intersected = original.copy()
        unioned = intersected.copy()

        assert original == intersected

        intersected &= c.z == 1
        unioned |= c.z == 1

        assert original != intersected
        assert unioned != intersected

    def test_reduce(self):
        c = self.c
        federation = (c.x >= 1) | (c.x <= 1)

        assert federation.get_size() == 2
        federation.reduce()
        assert federation.get_size() == 1

    def test_convex_hull(self):
        c = self.c
        d1 = (c.x >= 1) & (c.x <= 2) & (c.y >= 1) & (c.y <= 2)
        d2 = (c.x >= 3) & (c.x <= 4) & (c.y >= 3) & (c.y <= 4)
        d3 = (c.x - c.y <= 1) & (c.y - c.x <= 1) & (c.x >= 1) & (c.y >= 1) & (c.x <= 4) & (c.y <= 4)

        assert (d1 + d2) == d3
        assert (d1 | d2).convex_hull() == d3

        d1 += d2
        assert d1 == d3

    def test_sub(self):
        c = self.c
        d1 = (c.x >= 1) & (c.x <= 2) & (c.y >= 1) & (c.y <= 2)
        d2 = (c.x >= 3) & (c.x <= 4) & (c.y >= 3) & (c.y <= 4)
        d3 = d1 | d2

        assert d3 - d1 == d2
        d3 -= d2
        assert d3 == d1

    def test_up_down(self):
        c = Context(["x", "y"])
        d1 = (c.x >= 1) & (c.x <= 2) & (c.y >= 1) & (c.y <= 2)
        d2 = (c.x - c.y <= 1) & (c.y - c.x <= 1) & (c.x >= 1) & (c.y >= 1)
        d3 = (c.x - c.y <= 1) & (c.y - c.x <= 1) & (c.x <= 2) & (c.y <= 2)

        assert d1.up() == d2
        assert d1.down() == d3

    def test_non_mutating_operations(self):
        c = self.c
        original = (c.x - c.y <= 1) & (c.y - c.x <= 1) & (c.x >= 1) & (c.y >= 1) & (c.y <= 4)
        trial = original.copy()

        trial.up()
        trial.down()
        trial.free_clock(c.x)
        trial.convex_hull()
        trial.predt(trial)
        trial.reset_value(c.x)

        assert original == trial

    def test_set_init(self):
        c = self.c
        federation = (c.x - c.y <= 1) & (c.y - c.x <= 1) & (c.x >= 1) & (c.y >= 1) & (c.y <= 4)

        federation.set_init()

        assert federation == ((c.x >= 0) & (c.y >= 0) & (c.z >= 0))
        assert federation != ((c.x >= 1) & (c.y >= 0) & (c.z >= 0))

    def test_federation_relations(self):
        c = self.c
        d1 = (c.x - c.y <= 1) & (c.y - c.x <= 1) & (c.x >= 1) & (c.y >= 1) & (c.y <= 4)
        d2 = (c.x - c.y <= 1) & (c.y - c.x <= 1) & (c.x >= 1)

        assert d1 <= d2
        assert d1 < d2
        assert d2 >= d1
        assert d2 > d1
        assert d1 != d2

    def test_intern(self):
        c = self.c
        federation = c["x"] - c["y"] <= 1
        federation.intern()

    def test_extrapolate_max_bounds(self):
        c = self.c
        federation = (c.x - c.y <= 1) & (c.x < 150) & (c.z < 150) & (c.x - c.z <= 1000)
        bounds = {c.x: 100, c.y: 300, c.z: 400}

        assert federation.extrapolate_max_bounds(bounds) == ((c.x - c.y <= 1) & (c.z < 150))

    def test_free_clock(self):
        c = self.c
        assert ((c.x >= 10) & (c.y >= 10)).free_clock(c.x) == (c.y >= 10)

    def test_zero_federation(self):
        c = self.c
        assert c.get_zero_federation().is_zero()
        assert c.get_zero_federation().has_zero()
        assert Federation(c).is_zero()
        assert not (c.x == 1).is_zero()
        assert (c.x == 1) != c.get_zero_federation()

    def test_hash(self):
        c = self.c
        assert (c.x == 1).hash() == (c.x == 1).hash()
        assert (c.y == 1).hash() != (c.x == 1).hash()
        assert ((c.x == 1) | (c.y == 1)).hash() == ((c.y == 1) | (c.x == 1)).hash()

    def test_is_empty(self):
        c = self.c

        assert ((c.x == 1) & (c.x != 1)).is_empty()
        assert not ((c.x == 1) | (c.x != 1)).is_empty()
        assert not (c.x == 1).is_empty()
        assert not ((c.x == 1) & (c.y != 1)).is_empty()
        assert (((c.x == 1) & (c.x != 1)) | ((c.y == 1) & (c.y != 1))).is_empty()

    def test_clock_public_edge_cases(self):
        context = Context(["x", "y"], name="c")
        other = Context(["x"], name="other")
        anonymous = Context(["x"])

        assert repr(context.x) == "<Clock c.x>"
        assert anonymous.x.get_full_name() == "x"
        assert context.x == context.x
        assert context.x != context.y

        with pytest.raises(TypeError):
            _ = context.x - 1

        with pytest.raises(ValueError):
            _ = context.x - other.x

        with pytest.raises(TypeError):
            _ = context.x <= 1.5

        with pytest.raises(TypeError):
            _ = context.x >= 1.5

        with pytest.raises(TypeError):
            _ = context.x < 1.5

        with pytest.raises(TypeError):
            _ = context.x > 1.5

        with pytest.raises(TypeError):
            _ = context.x <= True

        with pytest.raises(TypeError):
            _ = context.x >= False

        with pytest.raises(TypeError):
            _ = context.x < True

        with pytest.raises(TypeError):
            _ = context.x > False

        assert (context.x == True) is False
        assert (context.x != True) is True

    def test_valuation_public_edge_cases(self, caplog):
        context = Context(["x", "y"])
        other = Context(["x"])
        valuation = Valuation(context)

        with pytest.raises(TypeError):
            valuation[1] = 1

        with pytest.raises(ValueError):
            valuation[other.x] = 1

        valuation["x"] = 1
        valuation[context.y] = 2

        assert valuation[context.y] == 2

        with caplog.at_level("ERROR", logger="pyudbm"):
            valuation.check()

        assert "Clock y is not present in the clock valuation." not in caplog.text

        incomplete = Valuation(context)
        incomplete["x"] = 1

        with caplog.at_level("ERROR", logger="pyudbm"):
            incomplete.check()

        assert "Clock y is not present in the clock valuation." in caplog.text

        float_valuation = FloatValuation(context)
        int_valuation = IntValuation(context)

        with pytest.raises(TypeError):
            int_valuation["x"] = True

        with pytest.raises(TypeError):
            float_valuation["x"] = "1.0"

        with pytest.raises(TypeError):
            float_valuation["x"] = True

    def test_variable_difference_public_edge_cases(self):
        context = Context(["x", "y"])
        other = Context(["x"])

        with pytest.raises(ValueError):
            VariableDifference([context.x])

        with pytest.raises(ValueError):
            VariableDifference([context.x, other.x])

        difference = context.x - context.y

        with pytest.raises(TypeError):
            _ = difference <= 0.5

        with pytest.raises(TypeError):
            _ = difference >= 0.5

        with pytest.raises(TypeError):
            _ = difference < 0.5

        with pytest.raises(TypeError):
            _ = difference > 0.5

        with pytest.raises(TypeError):
            _ = difference <= True

        with pytest.raises(TypeError):
            _ = difference >= False

        with pytest.raises(TypeError):
            _ = difference < True

        with pytest.raises(TypeError):
            _ = difference > False

        assert not (difference == object())
        assert difference != object()
        assert not (difference == True)
        assert difference != True

    def test_constraint_public_validation(self):
        context = Context(["x", "y"])
        other = Context(["x"])

        with pytest.raises(TypeError):
            Constraint(context.x, None, 1.5, False)

        with pytest.raises(ValueError):
            Constraint(None, None, 1, False)

        with pytest.raises(TypeError):
            Constraint("x", None, 1, False)

        with pytest.raises(TypeError):
            Constraint(context.x, "y", 1, False)

        with pytest.raises(ValueError):
            Constraint(context.x, other.x, 1, False)

    def test_federation_public_validation(self):
        context = Context(["x", "y"])
        other = Context(["x", "y"])
        federation = context.x <= 1

        with pytest.raises(TypeError):
            Federation(object())

        with pytest.raises(TypeError):
            _ = federation & 1

        with pytest.raises(ValueError):
            _ = federation & (other.x <= 1)

        assert not (federation == object())

        valuation = Valuation(context)
        valuation["x"] = 0
        valuation["y"] = 0

        with pytest.raises(TypeError):
            federation.contains(valuation)

        with pytest.raises(ValueError):
            federation.update_value(other.x, 1)

        with pytest.raises(TypeError):
            federation.free_clock("x")

        with pytest.raises(ValueError):
            federation.free_clock(other.x)

    def test_extrapolate_max_bounds_public_validation(self):
        context = Context(["x", "y", "z"])
        other = Context(["x"])
        federation = (context.x - context.y <= 1) & (context.x < 150) & (context.z < 150) & (context.x - context.z <= 1000)

        result = federation.extrapolate_max_bounds({"x": 100, "y": 300, "z": 400})
        assert result == ((context.x - context.y <= 1) & (context.z < 150))

        with pytest.raises(ValueError, match="requires bounds for every clock"):
            federation.extrapolate_max_bounds({"x": 100})

        with pytest.raises(ValueError, match="Duplicate bounds provided for clock: x"):
            federation.extrapolate_max_bounds({"x": 100, context.x: 200, context.y: 300, context.z: 400})

        with pytest.raises(TypeError):
            federation.extrapolate_max_bounds({context.x: 100, context.y: 200, 1: 300})

        with pytest.raises(ValueError):
            federation.extrapolate_max_bounds({other.x: 100, context.y: 200, context.z: 300})

    def test_context_public_edge_cases(self, caplog):
        with caplog.at_level("WARNING", logger="pyudbm"):
            warned = Context(["clocks", "x"])

        assert "already has attribute clocks" in caplog.text
        assert warned["clocks"].name == "clocks"

        context = Context(["x"])
        context.set_name("renamed")

        assert context.x.get_full_name() == "renamed.x"

        with pytest.raises(KeyError):
            _ = context["missing"]

        ambiguous = Context(["x", "x"])
        with pytest.raises(KeyError, match="Ambiguous clock name: x"):
            _ = ambiguous["x"]

    def test_camel_case_binding_methods_are_gone(self):
        context = Context(["x", "y"])
        federation = context.x <= 1

        assert not hasattr(context.x, "getFullName")
        assert not hasattr(context, "setName")
        assert not hasattr(context, "getZeroFederation")
        assert not hasattr(federation, "freeClock")
        assert not hasattr(federation, "setZero")
        assert not hasattr(federation, "hasZero")
        assert not hasattr(federation, "setInit")
        assert not hasattr(federation, "convexHull")
        assert not hasattr(federation, "updateValue")
        assert not hasattr(federation, "resetValue")
        assert not hasattr(federation, "getSize")
        assert not hasattr(federation, "extrapolateMaxBounds")
        assert not hasattr(federation, "isZero")
        assert not hasattr(federation, "isEmpty")
