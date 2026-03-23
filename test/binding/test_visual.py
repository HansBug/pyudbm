import math

import pytest

from pyudbm import Context, FloatValuation
from pyudbm.binding.visual import (
    EmptyGeometry,
    FederationGeometry2D,
    Interval1D,
    MultiInterval1D,
    Point2D,
    PointGeometry2D,
    PolygonGeometry2D,
    SegmentGeometry2D,
    extract_dbm_geometry,
    extract_federation_geometry,
)


def _contains_interval(interval, value):
    if value < interval.lower - 1e-9 or value > interval.upper + 1e-9:
        return False
    if math.isclose(value, interval.lower, abs_tol=1e-9) and not interval.lower_closed:
        return False
    if math.isclose(value, interval.upper, abs_tol=1e-9) and not interval.upper_closed:
        return False
    return interval.lower - 1e-9 <= value <= interval.upper + 1e-9


def _contains_segment(point, segment):
    cross = ((segment.end.x - segment.start.x) * (point.y - segment.start.y)) - (
        (segment.end.y - segment.start.y) * (point.x - segment.start.x)
    )
    if abs(cross) > 1e-8:
        return False

    min_x = min(segment.start.x, segment.end.x) - 1e-8
    max_x = max(segment.start.x, segment.end.x) + 1e-8
    min_y = min(segment.start.y, segment.end.y) - 1e-8
    max_y = max(segment.start.y, segment.end.y) + 1e-8
    if not (min_x <= point.x <= max_x and min_y <= point.y <= max_y):
        return False
    return segment.is_closed


def _point_in_loop_interior(point, loop):
    vertices = loop.vertices
    inside = False
    for index, left in enumerate(vertices):
        right = vertices[(index + 1) % len(vertices)]
        intersects = ((left.y > point.y) != (right.y > point.y)) and (
            point.x < (((right.x - left.x) * (point.y - left.y)) / (right.y - left.y + 1e-30)) + left.x
        )
        if intersects:
            inside = not inside
    return inside


def _geometry_contains_1d(geometry, value):
    if isinstance(geometry, EmptyGeometry):
        return False
    if isinstance(geometry, Interval1D):
        return _contains_interval(geometry, value)
    if isinstance(geometry, MultiInterval1D):
        return any(_contains_interval(interval, value) for interval in geometry.intervals)
    raise TypeError("Unsupported 1D geometry: {0!r}".format(type(geometry).__name__))


def _geometry_contains_2d(geometry, x_value, y_value):
    point = Point2D(float(x_value), float(y_value))
    if isinstance(geometry, EmptyGeometry):
        return False
    if isinstance(geometry, PolygonGeometry2D):
        return all(halfspace.contains(point, respect_strict=True) for halfspace in geometry.halfspaces)
    if isinstance(geometry, SegmentGeometry2D):
        return _contains_segment(point, geometry.segment)
    if isinstance(geometry, PointGeometry2D):
        return geometry.is_closed and math.isclose(point.x, geometry.point.x, abs_tol=1e-9) and math.isclose(
            point.y, geometry.point.y, abs_tol=1e-9
        )
    if isinstance(geometry, FederationGeometry2D):
        if any(_contains_segment(point, segment) for segment in geometry.boundary_segments):
            return True
        if any(_contains_segment(point, segment) for segment in geometry.isolated_segments):
            return True
        if any(math.isclose(point.x, item.x, abs_tol=1e-9) and math.isclose(point.y, item.y, abs_tol=1e-9) for item in geometry.isolated_points):
            return True
        for face in geometry.faces:
            if _point_in_loop_interior(point, face.outer) and not any(_point_in_loop_interior(point, hole) for hole in face.holes):
                return True
        return False
    raise TypeError("Unsupported 2D geometry: {0!r}".format(type(geometry).__name__))


def _federation_contains_1d(federation, value):
    valuation = FloatValuation(federation.context)
    valuation[federation.context.clocks[0]] = float(value)
    return federation.contains(valuation)


def _federation_contains_2d(federation, x_value, y_value):
    valuation = FloatValuation(federation.context)
    valuation[federation.context.clocks[0]] = float(x_value)
    valuation[federation.context.clocks[1]] = float(y_value)
    return federation.contains(valuation)


def _segment_probe_points(segment):
    midpoint = segment.midpoint
    direction_x = segment.end.x - segment.start.x
    direction_y = segment.end.y - segment.start.y
    length = math.hypot(direction_x, direction_y)
    if length <= 1e-9:
        return [midpoint]

    offset = 1e-4
    normal_x = -direction_y / length
    normal_y = direction_x / length
    return [
        midpoint,
        Point2D(midpoint.x + (normal_x * offset), midpoint.y + (normal_y * offset)),
        Point2D(midpoint.x - (normal_x * offset), midpoint.y - (normal_y * offset)),
    ]


@pytest.mark.unittest
class TestVisualizationGeometry:
    def test_extract_dbm_geometry_1d_matches_contains(self):
        context = Context(["x"])
        federation = (context.x >= 0) & (context.x < 3)

        geometry = extract_dbm_geometry(federation.to_dbm_list()[0], limits=(-1, 4))

        assert isinstance(geometry, Interval1D)
        assert geometry.lower == 0.0
        assert geometry.upper == 3.0
        assert geometry.lower_closed
        assert not geometry.upper_closed

        for value in [-1.0, 0.0, 0.5, 2.999, 3.0, 3.1]:
            assert _geometry_contains_1d(geometry, value) == _federation_contains_1d(federation, value)

    def test_extract_federation_geometry_1d_exact_union_matches_contains(self):
        context = Context(["x"])
        federation = ((context.x > 0) & (context.x < 1)) | ((context.x >= 1) & (context.x <= 2))

        geometry = extract_federation_geometry(federation, limits=(-1, 3))

        assert isinstance(geometry, MultiInterval1D)
        assert len(geometry.intervals) == 1
        assert geometry.intervals[0] == Interval1D(0.0, 2.0, False, True, False, False)

        for value in [-0.5, 0.0, 0.25, 0.999, 1.0, 1.5, 2.0, 2.01]:
            assert _geometry_contains_1d(geometry, value) == _federation_contains_1d(federation, value)

    def test_extract_dbm_geometry_2d_open_edge_matches_contains(self):
        context = Context(["x", "y"])
        federation = (context.x < 2) & (context.y <= 1)

        geometry = extract_dbm_geometry(federation.to_dbm_list()[0], limits=((0, 3), (0, 2)))

        assert isinstance(geometry, PolygonGeometry2D)
        assert len(geometry.edges) == 4
        open_edges = [edge for edge in geometry.edges if not edge.is_closed]
        assert len(open_edges) == 1
        assert math.isclose(open_edges[0].start.x, 2.0, abs_tol=1e-9)
        assert math.isclose(open_edges[0].end.x, 2.0, abs_tol=1e-9)

        sample_points = [
            (0.0, 0.0),
            (1.0, 0.5),
            (1.999, 0.5),
            (2.0, 0.5),
            (2.01, 0.5),
            (1.0, 1.0),
            (1.0, 1.1),
        ]
        for x_value, y_value in sample_points:
            assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(federation, x_value, y_value)

        for edge in geometry.edges:
            for probe in _segment_probe_points(edge):
                assert _geometry_contains_2d(geometry, probe.x, probe.y) == _federation_contains_2d(federation, probe.x, probe.y)

    def test_extract_dbm_geometry_2d_segment_degenerate_matches_contains(self):
        context = Context(["x", "y"])
        federation = (context.x - context.y == 0) & (context.x <= 1) & (context.y <= 1)

        geometry = extract_dbm_geometry(federation.to_dbm_list()[0], limits=((0, 2), (0, 2)))

        assert isinstance(geometry, SegmentGeometry2D)
        assert math.isclose(geometry.segment.start.x, 0.0, abs_tol=1e-9)
        assert math.isclose(geometry.segment.start.y, 0.0, abs_tol=1e-9)
        assert math.isclose(geometry.segment.end.x, 1.0, abs_tol=1e-9)
        assert math.isclose(geometry.segment.end.y, 1.0, abs_tol=1e-9)

        sample_points = [
            (0.0, 0.0),
            (0.5, 0.5),
            (1.0, 1.0),
            (0.5, 0.5001),
            (0.6, 0.4),
        ]
        for x_value, y_value in sample_points:
            assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(federation, x_value, y_value)

    def test_extract_federation_geometry_2d_exact_l_shape_boundary_matches_contains(self):
        context = Context(["x", "y"])
        left = (context.x >= 0) & (context.x <= 2) & (context.y >= 0) & (context.y <= 1)
        top = (context.x >= 1) & (context.x <= 2) & (context.y >= 1) & (context.y <= 2)
        federation = left | top

        geometry = extract_federation_geometry(federation, limits=((0, 3), (0, 3)))

        assert isinstance(geometry, FederationGeometry2D)
        assert len(geometry.loops) == 1
        assert len(geometry.faces) == 1
        assert len(geometry.boundary_segments) == 6
        assert {
            (round(segment.start.x, 6), round(segment.start.y, 6), round(segment.end.x, 6), round(segment.end.y, 6))
            for segment in geometry.boundary_segments
        } == {
            (2.0, 0.0, 2.0, 2.0),
            (2.0, 2.0, 1.0, 2.0),
            (1.0, 2.0, 1.0, 1.0),
            (1.0, 1.0, 0.0, 1.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 2.0, 0.0),
        }

        grid_points = [
            (x_value / 2.0, y_value / 2.0)
            for x_value in range(-1, 7)
            for y_value in range(-1, 7)
        ]
        for x_value, y_value in grid_points:
            assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(federation, x_value, y_value)

        for segment in geometry.boundary_segments:
            for probe in _segment_probe_points(segment):
                assert _geometry_contains_2d(geometry, probe.x, probe.y) == _federation_contains_2d(federation, probe.x, probe.y)

    def test_extract_federation_geometry_2d_disconnected_faces(self):
        context = Context(["x", "y"])
        left = (context.x >= 0) & (context.x <= 1) & (context.y >= 0) & (context.y <= 1)
        right = (context.x >= 3) & (context.x <= 4) & (context.y >= 0) & (context.y <= 1)
        federation = left | right

        geometry = extract_federation_geometry(federation, limits=((0, 4), (0, 2)))

        assert isinstance(geometry, FederationGeometry2D)
        assert len(geometry.faces) == 2
        assert len(geometry.loops) == 2

        grid_points = [
            (x_value / 2.0, y_value / 2.0)
            for x_value in range(0, 9)
            for y_value in range(0, 5)
        ]
        for x_value, y_value in grid_points:
            assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(federation, x_value, y_value)

    def test_extract_federation_geometry_rejects_reserved_3d(self):
        context = Context(["x", "y", "z"])
        federation = (context.x <= 1) & (context.y <= 1) & (context.z <= 1)

        with pytest.raises(NotImplementedError):
            extract_federation_geometry(federation)
