import pytest

import pyudbm


@pytest.mark.unittest
class TestLegacyApi:
    def setup_method(self):
        self.c = pyudbm.Context(["x", "y", "z"], name="c")

    def test_root_exports(self):
        assert pyudbm.Clock is not None
        assert pyudbm.Context is not None
        assert pyudbm.Federation is not None
        assert pyudbm.IntValuation is not None
        assert pyudbm.FloatValuation is not None

    def test_int_valuation(self):
        c = self.c
        valuation = pyudbm.IntValuation(c)

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
        valuation = pyudbm.FloatValuation(c)

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

        assert not (c.x == 1).hasZero()
        assert not (c.x > 1).hasZero()
        assert (c.x < 1).hasZero()
        assert ((c.x == 1) & (c.z == 2)).setZero() == ((c.x == 0) & (c.y == 0) & (c.z == 0))
        assert ((c.x == 1) & (c.z == 2)).setZero().hasZero()

    def test_update_clocks(self):
        c = self.c

        assert ((c.x == 1) | (c.z == 2)).updateValue(c.x, 2) == (c.x == 2)
        assert ((c.x == 1) & (c.z == 2)).resetValue(c.x) == ((c.x == 0) & (c.z == 2))

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

        assert federation.getSize() == 2
        federation.reduce()
        assert federation.getSize() == 1

    def test_convex_hull(self):
        c = self.c
        d1 = (c.x >= 1) & (c.x <= 2) & (c.y >= 1) & (c.y <= 2)
        d2 = (c.x >= 3) & (c.x <= 4) & (c.y >= 3) & (c.y <= 4)
        d3 = (c.x - c.y <= 1) & (c.y - c.x <= 1) & (c.x >= 1) & (c.y >= 1) & (c.x <= 4) & (c.y <= 4)

        assert (d1 + d2) == d3
        assert (d1 | d2).convexHull() == d3

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
        c = pyudbm.Context(["x", "y"])
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
        trial.freeClock(c.x)
        trial.convexHull()
        trial.predt(trial)
        trial.resetValue(c.x)

        assert original == trial

    def test_set_init(self):
        c = self.c
        federation = (c.x - c.y <= 1) & (c.y - c.x <= 1) & (c.x >= 1) & (c.y >= 1) & (c.y <= 4)

        federation.setInit()

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

        assert federation.extrapolateMaxBounds(bounds) == ((c.x - c.y <= 1) & (c.z < 150))

    def test_free_clock(self):
        c = self.c
        assert ((c.x >= 10) & (c.y >= 10)).freeClock(c.x) == (c.y >= 10)

    def test_zero_federation(self):
        c = self.c
        assert c.getZeroFederation().isZero()
        assert c.getZeroFederation().hasZero()
        assert pyudbm.Federation(c).isZero()
        assert not (c.x == 1).isZero()
        assert (c.x == 1) != c.getZeroFederation()

    def test_hash(self):
        c = self.c
        assert (c.x == 1).hash() == (c.x == 1).hash()
        assert (c.y == 1).hash() != (c.x == 1).hash()
        assert ((c.x == 1) | (c.y == 1)).hash() == ((c.y == 1) | (c.x == 1)).hash()

    def test_is_empty(self):
        c = self.c

        assert ((c.x == 1) & (c.x != 1)).isEmpty()
        assert not ((c.x == 1) | (c.x != 1)).isEmpty()
        assert not (c.x == 1).isEmpty()
        assert not ((c.x == 1) & (c.y != 1)).isEmpty()
        assert (((c.x == 1) & (c.x != 1)) | ((c.y == 1) & (c.y != 1))).isEmpty()
