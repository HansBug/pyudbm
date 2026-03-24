import gc

import pytest

import pyudbm.binding
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
        assert ctx.true().is_true()
        assert ctx.false().is_false()

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

    def test_bool_dsl_and_bdd_trace_rendering(self):
        base = Context(["x", "y"], name="c")
        ctx = base.to_cdd_context(bools=["door_open", "alarm"])
        bdd = ctx.door_open | ~ctx.alarm
        state = ((ctx.x <= 5) & ctx.door_open) | ((ctx.y <= 3) & ~ctx.door_open)
        traces = bdd.bdd_traces()
        extraction = state.extract_bdd_and_dbm()
        sparse_dicts = traces.to_dicts()

        assert isinstance(traces, BDDTraceSet)
        assert len(traces) == 2
        assert {"door_open": True} in sparse_dicts
        assert any(row.get("alarm") is False for row in sparse_dicts)
        assert {"door_open": True, "alarm": None} in traces.to_dicts(sparse=False)
        assert not extraction.remainder.is_false()
        assert isinstance(extraction.dbm, DBM)

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
