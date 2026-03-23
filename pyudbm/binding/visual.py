"""
Geometry foundation for visualization-oriented DBM / federation handling.

This module intentionally starts below the matplotlib layer. It provides the
pure-Python geometry extraction needed by future plotting helpers without
making matplotlib a hard dependency of :mod:`pyudbm`.

The current implementation covers the Phase 0 / Phase 1 foundation:

* 1D DBM interval extraction;
* 1D federation exact interval union;
* 2D DBM convex geometry extraction from DBM half-spaces;
* 2D federation exact boundary extraction for polygonal DBM unions.

Actual matplotlib rendering helpers are intentionally deferred to the later
plotting phase.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

from .udbm import DBM, Federation

__all__ = [
    "BoundaryLoop2D",
    "BoundarySegment2D",
    "EmptyGeometry",
    "Face2D",
    "FederationGeometry2D",
    "HalfSpace2D",
    "Interval1D",
    "MultiInterval1D",
    "Point2D",
    "PointGeometry2D",
    "PolygonGeometry2D",
    "SegmentGeometry2D",
    "extract_dbm_geometry",
    "extract_federation_geometry",
]

_GEOMETRY_EPSILON = 1e-9


@dataclass(frozen=True)
class EmptyGeometry:
    """Empty visualization geometry."""

    dimension: int


@dataclass(frozen=True)
class Interval1D:
    """Closed/open bounded interval after optional clipping."""

    lower: float
    upper: float
    lower_closed: bool
    upper_closed: bool
    lower_clipped: bool = False
    upper_clipped: bool = False

    @property
    def is_point(self) -> bool:
        """Return whether the interval collapses to one included point."""

        return _almost_equal(self.lower, self.upper) and self.lower_closed and self.upper_closed


@dataclass(frozen=True)
class MultiInterval1D:
    """Exact finite union of 1D intervals."""

    intervals: Tuple[Interval1D, ...]


@dataclass(frozen=True)
class Point2D:
    """One 2D point."""

    x: float
    y: float


@dataclass(frozen=True)
class HalfSpace2D:
    """Affine 2D half-space ``a*x + b*y <= c`` or ``< c``."""

    a: float
    b: float
    c: float
    is_strict: bool = False
    is_clip: bool = False

    def evaluate(self, point: Point2D) -> float:
        """Return ``a*x + b*y - c`` at ``point``."""

        return (self.a * point.x) + (self.b * point.y) - self.c

    def contains(self, point: Point2D, respect_strict: bool = True) -> bool:
        """Return whether ``point`` satisfies this half-space."""

        value = self.evaluate(point)
        if respect_strict and self.is_strict:
            return value < -_GEOMETRY_EPSILON
        return value <= _GEOMETRY_EPSILON

    def contains_on_closure(self, point: Point2D) -> bool:
        """Return whether ``point`` lies in the closure of this half-space."""

        return self.evaluate(point) <= _GEOMETRY_EPSILON

    def is_active(self, point: Point2D) -> bool:
        """Return whether ``point`` lies on the boundary line of this half-space."""

        return abs(self.evaluate(point)) <= _GEOMETRY_EPSILON


@dataclass(frozen=True)
class BoundarySegment2D:
    """One directed 2D boundary segment."""

    start: Point2D
    end: Point2D
    is_closed: bool
    is_clipped: bool

    @property
    def length(self) -> float:
        """Return Euclidean segment length."""

        return math.hypot(self.end.x - self.start.x, self.end.y - self.start.y)

    @property
    def midpoint(self) -> Point2D:
        """Return segment midpoint."""

        return Point2D((self.start.x + self.end.x) / 2.0, (self.start.y + self.end.y) / 2.0)


@dataclass(frozen=True)
class PolygonGeometry2D:
    """Convex 2D polygon extracted from one DBM plus clip box."""

    vertices: Tuple[Point2D, ...]
    edges: Tuple[BoundarySegment2D, ...]
    halfspaces: Tuple[HalfSpace2D, ...]


@dataclass(frozen=True)
class SegmentGeometry2D:
    """Degenerate 2D line-segment geometry extracted from one DBM."""

    segment: BoundarySegment2D
    halfspaces: Tuple[HalfSpace2D, ...]


@dataclass(frozen=True)
class PointGeometry2D:
    """Degenerate 2D point geometry extracted from one DBM."""

    point: Point2D
    is_closed: bool
    is_clipped: bool
    halfspaces: Tuple[HalfSpace2D, ...]


@dataclass(frozen=True)
class BoundaryLoop2D:
    """Closed boundary loop of one 2D federation component or hole."""

    segments: Tuple[BoundarySegment2D, ...]
    is_hole: bool

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        """Return ordered loop vertices."""

        return tuple(segment.start for segment in self.segments)

    @property
    def signed_area(self) -> float:
        """Return loop signed area."""

        return _signed_area(self.vertices)


@dataclass(frozen=True)
class Face2D:
    """One exact 2D face consisting of an outer loop and optional holes."""

    outer: BoundaryLoop2D
    holes: Tuple[BoundaryLoop2D, ...]


@dataclass(frozen=True)
class FederationGeometry2D:
    """Exact 2D geometry summary for one federation clipped to a render box."""

    dbm_geometries: Tuple[Union[PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D], ...]
    boundary_segments: Tuple[BoundarySegment2D, ...]
    loops: Tuple[BoundaryLoop2D, ...]
    faces: Tuple[Face2D, ...]
    isolated_segments: Tuple[BoundarySegment2D, ...]
    isolated_points: Tuple[Point2D, ...]
    limits: Tuple[Tuple[float, float], Tuple[float, float]]


def _almost_equal(left: float, right: float, epsilon: float = _GEOMETRY_EPSILON) -> bool:
    return abs(left - right) <= epsilon


def _point_key(point: Point2D) -> Tuple[int, int]:
    return int(round(point.x * 1000000000.0)), int(round(point.y * 1000000000.0))


def _normalize_1d_limits(limits: Optional[Tuple[float, float]], intervals: Sequence[Tuple[Optional[float], Optional[float]]]) -> Tuple[float, float]:
    if limits is not None:
        if not isinstance(limits, tuple) or len(limits) != 2:
            raise ValueError("1D limits must be a tuple of the form (xmin, xmax).")
        lower = float(limits[0])
        upper = float(limits[1])
        if not lower < upper:
            raise ValueError("1D limits require xmin < xmax.")
        return lower, upper

    finite_values = []  # type: List[float]
    for lower, upper in intervals:
        if lower is not None:
            finite_values.append(float(lower))
        if upper is not None:
            finite_values.append(float(upper))
    finite_values = finite_values or [-5.0, 5.0]

    minimum = min(finite_values)
    maximum = max(finite_values)
    if _almost_equal(minimum, maximum):
        return minimum - 1.0, maximum + 1.0

    return minimum, maximum


def _normalize_2d_limits(
    limits: Optional[Tuple[Tuple[float, float], Tuple[float, float]]],
    bounds: Sequence[Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]],
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    if limits is not None:
        if not isinstance(limits, tuple) or len(limits) != 2:
            raise ValueError("2D limits must be ((xmin, xmax), (ymin, ymax)).")
        x_limits = limits[0]
        y_limits = limits[1]
        if not isinstance(x_limits, tuple) or len(x_limits) != 2:
            raise ValueError("2D x limits must be a tuple of the form (xmin, xmax).")
        if not isinstance(y_limits, tuple) or len(y_limits) != 2:
            raise ValueError("2D y limits must be a tuple of the form (ymin, ymax).")

        xmin = float(x_limits[0])
        xmax = float(x_limits[1])
        ymin = float(y_limits[0])
        ymax = float(y_limits[1])
        if not xmin < xmax:
            raise ValueError("2D limits require xmin < xmax.")
        if not ymin < ymax:
            raise ValueError("2D limits require ymin < ymax.")
        return (xmin, xmax), (ymin, ymax)

    x_values = []  # type: List[float]
    y_values = []  # type: List[float]
    for xmin, xmax, ymin, ymax in bounds:
        if xmin is not None:
            x_values.append(float(xmin))
        if xmax is not None:
            x_values.append(float(xmax))
        if ymin is not None:
            y_values.append(float(ymin))
        if ymax is not None:
            y_values.append(float(ymax))
    x_values = x_values or [-5.0, 5.0]
    y_values = y_values or [-5.0, 5.0]

    x_lower = min(x_values)
    x_upper = max(x_values)
    y_lower = min(y_values)
    y_upper = max(y_values)

    if _almost_equal(x_lower, x_upper):
        x_lower -= 1.0
        x_upper += 1.0
    if _almost_equal(y_lower, y_upper):
        y_lower -= 1.0
        y_upper += 1.0

    return (x_lower, x_upper), (y_lower, y_upper)


def _dbm_axis_bounds_1d(dbm: DBM) -> Tuple[Optional[float], Optional[float], bool, bool]:
    lower = None  # type: Optional[float]
    upper = None  # type: Optional[float]
    lower_closed = True
    upper_closed = True

    if not dbm.is_infinity(0, 1):
        lower = float(-dbm.bound(0, 1))
        lower_closed = not dbm.is_strict(0, 1)

    if not dbm.is_infinity(1, 0):
        upper = float(dbm.bound(1, 0))
        upper_closed = not dbm.is_strict(1, 0)

    return lower, upper, lower_closed, upper_closed


def _dbm_axis_bounds_2d(dbm: DBM) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    x_lower = None if dbm.is_infinity(0, 1) else float(-dbm.bound(0, 1))
    x_upper = None if dbm.is_infinity(1, 0) else float(dbm.bound(1, 0))
    y_lower = None if dbm.is_infinity(0, 2) else float(-dbm.bound(0, 2))
    y_upper = None if dbm.is_infinity(2, 0) else float(dbm.bound(2, 0))
    return x_lower, x_upper, y_lower, y_upper


def _merge_intervals(intervals: Sequence[Interval1D]) -> MultiInterval1D:
    if not intervals:
        return MultiInterval1D(intervals=tuple())

    ordered = sorted(intervals, key=lambda item: (item.lower, not item.lower_closed, item.upper, item.upper_closed))
    merged = [ordered[0]]

    for interval in ordered[1:]:
        current = merged[-1]
        if interval.lower < current.upper - _GEOMETRY_EPSILON:
            merged[-1] = _merge_interval_pair(current, interval)
        elif _almost_equal(interval.lower, current.upper) and (current.upper_closed or interval.lower_closed):
            merged[-1] = _merge_interval_pair(current, interval)
        else:
            merged.append(interval)

    return MultiInterval1D(intervals=tuple(merged))


def _merge_interval_pair(left: Interval1D, right: Interval1D) -> Interval1D:
    upper = left.upper
    upper_closed = left.upper_closed
    upper_clipped = left.upper_clipped
    if right.upper > upper + _GEOMETRY_EPSILON:
        upper = right.upper
        upper_closed = right.upper_closed
        upper_clipped = right.upper_clipped
    elif _almost_equal(right.upper, upper):
        upper_closed = upper_closed or right.upper_closed
        upper_clipped = upper_clipped and right.upper_clipped

    return Interval1D(
        lower=left.lower,
        upper=upper,
        lower_closed=left.lower_closed,
        upper_closed=upper_closed,
        lower_clipped=left.lower_clipped,
        upper_clipped=upper_clipped,
    )


def _build_halfspaces_for_dbm_2d(dbm: DBM, limits: Tuple[Tuple[float, float], Tuple[float, float]]) -> Tuple[HalfSpace2D, ...]:
    result = []  # type: List[HalfSpace2D]
    for i in range(dbm.dimension):
        for j in range(dbm.dimension):
            if i == j or dbm.is_infinity(i, j):
                continue

            coefficients = [0.0, 0.0]
            if i > 0:
                coefficients[i - 1] += 1.0
            if j > 0:
                coefficients[j - 1] -= 1.0

            result.append(HalfSpace2D(coefficients[0], coefficients[1], float(dbm.bound(i, j)), dbm.is_strict(i, j), False))

    (xmin, xmax), (ymin, ymax) = limits
    result.extend(
        [
            HalfSpace2D(1.0, 0.0, xmax, False, True),
            HalfSpace2D(-1.0, 0.0, -xmin, False, True),
            HalfSpace2D(0.0, 1.0, ymax, False, True),
            HalfSpace2D(0.0, -1.0, -ymin, False, True),
        ]
    )
    return tuple(result)


def _pairwise_line_intersections(halfspaces: Sequence[HalfSpace2D]) -> List[Point2D]:
    points = []  # type: List[Point2D]
    for index, left in enumerate(halfspaces):
        for right in halfspaces[index + 1 :]:
            determinant = (left.a * right.b) - (left.b * right.a)
            if abs(determinant) <= _GEOMETRY_EPSILON:
                continue

            x = ((left.c * right.b) - (left.b * right.c)) / determinant
            y = ((left.a * right.c) - (left.c * right.a)) / determinant
            points.append(Point2D(x, y))
    return points


def _point_in_halfspaces(point: Point2D, halfspaces: Sequence[HalfSpace2D], respect_strict: bool = True) -> bool:
    return all(halfspace.contains(point, respect_strict=respect_strict) for halfspace in halfspaces)


def _unique_points(points: Iterable[Point2D]) -> Tuple[Point2D, ...]:
    mapping = {}  # type: Dict[Tuple[int, int], Point2D]
    for point in points:
        mapping[_point_key(point)] = point
    return tuple(mapping.values())


def _cross(origin: Point2D, left: Point2D, right: Point2D) -> float:
    return ((left.x - origin.x) * (right.y - origin.y)) - ((left.y - origin.y) * (right.x - origin.x))


def _convex_hull(points: Sequence[Point2D]) -> Tuple[Point2D, ...]:
    ordered = sorted(_unique_points(points), key=lambda item: (item.x, item.y))
    if len(ordered) <= 1:
        return tuple(ordered)

    lower = []  # type: List[Point2D]
    for point in ordered:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], point) <= _GEOMETRY_EPSILON:
            lower.pop()
        lower.append(point)

    upper = []  # type: List[Point2D]
    for point in reversed(ordered):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], point) <= _GEOMETRY_EPSILON:
            upper.pop()
        upper.append(point)

    hull = lower[:-1] + upper[:-1]
    return tuple(_unique_points(hull))


def _active_halfspaces(point: Point2D, halfspaces: Sequence[HalfSpace2D]) -> Tuple[HalfSpace2D, ...]:
    return tuple(halfspace for halfspace in halfspaces if halfspace.is_active(point))


def _segment_from_points(start: Point2D, end: Point2D, halfspaces: Sequence[HalfSpace2D]) -> BoundarySegment2D:
    midpoint = Point2D((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)
    active = _active_halfspaces(midpoint, halfspaces)
    return BoundarySegment2D(
        start=start,
        end=end,
        is_closed=_point_in_halfspaces(midpoint, halfspaces, respect_strict=True),
        is_clipped=bool(active) and all(halfspace.is_clip for halfspace in active),
    )


def _extract_dbm_geometry_2d(dbm: DBM, limits: Tuple[Tuple[float, float], Tuple[float, float]]) -> Union[EmptyGeometry, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D]:
    halfspaces = _build_halfspaces_for_dbm_2d(dbm, limits)
    candidate_points = [point for point in _pairwise_line_intersections(halfspaces) if _point_in_halfspaces(point, halfspaces, respect_strict=False)]
    unique_points = _unique_points(candidate_points)
    if not unique_points:
        return EmptyGeometry(dimension=2)

    hull = _convex_hull(unique_points)
    if len(hull) == 1:
        point = hull[0]
        return PointGeometry2D(
            point=point,
            is_closed=_point_in_halfspaces(point, halfspaces, respect_strict=True),
            is_clipped=any(halfspace.is_clip for halfspace in _active_halfspaces(point, halfspaces)),
            halfspaces=halfspaces,
        )
    if len(hull) == 2:
        segment = _segment_from_points(hull[0], hull[1], halfspaces)
        return SegmentGeometry2D(segment=segment, halfspaces=halfspaces)

    edges = []  # type: List[BoundarySegment2D]
    for index, start in enumerate(hull):
        end = hull[(index + 1) % len(hull)]
        edges.append(_segment_from_points(start, end, halfspaces))
    return PolygonGeometry2D(vertices=hull, edges=tuple(edges), halfspaces=halfspaces)


def _orientation(point_a: Point2D, point_b: Point2D, point_c: Point2D) -> float:
    return ((point_b.x - point_a.x) * (point_c.y - point_a.y)) - ((point_b.y - point_a.y) * (point_c.x - point_a.x))


def _segment_intersection_parameters(left: BoundarySegment2D, right: BoundarySegment2D) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    p = left.start
    q = right.start
    r = Point2D(left.end.x - left.start.x, left.end.y - left.start.y)
    s = Point2D(right.end.x - right.start.x, right.end.y - right.start.y)
    denominator = (r.x * s.y) - (r.y * s.x)
    qp = Point2D(q.x - p.x, q.y - p.y)

    if abs(denominator) <= _GEOMETRY_EPSILON:
        if abs((qp.x * r.y) - (qp.y * r.x)) > _GEOMETRY_EPSILON:
            return tuple(), tuple()

        if abs(r.x) >= abs(r.y):
            left_values = sorted([0.0, 1.0, (right.start.x - left.start.x) / r.x if abs(r.x) > _GEOMETRY_EPSILON else 0.0, (right.end.x - left.start.x) / r.x if abs(r.x) > _GEOMETRY_EPSILON else 0.0])
        else:
            left_values = sorted([0.0, 1.0, (right.start.y - left.start.y) / r.y if abs(r.y) > _GEOMETRY_EPSILON else 0.0, (right.end.y - left.start.y) / r.y if abs(r.y) > _GEOMETRY_EPSILON else 0.0])

        overlap_start = max(0.0, left_values[1])
        overlap_end = min(1.0, left_values[2])
        if overlap_end <= overlap_start + _GEOMETRY_EPSILON:
            return tuple(), tuple()

        if abs(s.x) >= abs(s.y):
            right_start = (left.start.x + (r.x * overlap_start) - right.start.x) / s.x if abs(s.x) > _GEOMETRY_EPSILON else 0.0
            right_end = (left.start.x + (r.x * overlap_end) - right.start.x) / s.x if abs(s.x) > _GEOMETRY_EPSILON else 0.0
        else:
            right_start = (left.start.y + (r.y * overlap_start) - right.start.y) / s.y if abs(s.y) > _GEOMETRY_EPSILON else 0.0
            right_end = (left.start.y + (r.y * overlap_end) - right.start.y) / s.y if abs(s.y) > _GEOMETRY_EPSILON else 0.0

        return (overlap_start, overlap_end), (right_start, right_end)

    left_parameter = ((qp.x * s.y) - (qp.y * s.x)) / denominator
    right_parameter = ((qp.x * r.y) - (qp.y * r.x)) / denominator
    if -_GEOMETRY_EPSILON <= left_parameter <= 1.0 + _GEOMETRY_EPSILON and -_GEOMETRY_EPSILON <= right_parameter <= 1.0 + _GEOMETRY_EPSILON:
        left_parameter = min(1.0, max(0.0, left_parameter))
        right_parameter = min(1.0, max(0.0, right_parameter))
        return (left_parameter,), (right_parameter,)
    return tuple(), tuple()


def _point_along(segment: BoundarySegment2D, parameter: float) -> Point2D:
    return Point2D(
        segment.start.x + ((segment.end.x - segment.start.x) * parameter),
        segment.start.y + ((segment.end.y - segment.start.y) * parameter),
    )


def _split_boundary_segments(segments: Sequence[BoundarySegment2D]) -> Tuple[BoundarySegment2D, ...]:
    split_parameters = {index: [0.0, 1.0] for index in range(len(segments))}  # type: Dict[int, List[float]]
    for left_index, left in enumerate(segments):
        for right_index in range(left_index + 1, len(segments)):
            right = segments[right_index]
            left_parameters, right_parameters = _segment_intersection_parameters(left, right)
            split_parameters[left_index].extend(left_parameters)
            split_parameters[right_index].extend(right_parameters)

    result = []  # type: List[BoundarySegment2D]
    for index, segment in enumerate(segments):
        parameters = sorted(set(min(1.0, max(0.0, value)) for value in split_parameters[index]))
        for left_parameter, right_parameter in zip(parameters, parameters[1:]):
            start = _point_along(segment, left_parameter)
            end = _point_along(segment, right_parameter)
            piece = BoundarySegment2D(start=start, end=end, is_closed=segment.is_closed, is_clipped=segment.is_clipped)
            if piece.length > _GEOMETRY_EPSILON:
                result.append(piece)
    return tuple(result)


def _offset_point_left_of(segment: BoundarySegment2D) -> Tuple[Point2D, Point2D]:
    direction_x = segment.end.x - segment.start.x
    direction_y = segment.end.y - segment.start.y
    length = math.hypot(direction_x, direction_y)
    offset = max(min(length, 1.0) * 1e-6, 1e-7)
    normal_x = -direction_y / length
    normal_y = direction_x / length
    midpoint = segment.midpoint
    return (
        Point2D(midpoint.x + (normal_x * offset), midpoint.y + (normal_y * offset)),
        Point2D(midpoint.x - (normal_x * offset), midpoint.y - (normal_y * offset)),
    )


def _point_in_polygon_union(point: Point2D, polygons: Sequence[PolygonGeometry2D]) -> bool:
    return any(_point_in_halfspaces(point, polygon.halfspaces, respect_strict=True) for polygon in polygons)


def _exact_federation_boundary_2d(polygons: Sequence[PolygonGeometry2D]) -> Tuple[BoundarySegment2D, ...]:
    if not polygons:
        return tuple()

    candidate_segments = []  # type: List[BoundarySegment2D]
    for polygon in polygons:
        candidate_segments.extend(polygon.edges)

    split_segments = _split_boundary_segments(candidate_segments)
    deduplicated = {}  # type: Dict[Tuple[Tuple[int, int], Tuple[int, int]], BoundarySegment2D]

    for segment in split_segments:
        left_probe, right_probe = _offset_point_left_of(segment)
        left_inside = _point_in_polygon_union(left_probe, polygons)
        right_inside = _point_in_polygon_union(right_probe, polygons)
        if left_inside == right_inside:
            continue

        midpoint = segment.midpoint
        is_closed = _point_in_polygon_union(midpoint, polygons)
        key = tuple(sorted((_point_key(segment.start), _point_key(segment.end))))  # type: ignore[arg-type]
        existing = deduplicated.get(key)
        if existing is None:
            deduplicated[key] = BoundarySegment2D(
                start=segment.start,
                end=segment.end,
                is_closed=is_closed,
                is_clipped=segment.is_clipped,
            )
        else:
            deduplicated[key] = BoundarySegment2D(
                start=existing.start,
                end=existing.end,
                is_closed=existing.is_closed or is_closed,
                is_clipped=existing.is_clipped and segment.is_clipped,
            )

    return tuple(deduplicated.values())


def _segment_angle(segment: BoundarySegment2D) -> float:
    return math.atan2(segment.end.y - segment.start.y, segment.end.x - segment.start.x)


def _choose_next_boundary_segment(current: BoundarySegment2D, candidates: Sequence[BoundarySegment2D]) -> BoundarySegment2D:
    current_angle = _segment_angle(current)
    best_segment = candidates[0]
    best_turn = None  # type: Optional[float]
    for candidate in candidates:
        turn = (_segment_angle(candidate) - current_angle) % (2.0 * math.pi)
        if best_turn is None or turn < best_turn - _GEOMETRY_EPSILON:
            best_turn = turn
            best_segment = candidate
    return best_segment


def _trace_boundary_loops(boundary_segments: Sequence[BoundarySegment2D]) -> Tuple[BoundaryLoop2D, ...]:
    outgoing = {}  # type: Dict[Tuple[int, int], List[int]]
    for index, segment in enumerate(boundary_segments):
        outgoing.setdefault(_point_key(segment.start), []).append(index)

    unused = set(range(len(boundary_segments)))
    loops = []  # type: List[BoundaryLoop2D]
    while unused:
        start_index = next(iter(unused))
        first = boundary_segments[start_index]
        current = first
        loop_segments = [current]
        unused.remove(start_index)
        start_key = _point_key(first.start)
        current_key = _point_key(first.end)

        while current_key != start_key:
            candidates = [index for index in outgoing.get(current_key, []) if index in unused]
            next_index = candidates[0]
            if len(candidates) > 1:
                next_segment = _choose_next_boundary_segment(current, [boundary_segments[index] for index in candidates])
                next_index = boundary_segments.index(next_segment)

            current = boundary_segments[next_index]
            loop_segments.append(current)
            unused.remove(next_index)
            current_key = _point_key(current.end)

        vertices = tuple(segment.start for segment in loop_segments)
        loops.append(BoundaryLoop2D(segments=tuple(loop_segments), is_hole=_signed_area(vertices) < 0.0))

    return tuple(loops)


def _segments_are_mergeable(left: BoundarySegment2D, right: Optional[BoundarySegment2D]) -> bool:
    if right is None:
        return False
    if left.is_closed != right.is_closed or left.is_clipped != right.is_clipped:
        return False

    left_dx = left.end.x - left.start.x
    left_dy = left.end.y - left.start.y
    right_dx = right.end.x - right.start.x
    right_dy = right.end.y - right.start.y
    return abs((left_dx * right_dy) - (left_dy * right_dx)) <= _GEOMETRY_EPSILON


def _merge_loop_segments(loop: BoundaryLoop2D) -> BoundaryLoop2D:
    segments = list(loop.segments)
    changed = True
    while changed and len(segments) > 1:
        changed = False
        merged = []  # type: List[BoundarySegment2D]
        index = 0
        while index < len(segments):
            current = segments[index]
            nxt = segments[index + 1] if index + 1 < len(segments) else None
            if _segments_are_mergeable(current, nxt):
                merged.append(
                    BoundarySegment2D(
                        start=current.start,
                        end=nxt.end,
                        is_closed=current.is_closed,
                        is_clipped=current.is_clipped,
                    )
                )
                changed = True
                index += 2
            else:
                merged.append(current)
                index += 1

        if len(merged) > 1 and _segments_are_mergeable(merged[-1], merged[0]):
            merged[0] = BoundarySegment2D(
                start=merged[-1].start,
                end=merged[0].end,
                is_closed=merged[0].is_closed,
                is_clipped=merged[0].is_clipped,
            )
            merged.pop()
            changed = True
        if changed:
            segments = merged

    return BoundaryLoop2D(segments=tuple(segments), is_hole=loop.is_hole)


def _merge_boundary_loops(loops: Sequence[BoundaryLoop2D]) -> Tuple[BoundaryLoop2D, ...]:
    return tuple(_merge_loop_segments(loop) for loop in loops)


def _signed_area(vertices: Sequence[Point2D]) -> float:
    if len(vertices) < 3:
        return 0.0
    area = 0.0
    for index, current in enumerate(vertices):
        nxt = vertices[(index + 1) % len(vertices)]
        area += (current.x * nxt.y) - (nxt.x * current.y)
    return area / 2.0


def _point_in_loop(point: Point2D, loop: BoundaryLoop2D) -> bool:
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


def _build_faces_from_loops(loops: Sequence[BoundaryLoop2D]) -> Tuple[Face2D, ...]:
    outers = [loop for loop in loops if not loop.is_hole]
    holes = [loop for loop in loops if loop.is_hole]
    faces = []  # type: List[Face2D]

    for outer in outers:
        contained_holes = []  # type: List[BoundaryLoop2D]
        for hole in holes:
            if _point_in_loop(hole.vertices[0], outer):
                contained_holes.append(hole)
        faces.append(Face2D(outer=outer, holes=tuple(contained_holes)))
    return tuple(faces)


def _extract_degenerate_union_segments(
    dbm_geometries: Sequence[Union[PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D]],
    polygons: Sequence[PolygonGeometry2D],
) -> Tuple[BoundarySegment2D, ...]:
    segments = []  # type: List[BoundarySegment2D]
    for geometry in dbm_geometries:
        if not isinstance(geometry, SegmentGeometry2D):
            continue
        midpoint = geometry.segment.midpoint
        if not _point_in_polygon_union(midpoint, polygons):
            segments.append(geometry.segment)
    return tuple(segments)


def _extract_degenerate_union_points(
    dbm_geometries: Sequence[Union[PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D]],
    polygons: Sequence[PolygonGeometry2D],
    segments: Sequence[BoundarySegment2D],
) -> Tuple[Point2D, ...]:
    result = []  # type: List[Point2D]
    for geometry in dbm_geometries:
        if not isinstance(geometry, PointGeometry2D):
            continue
        point = geometry.point
        if _point_in_polygon_union(point, polygons) or any(_point_on_segment(point, segment) for segment in segments):
            continue
        result.append(point)
    return tuple(_unique_points(result))


def _point_on_segment(point: Point2D, segment: BoundarySegment2D) -> bool:
    cross = _orientation(segment.start, segment.end, point)
    if abs(cross) > _GEOMETRY_EPSILON:
        return False

    min_x = min(segment.start.x, segment.end.x) - _GEOMETRY_EPSILON
    max_x = max(segment.start.x, segment.end.x) + _GEOMETRY_EPSILON
    min_y = min(segment.start.y, segment.end.y) - _GEOMETRY_EPSILON
    max_y = max(segment.start.y, segment.end.y) + _GEOMETRY_EPSILON
    return min_x <= point.x <= max_x and min_y <= point.y <= max_y


def extract_dbm_geometry(
    dbm: DBM,
    limits: Optional[Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]] = None,
) -> Union[EmptyGeometry, Interval1D, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D]:
    """
    Extract a pure-Python visualization geometry snapshot from one DBM.

    This is the geometry-layer Phase 1 entry point. It intentionally performs
    no matplotlib import or artist creation.
    """

    if not isinstance(dbm, DBM):
        raise TypeError("extract_dbm_geometry expects a DBM instance.")

    user_dimension = dbm.dimension - 1
    if user_dimension == 1:
        lower, upper, lower_closed, upper_closed = _dbm_axis_bounds_1d(dbm)
        normalized_limits = _normalize_1d_limits(limits, [(lower, upper)])  # type: ignore[arg-type]
        limit_lower, limit_upper = normalized_limits

        lower_clipped = False
        upper_clipped = False
        if lower is None or lower < limit_lower:
            lower = limit_lower
            lower_closed = True
            lower_clipped = True
        if upper is None or upper > limit_upper:
            upper = limit_upper
            upper_closed = True
            upper_clipped = True

        if lower > upper + _GEOMETRY_EPSILON:
            return EmptyGeometry(dimension=1)
        if _almost_equal(lower, upper) and not (lower_closed and upper_closed):
            return EmptyGeometry(dimension=1)

        return Interval1D(
            lower=lower,
            upper=upper,
            lower_closed=lower_closed,
            upper_closed=upper_closed,
            lower_clipped=lower_clipped,
            upper_clipped=upper_clipped,
        )

    if user_dimension == 2:
        normalized_limits = _normalize_2d_limits(limits, [_dbm_axis_bounds_2d(dbm)])  # type: ignore[arg-type]
        return _extract_dbm_geometry_2d(dbm, normalized_limits)

    if user_dimension == 3:
        raise NotImplementedError("3D visualization geometry is reserved for the later rendering phase.")
    raise ValueError("Visualization geometry currently supports only 1D, 2D, and reserved 3D contexts.")


def extract_federation_geometry(
    federation: Federation,
    limits: Optional[Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]] = None,
) -> Union[EmptyGeometry, MultiInterval1D, FederationGeometry2D]:
    """
    Extract a pure-Python visualization geometry snapshot from one federation.

    For 1D federations this returns the exact interval union. For 2D
    federations this returns the exact clipped polygon-union boundary for the
    polygonal DBM components.
    """

    if not isinstance(federation, Federation):
        raise TypeError("extract_federation_geometry expects a Federation instance.")

    user_dimension = len(federation.context.clocks)
    dbms = federation.to_dbm_list()
    if not dbms:
        return EmptyGeometry(dimension=user_dimension)

    if user_dimension == 1:
        bounds = [_dbm_axis_bounds_1d(dbm)[:2] for dbm in dbms]
        normalized_limits = _normalize_1d_limits(limits, bounds)  # type: ignore[arg-type]
        intervals = []  # type: List[Interval1D]
        for dbm in dbms:
            geometry = extract_dbm_geometry(dbm, normalized_limits)
            if isinstance(geometry, Interval1D):
                intervals.append(geometry)
        return _merge_intervals(intervals)

    if user_dimension == 2:
        normalized_limits = _normalize_2d_limits(limits, [_dbm_axis_bounds_2d(dbm) for dbm in dbms])  # type: ignore[arg-type]
        dbm_geometries = []  # type: List[Union[PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D]]
        polygons = []  # type: List[PolygonGeometry2D]
        for dbm in dbms:
            geometry = _extract_dbm_geometry_2d(dbm, normalized_limits)
            if isinstance(geometry, PolygonGeometry2D):
                polygons.append(geometry)
                dbm_geometries.append(geometry)
            elif isinstance(geometry, (SegmentGeometry2D, PointGeometry2D)):
                dbm_geometries.append(geometry)

        boundary_segments = _exact_federation_boundary_2d(polygons)
        loops = _trace_boundary_loops(boundary_segments) if boundary_segments else tuple()
        loops = _merge_boundary_loops(loops)
        boundary_segments = tuple(segment for loop in loops for segment in loop.segments)
        faces = _build_faces_from_loops(loops)
        isolated_segments = _extract_degenerate_union_segments(dbm_geometries, polygons)
        isolated_points = _extract_degenerate_union_points(dbm_geometries, polygons, isolated_segments)
        return FederationGeometry2D(
            dbm_geometries=tuple(dbm_geometries),
            boundary_segments=boundary_segments,
            loops=loops,
            faces=faces,
            isolated_segments=isolated_segments,
            isolated_points=isolated_points,
            limits=normalized_limits,
        )

    if user_dimension == 3:
        raise NotImplementedError("3D visualization geometry is reserved for the later rendering phase.")
    raise ValueError("Visualization geometry currently supports only 1D, 2D, and reserved 3D contexts.")
