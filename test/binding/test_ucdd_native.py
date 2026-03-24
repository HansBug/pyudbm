import gc
import importlib

import pytest

from pyudbm import Context
from pyudbm.binding import _ucdd as ucdd_module
from pyudbm.binding._ucdd import OP_AND, OP_XOR, TYPE_BDD, TYPE_CDD, _NativeCDD, _NativeCDDRuntime


def _flatten_raw_matrix(dbm):
    return [cell for row in dbm.to_matrix(mode="raw") for cell in row]


def _raw_dbm(federation):
    dbm = federation.to_dbm_list()[0]
    return dbm, _flatten_raw_matrix(dbm)


@pytest.fixture(autouse=True)
def reset_ucdd_runtime():
    gc.collect()
    if _NativeCDDRuntime.is_running():
        if _NativeCDD.live_count() != 0:
            raise AssertionError("UCDD runtime is still holding live _NativeCDD objects before the test starts.")
        _NativeCDDRuntime.done()

    yield

    gc.collect()
    if _NativeCDDRuntime.is_running():
        gc.collect()
        if _NativeCDD.live_count() != 0:
            raise AssertionError("UCDD runtime still has live _NativeCDD objects after the test finished.")
        _NativeCDDRuntime.done()


@pytest.mark.unittest
class TestUcddNative:
    def test_native_modules_are_importable(self):
        udbm_native = importlib.import_module("pyudbm.binding._udbm")
        ucdd_native = importlib.import_module("pyudbm.binding._ucdd")

        assert hasattr(udbm_native, "_NativeFederation")
        assert hasattr(ucdd_native, "_NativeCDDRuntime")
        assert hasattr(ucdd_native, "_NativeCDD")
        assert ucdd_module.TYPE_CDD == TYPE_CDD
        assert ucdd_module.TYPE_BDD == TYPE_BDD
        assert ucdd_module.OP_AND == OP_AND
        assert ucdd_module.OP_XOR == OP_XOR

    def test_runtime_metadata_and_level_info(self):
        _NativeCDDRuntime.ensure_running()
        _NativeCDDRuntime.add_clocks(2)
        first_bdd_level = _NativeCDDRuntime.add_bddvars(1)

        assert _NativeCDDRuntime.is_running()
        assert isinstance(_NativeCDDRuntime.version(), str)
        assert _NativeCDDRuntime.version_num() > 0
        assert _NativeCDDRuntime.getclocks() == 2
        assert _NativeCDDRuntime.get_bdd_level_count() == 1
        assert _NativeCDDRuntime.get_level_count() >= 2

        cdd_level = _NativeCDDRuntime.get_level_info(0)
        bdd_level = _NativeCDDRuntime.get_level_info(first_bdd_level)

        assert cdd_level.type == TYPE_CDD
        assert cdd_level.clock1 >= 0
        assert cdd_level.clock2 >= 0
        assert bdd_level.type == TYPE_BDD
        assert isinstance(repr(cdd_level), str)

    def test_runtime_done_rejects_live_cdds(self):
        _NativeCDDRuntime.ensure_running()
        alive = _NativeCDD.true()

        with pytest.raises(RuntimeError, match="still alive"):
            _NativeCDDRuntime.done()

        del alive
        gc.collect()
        _NativeCDDRuntime.done()
        assert not _NativeCDDRuntime.is_running()

    def test_cdd_static_constructors_and_basic_properties(self):
        context = Context(["x"])
        dbm, raw_dbm = _raw_dbm((context.x >= 1) & (context.x <= 2))

        _NativeCDDRuntime.ensure_running()
        _NativeCDDRuntime.add_clocks(dbm.dimension)
        first_bdd_level = _NativeCDDRuntime.add_bddvars(1)

        state = _NativeCDD.from_dbm(raw_dbm, dbm.dimension)
        upper = _NativeCDD.upper(1, 0, dbm.raw("x", "0"))
        lower = _NativeCDD.lower(1, 0, dbm.raw("0", "x"))
        interval = _NativeCDD.interval(1, 0, dbm.raw("0", "x"), dbm.raw("x", "0"))
        bdd = _NativeCDD.bddvar(first_bdd_level)
        nbdd = _NativeCDD.bddnvar(first_bdd_level)
        truthy = _NativeCDD.true()
        falsy = _NativeCDD.false()

        assert truthy.is_true()
        assert falsy.is_false()
        assert not upper.is_false()
        assert not lower.is_false()
        assert not interval.is_false()
        assert upper.and_op(lower).nodecount() > 0
        assert interval.reduce().nodecount() > 0
        assert bdd.is_bdd()
        assert nbdd.is_bdd()
        assert not state.is_bdd()
        assert state.nodecount() > 0
        assert state.edgecount() > 0
        assert isinstance(repr(state), str)

    def test_cdd_boolean_and_set_operators(self):
        context = Context(["x"])
        dbm, raw_dbm = _raw_dbm((context.x >= 1) & (context.x <= 2))

        _NativeCDDRuntime.ensure_running()
        _NativeCDDRuntime.add_clocks(dbm.dimension)
        first_bdd_level = _NativeCDDRuntime.add_bddvars(1)

        zone = _NativeCDD.from_dbm(raw_dbm, dbm.dimension)
        bdd = _NativeCDD.bddvar(first_bdd_level)
        nbdd = _NativeCDD.bddnvar(first_bdd_level)
        copied = zone.copy()

        assert _NativeCDD.live_count() >= 4
        assert copied.equiv(zone)
        assert zone.and_op(bdd).equiv(zone & bdd)
        assert zone.or_op(bdd).equiv(zone | bdd)
        assert zone.minus_op(bdd).equiv(zone - bdd)
        assert zone.xor_op(bdd).equiv(zone ^ bdd)
        assert zone.invert().equiv(~zone)
        assert zone.apply(OP_AND, bdd).equiv(zone.and_op(bdd))
        assert bdd.apply(OP_XOR, nbdd).is_true()
        assert zone.apply_reduce(OP_AND, _NativeCDD.true()).equiv(zone.reduce())
        assert bdd.ite(zone, _NativeCDD.false()).equiv(zone.and_op(bdd))
        assert bdd.or_op(nbdd).is_true()
        assert bdd.and_op(nbdd).is_false()
        assert zone.reduce2().equiv(zone.reduce())

    def test_cdd_extract_and_bdd_array(self):
        context = Context(["x"])
        dbm, raw_dbm = _raw_dbm((context.x >= 1) & (context.x <= 2))

        _NativeCDDRuntime.ensure_running()
        _NativeCDDRuntime.add_clocks(dbm.dimension)
        first_bdd_level = _NativeCDDRuntime.add_bddvars(1)

        state = _NativeCDD.from_dbm(raw_dbm, dbm.dimension)
        reduced = state.reduce()
        extracted = reduced.extract_bdd_and_dbm()
        remainder, raw_extracted = reduced.extract_dbm(dbm.dimension)
        extracted_bdd = reduced.extract_bdd(dbm.dimension)
        bdd = _NativeCDD.bddvar(first_bdd_level)
        nbdd = _NativeCDD.bddnvar(first_bdd_level)
        traces = bdd.bdd_to_array()
        empty_traces = _NativeCDD.false().bdd_to_array()
        mixed = state.and_op(nbdd).reduce().extract_bdd_and_dbm()

        assert state.contains_dbm(raw_dbm, dbm.dimension)
        assert extracted.dbm == raw_dbm
        assert extracted.bdd_part.is_true()
        assert extracted.cdd_part.is_false()
        assert raw_extracted == raw_dbm
        assert remainder.is_false()
        assert extracted_bdd.is_true()
        assert mixed.bdd_part.equiv(nbdd)
        assert mixed.cdd_part.is_false()
        assert traces.num_traces == 1
        assert traces.num_bools == 1
        assert traces.vars_matrix() == [[first_bdd_level]]
        assert traces.values_matrix() == [[1]]
        assert empty_traces.num_traces == 0
        assert empty_traces.vars_matrix() == []
        assert empty_traces.values_matrix() == []

    def test_delay_past_predt_and_transition_flows(self):
        context = Context(["x"])
        source = ((context.x >= 1) & (context.x <= 2))
        guard = context.x <= 2
        update = context.x == 0
        reset = source.reset_value(context.x)
        expected_delay = source.up().to_dbm_list()[0]
        expected_past = source.down().to_dbm_list()[0]
        expected_reset = reset.to_dbm_list()[0]
        expected_back = (context.x <= 2).to_dbm_list()[0]

        source_dbm, raw_source = _raw_dbm(source)
        guard_dbm, raw_guard = _raw_dbm(guard)
        update_dbm, raw_update = _raw_dbm(update)

        _NativeCDDRuntime.ensure_running()
        _NativeCDDRuntime.add_clocks(source_dbm.dimension)

        source_cdd = _NativeCDD.from_dbm(raw_source, source_dbm.dimension)
        guard_cdd = _NativeCDD.from_dbm(raw_guard, guard_dbm.dimension)
        update_cdd = _NativeCDD.from_dbm(raw_update, update_dbm.dimension)
        invariant_cdd = _NativeCDD.from_dbm(raw_guard, guard_dbm.dimension)

        delayed = source_cdd.delay().reduce().extract_bdd_and_dbm()
        past = source_cdd.past().reduce().extract_bdd_and_dbm()
        predt = source_cdd.predt(_NativeCDD.false()).reduce().extract_bdd_and_dbm()
        delayed_invariant = source_cdd.delay_invariant(invariant_cdd).reduce().extract_bdd_and_dbm()
        reset_state = source_cdd.apply_reset([1], [0], [], []).reduce().extract_bdd_and_dbm()
        transitioned = source_cdd.transition(guard_cdd, [1], [0], [], []).reduce().extract_bdd_and_dbm()
        back = reset_state.cdd_part
        assert back.is_false()

        transitioned_back = _NativeCDD.from_dbm(reset_state.dbm, source_dbm.dimension).transition_back(
            guard_cdd, update_cdd, [1], []
        ).reduce().extract_bdd_and_dbm()
        transitioned_back_past = _NativeCDD.from_dbm(reset_state.dbm, source_dbm.dimension).transition_back_past(
            guard_cdd, update_cdd, [1], []
        ).reduce().extract_bdd_and_dbm()

        assert delayed.dbm == _flatten_raw_matrix(expected_delay)
        assert past.dbm == _flatten_raw_matrix(expected_past)
        assert predt.dbm == _flatten_raw_matrix(expected_past)
        assert delayed_invariant.dbm == raw_source
        assert reset_state.dbm == _flatten_raw_matrix(expected_reset)
        assert transitioned.dbm == _flatten_raw_matrix(expected_reset)
        assert transitioned_back.dbm == _flatten_raw_matrix(expected_back)
        assert transitioned_back_past.dbm == _flatten_raw_matrix(expected_back)

    def test_remove_negative_and_validation_errors(self):
        context = Context(["x"])
        dbm, raw_dbm = _raw_dbm(context.x <= 2)

        _NativeCDDRuntime.ensure_running()
        _NativeCDDRuntime.add_clocks(dbm.dimension)
        level = _NativeCDDRuntime.add_bddvars(1)

        state = _NativeCDD.from_dbm(raw_dbm, dbm.dimension)
        negative = _NativeCDD.lower(1, 0, -3)
        non_negative = negative.remove_negative()
        assert not non_negative.is_false()
        assert non_negative.nodecount() > 0
        assert _NativeCDD.bddnvar(level).invert().equiv(_NativeCDD.bddvar(level))

        with pytest.raises(ValueError, match="DBM size does not match"):
            _NativeCDD.from_dbm(raw_dbm[:-1], dbm.dimension)

        with pytest.raises(ValueError, match="Clock reset indices and values must have the same length"):
            state.apply_reset([1], [], [], [])

        with pytest.raises(ValueError, match="Boolean reset levels and values must have the same length"):
            state.apply_reset([], [], [level], [])
