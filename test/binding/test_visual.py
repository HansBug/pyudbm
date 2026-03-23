import math

import pytest

from pyudbm import Context, FloatValuation
from pyudbm.binding.visual import (
    BoundaryEdge3D,
    BoundaryLoop2D,
    BoundarySegment2D,
    EmptyGeometry,
    Face3D,
    Face2D,
    FaceGeometry3D,
    FederationGeometry3D,
    FederationGeometry2D,
    HalfSpace3D,
    HalfSpace2D,
    Interval1D,
    MultiInterval1D,
    Point3D,
    PointGeometry3D,
    Point2D,
    PointGeometry2D,
    PolyhedronGeometry3D,
    PolygonGeometry2D,
    SegmentGeometry3D,
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


def _point_in_face_projection(point, vertices):
    xs = [vertex.x for vertex in vertices]
    ys = [vertex.y for vertex in vertices]
    zs = [vertex.z for vertex in vertices]
    x_span = max(xs) - min(xs)
    y_span = max(ys) - min(ys)
    z_span = max(zs) - min(zs)
    if x_span <= y_span and x_span <= z_span:
        projected_point = Point2D(point.y, point.z)
        projected_vertices = tuple(Point2D(vertex.y, vertex.z) for vertex in vertices)
    elif y_span <= x_span and y_span <= z_span:
        projected_point = Point2D(point.x, point.z)
        projected_vertices = tuple(Point2D(vertex.x, vertex.z) for vertex in vertices)
    else:
        projected_point = Point2D(point.x, point.y)
        projected_vertices = tuple(Point2D(vertex.x, vertex.y) for vertex in vertices)
    return _point_in_loop_interior(projected_point, type("Loop", (), {"vertices": projected_vertices})())


def _geometry_contains_3d(geometry, x_value, y_value, z_value):
    point = Point3D(float(x_value), float(y_value), float(z_value))
    if isinstance(geometry, EmptyGeometry):
        return False
    if isinstance(geometry, PolyhedronGeometry3D):
        return all(halfspace.contains(point, respect_strict=True) for halfspace in geometry.halfspaces)
    if isinstance(geometry, FaceGeometry3D):
        face = geometry.face
        plane_value = (
            (face.normal.x * (point.x - face.vertices[0].x))
            + (face.normal.y * (point.y - face.vertices[0].y))
            + (face.normal.z * (point.z - face.vertices[0].z))
        )
        if abs(plane_value) > 1e-8:
            return False
        return _point_in_face_projection(point, face.vertices) or any(
            _point_on_segment_3d(point, edge) and edge.is_closed for edge in face.edges
        )
    if isinstance(geometry, SegmentGeometry3D):
        return _point_on_segment_3d(point, geometry.segment) and geometry.segment.is_closed
    if isinstance(geometry, PointGeometry3D):
        return geometry.is_closed and math.isclose(point.x, geometry.point.x, abs_tol=1e-9) and math.isclose(
            point.y, geometry.point.y, abs_tol=1e-9
        ) and math.isclose(point.z, geometry.point.z, abs_tol=1e-9)
    if isinstance(geometry, FederationGeometry3D):
        return any(_geometry_contains_3d(item, x_value, y_value, z_value) for item in geometry.dbm_geometries)
    raise TypeError("Unsupported 3D geometry: {0!r}".format(type(geometry).__name__))


def _federation_contains_1d(federation, value):
    valuation = FloatValuation(federation.context)
    valuation[federation.context.clocks[0]] = float(value)
    return federation.contains(valuation)


def _federation_contains_2d(federation, x_value, y_value):
    valuation = FloatValuation(federation.context)
    valuation[federation.context.clocks[0]] = float(x_value)
    valuation[federation.context.clocks[1]] = float(y_value)
    return federation.contains(valuation)


def _federation_contains_3d(federation, x_value, y_value, z_value):
    valuation = FloatValuation(federation.context)
    valuation[federation.context.clocks[0]] = float(x_value)
    valuation[federation.context.clocks[1]] = float(y_value)
    valuation[federation.context.clocks[2]] = float(z_value)
    return federation.contains(valuation)


def _point_on_segment_3d(point, segment):
    dx = segment.end.x - segment.start.x
    dy = segment.end.y - segment.start.y
    dz = segment.end.z - segment.start.z
    tx = point.x - segment.start.x
    ty = point.y - segment.start.y
    tz = point.z - segment.start.z
    cross_x = (dy * tz) - (dz * ty)
    cross_y = (dz * tx) - (dx * tz)
    cross_z = (dx * ty) - (dy * tx)
    if math.sqrt((cross_x ** 2) + (cross_y ** 2) + (cross_z ** 2)) > 1e-8:
        return False
    dot = (tx * dx) + (ty * dy) + (tz * dz)
    if dot < -1e-8:
        return False
    length_sq = (dx * dx) + (dy * dy) + (dz * dz)
    if dot > length_sq + 1e-8:
        return False
    return True


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
    def test_public_geometry_data_objects(self):
        interval = Interval1D(1.0, 1.0, True, True)
        assert interval.is_point

        halfspace = HalfSpace2D(1.0, 0.0, 2.0, is_strict=True)
        boundary_point = Point2D(2.0, 0.0)
        inside_point = Point2D(1.5, 0.0)
        assert halfspace.evaluate(boundary_point) == 0.0
        assert halfspace.contains(inside_point)
        assert not halfspace.contains(boundary_point)
        assert halfspace.contains(boundary_point, respect_strict=False)
        assert halfspace.contains_on_closure(boundary_point)
        assert halfspace.is_active(boundary_point)

        segment = BoundarySegment2D(Point2D(0.0, 0.0), Point2D(2.0, 0.0), True, False)
        assert math.isclose(segment.length, 2.0, abs_tol=1e-9)
        assert segment.midpoint == Point2D(1.0, 0.0)

        loop = BoundaryLoop2D(
            segments=(
                BoundarySegment2D(Point2D(0.0, 0.0), Point2D(1.0, 0.0), True, False),
                BoundarySegment2D(Point2D(1.0, 0.0), Point2D(1.0, 1.0), True, False),
                BoundarySegment2D(Point2D(1.0, 1.0), Point2D(0.0, 1.0), True, False),
                BoundarySegment2D(Point2D(0.0, 1.0), Point2D(0.0, 0.0), True, False),
            ),
            is_hole=False,
        )
        assert loop.vertices == (
            Point2D(0.0, 0.0),
            Point2D(1.0, 0.0),
            Point2D(1.0, 1.0),
            Point2D(0.0, 1.0),
        )
        assert math.isclose(loop.signed_area, 1.0, abs_tol=1e-9)

        degenerate_loop = BoundaryLoop2D(segments=(segment, BoundarySegment2D(Point2D(2.0, 0.0), Point2D(0.0, 0.0), True, False)), is_hole=False)
        assert math.isclose(degenerate_loop.signed_area, 0.0, abs_tol=1e-9)

        face = Face2D(outer=loop, holes=(degenerate_loop,))
        assert face.outer is loop
        assert face.holes == (degenerate_loop,)

        halfspace_3d = HalfSpace3D(1.0, 0.0, 0.0, 2.0, is_strict=True)
        boundary_point_3d = Point3D(2.0, 0.0, 0.0)
        inside_point_3d = Point3D(1.5, 0.0, 0.0)
        assert halfspace_3d.evaluate(boundary_point_3d) == 0.0
        assert halfspace_3d.contains(inside_point_3d)
        assert not halfspace_3d.contains(boundary_point_3d)
        assert halfspace_3d.contains(boundary_point_3d, respect_strict=False)
        assert halfspace_3d.contains_on_closure(boundary_point_3d)
        assert halfspace_3d.is_active(boundary_point_3d)

        edge_3d = BoundaryEdge3D(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 2.0, 2.0), True, False)
        assert math.isclose(edge_3d.length, 3.0, abs_tol=1e-9)
        assert edge_3d.midpoint == Point3D(0.5, 1.0, 1.0)

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

    def test_extract_dbm_geometry_1d_auto_limits_and_clipping_variants(self):
        context = Context(["x"])

        point_geometry = extract_dbm_geometry((context.x == 1).to_dbm_list()[0])
        assert isinstance(point_geometry, Interval1D)
        assert point_geometry.is_point
        assert point_geometry.lower == 1.0
        assert point_geometry.upper == 1.0

        clipped = extract_dbm_geometry((context.x <= 0).to_dbm_list()[0], limits=(1, 2))
        assert clipped == EmptyGeometry(dimension=1)

        free_geometry = extract_dbm_geometry(context.get_zero_federation().free_clock(context.x).to_dbm_list()[0])
        assert isinstance(free_geometry, Interval1D)
        assert free_geometry.lower == 0.0
        assert free_geometry.upper == 1.0
        assert not free_geometry.lower_clipped
        assert free_geometry.upper_clipped

        equal_open_empty = extract_dbm_geometry((context.x < 1).to_dbm_list()[0], limits=(1, 2))
        assert equal_open_empty == EmptyGeometry(dimension=1)

    def test_extract_federation_geometry_1d_clipped_to_empty_intervals(self):
        context = Context(["x"])
        federation = ((context.x >= 10) & (context.x <= 20)) | ((context.x >= 30) & (context.x <= 40))

        geometry = extract_federation_geometry(federation, limits=(0, 1))

        assert geometry == MultiInterval1D(intervals=tuple())

    def test_extract_federation_geometry_1d_exact_union_matches_contains(self):
        context = Context(["x"])
        federation = ((context.x > 0) & (context.x < 1)) | ((context.x >= 1) & (context.x <= 2))

        geometry = extract_federation_geometry(federation, limits=(-1, 3))

        assert isinstance(geometry, MultiInterval1D)
        assert len(geometry.intervals) == 1
        assert geometry.intervals[0] == Interval1D(0.0, 2.0, False, True, False, False)

        for value in [-0.5, 0.0, 0.25, 0.999, 1.0, 1.5, 2.0, 2.01]:
            assert _geometry_contains_1d(geometry, value) == _federation_contains_1d(federation, value)

    def test_extract_federation_geometry_1d_overlap_with_shared_clipped_upper(self):
        context = Context(["x"])
        federation = ((context.x >= 0) & (context.x <= 5)) | ((context.x >= 2) & (context.x <= 7))

        geometry = extract_federation_geometry(federation, limits=(0, 4))

        assert geometry == MultiInterval1D(intervals=(Interval1D(0.0, 4.0, True, True, False, True),))

    def test_extract_federation_geometry_1d_overlap_and_empty_cases(self):
        context = Context(["x"])
        overlap = ((context.x >= 0) & (context.x <= 3)) | ((context.x >= 1) & (context.x < 3))
        overlap_geometry = extract_federation_geometry(overlap)
        assert isinstance(overlap_geometry, MultiInterval1D)
        assert overlap_geometry.intervals == (Interval1D(0.0, 3.0, True, True, False, False),)

        touching_open = ((context.x >= 0) & (context.x < 1)) | ((context.x > 1) & (context.x <= 2))
        touching_open_geometry = extract_federation_geometry(touching_open, limits=(-1, 3))
        assert isinstance(touching_open_geometry, MultiInterval1D)
        assert len(touching_open_geometry.intervals) == 2

        empty = (context.x < 0) & (context.x > 0)
        empty_geometry = extract_federation_geometry(empty, limits=(-1, 1))
        assert empty_geometry == EmptyGeometry(dimension=1)

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

    def test_extract_dbm_geometry_2d_point_and_empty_cases(self):
        context = Context(["x", "y"])

        point_federation = (context.x == 1) & (context.y == 2)
        point_geometry = extract_dbm_geometry(point_federation.to_dbm_list()[0], limits=((0, 3), (0, 3)))
        assert isinstance(point_geometry, PointGeometry2D)
        assert point_geometry.point == Point2D(1.0, 2.0)
        assert point_geometry.is_closed
        assert not point_geometry.is_clipped

        sample_points = [(1.0, 2.0), (1.0, 2.001), (0.0, 0.0)]
        for x_value, y_value in sample_points:
            assert _geometry_contains_2d(point_geometry, x_value, y_value) == _federation_contains_2d(point_federation, x_value, y_value)

        empty_federation = (context.x < 0) & (context.x > 0) & (context.y == 0)
        empty_geometry = extract_federation_geometry(empty_federation, limits=((0, 1), (0, 1)))
        assert empty_geometry == EmptyGeometry(dimension=2)

    def test_extract_dbm_geometry_2d_auto_limits_and_infinite_bounds(self):
        context = Context(["x", "y"])

        point_geometry = extract_dbm_geometry(((context.x == 2) & (context.y == 2)).to_dbm_list()[0])
        assert isinstance(point_geometry, PointGeometry2D)
        assert point_geometry.point == Point2D(2.0, 2.0)

        strip_federation = context.x <= 1
        strip_geometry = extract_dbm_geometry(strip_federation.to_dbm_list()[0], limits=((0, 2), (0, 2)))
        assert isinstance(strip_geometry, PolygonGeometry2D)
        assert len(strip_geometry.vertices) == 4
        assert sum(1 for halfspace in strip_geometry.halfspaces if halfspace.is_clip) == 4
        assert any(not halfspace.is_clip for halfspace in strip_geometry.halfspaces)
        for x_value, y_value in [(0.0, 0.0), (1.0, 1.0), (1.001, 1.0), (0.5, 2.0)]:
            assert _geometry_contains_2d(strip_geometry, x_value, y_value) == _federation_contains_2d(strip_federation, x_value, y_value)

        x_free_geometry = extract_dbm_geometry(context.get_zero_federation().free_clock(context.x).to_dbm_list()[0])
        assert isinstance(x_free_geometry, SegmentGeometry2D)
        assert math.isclose(x_free_geometry.segment.start.y, 0.0, abs_tol=1e-9)
        assert math.isclose(x_free_geometry.segment.end.y, 0.0, abs_tol=1e-9)

        y_free_geometry = extract_dbm_geometry(context.get_zero_federation().free_clock(context.y).to_dbm_list()[0])
        assert isinstance(y_free_geometry, SegmentGeometry2D)
        assert math.isclose(y_free_geometry.segment.start.x, 0.0, abs_tol=1e-9)
        assert math.isclose(y_free_geometry.segment.end.x, 0.0, abs_tol=1e-9)

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

    def test_extract_dbm_geometry_2d_clipped_to_empty(self):
        context = Context(["x", "y"])
        geometry = extract_dbm_geometry(
            ((context.x >= 0) & (context.x <= 1) & (context.y >= 0) & (context.y <= 1)).to_dbm_list()[0],
            limits=((2, 3), (2, 3)),
        )
        assert geometry == EmptyGeometry(dimension=2)

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

    def test_extract_federation_geometry_2d_adjacent_open_and_closed_edges_stay_separate(self):
        context = Context(["x", "y"])
        closed_left = (context.x >= 0) & (context.x <= 1) & (context.y >= 0) & (context.y <= 1)
        open_right = (context.x > 1) & (context.x < 2) & (context.y >= 0) & (context.y < 1)
        federation = closed_left | open_right

        geometry = extract_federation_geometry(federation, limits=((0, 3), (0, 2)))

        assert isinstance(geometry, FederationGeometry2D)
        assert len(geometry.boundary_segments) == 5

        top_segments = [
            segment for segment in geometry.boundary_segments
            if math.isclose(segment.start.y, 1.0, abs_tol=1e-9) and math.isclose(segment.end.y, 1.0, abs_tol=1e-9)
        ]
        assert len(top_segments) == 2
        assert sorted(
            (
                round(min(segment.start.x, segment.end.x), 6),
                round(max(segment.start.x, segment.end.x), 6),
                segment.is_closed,
            )
            for segment in top_segments
        ) == [
            (0.0, 1.0, True),
            (1.0, 2.0, False),
        ]

        for x_value in [0.0, 0.5, 1.0, 1.5, 1.999]:
            for y_value in [0.0, 0.5, 0.999, 1.0]:
                assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(
                    federation, x_value, y_value
                )

    def test_extract_federation_geometry_2d_with_hole_and_public_face_structure(self):
        context = Context(["x", "y"])
        parts = [
            (context.x >= 0) & (context.x <= 3) & (context.y >= 0) & (context.y <= 1),
            (context.x >= 0) & (context.x <= 3) & (context.y >= 2) & (context.y <= 3),
            (context.x >= 0) & (context.x <= 1) & (context.y >= 1) & (context.y <= 2),
            (context.x >= 2) & (context.x <= 3) & (context.y >= 1) & (context.y <= 2),
        ]
        federation = parts[0] | parts[1] | parts[2] | parts[3]

        geometry = extract_federation_geometry(federation, limits=((0, 3), (0, 3)))

        assert isinstance(geometry, FederationGeometry2D)
        assert len(geometry.faces) == 1
        assert len(geometry.loops) == 2
        assert len(geometry.faces[0].holes) == 1

        outer = geometry.faces[0].outer
        hole = geometry.faces[0].holes[0]
        assert not outer.is_hole
        assert hole.is_hole
        assert math.isclose(outer.signed_area, 9.0, abs_tol=1e-9)
        assert math.isclose(hole.signed_area, -1.0, abs_tol=1e-9)

        grid_points = [
            (x_value / 2.0, y_value / 2.0)
            for x_value in range(0, 7)
            for y_value in range(0, 7)
        ]
        for x_value, y_value in grid_points:
            assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(federation, x_value, y_value)

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

    def test_extract_federation_geometry_2d_boundary_dedup_matches_contains(self):
        context = Context(["x", "y"])
        parts = [
            (context.x >= 0) & (context.x <= 1) & (context.y >= 0) & (context.y <= 1),
            (context.x >= 0) & (context.x <= 1) & (context.y >= 0) & (context.y <= 2),
            (context.x >= 0) & (context.x <= 1) & (context.y >= 1) & (context.y <= 3),
        ]
        federation = parts[0] | parts[1] | parts[2]

        geometry = extract_federation_geometry(federation, limits=((0, 1), (0, 3)))

        assert isinstance(geometry, FederationGeometry2D)
        assert len(geometry.dbm_geometries) >= 2
        assert len(geometry.faces) == 1
        assert len(geometry.loops) == 1
        assert len(geometry.boundary_segments) == 4
        assert math.isclose(geometry.loops[0].signed_area, 3.0, abs_tol=1e-9)

        for x_value in [0.0, 0.5, 1.0]:
            for y_value in [0.0, 1.0, 2.0, 3.0]:
                assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(federation, x_value, y_value)

    def test_extract_federation_geometry_2d_branching_boundary_matches_contains(self):
        context = Context(["x", "y"])
        parts = [
            (context.x >= 0) & (context.x <= 1) & (context.y >= 0) & (context.y <= 1),
            (context.x >= 0) & (context.x <= 1) & (context.y >= 0) & (context.y <= 2),
            (context.x >= 0) & (context.x <= 1) & (context.y >= 3) & (context.y <= 4),
            (context.x >= 1) & (context.x <= 2) & (context.y >= 1) & (context.y <= 3),
        ]
        federation = parts[0]
        for part in parts[1:]:
            federation = federation | part

        geometry = extract_federation_geometry(federation, limits=((0, 2), (0, 4)))

        assert isinstance(geometry, FederationGeometry2D)
        assert len(geometry.dbm_geometries) >= 3
        assert len(geometry.faces) == 2
        assert len(geometry.loops) == 2
        assert len(geometry.boundary_segments) == 12

        grid_points = [
            (x_value / 2.0, y_value / 2.0)
            for x_value in range(0, 5)
            for y_value in range(0, 9)
        ]
        for x_value, y_value in grid_points:
            assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(federation, x_value, y_value)

    def test_extract_federation_geometry_2d_complex_multi_hole_matches_contains(self):
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

        geometry = extract_federation_geometry(federation, limits=((0, 5), (0, 5)))

        assert isinstance(geometry, FederationGeometry2D)
        assert len(geometry.dbm_geometries) == 5
        assert len(geometry.faces) == 1
        assert len(geometry.loops) == 3
        assert len(geometry.boundary_segments) == 12
        assert len(geometry.faces[0].holes) == 2

        areas = sorted(round(loop.signed_area, 6) for loop in geometry.loops)
        assert areas == [-3.0, -3.0, 25.0]

        grid_points = [
            (x_value / 2.0, y_value / 2.0)
            for x_value in range(0, 11)
            for y_value in range(0, 11)
        ]
        for x_value, y_value in grid_points:
            assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(federation, x_value, y_value)

    def test_extract_federation_geometry_2d_isolated_segments_and_points(self):
        context = Context(["x", "y"])

        segment_federation = ((context.x - context.y == 0) & (context.x <= 1) & (context.y <= 1)) | (
            (context.x - context.y == 1) & (context.x <= 2) & (context.y <= 1)
        )
        segment_geometry = extract_federation_geometry(segment_federation, limits=((0, 3), (0, 3)))

        assert isinstance(segment_geometry, FederationGeometry2D)
        assert len(segment_geometry.boundary_segments) == 0
        assert len(segment_geometry.isolated_segments) == 2
        assert len(segment_geometry.isolated_points) == 0
        for x_value, y_value in [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0), (2.0, 1.0), (1.0, 1.0), (2.0, 0.0)]:
            assert _geometry_contains_2d(segment_geometry, x_value, y_value) == _federation_contains_2d(
                segment_federation, x_value, y_value
            )

        point_federation = (context.x == 0) & (context.y == 0)
        point_geometry = extract_federation_geometry(point_federation, limits=((0, 1), (0, 1)))
        assert isinstance(point_geometry, FederationGeometry2D)
        assert len(point_geometry.boundary_segments) == 0
        assert len(point_geometry.isolated_segments) == 0
        assert point_geometry.isolated_points == (Point2D(0.0, 0.0),)
        for x_value, y_value in [(0.0, 0.0), (0.0, 0.1), (0.1, 0.0)]:
            assert _geometry_contains_2d(point_geometry, x_value, y_value) == _federation_contains_2d(
                point_federation, x_value, y_value
            )

    def test_extract_federation_geometry_2d_point_filtered_by_polygon_or_segment(self):
        context = Context(["x", "y"])

        polygon_plus_inner_point = ((context.x >= 0) & (context.x <= 1) & (context.y >= 0) & (context.y <= 1)) | (
            (context.x == 0) & (context.y == 0)
        )
        polygon_geometry = extract_federation_geometry(polygon_plus_inner_point, limits=((0, 1), (0, 1)))
        assert isinstance(polygon_geometry, FederationGeometry2D)
        assert polygon_geometry.isolated_points == tuple()

        segment_plus_endpoint = ((context.x - context.y == 0) & (context.x <= 1) & (context.y <= 1)) | ((context.x == 0) & (context.y == 0))
        segment_geometry = extract_federation_geometry(segment_plus_endpoint, limits=((0, 1), (0, 1)))
        assert isinstance(segment_geometry, FederationGeometry2D)
        assert len(segment_geometry.isolated_segments) == 1
        assert segment_geometry.isolated_points == tuple()

        open_segment_plus_endpoint = (
            ((context.x - context.y == 0) & (context.x > 0) & (context.x < 1) & (context.y > 0) & (context.y < 1))
            | ((context.x == 0) & (context.y == 0))
        )
        open_segment_geometry = extract_federation_geometry(open_segment_plus_endpoint, limits=((0, 2), (0, 2)))
        assert isinstance(open_segment_geometry, FederationGeometry2D)
        assert len(open_segment_geometry.isolated_segments) == 1
        assert open_segment_geometry.isolated_points == tuple()

        open_segment_plus_off_point = (
            ((context.x - context.y == 0) & (context.x > 0) & (context.x < 1) & (context.y > 0) & (context.y < 1))
            | ((context.x == 0) & (context.y == 1))
        )
        off_point_geometry = extract_federation_geometry(open_segment_plus_off_point, limits=((0, 2), (0, 2)))
        assert isinstance(off_point_geometry, FederationGeometry2D)
        assert len(off_point_geometry.isolated_segments) == 1
        assert off_point_geometry.isolated_points == (Point2D(0.0, 1.0),)

    def test_extract_federation_geometry_2d_clipped_single_polygon_matches_contains(self):
        context = Context(["x", "y"])
        federation = context.x <= 1

        geometry = extract_federation_geometry(federation, limits=((0, 2), (0, 2)))

        assert isinstance(geometry, FederationGeometry2D)
        assert len(geometry.faces) == 1
        assert len(geometry.loops) == 1
        assert len(geometry.boundary_segments) == 4

        for x_value, y_value in [(0.0, 0.0), (1.0, 1.0), (1.5, 1.0), (0.5, 2.0)]:
            assert _geometry_contains_2d(geometry, x_value, y_value) == _federation_contains_2d(federation, x_value, y_value)

    def test_extract_dbm_geometry_3d_polyhedron_matches_contains(self):
        context = Context(["x", "y", "z"])
        federation = (
            (context.x >= 0) & (context.x <= 2)
            & (context.y >= 0) & (context.y <= 2)
            & (context.z >= 0) & (context.z <= 2)
            & (context.x - context.y < 1)
            & (context.y - context.z <= 1)
        )

        geometry = extract_dbm_geometry(federation.to_dbm_list()[0], limits=((0, 2), (0, 2), (0, 2)))

        assert isinstance(geometry, PolyhedronGeometry3D)
        assert len(geometry.vertices) >= 4
        assert len(geometry.faces) >= 4
        assert len(geometry.edges) >= 6

        sample_points = [
            (0.0, 0.0, 0.0),
            (0.5, 0.5, 0.5),
            (1.5, 1.0, 0.5),
            (2.0, 2.0, 2.0),
            (2.0, 0.0, 0.0),
            (1.5, 0.0, 2.0),
        ]
        for x_value, y_value, z_value in sample_points:
            assert _geometry_contains_3d(geometry, x_value, y_value, z_value) == _federation_contains_3d(
                federation, x_value, y_value, z_value
            )

    def test_extract_dbm_geometry_3d_face_segment_point_and_empty_cases(self):
        context = Context(["x", "y", "z"])

        face_geometry = extract_dbm_geometry(
            ((context.x <= 1) & (context.y <= 1) & (context.z == 0)).to_dbm_list()[0],
            limits=((0, 2), (0, 2), (0, 1)),
        )
        assert isinstance(face_geometry, FaceGeometry3D)
        assert len(face_geometry.face.vertices) == 4

        segment_geometry = extract_dbm_geometry(
            ((context.x == 0) & (context.y == 0) & (context.z <= 1)).to_dbm_list()[0],
            limits=((0, 1), (0, 1), (0, 2)),
        )
        assert isinstance(segment_geometry, SegmentGeometry3D)
        assert math.isclose(segment_geometry.segment.start.z, 0.0, abs_tol=1e-9)
        assert math.isclose(segment_geometry.segment.end.z, 1.0, abs_tol=1e-9)

        point_geometry = extract_dbm_geometry(
            ((context.x == 1) & (context.y == 1) & (context.z == 1)).to_dbm_list()[0],
            limits=((0, 2), (0, 2), (0, 2)),
        )
        assert isinstance(point_geometry, PointGeometry3D)
        assert point_geometry.point == Point3D(1.0, 1.0, 1.0)

        empty_geometry = extract_federation_geometry(
            (context.x < 0) & (context.x > 0) & (context.y == 0) & (context.z == 0),
            limits=((0, 1), (0, 1), (0, 1)),
        )
        assert empty_geometry == EmptyGeometry(dimension=3)

    def test_extract_dbm_geometry_3d_auto_limits_expand_single_point_and_clipped_empty_federation(self):
        context = Context(["x", "y", "z"])

        point_geometry = extract_dbm_geometry(
            ((context.x == 1) & (context.y == 1) & (context.z == 1)).to_dbm_list()[0]
        )
        assert isinstance(point_geometry, PointGeometry3D)
        assert point_geometry.point == Point3D(1.0, 1.0, 1.0)

        clipped_empty = extract_federation_geometry(
            ((context.x >= 10) & (context.x <= 11) & (context.y >= 10) & (context.y <= 11) & (context.z >= 10) & (context.z <= 11)),
            limits=((0, 1), (0, 1), (0, 1)),
        )
        assert clipped_empty == EmptyGeometry(dimension=3)

    def test_extract_federation_geometry_3d_matches_contains(self):
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
        federation = left | right

        geometry = extract_federation_geometry(federation, limits=((0, 3), (0, 1), (0, 1)))

        assert isinstance(geometry, FederationGeometry3D)
        assert len(geometry.dbm_geometries) == 2

        sample_points = [
            (0.5, 0.5, 0.5),
            (2.5, 0.5, 0.5),
            (1.5, 0.5, 0.5),
            (3.0, 1.0, 1.0),
        ]
        for x_value, y_value, z_value in sample_points:
            assert _geometry_contains_3d(geometry, x_value, y_value, z_value) == _federation_contains_3d(
                federation, x_value, y_value, z_value
            )

    def test_extract_geometry_invalid_inputs_and_invalid_limits(self):
        context_1d = Context(["x"])
        context_2d = Context(["x", "y"])
        context_4d = Context(["a", "b", "c", "d"])

        with pytest.raises(TypeError):
            extract_dbm_geometry(object())
        with pytest.raises(TypeError):
            extract_federation_geometry(object())

        dbm_1d = (context_1d.x <= 1).to_dbm_list()[0]
        with pytest.raises(ValueError):
            extract_dbm_geometry(dbm_1d, limits=(0,))
        with pytest.raises(ValueError):
            extract_dbm_geometry(dbm_1d, limits=(2, 1))

        dbm_2d = ((context_2d.x <= 1) & (context_2d.y <= 1)).to_dbm_list()[0]
        with pytest.raises(ValueError):
            extract_dbm_geometry(dbm_2d, limits=(0, 1))
        with pytest.raises(ValueError):
            extract_dbm_geometry(dbm_2d, limits="invalid")
        with pytest.raises(ValueError):
            extract_dbm_geometry(dbm_2d, limits=((0, 1),))
        with pytest.raises(ValueError):
            extract_dbm_geometry(dbm_2d, limits=((0, 1), 1))
        with pytest.raises(ValueError):
            extract_dbm_geometry(dbm_2d, limits=((1, 0), (0, 1)))
        with pytest.raises(ValueError):
            extract_dbm_geometry(dbm_2d, limits=((0, 1), (1, 0)))

        dbm_4d = (context_4d.a <= 1).to_dbm_list()[0]
        with pytest.raises(ValueError):
            extract_dbm_geometry(dbm_4d)
        with pytest.raises(ValueError):
            extract_federation_geometry(context_4d.a <= 1)

    def test_extract_federation_geometry_3d_invalid_and_high_dim_cases(self):
        context = Context(["x", "y", "z"])
        federation = (context.x <= 1) & (context.y <= 1) & (context.z <= 1)
        context_4d = Context(["a", "b", "c", "d"])

        geometry = extract_dbm_geometry(federation.to_dbm_list()[0])
        federation_geometry = extract_federation_geometry(federation)
        assert isinstance(geometry, PolyhedronGeometry3D)
        assert isinstance(federation_geometry, FederationGeometry3D)

        with pytest.raises(ValueError):
            extract_dbm_geometry(federation.to_dbm_list()[0], limits=((0, 1), (0, 1)))
        with pytest.raises(ValueError):
            extract_dbm_geometry(federation.to_dbm_list()[0], limits=((0, 1), (0, 1), (1, 0)))
        with pytest.raises(ValueError):
            extract_dbm_geometry(federation.to_dbm_list()[0], limits=(0, 1, 2))
        with pytest.raises(ValueError):
            extract_dbm_geometry(federation.to_dbm_list()[0], limits=((0, 1, 2), (0, 1), (0, 1)))
        with pytest.raises(ValueError):
            extract_dbm_geometry(federation.to_dbm_list()[0], limits=((0, 1), (0, 1, 2), (0, 1)))
        with pytest.raises(ValueError):
            extract_dbm_geometry(federation.to_dbm_list()[0], limits=((0, 1), (0, 1), (0, 1, 2)))
        with pytest.raises(ValueError):
            extract_dbm_geometry(federation.to_dbm_list()[0], limits=((1, 0), (0, 1), (0, 1)))
        with pytest.raises(ValueError):
            extract_dbm_geometry(federation.to_dbm_list()[0], limits=((0, 1), (1, 0), (0, 1)))

        with pytest.raises(ValueError):
            extract_dbm_geometry((context_4d.a <= 1).to_dbm_list()[0])
        with pytest.raises(ValueError):
            extract_federation_geometry(context_4d.a <= 1)
