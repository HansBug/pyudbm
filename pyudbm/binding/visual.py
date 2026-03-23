"""
Geometry foundation for visualization-oriented DBM / federation handling.

This module keeps matplotlib optional while exposing both the pure geometry
layer and the first plotting-layer helpers built on top of it.

The current implementation covers the Phase 0 / Phase 1 / Phase 2 foundation:

* 1D DBM interval extraction;
* 1D federation exact interval union;
* 2D DBM convex geometry extraction from DBM half-spaces;
* 2D federation exact boundary extraction for polygonal DBM unions.
* 1D / 2D matplotlib rendering helpers for DBMs and federations.
"""

from __future__ import annotations

import importlib
import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

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
    "PlotResult",
    "SegmentGeometry2D",
    "extract_dbm_geometry",
    "extract_federation_geometry",
    "plot_dbm",
    "plot_federation",
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


@dataclass(frozen=True)
class PlotResult:
    """Matplotlib artist container returned by plotting helpers."""

    ax: Any
    fills: Tuple[Any, ...] = tuple()
    boundaries: Tuple[Any, ...] = tuple()
    markers: Tuple[Any, ...] = tuple()
    arrows: Tuple[Any, ...] = tuple()
    annotations: Tuple[Any, ...] = tuple()


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


def _require_matplotlib() -> Tuple[Any, Any, Any]:
    try:
        pyplot = importlib.import_module("matplotlib.pyplot")
        patches = importlib.import_module("matplotlib.patches")
        path = importlib.import_module("matplotlib.path")
    except ImportError as err:
        raise ImportError("matplotlib is required for visualization support. Install pyudbm[plot].") from err
    return pyplot, patches, path


def _auto_plot_axis_limits(bounds: Sequence[Tuple[Optional[float], Optional[float]]]) -> Tuple[float, float]:
    finite_lowers = [float(lower) for lower, _ in bounds if lower is not None]
    finite_uppers = [float(upper) for _, upper in bounds if upper is not None]

    if finite_lowers and finite_uppers:
        minimum = min(finite_lowers)
        maximum = max(finite_uppers)
        span = max(maximum - minimum, 1.0)
        pad = max(span * 0.15, 0.5)
        lower = min(minimum - pad, -pad)
        upper = maximum + pad
    elif finite_lowers:
        bound = min(finite_lowers)
        scale = max(abs(bound), 1.0)
        pad = max(scale * 0.15, 0.5)
        span = max(scale * 0.5, 3.0)
        lower = min(bound - pad, -pad)
        upper = bound + span
    elif finite_uppers:
        bound = max(finite_uppers)
        scale = max(abs(bound), 1.0)
        pad = max(scale * 0.15, 0.5)
        span = max(scale * 0.5, 3.0)
        lower = min(bound - span, -pad)
        upper = bound + pad
    else:
        return -5.0, 5.0

    if not lower < upper:
        center = (lower + upper) / 2.0
        lower = center - 1.0
        upper = center + 1.0
    return lower, upper


def _auto_plot_limits_for_dbm(
    dbm: DBM,
) -> Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]:
    user_dimension = dbm.dimension - 1
    if user_dimension == 1:
        lower, upper, _, _ = _dbm_axis_bounds_1d(dbm)
        return _auto_plot_axis_limits([(lower, upper)])
    if user_dimension == 2:
        x_lower, x_upper, y_lower, y_upper = _dbm_axis_bounds_2d(dbm)
        return _auto_plot_axis_limits([(x_lower, x_upper)]), _auto_plot_axis_limits([(y_lower, y_upper)])
    raise NotImplementedError("Automatic plot limits currently support only 1D and 2D DBMs.")


def _auto_plot_limits_for_federation(
    federation: Federation,
) -> Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]:
    user_dimension = len(federation.context.clocks)
    dbms = federation.to_dbm_list()
    if user_dimension == 1:
        bounds = [_dbm_axis_bounds_1d(dbm)[:2] for dbm in dbms]
        return _auto_plot_axis_limits(bounds)
    if user_dimension == 2:
        x_bounds = []  # type: List[Tuple[Optional[float], Optional[float]]]
        y_bounds = []  # type: List[Tuple[Optional[float], Optional[float]]]
        for dbm in dbms:
            x_lower, x_upper, y_lower, y_upper = _dbm_axis_bounds_2d(dbm)
            x_bounds.append((x_lower, x_upper))
            y_bounds.append((y_lower, y_upper))
        return _auto_plot_axis_limits(x_bounds), _auto_plot_axis_limits(y_bounds)
    raise NotImplementedError("Automatic plot limits currently support only 1D and 2D federations.")


def _set_axis_clock_labels(ax: Any, clock_names: Sequence[str], dimension: int) -> None:
    if dimension >= 1 and len(clock_names) >= 1:
        ax.set_xlabel(clock_names[0])
    if dimension >= 2 and len(clock_names) >= 2:
        ax.set_ylabel(clock_names[1])
    elif dimension == 1:
        ax.set_ylabel("visual baseline")


def _resolve_limits_from_geometry(
    geometry: Union[EmptyGeometry, Interval1D, MultiInterval1D, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D, FederationGeometry2D]
) -> Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]:
    if isinstance(geometry, EmptyGeometry):
        if geometry.dimension == 1:
            return -1.0, 1.0
        return (-1.0, 1.0), (-1.0, 1.0)

    if isinstance(geometry, Interval1D):
        return geometry.lower, geometry.upper
    if isinstance(geometry, MultiInterval1D):
        if geometry.intervals:
            return geometry.intervals[0].lower, geometry.intervals[-1].upper
        return -1.0, 1.0
    if isinstance(geometry, FederationGeometry2D):
        return geometry.limits

    x_values = []  # type: List[float]
    y_values = []  # type: List[float]
    if isinstance(geometry, PolygonGeometry2D):
        x_values.extend(point.x for point in geometry.vertices)
        y_values.extend(point.y for point in geometry.vertices)
    elif isinstance(geometry, SegmentGeometry2D):
        x_values.extend([geometry.segment.start.x, geometry.segment.end.x])
        y_values.extend([geometry.segment.start.y, geometry.segment.end.y])
    elif isinstance(geometry, PointGeometry2D):
        x_values.append(geometry.point.x)
        y_values.append(geometry.point.y)

    x_values = x_values or [-1.0, 1.0]
    y_values = y_values or [-1.0, 1.0]

    xmin = min(x_values)
    xmax = max(x_values)
    ymin = min(y_values)
    ymax = max(y_values)
    if _almost_equal(xmin, xmax):
        xmin -= 1.0
        xmax += 1.0
    if _almost_equal(ymin, ymax):
        ymin -= 1.0
        ymax += 1.0
    return (xmin, xmax), (ymin, ymax)


def _resolve_strict_epsilon(
    geometry: Union[EmptyGeometry, Interval1D, MultiInterval1D, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D, FederationGeometry2D],
    strict_epsilon: Optional[float],
) -> float:
    if strict_epsilon is not None:
        value = float(strict_epsilon)
        if value <= 0.0:
            raise ValueError("strict_epsilon must be positive when specified.")
        return value

    limits = _resolve_limits_from_geometry(geometry)
    if isinstance(limits[0], tuple):
        x_limits, y_limits = limits  # type: ignore[misc]
        scale = min(float(x_limits[1]) - float(x_limits[0]), float(y_limits[1]) - float(y_limits[0]))
    else:
        scale = float(limits[1]) - float(limits[0])  # type: ignore[index]
    return max(scale * 1e-4, 1e-7)


def _resolve_style(facecolor: Optional[Any], edgecolor: Optional[Any], alpha: Optional[float], linewidth: Optional[float], linestyle: Optional[Any]) -> Tuple[Any, Any, float, float, Any]:
    resolved_edgecolor = edgecolor if edgecolor is not None else "C0"
    resolved_facecolor = facecolor if facecolor is not None else resolved_edgecolor
    resolved_alpha = 0.25 if alpha is None else float(alpha)
    resolved_linewidth = 1.5 if linewidth is None else float(linewidth)
    resolved_linestyle = "-" if linestyle is None else linestyle
    return resolved_facecolor, resolved_edgecolor, resolved_alpha, resolved_linewidth, resolved_linestyle


def _make_axes(pyplot: Any, ax: Optional[Any], dimension: int) -> Any:
    if ax is not None:
        return ax
    _, new_ax = pyplot.subplots(subplot_kw=None if dimension != 2 else None)
    return new_ax


def _set_default_view(
    ax: Any,
    geometry: Union[EmptyGeometry, Interval1D, MultiInterval1D, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D, FederationGeometry2D],
    baseline: float,
    view_limits: Optional[Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]] = None,
) -> None:
    limits = view_limits if view_limits is not None else _resolve_limits_from_geometry(geometry)
    if isinstance(limits[0], tuple):
        x_limits, y_limits = limits  # type: ignore[misc]
        ax.set_xlim(*x_limits)
        ax.set_ylim(*y_limits)
        ax.set_aspect("equal", adjustable="box")
    else:
        x_limits = limits  # type: ignore[assignment]
        ax.set_xlim(*x_limits)
        ax.set_ylim(baseline - 1.0, baseline + 1.0)


def _line_label(label: Optional[str], index: int) -> Optional[str]:
    if label is None:
        return None
    return label if index == 0 else "_nolegend_"


def _endpoint_marker_style(is_closed: bool, edgecolor: Any) -> Dict[str, Any]:
    return {
        "marker": "o",
        "markersize": 6.0,
        "markeredgecolor": edgecolor,
        "markerfacecolor": edgecolor if is_closed else "none",
        "linestyle": "None",
    }


def _interval_line_range(interval: Interval1D, epsilon: float) -> Tuple[float, float]:
    start = interval.lower + (epsilon if not interval.lower_closed else 0.0)
    end = interval.upper - (epsilon if not interval.upper_closed else 0.0)
    return start, end


def _plot_interval(ax: Any, interval: Interval1D, baseline: float, epsilon: float, edgecolor: Any, linewidth: float, zorder: Optional[float], label: Optional[str]) -> PlotResult:
    boundaries = []  # type: List[Any]
    markers = []  # type: List[Any]
    start, end = _interval_line_range(interval, epsilon)
    if start <= end + _GEOMETRY_EPSILON:
        line = ax.plot(
            [max(interval.lower, start), min(interval.upper, end)],
            [baseline, baseline],
            color=edgecolor,
            linewidth=linewidth,
            linestyle="-",
            zorder=zorder,
            label=label,
        )[0]
        boundaries.append(line)

    lower_marker = ax.plot([interval.lower], [baseline], color=edgecolor, zorder=zorder, **_endpoint_marker_style(interval.lower_closed, edgecolor))[0]
    upper_marker = ax.plot([interval.upper], [baseline], color=edgecolor, zorder=zorder, **_endpoint_marker_style(interval.upper_closed, edgecolor))[0]
    markers.extend([lower_marker, upper_marker])
    return PlotResult(ax=ax, boundaries=tuple(boundaries), markers=tuple(markers))


def _arrow_for_interval(ax: Any, x_value: float, baseline: float, direction: float, edgecolor: Any, linewidth: float, zorder: Optional[float], patches: Any, extent: float) -> Any:
    delta = max(extent * 0.08, 0.1)
    return patches.FancyArrowPatch(
        (x_value, baseline),
        (x_value + (direction * delta), baseline),
        arrowstyle="->",
        mutation_scale=10.0,
        color=edgecolor,
        linewidth=linewidth,
        zorder=zorder,
    )


def _plot_1d_geometry(
    geometry: Union[EmptyGeometry, Interval1D, MultiInterval1D],
    ax: Any,
    baseline: float,
    strict_epsilon: float,
    show_unbounded: bool,
    annotate: bool,
    facecolor: Optional[Any],
    edgecolor: Optional[Any],
    alpha: Optional[float],
    linewidth: Optional[float],
    linestyle: Optional[Any],
    label: Optional[str],
    zorder: Optional[float],
) -> PlotResult:
    del facecolor, alpha, linestyle
    _, resolved_edgecolor, _, resolved_linewidth, _ = _resolve_style(None, edgecolor, None, linewidth, None)
    _, patches, _ = _require_matplotlib()

    boundaries = []  # type: List[Any]
    markers = []  # type: List[Any]
    arrows = []  # type: List[Any]
    annotations = []  # type: List[Any]
    intervals = geometry.intervals if isinstance(geometry, MultiInterval1D) else ((geometry,) if isinstance(geometry, Interval1D) else tuple())

    for index, interval in enumerate(intervals):
        result = _plot_interval(ax, interval, baseline, strict_epsilon, resolved_edgecolor, resolved_linewidth, zorder, _line_label(label, index))
        boundaries.extend(result.boundaries)
        markers.extend(result.markers)
        extent = max(interval.upper - interval.lower, 1.0)
        if show_unbounded and interval.lower_clipped:
            arrow = _arrow_for_interval(ax, interval.lower, baseline, -1.0, resolved_edgecolor, resolved_linewidth, zorder, patches, extent)
            ax.add_patch(arrow)
            arrows.append(arrow)
        if show_unbounded and interval.upper_clipped:
            arrow = _arrow_for_interval(ax, interval.upper, baseline, 1.0, resolved_edgecolor, resolved_linewidth, zorder, patches, extent)
            ax.add_patch(arrow)
            arrows.append(arrow)
        if annotate:
            annotation = ax.text((interval.lower + interval.upper) / 2.0, baseline + 0.08, "interval", color=resolved_edgecolor)
            annotations.append(annotation)

    return PlotResult(
        ax=ax,
        boundaries=tuple(boundaries),
        markers=tuple(markers),
        arrows=tuple(arrows),
        annotations=tuple(annotations),
    )


def _polygon_fill_vertices(geometry: PolygonGeometry2D, epsilon: float) -> Tuple[Point2D, ...]:
    adjusted = tuple(
        HalfSpace2D(
            a=halfspace.a,
            b=halfspace.b,
            c=halfspace.c - (epsilon if halfspace.is_strict else 0.0),
            is_strict=False,
            is_clip=halfspace.is_clip,
        )
        for halfspace in geometry.halfspaces
    )
    candidate_points = [point for point in _pairwise_line_intersections(adjusted) if _point_in_halfspaces(point, adjusted, respect_strict=False)]
    unique_points = _unique_points(candidate_points)
    if len(unique_points) < 3:
        return tuple()
    return _convex_hull(unique_points)


def _edge_linestyle(segment: BoundarySegment2D, default_linestyle: Any) -> Any:
    if not segment.is_closed:
        return "--"
    return default_linestyle


def _plot_boundary_segment(ax: Any, segment: BoundarySegment2D, edgecolor: Any, linewidth: float, linestyle: Any, zorder: Optional[float], label: Optional[str]) -> Any:
    return ax.plot(
        [segment.start.x, segment.end.x],
        [segment.start.y, segment.end.y],
        color=edgecolor,
        linewidth=linewidth,
        linestyle=_edge_linestyle(segment, linestyle),
        zorder=zorder,
        label=label,
    )[0]


def _arrow_for_segment(ax: Any, segment: BoundarySegment2D, edgecolor: Any, linewidth: float, zorder: Optional[float], patches: Any, outward_sign: float) -> Any:
    direction_x = segment.end.x - segment.start.x
    direction_y = segment.end.y - segment.start.y
    length = math.hypot(direction_x, direction_y)
    normal_x = outward_sign * (direction_y / length)
    normal_y = outward_sign * (-direction_x / length)
    arrow_length = max(min(length, 1.0) * 0.12, 0.08)
    midpoint = segment.midpoint
    return patches.FancyArrowPatch(
        (midpoint.x, midpoint.y),
        (midpoint.x + (normal_x * arrow_length), midpoint.y + (normal_y * arrow_length)),
        arrowstyle="->",
        mutation_scale=10.0,
        color=edgecolor,
        linewidth=linewidth,
        zorder=zorder,
    )


def _arrows_for_segment(ax: Any, segment: BoundarySegment2D, edgecolor: Any, linewidth: float, zorder: Optional[float], patches: Any, outward_sign: float) -> Tuple[Any, ...]:
    length = segment.length
    if length >= 3.0:
        parameters = [0.3, 0.7]
    else:
        parameters = [0.5]

    direction_x = segment.end.x - segment.start.x
    direction_y = segment.end.y - segment.start.y
    magnitude = math.hypot(direction_x, direction_y)
    normal_x = outward_sign * (direction_y / magnitude)
    normal_y = outward_sign * (-direction_x / magnitude)
    arrow_length = max(min(length, 1.0) * 0.12, 0.08)

    result = []
    for parameter in parameters:
        anchor = Point2D(
            segment.start.x + (direction_x * parameter),
            segment.start.y + (direction_y * parameter),
        )
        arrow = patches.FancyArrowPatch(
            (anchor.x, anchor.y),
            (anchor.x + (normal_x * arrow_length), anchor.y + (normal_y * arrow_length)),
            arrowstyle="->",
            mutation_scale=10.0,
            color=edgecolor,
            linewidth=linewidth,
            zorder=zorder,
        )
        result.append(arrow)
    return tuple(result)


def _plot_dbm_2d_geometry(
    geometry: Union[EmptyGeometry, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D],
    ax: Any,
    strict_epsilon: float,
    show_unbounded: bool,
    annotate: bool,
    facecolor: Optional[Any],
    edgecolor: Optional[Any],
    alpha: Optional[float],
    linewidth: Optional[float],
    linestyle: Optional[Any],
    label: Optional[str],
    zorder: Optional[float],
) -> PlotResult:
    pyplot, patches, _ = _require_matplotlib()
    del pyplot
    resolved_facecolor, resolved_edgecolor, resolved_alpha, resolved_linewidth, resolved_linestyle = _resolve_style(
        facecolor, edgecolor, alpha, linewidth, linestyle
    )

    fills = []  # type: List[Any]
    boundaries = []  # type: List[Any]
    markers = []  # type: List[Any]
    arrows = []  # type: List[Any]
    annotations = []  # type: List[Any]

    if isinstance(geometry, PolygonGeometry2D):
        fill_vertices = _polygon_fill_vertices(geometry, strict_epsilon)
        if len(fill_vertices) >= 3:
            patch = patches.Polygon(
                [(point.x, point.y) for point in fill_vertices],
                closed=True,
                facecolor=resolved_facecolor,
                edgecolor="none",
                alpha=resolved_alpha,
                zorder=zorder,
                label=label,
            )
            ax.add_patch(patch)
            fills.append(patch)

        for index, segment in enumerate(geometry.edges):
            line = _plot_boundary_segment(ax, segment, resolved_edgecolor, resolved_linewidth, resolved_linestyle, zorder, _line_label(label, index if not fills else index + 1))
            boundaries.append(line)
            if show_unbounded and segment.is_clipped:
                for arrow in _arrows_for_segment(ax, segment, resolved_edgecolor, resolved_linewidth, zorder, patches, -1.0):
                    ax.add_patch(arrow)
                    arrows.append(arrow)
        if annotate:
            center_x = sum(point.x for point in geometry.vertices) / float(len(geometry.vertices))
            center_y = sum(point.y for point in geometry.vertices) / float(len(geometry.vertices))
            annotations.append(ax.text(center_x, center_y, "dbm", color=resolved_edgecolor))

    elif isinstance(geometry, SegmentGeometry2D):
        line = _plot_boundary_segment(ax, geometry.segment, resolved_edgecolor, resolved_linewidth, resolved_linestyle, zorder, label)
        boundaries.append(line)
        markers.append(ax.plot([geometry.segment.start.x], [geometry.segment.start.y], color=resolved_edgecolor, zorder=zorder, **_endpoint_marker_style(geometry.segment.is_closed, resolved_edgecolor))[0])
        markers.append(ax.plot([geometry.segment.end.x], [geometry.segment.end.y], color=resolved_edgecolor, zorder=zorder, **_endpoint_marker_style(geometry.segment.is_closed, resolved_edgecolor))[0])
        if annotate:
            annotations.append(ax.text(geometry.segment.midpoint.x, geometry.segment.midpoint.y, "segment", color=resolved_edgecolor))

    elif isinstance(geometry, PointGeometry2D):
        marker = ax.plot([geometry.point.x], [geometry.point.y], color=resolved_edgecolor, zorder=zorder, label=label, **_endpoint_marker_style(geometry.is_closed, resolved_edgecolor))[0]
        markers.append(marker)
        if annotate:
            annotations.append(ax.text(geometry.point.x, geometry.point.y, "point", color=resolved_edgecolor))

    return PlotResult(
        ax=ax,
        fills=tuple(fills),
        boundaries=tuple(boundaries),
        markers=tuple(markers),
        arrows=tuple(arrows),
        annotations=tuple(annotations),
    )


def _face_path(face: Face2D, path_module: Any) -> Any:
    vertices = []  # type: List[Tuple[float, float]]
    codes = []  # type: List[int]

    def _append_loop(loop: BoundaryLoop2D) -> None:
        loop_vertices = list(loop.vertices)
        vertices.append((loop_vertices[0].x, loop_vertices[0].y))
        codes.append(path_module.Path.MOVETO)
        for point in loop_vertices[1:]:
            vertices.append((point.x, point.y))
            codes.append(path_module.Path.LINETO)
        vertices.append((loop_vertices[0].x, loop_vertices[0].y))
        codes.append(path_module.Path.CLOSEPOLY)

    _append_loop(face.outer)
    for hole in face.holes:
        _append_loop(hole)
    return path_module.Path(vertices, codes)


def _plot_federation_2d_geometry(
    geometry: Union[EmptyGeometry, FederationGeometry2D],
    ax: Any,
    strict_epsilon: float,
    show_unbounded: bool,
    annotate: bool,
    color_mode: str,
    facecolor: Optional[Any],
    edgecolor: Optional[Any],
    alpha: Optional[float],
    linewidth: Optional[float],
    linestyle: Optional[Any],
    label: Optional[str],
    zorder: Optional[float],
) -> PlotResult:
    if color_mode not in {"shared", "per_dbm"}:
        raise ValueError("color_mode must be 'shared' or 'per_dbm'.")

    _, patches, path_module = _require_matplotlib()
    resolved_facecolor, resolved_edgecolor, resolved_alpha, resolved_linewidth, resolved_linestyle = _resolve_style(
        facecolor, edgecolor, alpha, linewidth, linestyle
    )

    fills = []  # type: List[Any]
    boundaries = []  # type: List[Any]
    markers = []  # type: List[Any]
    arrows = []  # type: List[Any]
    annotations = []  # type: List[Any]

    if isinstance(geometry, FederationGeometry2D):
        if color_mode == "per_dbm":
            color_cycle = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
            for index, dbm_geometry in enumerate(geometry.dbm_geometries):
                dbm_result = _plot_dbm_2d_geometry(
                    dbm_geometry,
                    ax=ax,
                    strict_epsilon=strict_epsilon,
                    show_unbounded=False,
                    annotate=False,
                    facecolor=color_cycle[index % len(color_cycle)],
                    edgecolor=color_cycle[index % len(color_cycle)],
                    alpha=min(resolved_alpha, 0.2),
                    linewidth=max(resolved_linewidth * 0.75, 0.8),
                    linestyle=resolved_linestyle,
                    label=_line_label(label, index),
                    zorder=zorder,
                )
                fills.extend(dbm_result.fills)
                markers.extend(dbm_result.markers)

        elif geometry.faces:
            for index, face in enumerate(geometry.faces):
                patch = patches.PathPatch(
                    _face_path(face, path_module),
                    facecolor=resolved_facecolor,
                    edgecolor="none",
                    alpha=resolved_alpha,
                    zorder=zorder,
                    label=_line_label(label, index),
                )
                ax.add_patch(patch)
                fills.append(patch)

        loop_lookup = {}  # type: Dict[Tuple[Tuple[int, int], Tuple[int, int]], float]
        for loop in geometry.loops:
            outward_sign = 1.0 if loop.is_hole else -1.0
            for segment in loop.segments:
                key = (_point_key(segment.start), _point_key(segment.end))
                loop_lookup[key] = outward_sign

        for index, segment in enumerate(geometry.boundary_segments):
            line = _plot_boundary_segment(ax, segment, resolved_edgecolor, resolved_linewidth, resolved_linestyle, zorder, _line_label(label, index if not fills else index + 1))
            boundaries.append(line)
            if show_unbounded and segment.is_clipped:
                sign = loop_lookup.get((_point_key(segment.start), _point_key(segment.end)), -1.0)
                for arrow in _arrows_for_segment(ax, segment, resolved_edgecolor, resolved_linewidth, zorder, patches, sign):
                    ax.add_patch(arrow)
                    arrows.append(arrow)

        for segment in geometry.isolated_segments:
            line = _plot_boundary_segment(ax, segment, resolved_edgecolor, resolved_linewidth, resolved_linestyle, zorder, None)
            boundaries.append(line)

        for point in geometry.isolated_points:
            markers.append(ax.plot([point.x], [point.y], color=resolved_edgecolor, zorder=zorder, **_endpoint_marker_style(True, resolved_edgecolor))[0])

        if annotate:
            for index, face in enumerate(geometry.faces):
                vertices = face.outer.vertices
                center_x = sum(point.x for point in vertices) / float(len(vertices))
                center_y = sum(point.y for point in vertices) / float(len(vertices))
                annotations.append(ax.text(center_x, center_y, "face{0}".format(index), color=resolved_edgecolor))

    return PlotResult(
        ax=ax,
        fills=tuple(fills),
        boundaries=tuple(boundaries),
        markers=tuple(markers),
        arrows=tuple(arrows),
        annotations=tuple(annotations),
    )


def plot_dbm(
    dbm: DBM,
    ax: Optional[Any] = None,
    *,
    limits: Optional[Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]] = None,
    strict_epsilon: Optional[float] = None,
    show_unbounded: bool = True,
    annotate: bool = False,
    baseline: float = 0.0,
    facecolor: Optional[Any] = None,
    edgecolor: Optional[Any] = None,
    alpha: Optional[float] = None,
    linewidth: Optional[float] = None,
    linestyle: Optional[Any] = None,
    label: Optional[str] = None,
    zorder: Optional[float] = None,
) -> PlotResult:
    """
    Plot one DBM with matplotlib.

    Matplotlib remains an optional dependency. Importing this module does not
    require it, but calling :func:`plot_dbm` does.
    """

    user_dimension = dbm.dimension - 1
    if user_dimension not in {1, 2}:
        raise NotImplementedError("Matplotlib plotting currently supports only 1D and 2D DBMs.")

    plot_limits = limits if limits is not None else _auto_plot_limits_for_dbm(dbm)
    pyplot, _, _ = _require_matplotlib()
    geometry = extract_dbm_geometry(dbm, limits=plot_limits)
    ax = _make_axes(pyplot, ax, user_dimension)
    epsilon = _resolve_strict_epsilon(geometry, strict_epsilon)
    _set_default_view(ax, geometry, baseline, view_limits=plot_limits)
    _set_axis_clock_labels(ax, [clock.get_full_name() for clock in dbm.context.clocks], user_dimension)
    if user_dimension == 1:
        return _plot_1d_geometry(
            geometry,  # type: ignore[arg-type]
            ax=ax,
            baseline=float(baseline),
            strict_epsilon=epsilon,
            show_unbounded=show_unbounded,
            annotate=annotate,
            facecolor=facecolor,
            edgecolor=edgecolor,
            alpha=alpha,
            linewidth=linewidth,
            linestyle=linestyle,
            label=label,
            zorder=zorder,
        )
    return _plot_dbm_2d_geometry(
        geometry,  # type: ignore[arg-type]
        ax=ax,
        strict_epsilon=epsilon,
        show_unbounded=show_unbounded,
        annotate=annotate,
        facecolor=facecolor,
        edgecolor=edgecolor,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        label=label,
        zorder=zorder,
    )


def plot_federation(
    federation: Federation,
    ax: Optional[Any] = None,
    *,
    limits: Optional[Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]] = None,
    strict_epsilon: Optional[float] = None,
    show_unbounded: bool = True,
    annotate: bool = False,
    baseline: float = 0.0,
    color_mode: str = "shared",
    facecolor: Optional[Any] = None,
    edgecolor: Optional[Any] = None,
    alpha: Optional[float] = None,
    linewidth: Optional[float] = None,
    linestyle: Optional[Any] = None,
    label: Optional[str] = None,
    zorder: Optional[float] = None,
) -> PlotResult:
    """
    Plot one federation with matplotlib.

    For 1D federations this renders the exact interval union. For 2D
    federations this renders the exact clipped boundary extracted in the
    geometry layer.
    """

    user_dimension = len(federation.context.clocks)
    if user_dimension not in {1, 2}:
        raise NotImplementedError("Matplotlib plotting currently supports only 1D and 2D federations.")

    plot_limits = limits if limits is not None else _auto_plot_limits_for_federation(federation)
    pyplot, _, _ = _require_matplotlib()
    geometry = extract_federation_geometry(federation, limits=plot_limits)
    ax = _make_axes(pyplot, ax, user_dimension)
    epsilon = _resolve_strict_epsilon(geometry, strict_epsilon)
    _set_default_view(ax, geometry, baseline, view_limits=plot_limits)
    _set_axis_clock_labels(ax, [clock.get_full_name() for clock in federation.context.clocks], user_dimension)
    if user_dimension == 1:
        return _plot_1d_geometry(
            geometry,  # type: ignore[arg-type]
            ax=ax,
            baseline=float(baseline),
            strict_epsilon=epsilon,
            show_unbounded=show_unbounded,
            annotate=annotate,
            facecolor=facecolor,
            edgecolor=edgecolor,
            alpha=alpha,
            linewidth=linewidth,
            linestyle=linestyle,
            label=label,
            zorder=zorder,
        )
    return _plot_federation_2d_geometry(
        geometry,  # type: ignore[arg-type]
        ax=ax,
        strict_epsilon=epsilon,
        show_unbounded=show_unbounded,
        annotate=annotate,
        color_mode=color_mode,
        facecolor=facecolor,
        edgecolor=edgecolor,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        label=label,
        zorder=zorder,
    )
