import importlib
import importlib.util

import pytest

_MATPLOTLIB_SPEC = importlib.util.find_spec("matplotlib")
_HAS_MATPLOTLIB = _MATPLOTLIB_SPEC is not None

if _HAS_MATPLOTLIB:
    matplotlib = importlib.import_module("matplotlib")
    matplotlib.use("Agg")
    plt = importlib.import_module("matplotlib.pyplot")
    to_hex = importlib.import_module("matplotlib.colors").to_hex
else:
    matplotlib = None
    plt = None
    to_hex = None

from pyudbm import Context
from pyudbm.binding import PlotResult, plot_dbm, plot_federation


class FakeArtist:
    def __init__(self, color=None, label=None, marker=None, markerfacecolor=None, markeredgecolor=None, linestyle="-"):
        self._color = color
        self._label = label
        self._marker = marker
        self._markerfacecolor = markerfacecolor
        self._markeredgecolor = markeredgecolor
        self._linestyle = linestyle

    def get_color(self):
        return self._color

    def get_label(self):
        return self._label

    def get_marker(self):
        return self._marker

    def get_markerfacecolor(self):
        return self._markerfacecolor

    def get_markeredgecolor(self):
        return self._markeredgecolor

    def get_linestyle(self):
        return self._linestyle


class FakeAxis:
    def __init__(self):
        self._xlim = (0.0, 1.0)
        self._ylim = (0.0, 1.0)
        self._has_data = False
        self._xlabel = ""
        self._ylabel = ""
        self.lines = []
        self.patches = []
        self.texts = []

    def has_data(self):
        return self._has_data

    def plot(self, x_values, y_values, **kwargs):
        self._has_data = True
        artist = FakeArtist(
            color=kwargs.get("color"),
            label=kwargs.get("label"),
            marker=kwargs.get("marker"),
            markerfacecolor=kwargs.get("markerfacecolor"),
            markeredgecolor=kwargs.get("markeredgecolor"),
            linestyle=kwargs.get("linestyle", "-"),
        )
        self.lines.append((tuple(x_values), tuple(y_values), artist))
        return [artist]

    def add_patch(self, patch):
        self._has_data = True
        self.patches.append(patch)

    def text(self, x, y, text, **kwargs):
        self._has_data = True
        artist = FakeArtist(color=kwargs.get("color"), label=text)
        artist.get_position = lambda: (x, y)
        artist.get_text = lambda: text
        self.texts.append(artist)
        return artist

    def set_xlim(self, left, right):
        self._xlim = (float(left), float(right))

    def get_xlim(self):
        return self._xlim

    def set_ylim(self, bottom, top):
        self._ylim = (float(bottom), float(top))

    def get_ylim(self):
        return self._ylim

    def set_xlabel(self, value):
        self._xlabel = value

    def get_xlabel(self):
        return self._xlabel

    def set_ylabel(self, value):
        self._ylabel = value

    def get_ylabel(self):
        return self._ylabel

    def set_aspect(self, *_args, **_kwargs):
        return None


@pytest.mark.unittest
@pytest.mark.skipif(not _HAS_MATPLOTLIB, reason="matplotlib is not installed")
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

    def test_plot_dbm_default_label_uses_dbm_string_and_same_ax_auto_merges_view(self):
        context = Context(["x", "y"])
        left_dbm = ((context.x <= 1) & (context.y <= 1)).to_dbm_list()[0]
        right_dbm = ((context.x >= 3) & (context.y >= 2)).to_dbm_list()[0]
        _, ax = plt.subplots()

        left_result = plot_dbm(left_dbm, ax=ax)
        right_result = plot_dbm(right_dbm, ax=ax)

        assert isinstance(left_result, PlotResult)
        assert isinstance(right_result, PlotResult)
        handles, labels = ax.get_legend_handles_labels()
        del handles
        assert str(left_dbm) in labels
        assert str(right_dbm) in labels
        assert left_result.boundaries[0].get_color() != right_result.boundaries[0].get_color()
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        assert xlim[0] <= 0.0
        assert xlim[1] > 3.0
        assert ylim[0] <= 0.0
        assert ylim[1] > 2.0

    def test_plot_dbm_default_label_uses_dbm_string_and_same_ax_auto_merges_view_in_1d(self):
        context = Context(["x"])
        left_dbm = ((context.x > 0) & (context.x <= 1)).to_dbm_list()[0]
        right_dbm = ((context.x >= 3) & (context.x < 5)).to_dbm_list()[0]
        _, ax = plt.subplots()

        left_result = plot_dbm(left_dbm, ax=ax)
        right_result = plot_dbm(right_dbm, ax=ax)

        assert isinstance(left_result, PlotResult)
        assert isinstance(right_result, PlotResult)
        assert ax.get_xlim()[0] <= 0.0
        assert ax.get_xlim()[1] > 4.0

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
        assert lower_result.markers[0].get_marker() == "s"
        assert lower_result.markers[1].get_marker() == "o"

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

    def test_plot_dbm_2d_clipped_boundaries_use_distinct_linestyle(self):
        context = Context(["x", "y"])
        dbm = (context.x <= 1).to_dbm_list()[0]

        result = plot_dbm(dbm, limits=((0, 2), (0, 2)))

        assert isinstance(result, PlotResult)
        linestyles = [line.get_linestyle() for line in result.boundaries]
        assert "-" in linestyles
        assert "-." in linestyles

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

    def test_plot_dbm_facecolor_without_edgecolor_reuses_fill_color(self):
        context = Context(["x", "y"])
        dbm = ((context.x <= 1) & (context.y <= 1)).to_dbm_list()[0]

        result = plot_dbm(dbm, limits=((0, 2), (0, 2)), facecolor="#123456")

        assert isinstance(result, PlotResult)
        assert to_hex(result.fills[0].get_facecolor()) == "#123456"
        assert result.boundaries[0].get_color() == "#123456"

    def test_plot_dbm_annotation_text_defaults_to_minimal_expression(self):
        context = Context(["x", "y"])
        dbm = ((context.x <= 1) & (context.y <= 1)).to_dbm_list()[0]

        result = plot_dbm(dbm, annotate=True)

        assert isinstance(result, PlotResult)
        assert len(result.annotations) == 1
        assert result.annotations[0].get_text() == str(dbm)

    def test_plot_dbm_explicit_annotate_text_forces_annotation_only_when_needed(self):
        context = Context(["x", "y"])
        dbm = ((context.x <= 1) & (context.y <= 1)).to_dbm_list()[0]

        with pytest.warns(UserWarning, match="annotate_text"):
            forced_result = plot_dbm(dbm, annotate=False, annotate_text="dbm zone")

        explicit_result = plot_dbm(dbm, annotate=True, annotate_text="dbm zone")

        assert len(forced_result.annotations) == 1
        assert forced_result.annotations[0].get_text() == "dbm zone"
        assert len(explicit_result.annotations) == 1
        assert explicit_result.annotations[0].get_text() == "dbm zone"

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

    def test_plot_federation_annotation_text_defaults_to_minimal_expression(self):
        context = Context(["x", "y"])
        federation = (context.x <= 1) & (context.y <= 1)

        result = plot_federation(federation, annotate=True)

        assert isinstance(result, PlotResult)
        assert len(result.annotations) == 1
        assert result.annotations[0].get_text() == str(federation)

    def test_plot_federation_explicit_annotate_text_forces_annotation_only_when_needed(self):
        context = Context(["x", "y"])
        federation = (context.x <= 1) & (context.y <= 1)

        with pytest.warns(UserWarning, match="annotate_text"):
            forced_result = plot_federation(federation, annotate=False, annotate_text="fed zone")

        explicit_result = plot_federation(federation, annotate=True, annotate_text="fed zone")

        assert len(forced_result.annotations) == 1
        assert forced_result.annotations[0].get_text() == "fed zone"
        assert len(explicit_result.annotations) == 1
        assert explicit_result.annotations[0].get_text() == "fed zone"

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
        assert len({to_hex(fill.get_facecolor()) for fill in result.fills}) >= 2

    def test_plot_federation_default_label_uses_federation_string_and_same_ax_auto_merges_view(self):
        context = Context(["x", "y"])
        left = (context.x <= 1) & (context.y <= 1)
        right = (context.x >= 3) & (context.y >= 2)
        _, ax = plt.subplots()

        left_result = plot_federation(left, ax=ax)
        right_result = plot_federation(right, ax=ax)

        assert isinstance(left_result, PlotResult)
        assert isinstance(right_result, PlotResult)
        handles, labels = ax.get_legend_handles_labels()
        del handles
        assert str(left) in labels
        assert str(right) in labels
        assert left_result.boundaries[0].get_color() != right_result.boundaries[0].get_color()
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        assert xlim[0] <= 0.0
        assert xlim[1] > 3.0
        assert ylim[0] <= 0.0
        assert ylim[1] > 2.0

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

    def test_plot_dbm_3d_without_axes_uses_auto_limits_and_same_ax_merges_view(self):
        context = Context(["x", "y", "z"])
        left_dbm = ((context.x <= 1) & (context.y <= 1) & (context.z <= 1)).to_dbm_list()[0]
        right_dbm = (
            (context.x >= 3) & (context.x <= 4)
            & (context.y >= 2) & (context.y <= 3)
            & (context.z >= 1) & (context.z <= 2)
        ).to_dbm_list()[0]

        left_result = plot_dbm(left_dbm, label="left")
        right_result = plot_dbm(right_dbm, ax=left_result.ax, label="right")

        assert isinstance(left_result, PlotResult)
        assert isinstance(right_result, PlotResult)
        assert right_result.ax is left_result.ax
        assert left_result.ax.get_zlabel() == "z"
        assert left_result.ax.get_xlim()[0] <= 0.0
        assert left_result.ax.get_xlim()[1] > 4.0
        assert left_result.ax.get_ylim()[0] <= 0.0
        assert left_result.ax.get_ylim()[1] > 3.0
        assert left_result.ax.get_zlim()[0] <= 0.0
        assert left_result.ax.get_zlim()[1] > 2.0

    def test_plot_dbm_3d_polyhedron_and_degenerate_render(self):
        context = Context(["x", "y", "z"])
        polyhedron_dbm = (
            (context.x <= 1) & (context.y <= 1) & (context.z <= 1) & (context.x - context.y < 1)
        ).to_dbm_list()[0]
        face_dbm = ((context.x <= 1) & (context.y <= 1) & (context.z == 0)).to_dbm_list()[0]
        segment_dbm = ((context.x == 0) & (context.y == 0) & (context.z <= 1)).to_dbm_list()[0]
        point_dbm = ((context.x == 1) & (context.y == 1) & (context.z == 1)).to_dbm_list()[0]

        figure = plt.figure(figsize=(10, 8))
        polyhedron_ax = figure.add_subplot(221, projection="3d")
        face_ax = figure.add_subplot(222, projection="3d")
        segment_ax = figure.add_subplot(223, projection="3d")
        point_ax = figure.add_subplot(224, projection="3d")

        polyhedron_result = plot_dbm(polyhedron_dbm, ax=polyhedron_ax, limits=((0, 2), (0, 2), (0, 2)), label="polyhedron")
        face_result = plot_dbm(face_dbm, ax=face_ax, limits=((0, 2), (0, 2), (0, 1)), label="face")
        segment_result = plot_dbm(segment_dbm, ax=segment_ax, limits=((0, 1), (0, 1), (0, 2)), label="segment")
        point_result = plot_dbm(point_dbm, ax=point_ax, limits=((0, 2), (0, 2), (0, 2)), label="point")
        polyhedron_legend = polyhedron_ax.legend(loc="upper right")
        face_legend = face_ax.legend(loc="upper right")
        segment_legend = segment_ax.legend(loc="upper right")
        point_legend = point_ax.legend(loc="upper right")

        assert isinstance(polyhedron_result, PlotResult)
        assert polyhedron_result.ax is polyhedron_ax
        assert len(polyhedron_result.fills) == 1
        assert polyhedron_result.fills[0].__class__.__name__ == "Poly3DCollection"
        assert len(polyhedron_result.boundaries) >= 6
        assert polyhedron_ax.get_zlabel() == "z"
        assert [text.get_text() for text in polyhedron_legend.get_texts()] == ["polyhedron"]

        assert isinstance(face_result, PlotResult)
        assert len(face_result.fills) == 1
        assert len(face_result.boundaries) == 4
        assert [text.get_text() for text in face_legend.get_texts()] == ["face"]
        assert isinstance(segment_result, PlotResult)
        assert len(segment_result.boundaries) == 1
        assert len(segment_result.markers) == 2
        assert [text.get_text() for text in segment_legend.get_texts()] == ["segment"]
        assert isinstance(point_result, PlotResult)
        assert len(point_result.markers) == 1
        assert [text.get_text() for text in point_legend.get_texts()] == ["point"]

    def test_plot_dbm_3d_zorder_and_degenerate_annotations(self):
        context = Context(["x", "y", "z"])
        polyhedron_dbm = ((context.x <= 1) & (context.y <= 1) & (context.z <= 1)).to_dbm_list()[0]
        face_dbm = ((context.x <= 1) & (context.y <= 1) & (context.z == 0)).to_dbm_list()[0]
        segment_dbm = ((context.x == 0) & (context.y == 0) & (context.z <= 1)).to_dbm_list()[0]
        clipped_point_dbm = ((context.x <= 0) & (context.y <= 0) & (context.z <= 0)).to_dbm_list()[0]

        figure = plt.figure(figsize=(10, 8))
        polyhedron_ax = figure.add_subplot(221, projection="3d")
        face_ax = figure.add_subplot(222, projection="3d")
        segment_ax = figure.add_subplot(223, projection="3d")
        point_ax = figure.add_subplot(224, projection="3d")

        polyhedron_result = plot_dbm(polyhedron_dbm, ax=polyhedron_ax, limits=((0, 2), (0, 2), (0, 2)), zorder=7)
        face_result = plot_dbm(face_dbm, ax=face_ax, limits=((0, 2), (0, 2), (0, 1)), annotate=True, zorder=6)
        segment_result = plot_dbm(segment_dbm, ax=segment_ax, limits=((0, 1), (0, 1), (0, 2)), annotate=True)
        point_result = plot_dbm(clipped_point_dbm, ax=point_ax, limits=((0, 1), (0, 1), (0, 1)), annotate=True)

        assert polyhedron_result.fills[0].get_zorder() == 7
        assert face_result.fills[0].get_zorder() == 6
        assert len(face_result.annotations) == 1
        assert len(segment_result.annotations) == 1
        assert len(point_result.annotations) == 1
        assert len(point_result.arrows) >= 1
        assert point_result.markers[0].get_marker() == "s"

    def test_plot_federation_3d_handles_multiple_dbms_and_unbounded_arrows(self):
        context = Context(["x", "y", "z"])
        left = (
            (context.x >= 0) & (context.x <= 1)
            & (context.y >= 0) & (context.y <= 1)
            & (context.z >= 0) & (context.z <= 1)
        )
        right = (
            (context.x >= 2) & (context.x <= 3)
            & (context.y >= 0) & (context.y <= 1)
            & (context.z >= 0) & (context.z <= 1)
        )
        unbounded = context.x <= 1

        figure = plt.figure(figsize=(10, 4))
        shared_ax = figure.add_subplot(121, projection="3d")
        per_dbm_ax = figure.add_subplot(122, projection="3d")

        shared_result = plot_federation(left | right, ax=shared_ax, limits=((0, 3), (0, 1), (0, 1)), label="boxes")
        per_dbm_result = plot_federation(
            unbounded,
            ax=per_dbm_ax,
            limits=((0, 2), (0, 2), (0, 2)),
            color_mode="per_dbm",
            annotate=True,
            label="unbounded",
        )
        shared_legend = shared_ax.legend(loc="upper right")
        per_dbm_legend = per_dbm_ax.legend(loc="upper right")

        assert isinstance(shared_result, PlotResult)
        assert len(shared_result.fills) >= 2
        assert [text.get_text() for text in shared_legend.get_texts()] == ["boxes"]
        assert isinstance(per_dbm_result, PlotResult)
        assert len(per_dbm_result.arrows) >= 1
        assert len(per_dbm_result.annotations) >= 1
        assert [text.get_text() for text in per_dbm_legend.get_texts()] == ["unbounded"]

    def test_plot_federation_3d_empty_defaults_and_invalid_color_mode(self):
        context = Context(["x", "y", "z"])
        empty_federation = (context.x < 0) & (context.x > 0) & (context.y == 0) & (context.z == 0)
        non_empty_federation = (context.x <= 1) & (context.y <= 1) & (context.z <= 1)

        empty_result = plot_federation(empty_federation)
        bounded_result = plot_federation(non_empty_federation)

        assert isinstance(empty_result, PlotResult)
        assert isinstance(bounded_result, PlotResult)
        assert empty_result.ax.get_zlabel() == "z"
        assert tuple(round(value, 6) for value in empty_result.ax.get_xlim()) == (-5.0, 5.0)
        assert tuple(round(value, 6) for value in empty_result.ax.get_ylim()) == (-5.0, 5.0)
        assert tuple(round(value, 6) for value in empty_result.ax.get_zlim()) == (-5.0, 5.0)
        assert tuple(round(value, 6) for value in bounded_result.ax.get_xlim()) == (-0.5, 1.5)
        assert tuple(round(value, 6) for value in bounded_result.ax.get_ylim()) == (-0.5, 1.5)
        assert tuple(round(value, 6) for value in bounded_result.ax.get_zlim()) == (-0.5, 1.5)

        with pytest.raises(ValueError, match="color_mode"):
            plot_federation(non_empty_federation, color_mode="invalid")

    def test_plot_invalid_plot_arguments_raise_clear_errors(self):
        context = Context(["x", "y"])
        dbm = (context.x <= 1).to_dbm_list()[0]
        federation = context.x <= 1
        context_4d = Context(["a", "b", "c", "d"])
        federation_4d = (context_4d.a <= 1) & (context_4d.b <= 1) & (context_4d.c <= 1) & (context_4d.d <= 1)

        with pytest.raises(ValueError, match="strict_epsilon"):
            plot_dbm(dbm, strict_epsilon=0.0)
        with pytest.raises(ValueError, match="color_mode"):
            plot_federation(federation, limits=((0, 2), (0, 2)), color_mode="invalid")
        with pytest.raises(NotImplementedError):
            plot_dbm(federation_4d.to_dbm_list()[0])
        with pytest.raises(NotImplementedError):
            plot_federation(federation_4d)

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

    def test_plot_dbm_3d_missing_mplot3d_raises_clear_error(self, monkeypatch):
        context = Context(["x", "y", "z"])
        dbm = ((context.x <= 1) & (context.y <= 1) & (context.z <= 1)).to_dbm_list()[0]
        original_import_module = importlib.import_module

        def _fake_import_module(name, package=None):
            if name == "mpl_toolkits.mplot3d.art3d":
                raise ImportError("missing mplot3d")
            return original_import_module(name, package)

        monkeypatch.setattr(importlib, "import_module", _fake_import_module)

        with pytest.raises(ImportError, match=r"pyudbm\[plot\]"):
            plot_dbm(dbm)

    def test_plot_dbm_falls_back_to_public_matplotlib_cycle_when_axes_has_no_line_helper(self):
        context = Context(["x"])
        left_dbm = ((context.x > 0) & (context.x <= 1)).to_dbm_list()[0]
        right_dbm = ((context.x >= 2) & (context.x <= 3)).to_dbm_list()[0]
        ax = FakeAxis()

        left_result = plot_dbm(left_dbm, ax=ax, label="left")
        right_result = plot_dbm(right_dbm, ax=ax, label="right")

        assert isinstance(left_result, PlotResult)
        assert isinstance(right_result, PlotResult)
        assert left_result.boundaries[0].get_color() == "#1f77b4"
        assert right_result.boundaries[0].get_color() == "#ff7f0e"
        assert ax.get_xlabel() == "x"
        assert ax.get_ylabel() == "visual baseline"
