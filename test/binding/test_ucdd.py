import gc
import importlib

import pytest

import pyudbm.binding
import pyudbm.binding.ucdd as ucdd_module
from pyudbm import Context
from pyudbm.binding import BDDTraceSet, CDD, CDDContext, CDDExtraction, CDDBool, CDDClock, DBM


@pytest.fixture(autouse=True)
def collect_garbage():
    gc.collect()
    yield
    gc.collect()


@pytest.mark.unittest
class TestUcddApi:
    def test_binding_exports_and_context_surface(self):
        base = Context(["x", "y"], name="c")
        ctx = base.to_cdd_context(bools=["door_open", "alarm"])

        assert CDDContext is pyudbm.binding.CDDContext
        assert CDD is pyudbm.binding.CDD
        assert ctx.base_context is base
        assert isinstance(ctx.x, CDDClock)
        assert isinstance(ctx.door_open, CDDBool)
        assert ctx["x"] is ctx.x
        assert ctx["door_open"] is ctx.door_open
        assert ctx.clock_names == ("x", "y")
        assert ctx.bool_names == ("door_open", "alarm")
        assert len(ctx.all_level_info()) >= len(ctx.bool_names)
        assert ctx.bool_name_for_level(ctx.door_open.level) == "door_open"
        assert ctx.level_info(ctx.door_open.level).level == ctx.door_open.level
        assert ctx.true().is_true()
        assert ctx.false().is_false()
        assert isinstance(hash(ctx), int)
        assert isinstance(hash(ctx.x), int)
        assert isinstance(hash(ctx.door_open), int)
        assert ctx.x.get_full_name() == "c.x"
        assert ctx.door_open.get_full_name() == "c.door_open"
        assert "CDDClock" in repr(ctx.x)
        assert "CDDBool" in repr(ctx.door_open)

        renamed = base.to_cdd_context(name="renamed")
        direct = CDDContext(["u"], bools=["enabled"], name="sys")

        assert renamed.base_context.name == "renamed"
        assert direct.u.get_full_name() == "sys.u"
        assert direct.enabled.get_full_name() == "sys.enabled"
        anonymous = CDDContext(["x"], bools=["flag"])
        assert anonymous.flag.get_full_name() == "flag"

    def test_context_validation_and_runtime_layout_switching(self):
        with pytest.raises(ValueError, match="must be unique"):
            CDDContext(["x"], bools=["dup", "dup"])

        with pytest.raises(ValueError, match="cannot collide with clock names"):
            CDDContext(["x"], bools=["x"])

        ctx_xy = Context(["x", "y"]).to_cdd_context(bools=["flag"])
        hold_xy = ctx_xy.true()
        with pytest.raises(RuntimeError, match="already uses 3 clocks"):
            Context(["x"]).to_cdd_context()
        del hold_xy
        gc.collect()

        ctx_x = Context(["x"]).to_cdd_context()
        assert ctx_x.dimension == 2

        base = Context(["x"])
        prefix = base.to_cdd_context(bools=["a"])
        expanded = base.to_cdd_context(bools=["a", "b"])
        reused_prefix = base.to_cdd_context(bools=["a"])
        assert prefix.bool_names == ("a",)
        assert expanded.bool_names == ("a", "b")
        assert reused_prefix.bool_names == ("a",)

        conflicting = base.to_cdd_context(bools=["a"])
        hold_bool = conflicting.true()
        with pytest.raises(RuntimeError, match="already uses boolean names"):
            base.to_cdd_context(bools=["b"])
        del hold_bool
        gc.collect()

        restarted = base.to_cdd_context(bools=["b"])
        assert restarted.bool_names == ("b",)
        with pytest.raises(KeyError):
            _ = restarted["missing"]
        with pytest.raises(KeyError):
            restarted.clock("missing")
        with pytest.raises(KeyError):
            restarted.bool("missing")

    def test_pure_clock_roundtrip_and_extraction(self):
        base = Context(["x", "y"], name="c")
        zone = ((base.x >= 1) & (base.x <= 2)) | (base.y == 0)
        cdd = zone.to_cdd()
        extracted = cdd.extract_bdd_and_dbm()
        first_dbm = zone.to_dbm_list()[0]

        assert cdd.to_federation() == zone
        assert isinstance(extracted, CDDExtraction)
        assert extracted.bdd_part.is_true()
        assert isinstance(extracted.dbm, DBM)
        assert extracted.to_federation().get_size() == 1
        assert zone >= extracted.to_federation()
        assert cdd.contains_dbm(extracted.dbm)
        assert first_dbm.to_cdd().to_federation().get_size() == 1
        remainder, extracted_dbm = cdd.extract_dbm()
        assert isinstance(remainder, CDD)
        assert isinstance(extracted_dbm, DBM)
        assert extracted_dbm.to_cdd().to_federation().get_size() == 1
        assert cdd.extract_bdd().is_true()
        assert isinstance(cdd.copy().nodecount(), int)
        assert isinstance(repr(cdd.copy()), str)

    def test_bool_dsl_and_bdd_trace_rendering(self):
        base = Context(["x", "y"], name="c")
        ctx = base.to_cdd_context(bools=["door_open", "alarm"])
        bdd = ctx.door_open | ~ctx.alarm
        state = ((ctx.x <= 5) & ctx.door_open) | ((ctx.y <= 3) & ~ctx.door_open)
        traces = bdd.bdd_traces()
        extraction = state.extract_bdd_and_dbm()
        guarded_extraction = ((ctx.x <= 5) & ctx.door_open).extract_bdd_and_dbm()
        sparse_dicts = traces.to_dicts()

        assert isinstance(traces, BDDTraceSet)
        assert len(traces) == 2
        assert {"door_open": True} in sparse_dicts
        assert any(row.get("alarm") is False for row in sparse_dicts)
        assert list(traces) == sparse_dicts
        assert len(traces.to_rows()) == 2
        assert {"door_open": True, "alarm": None} in traces.to_dicts(sparse=False)
        assert not extraction.remainder.is_false()
        assert extraction.bdd_part.extract_bdd().equiv(extraction.bdd_part.reduce())
        assert guarded_extraction.has_bdd_part()
        assert isinstance(extraction.dbm, DBM)
        assert ctx.door_open.as_cdd().equiv(CDD.bddvar(ctx, "door_open"))
        assert (~ctx.door_open).equiv(CDD.bddnvar(ctx, "door_open"))
        assert (ctx.door_open == True).equiv(ctx.door_open)
        assert (ctx.door_open == False).equiv(~ctx.door_open)
        assert (ctx.door_open != True).equiv(~ctx.door_open)
        assert (ctx.door_open != False).equiv(ctx.door_open)
        assert not (ctx.door_open == object())
        assert ctx.door_open != object()

    def test_public_symbolic_constructors_and_algebra(self):
        base = Context(["x", "y"], name="c")
        ctx = base.to_cdd_context(bools=["door_open", "alarm"])
        dbm = (base.x <= 2).to_dbm_list()[0]
        named_bdd = CDD.bddvar(ctx, "door_open")
        named_nbdd = CDD.bddnvar(ctx, "alarm")
        upper = CDD.upper(ctx, 1, 0, dbm.raw("x", "0"))
        lower = CDD.lower(ctx, 1, 0, dbm.raw("0", "x"))
        interval = CDD.interval(ctx, 1, 0, dbm.raw("0", "x"), dbm.raw("x", "0"))
        copied = interval.copy()
        difference = ctx.x - ctx.y
        state = (ctx.x <= 5) & ctx.door_open

        assert named_bdd.is_bdd()
        assert named_nbdd.is_bdd()
        assert (upper & lower).equiv(interval)
        assert upper.apply(ucdd_module.OP_AND, lower).equiv(interval)
        assert upper.apply_reduce(ucdd_module.OP_AND, lower).equiv(interval.reduce())
        assert copied.equiv(interval)
        assert copied == interval
        assert copied != named_bdd
        assert not (copied == object())
        assert copied != object()
        assert copied.ite(named_bdd, named_nbdd).equiv((copied & named_bdd) | ((~copied) & named_nbdd))
        assert copied.reduce2().equiv(copied.reduce())
        assert isinstance(copied.nodecount(), int)
        assert isinstance(copied.edgecount(), int)
        assert not copied.is_bdd()
        assert not copied.is_false()
        assert not copied.is_true()
        assert not CDD.false(ctx).remove_negative().is_true()
        assert ((ctx.x >= 1) & (ctx.x <= 2)).delay().to_federation() == ((base.x >= 1) & (base.x <= 2)).up()
        assert ((ctx.x >= 1) & (ctx.x <= 2)).past().to_federation() == ((base.x >= 1) & (base.x <= 2)).down()
        assert ((ctx.x >= 1) & (ctx.x <= 2)).delay_invariant(ctx.x <= 2).to_federation() == (base.x >= 1) & (base.x <= 2)
        assert ((ctx.x >= 1) & (ctx.x <= 2)).predt(ctx.false()).to_federation() == ((base.x >= 1) & (base.x <= 2)).down()
        assert state.__rand__(ctx.alarm).equiv(ctx.alarm & state)
        assert state.__ror__(ctx.alarm).equiv(ctx.alarm | state)
        assert state.__rsub__(ctx.alarm).equiv(ctx.alarm - state)
        assert state.__rxor__(ctx.alarm).equiv(ctx.alarm ^ state)
        assert ctx.door_open.__rand__(ctx.x <= 5).equiv((ctx.x <= 5) & ctx.door_open)
        assert ctx.door_open.__ror__(ctx.x <= 5).equiv((ctx.x <= 5) | ctx.door_open)
        assert ctx.door_open.__rxor__(ctx.x <= 5).equiv((ctx.x <= 5) ^ ctx.door_open)
        assert ctx.door_open.__rsub__(ctx.x <= 5).equiv((ctx.x <= 5) - ctx.door_open)
        assert (difference <= 1).to_federation() == (base.x - base.y <= 1)
        assert (difference >= -1).to_federation() == (base.x - base.y >= -1)
        assert (difference < 2).to_federation() == (base.x - base.y < 2)
        assert (difference > -2).to_federation() == (base.x - base.y > -2)
        assert (difference == 0).to_federation() == (base.x - base.y == 0)
        assert (difference != 0).to_federation() == (base.x - base.y != 0)
        assert not (difference == "bad")
        assert difference != "bad"
        assert (ctx.x < 2).to_federation() == (base.x < 2)
        assert (ctx.x > -1).to_federation() == (base.x > -1)
        assert (ctx.x != 0).to_federation() == (base.x != 0)
        assert not (ctx.x == object())
        assert ctx.x != ctx.y
        assert ctx.x != object()

    def test_public_validation_errors(self):
        base = Context(["x"], name="c")
        ctx = base.to_cdd_context(bools=["flag"])
        other_same = Context(["x"], name="other").to_cdd_context(bools=["flag"])
        other_layout = Context(["y"], name="other").to_cdd_context(bools=["flag"])
        dbm = (base.x <= 2).to_dbm_list()[0]
        other_dbm = (Context(["y"]).y <= 1).to_dbm_list()[0]
        federation = base.x <= 2
        other_federation = Context(["y"]).y <= 1

        with pytest.raises(TypeError):
            CDD.true("bad")
        with pytest.raises(TypeError):
            CDD.from_dbm("bad")
        with pytest.raises(TypeError):
            CDD.from_federation("bad")
        with pytest.raises(ValueError, match="incompatible with the DBM context"):
            CDD.from_dbm(dbm, cdd_context=other_layout)
        with pytest.raises(ValueError, match="incompatible with the Federation context"):
            CDD.from_federation(federation, cdd_context=other_layout)
        with pytest.raises(TypeError):
            _ = ctx.x <= 1.5
        with pytest.raises(TypeError):
            _ = ctx.x >= 1.5
        with pytest.raises(TypeError):
            _ = ctx.x < 1.5
        with pytest.raises(TypeError):
            _ = ctx.x > 1.5
        assert ctx.x.__sub__(1) is NotImplemented
        with pytest.raises(ValueError, match="same CDDContext"):
            _ = ctx.x - other_same.x
        with pytest.raises(TypeError):
            _ = (ctx.x - ctx.x) <= 1.5
        with pytest.raises(TypeError):
            _ = (ctx.x - ctx.x) >= 1.5
        with pytest.raises(TypeError):
            _ = (ctx.x - ctx.x) < 1.5
        with pytest.raises(TypeError):
            _ = (ctx.x - ctx.x) > 1.5
        with pytest.raises(ValueError, match="exactly two clocks"):
            ucdd_module.CDDVariableDifference([ctx.x])
        with pytest.raises(ValueError, match="same CDDContext"):
            ucdd_module.CDDVariableDifference([ctx.x, other_same.x])
        with pytest.raises(TypeError):
            _ = ctx.true() & 1.0
        assert ctx.true().__and__(federation).to_federation() == federation
        assert ctx.true().__and__(dbm).to_federation().get_size() == 1
        with pytest.raises(TypeError):
            ctx.true().__rand__(object())
        with pytest.raises(ValueError, match="same CDDContext"):
            _ = ctx.true() & other_same.true()
        with pytest.raises(ValueError, match="same CDDContext"):
            _ = ctx.true() & other_same.flag
        with pytest.raises(ValueError, match="same CDDContext"):
            _ = ctx.true().equiv(other_same.true())
        assert ctx.true().__ne__(other_same.true())
        with pytest.raises(TypeError, match="contains_dbm expects"):
            ctx.true().contains_dbm("bad")
        with pytest.raises(ValueError, match="DBM context is incompatible"):
            ctx.true().contains_dbm(other_dbm)
        with pytest.raises(TypeError, match="Clock reset values must be plain integers"):
            ctx.true().apply_reset(clock_resets={ctx.x: 1.5})
        with pytest.raises(TypeError, match="Clock reset keys must be names, Clock objects, or CDDClock objects"):
            ctx.true().apply_reset(clock_resets={object(): 0})
        with pytest.raises(ValueError, match="incompatible context"):
            ctx.true().apply_reset(clock_resets={Context(["y"]).y: 0})
        assert ctx.true().apply_reset(clock_resets={"x": 0}).to_federation() == (base.x == 0)
        assert ctx.true().apply_reset(clock_resets={other_same.base_context.x: 0}).to_federation() == (base.x == 0)
        with pytest.raises(ValueError, match="same CDDContext"):
            ctx.true().apply_reset(clock_resets={other_same.x: 0})
        with pytest.raises(TypeError, match="Boolean reset values must be bool"):
            ctx.true().apply_reset(bool_resets={ctx.flag: 1})
        with pytest.raises(TypeError, match="Boolean reset keys must be names or CDDBool objects"):
            ctx.true().apply_reset(bool_resets={object(): True})
        assert isinstance(ctx.flag.as_cdd().apply_reset(bool_resets={"flag": False}), CDD)
        with pytest.raises(ValueError, match="same CDDContext"):
            ctx.true().apply_reset(bool_resets={other_same.flag: True})
        with pytest.raises(ValueError, match="same CDDContext"):
            ctx.true().transition_back(guard=ctx.true(), update=ctx.true(), clock_resets=[other_same.x])
        with pytest.raises(ValueError, match="incompatible context"):
            ctx.true().transition_back(guard=ctx.true(), update=ctx.true(), clock_resets=[Context(["y"]).y])
        with pytest.raises(TypeError, match="Clock reset lists must contain names, Clock objects, or CDDClock objects"):
            ctx.true().transition_back(guard=ctx.true(), update=ctx.true(), clock_resets=[object()])
        assert ctx.true().transition_back(guard=ctx.true(), update=ctx.true(), clock_resets=["x"]).to_federation().get_size() >= 1
        assert (
            ctx.true().transition_back(guard=ctx.true(), update=ctx.true(), clock_resets=[other_same.base_context.x])
            .to_federation()
            .get_size()
            >= 1
        )
        with pytest.raises(ValueError, match="same CDDContext"):
            ctx.true().transition_back(guard=ctx.true(), update=ctx.true(), bool_resets=[other_same.flag])
        with pytest.raises(TypeError, match="Boolean reset lists must contain names or CDDBool objects"):
            ctx.true().transition_back(guard=ctx.true(), update=ctx.true(), bool_resets=[object()])
        assert ctx.true().transition_back(guard=ctx.true(), update=ctx.true(), bool_resets=["flag"]).equiv(ctx.true())
        with pytest.raises(NotImplementedError, match="guarded federations"):
            (ctx.flag & (ctx.x <= 2)).extract_bdd_and_dbm().to_federation(require_pure=False)
        with pytest.raises(NotImplementedError, match="guarded federations"):
            (ctx.flag & (ctx.x <= 2)).to_federation(require_pure=False)
        with pytest.raises(ValueError, match="mixed bool/clock CDD"):
            (ctx.flag & (ctx.x <= 2)).to_federation()
        with pytest.raises(ValueError, match="non-trivial boolean guard"):
            (ctx.flag & (ctx.x <= 2)).extract_bdd_and_dbm().to_federation()
        assert CDD.bddvar(ctx, ctx.flag.level).equiv(ctx.flag)
        assert CDD.bddnvar(ctx, ctx.flag.level).equiv(~ctx.flag)
        assert CDD.true(base).is_true()
        assert CDD.false(base).is_false()
        assert CDD.from_federation(other_federation, cdd_context=other_layout).to_federation().get_size() == 1
        assert CDD.from_dbm(dbm).to_federation().get_size() == 1

    def test_runtime_state_switching_and_reload_through_public_module(self):
        base_x = Context(["x"])
        ctx_x = base_x.to_cdd_context(bools=["flag"])
        hold_flag = ctx_x.true()
        with pytest.raises(RuntimeError, match="already uses 2 clocks"):
            Context(["x", "y"]).to_cdd_context(bools=["flag"])
        del hold_flag
        gc.collect()

        base_xy = Context(["x", "y"])
        ctx_xy = base_xy.to_cdd_context(bools=["flag"])
        hold_xy = ctx_xy.true()
        reloaded = importlib.reload(ucdd_module)
        with pytest.raises(RuntimeError, match="boolean levels"):
            reloaded.CDDContext(["x", "y"], bools=())
        del hold_xy
        gc.collect()

        restarted = reloaded.CDDContext(["x", "y"], bools=())
        assert restarted.dimension == 3
        restarted_x = Context(["x"]).to_cdd_context()
        assert restarted_x.dimension == 2

    def test_pure_clock_transition_flows(self):
        base = Context(["x"], name="c")
        ctx = base.to_cdd_context()
        source = (ctx.x >= 1) & (ctx.x <= 2)
        guard = ctx.x <= 2
        update = ctx.x == 0

        next_state = source.transition(guard=guard, clock_resets={ctx.x: 0}).reduce()
        prev_state = next_state.transition_back(guard=guard, update=update, clock_resets=[ctx.x]).reduce()
        prev_state_past = next_state.transition_back_past(guard=guard, update=update, clock_resets=[ctx.x]).reduce()

        assert next_state.to_federation() == (base.x == 0)
        assert prev_state.to_federation() == (base.x <= 2)
        assert prev_state_past.to_federation() == (base.x <= 2)

    def test_mixed_clock_bool_resets_and_guarded_extraction(self):
        base = Context(["x"], name="c")
        ctx = base.to_cdd_context(bools=["door_open", "alarm"])
        source = ((ctx.x >= 1) & (ctx.x <= 2) & ctx.door_open) & ~ctx.alarm
        guard = (ctx.x <= 2) & ctx.door_open

        next_state = source.transition(
            guard=guard,
            clock_resets={ctx.x: 0},
            bool_resets={ctx.door_open: False, "alarm": True},
        ).reduce()
        extracted = next_state.extract_bdd_and_dbm()

        assert extracted.bdd_part.equiv((~ctx.door_open) & ctx.alarm)
        assert extracted.dbm.to_cdd().to_federation() == (base.x == 0)

        with pytest.raises(ValueError, match="mixed bool/clock CDD"):
            next_state.to_federation()
