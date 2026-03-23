import importlib

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

from matplotlib import pyplot as plt

from pyudbm import Context
from pyudbm.binding import PlotResult, plot_dbm, plot_federation


@pytest.mark.unittest
class TestMatplotlibVisualization:
    def teardown_method(self):
        plt.close("all")

    def test_plot_dbm_reuses_axes_and_distinguishes_open_closed_endpoints(self):
        context = Context(["x"])
        dbm = ((context.x > 0) & (context.x <= 2)).to_dbm_list()[0]
        _, ax = plt.subplots()

        result = plot_dbm(dbm, ax=ax, limits=(-1, 3), label="zone")

        assert isinstance(result, PlotResult)
        assert result.ax is ax
        assert len(result.boundaries) == 1
        assert len(result.markers) == 2
        assert result.markers[0].get_markerfacecolor() == "none"
        assert result.markers[1].get_markerfacecolor() != "none"
        assert tuple(round(value, 6) for value in ax.get_xlim()) == (-1.0, 3.0)
        assert ax.get_xlabel() == "x"
        assert ax.get_ylabel() == "visual baseline"

    def test_plot_dbm_1d_unbounded_interval_adds_arrow(self):
        context = Context(["x"])
        dbm = context.get_zero_federation().free_clock(context.x).to_dbm_list()[0]

        result = plot_dbm(dbm)

        assert isinstance(result, PlotResult)
        assert len(result.arrows) == 1
        assert result.ax.get_xlim()[0] < 0.0
        assert result.ax.get_xlim()[1] > 1.0

    def test_plot_federation_1d_empty_union_arrow_and_annotation(self):
        context = Context(["x"])
        clipped_empty = ((context.x >= 10) & (context.x <= 20)) | ((context.x >= 30) & (context.x <= 40))
        implicit_empty = (context.x < 0) & (context.x > 0)
        lower_clipped = (context.x >= 0) & (context.x <= 1)
        context_2d = Context(["x", "y"])
        empty_2d = (context_2d.x < 0) & (context_2d.x > 0)

        empty_result = plot_federation(clipped_empty, limits=(0, 1))
        implicit_empty_result = plot_federation(implicit_empty)
        lower_result = plot_federation(lower_clipped, limits=(0.5, 1.5), annotate=True)
        empty_2d_result = plot_federation(empty_2d)

        assert isinstance(empty_result, PlotResult)
        assert len(empty_result.boundaries) == 0
        assert isinstance(implicit_empty_result, PlotResult)
        assert len(lower_result.arrows) == 1
        assert len(lower_result.annotations) == 1
        assert isinstance(empty_2d_result, PlotResult)

    def test_plot_dbm_2d_polygon_segment_and_point_render(self):
        context = Context(["x", "y"])
        polygon_dbm = ((context.x < 2) & (context.y <= 1)).to_dbm_list()[0]
        segment_dbm = ((context.x - context.y == 0) & (context.x <= 1) & (context.y <= 1)).to_dbm_list()[0]
        point_dbm = ((context.x == 1) & (context.y == 2)).to_dbm_list()[0]

        _, axes = plt.subplots(1, 3, figsize=(9, 3))
        polygon_result = plot_dbm(polygon_dbm, ax=axes[0], limits=((0, 3), (0, 2)))
        segment_result = plot_dbm(segment_dbm, ax=axes[1], limits=((0, 2), (0, 2)))
        point_result = plot_dbm(point_dbm, ax=axes[2], limits=((0, 3), (0, 3)))

        assert isinstance(polygon_result, PlotResult)
        assert len(polygon_result.fills) == 1
        assert len(polygon_result.boundaries) == 4
        assert any(line.get_linestyle() == "--" for line in polygon_result.boundaries)
        assert axes[0].get_xlabel() == "x"
        assert axes[0].get_ylabel() == "y"
        assert isinstance(segment_result, PlotResult)
        assert len(segment_result.boundaries) == 1
        assert len(segment_result.markers) == 2
        assert isinstance(point_result, PlotResult)
        assert len(point_result.markers) == 1

    def test_plot_dbm_2d_annotations_arrows_and_custom_strict_epsilon(self):
        context = Context(["x", "y"])
        polygon_dbm = (context.x <= 1).to_dbm_list()[0]
        segment_dbm = ((context.x - context.y == 0) & (context.x <= 1) & (context.y <= 1)).to_dbm_list()[0]
        point_dbm = ((context.x == 1) & (context.y == 2)).to_dbm_list()[0]
        thin_polygon_dbm = ((context.x > 0) & (context.x < 1) & (context.y > 0) & (context.y < 1)).to_dbm_list()[0]

        polygon_result = plot_dbm(polygon_dbm, limits=((0, 2), (0, 2)), annotate=True)
        segment_result = plot_dbm(segment_dbm, limits=((0, 2), (0, 2)), annotate=True)
        point_result = plot_dbm(point_dbm, limits=((0, 3), (0, 3)), annotate=True)
        thin_result = plot_dbm(thin_polygon_dbm, limits=((0, 1), (0, 1)), strict_epsilon=1.0)
        custom_epsilon_result = plot_dbm((context.x <= 1).to_dbm_list()[0], limits=((0, 2), (0, 2)), strict_epsilon=0.01)

        assert len(polygon_result.arrows) >= 1
        assert len(polygon_result.annotations) == 1
        assert len(segment_result.annotations) == 1
        assert len(point_result.annotations) == 1
        assert len(thin_result.fills) == 0
        assert isinstance(custom_epsilon_result, PlotResult)

    def test_plot_dbm_default_limits_include_negative_space_and_bounded_end_padding(self):
        context = Context(["x", "y"])
        dbm = ((context.x >= 1) & (context.y >= 2)).to_dbm_list()[0]

        result = plot_dbm(dbm)

        assert isinstance(result, PlotResult)
        assert result.ax.get_xlim()[0] < 0.0
        assert result.ax.get_xlim()[1] > 1.0
        assert result.ax.get_ylim()[0] < 0.0
        assert result.ax.get_ylim()[1] > 2.0
        assert len(result.arrows) >= 2

    def test_plot_federation_2d_uses_exact_boundary(self):
        context = Context(["x", "y"])
        left = (context.x >= 0) & (context.x <= 2) & (context.y >= 0) & (context.y <= 1)
        top = (context.x >= 1) & (context.x <= 2) & (context.y >= 1) & (context.y <= 2)
        federation = left | top
        _, ax = plt.subplots()

        result = plot_federation(federation, ax=ax, limits=((0, 3), (0, 3)))

        assert isinstance(result, PlotResult)
        assert result.ax is ax
        assert len(result.fills) == 1
        assert len(result.boundaries) == 6

    def test_plot_federation_2d_annotations_holes_and_unbounded_arrows(self):
        context = Context(["x", "y"])
        parts = [
            (context.x >= 0) & (context.x <= 3) & (context.y >= 0) & (context.y <= 1),
            (context.x >= 0) & (context.x <= 3) & (context.y >= 2) & (context.y <= 3),
            (context.x >= 0) & (context.x <= 1) & (context.y >= 1) & (context.y <= 2),
            (context.x >= 2) & (context.x <= 3) & (context.y >= 1) & (context.y <= 2),
        ]
        hole_federation = parts[0] | parts[1] | parts[2] | parts[3]
        unbounded_federation = context.x <= 1

        hole_result = plot_federation(hole_federation, limits=((0, 3), (0, 3)), annotate=True)
        unbounded_result = plot_federation(unbounded_federation, limits=((0, 2), (0, 2)))

        assert isinstance(hole_result, PlotResult)
        assert len(hole_result.annotations) == 1
        assert len(unbounded_result.arrows) >= 1

    def test_plot_federation_default_limits_and_axis_labels(self):
        context = Context(["x", "y"])
        federation = (context.x >= 1) & (context.y >= 2)

        result = plot_federation(federation)

        assert isinstance(result, PlotResult)
        assert result.ax.get_xlabel() == "x"
        assert result.ax.get_ylabel() == "y"
        assert result.ax.get_xlim()[0] < 0.0
        assert result.ax.get_xlim()[1] > 1.0
        assert result.ax.get_ylim()[0] < 0.0
        assert result.ax.get_ylim()[1] > 2.0
        assert len(result.arrows) >= 2

    def test_plot_federation_2d_multi_dbm_and_per_dbm_mode(self):
        context = Context(["x", "y"])
        parts = [
            (context.x >= 0) & (context.x <= 5) & (context.y >= 0) & (context.y <= 1),
            (context.x >= 0) & (context.x <= 1) & (context.y >= 1) & (context.y <= 5),
            (context.x >= 4) & (context.x <= 5) & (context.y >= 1) & (context.y <= 5),
            (context.x >= 1) & (context.x <= 4) & (context.y >= 4) & (context.y <= 5),
            (context.x >= 2) & (context.x <= 3) & (context.y >= 1) & (context.y <= 4),
        ]
        federation = parts[0]
        for part in parts[1:]:
            federation = federation | part

        result = plot_federation(federation, limits=((0, 5), (0, 5)), color_mode="per_dbm")

        assert isinstance(result, PlotResult)
        assert len(result.fills) >= 5
        assert len(result.boundaries) == 12

    def test_plot_methods_forward_correctly(self):
        context = Context(["x", "y"])
        dbm = ((context.x <= 1) & (context.y <= 1)).to_dbm_list()[0]
        federation = (context.x <= 1) & (context.y <= 1)

        dbm_result = dbm.plot(limits=((0, 2), (0, 2)))
        federation_result = federation.plot(limits=((0, 2), (0, 2)))

        assert isinstance(dbm_result, PlotResult)
        assert isinstance(federation_result, PlotResult)

    def test_plot_federation_degenerate_geometries_do_not_fail(self):
        context = Context(["x", "y"])
        segment_federation = ((context.x - context.y == 0) & (context.x <= 1) & (context.y <= 1)) | (
            (context.x == 0) & (context.y == 0)
        )
        point_federation = (context.x == 0) & (context.y == 0)

        segment_result = plot_federation(segment_federation, limits=((0, 1), (0, 1)))
        point_result = plot_federation(point_federation, limits=((0, 1), (0, 1)))

        assert isinstance(segment_result, PlotResult)
        assert len(segment_result.boundaries) == 1
        assert len(segment_result.markers) == 0
        assert isinstance(point_result, PlotResult)
        assert len(point_result.markers) == 1

    def test_plot_invalid_plot_arguments_raise_clear_errors(self):
        context = Context(["x", "y"])
        dbm = (context.x <= 1).to_dbm_list()[0]
        federation = context.x <= 1
        context_3d = Context(["x", "y", "z"])
        federation_3d = (context_3d.x <= 1) & (context_3d.y <= 1) & (context_3d.z <= 1)

        with pytest.raises(ValueError, match="strict_epsilon"):
            plot_dbm(dbm, strict_epsilon=0.0)
        with pytest.raises(ValueError, match="color_mode"):
            plot_federation(federation, limits=((0, 2), (0, 2)), color_mode="invalid")
        with pytest.raises(NotImplementedError):
            plot_dbm(federation_3d.to_dbm_list()[0])
        with pytest.raises(NotImplementedError):
            plot_federation(federation_3d)

    def test_plot_dbm_missing_matplotlib_raises_clear_error(self, monkeypatch):
        context = Context(["x"])
        dbm = (context.x <= 1).to_dbm_list()[0]
        original_import_module = importlib.import_module

        def _fake_import_module(name, package=None):
            if name.startswith("matplotlib"):
                raise ImportError("missing matplotlib")
            return original_import_module(name, package)

        monkeypatch.setattr(importlib, "import_module", _fake_import_module)

        with pytest.raises(ImportError, match=r"pyudbm\[plot\]"):
            plot_dbm(dbm)
