"""
Geometry foundation for visualization-oriented DBM / federation handling.

This module keeps matplotlib optional while exposing both the pure geometry
layer and the first plotting-layer helpers built on top of it.
"""

from __future__ import annotations

import importlib
import math
import warnings
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from .udbm import DBM, Federation

__all__ = [
    "BoundaryEdge3D",
    "BoundaryLoop2D",
    "BoundarySegment2D",
    "EmptyGeometry",
    "Face3D",
    "Face2D",
    "FaceGeometry3D",
    "FederationGeometry3D",
    "FederationGeometry2D",
    "HalfSpace3D",
    "HalfSpace2D",
    "Interval1D",
    "MultiInterval1D",
    "Point3D",
    "PointGeometry3D",
    "Point2D",
    "PointGeometry2D",
    "PolyhedronGeometry3D",
    "PolygonGeometry2D",
    "PlotResult",
    "SegmentGeometry3D",
    "SegmentGeometry2D",
    "extract_dbm_geometry",
    "extract_federation_geometry",
    "plot_dbm",
    "plot_federation",
]

_GEOMETRY_EPSILON = 1e-9


@dataclass(frozen=True)
class EmptyGeometry:
    """
    Empty visualization geometry placeholder.

    This is returned when clipping removes the whole region or when the source
    DBM / federation is empty in the requested render box.

    :ivar dimension: User-visible geometry dimension.
    :vartype dimension: int
    """

    dimension: int


@dataclass(frozen=True)
class Interval1D:
    """
    One clipped 1D interval with exact open/closed endpoint semantics.

    The interval is always finite after clipping. Whether an endpoint comes
    from the original DBM or from the render-box clipping step is tracked
    separately.

    :ivar lower: Lower endpoint after clipping.
    :vartype lower: float
    :ivar upper: Upper endpoint after clipping.
    :vartype upper: float
    :ivar lower_closed: Whether the lower endpoint is included.
    :vartype lower_closed: bool
    :ivar upper_closed: Whether the upper endpoint is included.
    :vartype upper_closed: bool
    :ivar lower_clipped: Whether the lower endpoint was introduced by clipping.
    :vartype lower_clipped: bool
    :ivar upper_clipped: Whether the upper endpoint was introduced by clipping.
    :vartype upper_clipped: bool
    """

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
    """
    Exact finite union of 1D intervals.

    This is the 1D geometry form returned for federations.

    :ivar intervals: Normalized exact interval union in ascending order.
    :vartype intervals: Tuple[Interval1D, ...]
    """

    intervals: Tuple[Interval1D, ...]


@dataclass(frozen=True)
class Point2D:
    """
    One 2D point.

    :ivar x: X coordinate.
    :vartype x: float
    :ivar y: Y coordinate.
    :vartype y: float
    """

    x: float
    y: float


@dataclass(frozen=True)
class HalfSpace2D:
    """
    One affine 2D half-space ``a*x + b*y <= c`` or ``a*x + b*y < c``.

    DBM constraints and clipping box edges are both converted to this common
    representation before polygon extraction.

    :ivar a: Coefficient of ``x``.
    :vartype a: float
    :ivar b: Coefficient of ``y``.
    :vartype b: float
    :ivar c: Right-hand-side constant.
    :vartype c: float
    :ivar is_strict: Whether the inequality is strict.
    :vartype is_strict: bool
    :ivar is_clip: Whether this half-space comes from the render-box clipping boundary.
    :vartype is_clip: bool
    """

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
    """
    One directed 2D boundary segment.

    Direction matters for loop tracing and for deciding outward arrow
    directions on unbounded clipped edges.

    :ivar start: Segment start point.
    :vartype start: Point2D
    :ivar end: Segment end point.
    :vartype end: Point2D
    :ivar is_closed: Whether this boundary segment is included in the represented set.
    :vartype is_closed: bool
    :ivar is_clipped: Whether this segment lies on the clipping box.
    :vartype is_clipped: bool
    """

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
    """
    Convex 2D polygon extracted from one DBM inside the clip box.

    :ivar vertices: Polygon vertices in boundary order.
    :vartype vertices: Tuple[Point2D, ...]
    :ivar edges: Directed boundary edges in boundary order.
    :vartype edges: Tuple[BoundarySegment2D, ...]
    :ivar halfspaces: Active DBM and clip half-spaces used to define the polygon.
    :vartype halfspaces: Tuple[HalfSpace2D, ...]
    """

    vertices: Tuple[Point2D, ...]
    edges: Tuple[BoundarySegment2D, ...]
    halfspaces: Tuple[HalfSpace2D, ...]


@dataclass(frozen=True)
class SegmentGeometry2D:
    """
    Degenerate 2D line-segment geometry extracted from one DBM.

    :ivar segment: Exact visible segment.
    :vartype segment: BoundarySegment2D
    :ivar halfspaces: Original half-space constraints used during extraction.
    :vartype halfspaces: Tuple[HalfSpace2D, ...]
    """

    segment: BoundarySegment2D
    halfspaces: Tuple[HalfSpace2D, ...]


@dataclass(frozen=True)
class PointGeometry2D:
    """
    Degenerate 2D point geometry extracted from one DBM.

    :ivar point: Exact visible point.
    :vartype point: Point2D
    :ivar is_closed: Whether the point is included.
    :vartype is_closed: bool
    :ivar is_clipped: Whether the point lies on the clipping box.
    :vartype is_clipped: bool
    :ivar halfspaces: Original half-space constraints used during extraction.
    :vartype halfspaces: Tuple[HalfSpace2D, ...]
    """

    point: Point2D
    is_closed: bool
    is_clipped: bool
    halfspaces: Tuple[HalfSpace2D, ...]


@dataclass(frozen=True)
class BoundaryLoop2D:
    """
    Closed 2D boundary loop of one federation component or hole.

    :ivar segments: Directed boundary segments that form the loop.
    :vartype segments: Tuple[BoundarySegment2D, ...]
    :ivar is_hole: Whether this loop bounds a hole instead of an outer face.
    :vartype is_hole: bool
    """

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
    """
    One exact 2D face consisting of an outer loop and optional holes.

    :ivar outer: Outer boundary loop.
    :vartype outer: BoundaryLoop2D
    :ivar holes: Hole loops contained inside the outer boundary.
    :vartype holes: Tuple[BoundaryLoop2D, ...]
    """

    outer: BoundaryLoop2D
    holes: Tuple[BoundaryLoop2D, ...]


@dataclass(frozen=True)
class FederationGeometry2D:
    """
    Exact 2D geometry summary for one federation inside one render box.

    It contains both the original per-DBM geometries and the exact union-level
    boundary decomposition.

    :ivar dbm_geometries: Exact clipped geometries of the individual DBMs.
    :vartype dbm_geometries: Tuple[Union[PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D], ...]
    :ivar boundary_segments: Exact union boundary segments after simplification and loop tracing.
    :vartype boundary_segments: Tuple[BoundarySegment2D, ...]
    :ivar loops: Closed outer and hole loops reconstructed from the boundary graph.
    :vartype loops: Tuple[BoundaryLoop2D, ...]
    :ivar faces: Final union faces with hole assignment.
    :vartype faces: Tuple[Face2D, ...]
    :ivar isolated_segments: Degenerate union segments not absorbed into 2D faces.
    :vartype isolated_segments: Tuple[BoundarySegment2D, ...]
    :ivar isolated_points: Degenerate union points not absorbed into segments or faces.
    :vartype isolated_points: Tuple[Point2D, ...]
    :ivar limits: Effective 2D clip box used during extraction.
    :vartype limits: Tuple[Tuple[float, float], Tuple[float, float]]
    """

    dbm_geometries: Tuple[Union[PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D], ...]
    boundary_segments: Tuple[BoundarySegment2D, ...]
    loops: Tuple[BoundaryLoop2D, ...]
    faces: Tuple[Face2D, ...]
    isolated_segments: Tuple[BoundarySegment2D, ...]
    isolated_points: Tuple[Point2D, ...]
    limits: Tuple[Tuple[float, float], Tuple[float, float]]


@dataclass(frozen=True)
class Point3D:
    """
    One 3D point.

    :ivar x: X coordinate.
    :vartype x: float
    :ivar y: Y coordinate.
    :vartype y: float
    :ivar z: Z coordinate.
    :vartype z: float
    """

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class HalfSpace3D:
    """
    One affine 3D half-space ``a*x + b*y + c*z <= d`` or ``< d``.

    :ivar a: Coefficient of ``x``.
    :vartype a: float
    :ivar b: Coefficient of ``y``.
    :vartype b: float
    :ivar c: Coefficient of ``z``.
    :vartype c: float
    :ivar d: Right-hand-side constant.
    :vartype d: float
    :ivar is_strict: Whether the inequality is strict.
    :vartype is_strict: bool
    :ivar is_clip: Whether this half-space comes from the render-box clipping boundary.
    :vartype is_clip: bool
    """

    a: float
    b: float
    c: float
    d: float
    is_strict: bool = False
    is_clip: bool = False

    def evaluate(self, point: Point3D) -> float:
        """Return ``a*x + b*y + c*z - d`` at ``point``."""

        return (self.a * point.x) + (self.b * point.y) + (self.c * point.z) - self.d

    def contains(self, point: Point3D, respect_strict: bool = True) -> bool:
        """Return whether ``point`` satisfies this half-space."""

        value = self.evaluate(point)
        if respect_strict and self.is_strict:
            return value < -_GEOMETRY_EPSILON
        return value <= _GEOMETRY_EPSILON

    def contains_on_closure(self, point: Point3D) -> bool:
        """Return whether ``point`` lies in the closure of this half-space."""

        return self.evaluate(point) <= _GEOMETRY_EPSILON

    def is_active(self, point: Point3D) -> bool:
        """Return whether ``point`` lies on the boundary plane of this half-space."""

        return abs(self.evaluate(point)) <= _GEOMETRY_EPSILON


@dataclass(frozen=True)
class BoundaryEdge3D:
    """
    One directed 3D boundary edge.

    :ivar start: Edge start point.
    :vartype start: Point3D
    :ivar end: Edge end point.
    :vartype end: Point3D
    :ivar is_closed: Whether this edge is included in the represented set.
    :vartype is_closed: bool
    :ivar is_clipped: Whether this edge lies on the clipping box.
    :vartype is_clipped: bool
    """

    start: Point3D
    end: Point3D
    is_closed: bool
    is_clipped: bool

    @property
    def length(self) -> float:
        """Return Euclidean edge length."""

        return math.sqrt(
            ((self.end.x - self.start.x) ** 2)
            + ((self.end.y - self.start.y) ** 2)
            + ((self.end.z - self.start.z) ** 2)
        )

    @property
    def midpoint(self) -> Point3D:
        """Return edge midpoint."""

        return Point3D(
            (self.start.x + self.end.x) / 2.0,
            (self.start.y + self.end.y) / 2.0,
            (self.start.z + self.end.z) / 2.0,
        )


@dataclass(frozen=True)
class Face3D:
    """
    One polygonal 3D face.

    :ivar vertices: Ordered face vertices.
    :vartype vertices: Tuple[Point3D, ...]
    :ivar edges: Directed face edges in boundary order.
    :vartype edges: Tuple[BoundaryEdge3D, ...]
    :ivar normal: Outward face normal.
    :vartype normal: Point3D
    :ivar is_closed: Whether the face boundary plane is included.
    :vartype is_closed: bool
    :ivar is_clipped: Whether the face comes only from the clipping box.
    :vartype is_clipped: bool
    """

    vertices: Tuple[Point3D, ...]
    edges: Tuple[BoundaryEdge3D, ...]
    normal: Point3D
    is_closed: bool
    is_clipped: bool


@dataclass(frozen=True)
class FaceGeometry3D:
    """
    Degenerate 3D polygonal face geometry extracted from one DBM.

    :ivar face: Exact visible face.
    :vartype face: Face3D
    :ivar halfspaces: Original half-space constraints used during extraction.
    :vartype halfspaces: Tuple[HalfSpace3D, ...]
    """

    face: Face3D
    halfspaces: Tuple[HalfSpace3D, ...]


@dataclass(frozen=True)
class SegmentGeometry3D:
    """
    Degenerate 3D line-segment geometry extracted from one DBM.

    :ivar segment: Exact visible segment.
    :vartype segment: BoundaryEdge3D
    :ivar halfspaces: Original half-space constraints used during extraction.
    :vartype halfspaces: Tuple[HalfSpace3D, ...]
    """

    segment: BoundaryEdge3D
    halfspaces: Tuple[HalfSpace3D, ...]


@dataclass(frozen=True)
class PointGeometry3D:
    """
    Degenerate 3D point geometry extracted from one DBM.

    :ivar point: Exact visible point.
    :vartype point: Point3D
    :ivar is_closed: Whether the point is included.
    :vartype is_closed: bool
    :ivar is_clipped: Whether the point lies on the clipping box.
    :vartype is_clipped: bool
    :ivar halfspaces: Original half-space constraints used during extraction.
    :vartype halfspaces: Tuple[HalfSpace3D, ...]
    """

    point: Point3D
    is_closed: bool
    is_clipped: bool
    halfspaces: Tuple[HalfSpace3D, ...]


@dataclass(frozen=True)
class PolyhedronGeometry3D:
    """
    Convex 3D polyhedron extracted from one DBM inside the clip box.

    :ivar vertices: Unique polyhedron vertices.
    :vartype vertices: Tuple[Point3D, ...]
    :ivar edges: Unique visible boundary edges.
    :vartype edges: Tuple[BoundaryEdge3D, ...]
    :ivar faces: Polygonal boundary faces.
    :vartype faces: Tuple[Face3D, ...]
    :ivar halfspaces: Active DBM and clip half-spaces used to define the polyhedron.
    :vartype halfspaces: Tuple[HalfSpace3D, ...]
    """

    vertices: Tuple[Point3D, ...]
    edges: Tuple[BoundaryEdge3D, ...]
    faces: Tuple[Face3D, ...]
    halfspaces: Tuple[HalfSpace3D, ...]


@dataclass(frozen=True)
class FederationGeometry3D:
    """
    Exact clipped 3D geometry summary for one federation.

    The current 3D federation form keeps the exact clipped geometry of each
    constituent DBM instead of attempting a full 3D boolean-union boundary
    simplification.

    :ivar dbm_geometries: Exact clipped geometries of the individual DBMs.
    :vartype dbm_geometries: Tuple[Union[PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D], ...]
    :ivar limits: Effective 3D clip box used during extraction.
    :vartype limits: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]
    """

    dbm_geometries: Tuple[Union[PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D], ...]
    limits: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]


@dataclass(frozen=True)
class PlotResult:
    """
    Matplotlib artist container returned by :func:`plot_dbm` and :func:`plot_federation`.

    The returned artists are grouped by role so callers can inspect, restyle,
    or remove them after plotting.

    :ivar ax: Axes that received the plotted artists.
    :vartype ax: Any
    :ivar fills: Filled polygon/path artists.
    :vartype fills: Tuple[Any, ...]
    :ivar boundaries: Line artists for visible boundaries.
    :vartype boundaries: Tuple[Any, ...]
    :ivar markers: Point artists for endpoints or isolated points.
    :vartype markers: Tuple[Any, ...]
    :ivar arrows: Arrow artists indicating unbounded continuation.
    :vartype arrows: Tuple[Any, ...]
    :ivar annotations: Text artists created by annotation support.
    :vartype annotations: Tuple[Any, ...]
    """

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


def _point_key_3d(point: Point3D) -> Tuple[int, int, int]:
    return (
        int(round(point.x * 1000000000.0)),
        int(round(point.y * 1000000000.0)),
        int(round(point.z * 1000000000.0)),
    )


def _normalize_1d_limits(limits: Optional[Tuple[float, float]],
                         intervals: Sequence[Tuple[Optional[float], Optional[float]]]) -> Tuple[float, float]:
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


def _normalize_3d_limits(
        limits: Optional[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]],
        bounds: Sequence[
            Tuple[
                Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]
            ]
        ],
) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
    if limits is not None:
        if not isinstance(limits, tuple) or len(limits) != 3:
            raise ValueError("3D limits must be ((xmin, xmax), (ymin, ymax), (zmin, zmax)).")
        x_limits = limits[0]
        y_limits = limits[1]
        z_limits = limits[2]
        if not isinstance(x_limits, tuple) or len(x_limits) != 2:
            raise ValueError("3D x limits must be a tuple of the form (xmin, xmax).")
        if not isinstance(y_limits, tuple) or len(y_limits) != 2:
            raise ValueError("3D y limits must be a tuple of the form (ymin, ymax).")
        if not isinstance(z_limits, tuple) or len(z_limits) != 2:
            raise ValueError("3D z limits must be a tuple of the form (zmin, zmax).")

        xmin = float(x_limits[0])
        xmax = float(x_limits[1])
        ymin = float(y_limits[0])
        ymax = float(y_limits[1])
        zmin = float(z_limits[0])
        zmax = float(z_limits[1])
        if not xmin < xmax:
            raise ValueError("3D limits require xmin < xmax.")
        if not ymin < ymax:
            raise ValueError("3D limits require ymin < ymax.")
        if not zmin < zmax:
            raise ValueError("3D limits require zmin < zmax.")
        return (xmin, xmax), (ymin, ymax), (zmin, zmax)

    x_values = []  # type: List[float]
    y_values = []  # type: List[float]
    z_values = []  # type: List[float]
    for xmin, xmax, ymin, ymax, zmin, zmax in bounds:
        if xmin is not None:
            x_values.append(float(xmin))
        if xmax is not None:
            x_values.append(float(xmax))
        if ymin is not None:
            y_values.append(float(ymin))
        if ymax is not None:
            y_values.append(float(ymax))
        if zmin is not None:
            z_values.append(float(zmin))
        if zmax is not None:
            z_values.append(float(zmax))

    x_values = x_values or [-5.0, 5.0]
    y_values = y_values or [-5.0, 5.0]
    z_values = z_values or [-5.0, 5.0]

    x_lower = min(x_values)
    x_upper = max(x_values)
    y_lower = min(y_values)
    y_upper = max(y_values)
    z_lower = min(z_values)
    z_upper = max(z_values)

    if _almost_equal(x_lower, x_upper):
        x_lower -= 1.0
        x_upper += 1.0
    if _almost_equal(y_lower, y_upper):
        y_lower -= 1.0
        y_upper += 1.0
    if _almost_equal(z_lower, z_upper):
        z_lower -= 1.0
        z_upper += 1.0

    return (x_lower, x_upper), (y_lower, y_upper), (z_lower, z_upper)


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


def _dbm_axis_bounds_3d(
        dbm: DBM,
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
    x_lower = None if dbm.is_infinity(0, 1) else float(-dbm.bound(0, 1))
    x_upper = None if dbm.is_infinity(1, 0) else float(dbm.bound(1, 0))
    y_lower = None if dbm.is_infinity(0, 2) else float(-dbm.bound(0, 2))
    y_upper = None if dbm.is_infinity(2, 0) else float(dbm.bound(2, 0))
    z_lower = None if dbm.is_infinity(0, 3) else float(-dbm.bound(0, 3))
    z_upper = None if dbm.is_infinity(3, 0) else float(dbm.bound(3, 0))
    return x_lower, x_upper, y_lower, y_upper, z_lower, z_upper


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


def _build_halfspaces_for_dbm_2d(dbm: DBM, limits: Tuple[Tuple[float, float], Tuple[float, float]]) -> Tuple[
    HalfSpace2D, ...]:
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

            result.append(
                HalfSpace2D(coefficients[0], coefficients[1], float(dbm.bound(i, j)), dbm.is_strict(i, j), False))

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
        for right in halfspaces[index + 1:]:
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


def _extract_dbm_geometry_2d(dbm: DBM, limits: Tuple[Tuple[float, float], Tuple[float, float]]) -> Union[
    EmptyGeometry, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D]:
    halfspaces = _build_halfspaces_for_dbm_2d(dbm, limits)
    candidate_points = [point for point in _pairwise_line_intersections(halfspaces) if
                        _point_in_halfspaces(point, halfspaces, respect_strict=False)]
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


def _build_halfspaces_for_dbm_3d(
        dbm: DBM,
        limits: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
) -> Tuple[HalfSpace3D, ...]:
    result = []  # type: List[HalfSpace3D]
    for i in range(dbm.dimension):
        for j in range(dbm.dimension):
            if i == j or dbm.is_infinity(i, j):
                continue

            coefficients = [0.0, 0.0, 0.0]
            if i > 0:
                coefficients[i - 1] += 1.0
            if j > 0:
                coefficients[j - 1] -= 1.0

            result.append(
                HalfSpace3D(
                    coefficients[0],
                    coefficients[1],
                    coefficients[2],
                    float(dbm.bound(i, j)),
                    dbm.is_strict(i, j),
                    False,
                )
            )

    (xmin, xmax), (ymin, ymax), (zmin, zmax) = limits
    result.extend(
        [
            HalfSpace3D(1.0, 0.0, 0.0, xmax, False, True),
            HalfSpace3D(-1.0, 0.0, 0.0, -xmin, False, True),
            HalfSpace3D(0.0, 1.0, 0.0, ymax, False, True),
            HalfSpace3D(0.0, -1.0, 0.0, -ymin, False, True),
            HalfSpace3D(0.0, 0.0, 1.0, zmax, False, True),
            HalfSpace3D(0.0, 0.0, -1.0, -zmin, False, True),
        ]
    )
    return tuple(result)


def _point_in_halfspaces_3d(point: Point3D, halfspaces: Sequence[HalfSpace3D], respect_strict: bool = True) -> bool:
    return all(halfspace.contains(point, respect_strict=respect_strict) for halfspace in halfspaces)


def _unique_points_3d(points: Iterable[Point3D]) -> Tuple[Point3D, ...]:
    mapping = {}  # type: Dict[Tuple[int, int, int], Point3D]
    for point in points:
        mapping[_point_key_3d(point)] = point
    return tuple(mapping.values())


def _vector3(left: Point3D, right: Point3D) -> Point3D:
    return Point3D(right.x - left.x, right.y - left.y, right.z - left.z)


def _dot3(left: Point3D, right: Point3D) -> float:
    return (left.x * right.x) + (left.y * right.y) + (left.z * right.z)


def _cross3(left: Point3D, right: Point3D) -> Point3D:
    return Point3D(
        (left.y * right.z) - (left.z * right.y),
        (left.z * right.x) - (left.x * right.z),
        (left.x * right.y) - (left.y * right.x),
    )


def _norm3(vector: Point3D) -> float:
    return math.sqrt((vector.x ** 2) + (vector.y ** 2) + (vector.z ** 2))


def _normalize3(vector: Point3D) -> Point3D:
    length = _norm3(vector)
    if length <= _GEOMETRY_EPSILON:
        return Point3D(0.0, 0.0, 0.0)
    return Point3D(vector.x / length, vector.y / length, vector.z / length)


def _determinant3(rows: Sequence[Tuple[float, float, float]]) -> float:
    return (
        (rows[0][0] * ((rows[1][1] * rows[2][2]) - (rows[1][2] * rows[2][1])))
        - (rows[0][1] * ((rows[1][0] * rows[2][2]) - (rows[1][2] * rows[2][0])))
        + (rows[0][2] * ((rows[1][0] * rows[2][1]) - (rows[1][1] * rows[2][0])))
    )


def _triple_plane_intersections(halfspaces: Sequence[HalfSpace3D]) -> Tuple[Point3D, ...]:
    points = []  # type: List[Point3D]
    for first_index in range(len(halfspaces)):
        for second_index in range(first_index + 1, len(halfspaces)):
            for third_index in range(second_index + 1, len(halfspaces)):
                first = halfspaces[first_index]
                second = halfspaces[second_index]
                third = halfspaces[third_index]
                coefficients = [
                    (first.a, first.b, first.c),
                    (second.a, second.b, second.c),
                    (third.a, third.b, third.c),
                ]
                determinant = _determinant3(coefficients)
                if abs(determinant) <= _GEOMETRY_EPSILON:
                    continue

                x_determinant = _determinant3(
                    [
                        (first.d, first.b, first.c),
                        (second.d, second.b, second.c),
                        (third.d, third.b, third.c),
                    ]
                )
                y_determinant = _determinant3(
                    [
                        (first.a, first.d, first.c),
                        (second.a, second.d, second.c),
                        (third.a, third.d, third.c),
                    ]
                )
                z_determinant = _determinant3(
                    [
                        (first.a, first.b, first.d),
                        (second.a, second.b, second.d),
                        (third.a, third.b, third.d),
                    ]
                )
                points.append(
                    Point3D(
                        x_determinant / determinant,
                        y_determinant / determinant,
                        z_determinant / determinant,
                    )
                )
    return tuple(points)


def _active_halfspaces_3d(point: Point3D, halfspaces: Sequence[HalfSpace3D]) -> Tuple[HalfSpace3D, ...]:
    return tuple(halfspace for halfspace in halfspaces if halfspace.is_active(point))


def _segment_from_points_3d(start: Point3D, end: Point3D, halfspaces: Sequence[HalfSpace3D]) -> BoundaryEdge3D:
    midpoint = Point3D(
        (start.x + end.x) / 2.0,
        (start.y + end.y) / 2.0,
        (start.z + end.z) / 2.0,
    )
    active = _active_halfspaces_3d(midpoint, halfspaces)
    return BoundaryEdge3D(
        start=start,
        end=end,
        is_closed=_point_in_halfspaces_3d(midpoint, halfspaces, respect_strict=True),
        is_clipped=bool(active) and all(halfspace.is_clip for halfspace in active),
    )


def _plane_basis(normal: Point3D) -> Tuple[Point3D, Point3D]:
    normalized = _normalize3(normal)
    if abs(normalized.x) < 0.9:
        reference = Point3D(1.0, 0.0, 0.0)
    else:
        reference = Point3D(0.0, 1.0, 0.0)
    axis_u = _normalize3(_cross3(normalized, reference))
    axis_v = _normalize3(_cross3(normalized, axis_u))
    return axis_u, axis_v


def _order_face_vertices_3d(vertices: Sequence[Point3D], normal: Point3D) -> Tuple[Point3D, ...]:
    unique_vertices = _unique_points_3d(vertices)
    if len(unique_vertices) <= 2:
        return unique_vertices

    center = Point3D(
        sum(point.x for point in unique_vertices) / float(len(unique_vertices)),
        sum(point.y for point in unique_vertices) / float(len(unique_vertices)),
        sum(point.z for point in unique_vertices) / float(len(unique_vertices)),
    )
    axis_u, axis_v = _plane_basis(normal)
    return tuple(
        sorted(
            unique_vertices,
            key=lambda point: math.atan2(
                _dot3(_vector3(center, point), axis_v),
                _dot3(_vector3(center, point), axis_u),
            ),
        )
    )


def _plane_key_3d(halfspace: HalfSpace3D) -> Tuple[int, int, int, int]:
    normalized = _normalize3(Point3D(halfspace.a, halfspace.b, halfspace.c))
    scale = math.sqrt((halfspace.a ** 2) + (halfspace.b ** 2) + (halfspace.c ** 2))
    d_value = halfspace.d / scale if scale > _GEOMETRY_EPSILON else halfspace.d
    values = [normalized.x, normalized.y, normalized.z, d_value]
    for candidate in values[:3]:
        if abs(candidate) > _GEOMETRY_EPSILON:
            if candidate < 0.0:
                values = [-item for item in values]
            break
    return tuple(int(round(item * 1000000000.0)) for item in values)  # type: ignore[return-value]


def _edge_key_3d(edge: BoundaryEdge3D) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    return tuple(sorted((_point_key_3d(edge.start), _point_key_3d(edge.end))))  # type: ignore[return-value]


def _deduplicate_edges_3d(edges: Sequence[BoundaryEdge3D]) -> Tuple[BoundaryEdge3D, ...]:
    result = {}  # type: Dict[Tuple[Tuple[int, int, int], Tuple[int, int, int]], BoundaryEdge3D]
    for edge in edges:
        key = _edge_key_3d(edge)
        existing = result.get(key)
        if existing is None:
            result[key] = edge
        else:
            result[key] = BoundaryEdge3D(
                start=existing.start,
                end=existing.end,
                is_closed=existing.is_closed or edge.is_closed,
                is_clipped=existing.is_clipped and edge.is_clipped,
            )
    return tuple(result.values())


def _point_on_segment_3d(point: Point3D, segment: BoundaryEdge3D) -> bool:
    left = _vector3(segment.start, segment.end)
    right = _vector3(segment.start, point)
    cross = _cross3(left, right)
    if _norm3(cross) > _GEOMETRY_EPSILON:
        return False
    dot = _dot3(right, left)
    if dot < -_GEOMETRY_EPSILON:
        return False
    if dot > _dot3(left, left) + _GEOMETRY_EPSILON:
        return False
    return True


def _build_face_from_vertices_3d(
        vertices: Sequence[Point3D],
        normal: Point3D,
        halfspaces: Sequence[HalfSpace3D],
        plane_halfspaces: Sequence[HalfSpace3D],
) -> Face3D:
    ordered = _order_face_vertices_3d(vertices, normal)
    edges = []  # type: List[BoundaryEdge3D]
    for index, start in enumerate(ordered):
        end = ordered[(index + 1) % len(ordered)]
        edges.append(_segment_from_points_3d(start, end, halfspaces))

    center = Point3D(
        sum(point.x for point in ordered) / float(len(ordered)),
        sum(point.y for point in ordered) / float(len(ordered)),
        sum(point.z for point in ordered) / float(len(ordered)),
    )
    is_closed = _point_in_halfspaces_3d(center, halfspaces, respect_strict=True)
    is_clipped = all(halfspace.is_clip for halfspace in plane_halfspaces)
    return Face3D(
        vertices=ordered,
        edges=tuple(edges),
        normal=_normalize3(normal),
        is_closed=is_closed,
        is_clipped=is_clipped,
    )


def _polyhedron_faces_3d(
        vertices: Sequence[Point3D],
        halfspaces: Sequence[HalfSpace3D],
) -> Tuple[Face3D, ...]:
    groups = {}  # type: Dict[Tuple[int, int, int, int], List[HalfSpace3D]]
    for halfspace in halfspaces:
        groups.setdefault(_plane_key_3d(halfspace), []).append(halfspace)

    faces = []  # type: List[Face3D]
    for plane_halfspaces in groups.values():
        representative = plane_halfspaces[0]
        face_vertices = [point for point in vertices if representative.is_active(point)]
        face_vertices = list(_unique_points_3d(face_vertices))
        if len(face_vertices) < 3:
            continue
        faces.append(
            _build_face_from_vertices_3d(
                face_vertices,
                Point3D(representative.a, representative.b, representative.c),
                halfspaces,
                plane_halfspaces,
            )
        )
    return tuple(faces)


def _classify_points_3d(points: Sequence[Point3D]) -> Tuple[str, Optional[Point3D]]:
    ordered = list(_unique_points_3d(points))
    if not ordered:
        return "empty", None
    if len(ordered) == 1:
        return "point", None

    origin = ordered[0]
    direction = None  # type: Optional[Point3D]
    for point in ordered[1:]:
        candidate = _vector3(origin, point)
        if _norm3(candidate) > _GEOMETRY_EPSILON:
            direction = candidate
            break
    if direction is None:
        return "point", None

    normal = None  # type: Optional[Point3D]
    for point in ordered[1:]:
        candidate = _cross3(direction, _vector3(origin, point))
        if _norm3(candidate) > _GEOMETRY_EPSILON:
            normal = candidate
            break
    if normal is None:
        return "segment", _normalize3(direction)

    for point in ordered[1:]:
        distance = _dot3(_vector3(origin, point), normal)
        if abs(distance) > _GEOMETRY_EPSILON:
            return "polyhedron", _normalize3(normal)
    return "face", _normalize3(normal)


def _extract_dbm_geometry_3d(
        dbm: DBM,
        limits: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
) -> Union[EmptyGeometry, PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D]:
    halfspaces = _build_halfspaces_for_dbm_3d(dbm, limits)
    candidate_points = [
        point for point in _triple_plane_intersections(halfspaces)
        if _point_in_halfspaces_3d(point, halfspaces, respect_strict=False)
    ]
    unique_points = _unique_points_3d(candidate_points)
    if not unique_points:
        return EmptyGeometry(dimension=3)

    kind, normal = _classify_points_3d(unique_points)
    if kind == "point":
        point = unique_points[0]
        return PointGeometry3D(
            point=point,
            is_closed=_point_in_halfspaces_3d(point, halfspaces, respect_strict=True),
            is_clipped=any(halfspace.is_clip for halfspace in _active_halfspaces_3d(point, halfspaces)),
            halfspaces=halfspaces,
        )

    if kind == "segment":
        origin = unique_points[0]
        direction = normal if normal is not None else Point3D(1.0, 0.0, 0.0)
        ordered = sorted(unique_points, key=lambda point: _dot3(_vector3(origin, point), direction))
        segment = _segment_from_points_3d(ordered[0], ordered[-1], halfspaces)
        return SegmentGeometry3D(segment=segment, halfspaces=halfspaces)

    if kind == "face":
        face = _build_face_from_vertices_3d(unique_points, normal or Point3D(0.0, 0.0, 1.0), halfspaces, _active_halfspaces_3d(unique_points[0], halfspaces))
        return FaceGeometry3D(face=face, halfspaces=halfspaces)

    faces = _polyhedron_faces_3d(unique_points, halfspaces)
    edges = _deduplicate_edges_3d([edge for face in faces for edge in face.edges])
    return PolyhedronGeometry3D(
        vertices=tuple(unique_points),
        edges=edges,
        faces=faces,
        halfspaces=halfspaces,
    )


def _orientation(point_a: Point2D, point_b: Point2D, point_c: Point2D) -> float:
    return ((point_b.x - point_a.x) * (point_c.y - point_a.y)) - ((point_b.y - point_a.y) * (point_c.x - point_a.x))


def _segment_intersection_parameters(left: BoundarySegment2D, right: BoundarySegment2D) -> Tuple[
    Tuple[float, ...], Tuple[float, ...]]:
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
            left_values = sorted(
                [0.0, 1.0, (right.start.x - left.start.x) / r.x if abs(r.x) > _GEOMETRY_EPSILON else 0.0,
                 (right.end.x - left.start.x) / r.x if abs(r.x) > _GEOMETRY_EPSILON else 0.0])
        else:
            left_values = sorted(
                [0.0, 1.0, (right.start.y - left.start.y) / r.y if abs(r.y) > _GEOMETRY_EPSILON else 0.0,
                 (right.end.y - left.start.y) / r.y if abs(r.y) > _GEOMETRY_EPSILON else 0.0])

        overlap_start = max(0.0, left_values[1])
        overlap_end = min(1.0, left_values[2])
        if overlap_end <= overlap_start + _GEOMETRY_EPSILON:
            return tuple(), tuple()

        if abs(s.x) >= abs(s.y):
            right_start = (left.start.x + (r.x * overlap_start) - right.start.x) / s.x if abs(
                s.x) > _GEOMETRY_EPSILON else 0.0
            right_end = (left.start.x + (r.x * overlap_end) - right.start.x) / s.x if abs(
                s.x) > _GEOMETRY_EPSILON else 0.0
        else:
            right_start = (left.start.y + (r.y * overlap_start) - right.start.y) / s.y if abs(
                s.y) > _GEOMETRY_EPSILON else 0.0
            right_end = (left.start.y + (r.y * overlap_end) - right.start.y) / s.y if abs(
                s.y) > _GEOMETRY_EPSILON else 0.0

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


def _choose_next_boundary_segment(current: BoundarySegment2D,
                                  candidates: Sequence[BoundarySegment2D]) -> BoundarySegment2D:
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
                next_segment = _choose_next_boundary_segment(current,
                                                             [boundary_segments[index] for index in candidates])
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
    # Preserve semantic transition points on the traced boundary.
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
        limits: Optional[
            Union[
                Tuple[float, float],
                Tuple[Tuple[float, float], Tuple[float, float]],
                Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
            ]
        ] = None,
) -> Union[
    EmptyGeometry, Interval1D, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D,
    PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D
]:
    """
    Extract a pure-Python visualization geometry snapshot from one DBM.

    This is the geometry-layer Phase 1 entry point. It intentionally performs
    no matplotlib import or artist creation.

    For a 1D DBM this returns one clipped :class:`Interval1D` or
    :class:`EmptyGeometry`. For a 2D DBM it returns one exact clipped geometry
    object among :class:`PolygonGeometry2D`, :class:`SegmentGeometry2D`,
    :class:`PointGeometry2D`, or :class:`EmptyGeometry`.

    :param dbm: Source DBM to convert into visualization geometry.
    :type dbm: DBM
    :param limits: Optional render limits. Use ``(xmin, xmax)`` for 1D,
        ``((xmin, xmax), (ymin, ymax))`` for 2D, and
        ``((xmin, xmax), (ymin, ymax), (zmin, zmax))`` for 3D. When omitted,
        limits are derived from the finite DBM bounds.
    :type limits: Optional[Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]], Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]]]
    :return: Pure-Python exact geometry snapshot for the requested render box.
    :rtype: Union[EmptyGeometry, Interval1D, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D, PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D]
    :raises TypeError: If ``dbm`` is not a :class:`DBM`.
    :raises ValueError: If the DBM dimension is outside the supported range or if ``limits`` are malformed.
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
        normalized_limits = _normalize_3d_limits(limits, [_dbm_axis_bounds_3d(dbm)])  # type: ignore[arg-type]
        return _extract_dbm_geometry_3d(dbm, normalized_limits)
    raise ValueError("Visualization geometry currently supports only 1D, 2D, and 3D contexts.")


def extract_federation_geometry(
        federation: Federation,
        limits: Optional[
            Union[
                Tuple[float, float],
                Tuple[Tuple[float, float], Tuple[float, float]],
                Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
            ]
        ] = None,
) -> Union[EmptyGeometry, MultiInterval1D, FederationGeometry2D, FederationGeometry3D]:
    """
    Extract a pure-Python visualization geometry snapshot from one federation.

    For 1D federations this returns the exact interval union. For 2D
    federations this returns the exact clipped polygon-union boundary for the
    polygonal DBM components.

    :param federation: Source federation to convert into visualization geometry.
    :type federation: Federation
    :param limits: Optional render limits. Use ``(xmin, xmax)`` for 1D,
        ``((xmin, xmax), (ymin, ymax))`` for 2D, and
        ``((xmin, xmax), (ymin, ymax), (zmin, zmax))`` for 3D. When omitted,
        limits are derived from the finite bounds of all DBMs in the federation.
    :type limits: Optional[Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]], Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]]]
    :return: Exact pure-Python geometry summary for the requested render box.
    :rtype: Union[EmptyGeometry, MultiInterval1D, FederationGeometry2D, FederationGeometry3D]
    :raises TypeError: If ``federation`` is not a :class:`Federation`.
    :raises ValueError: If the dimension is outside the supported range or if ``limits`` are malformed.
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
        normalized_limits = _normalize_2d_limits(limits,
                                                 [_dbm_axis_bounds_2d(dbm) for dbm in dbms])  # type: ignore[arg-type]
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
        normalized_limits = _normalize_3d_limits(limits, [_dbm_axis_bounds_3d(dbm) for dbm in dbms])  # type: ignore[arg-type]
        dbm_geometries = []  # type: List[Union[PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D]]
        for dbm in dbms:
            geometry = _extract_dbm_geometry_3d(dbm, normalized_limits)
            if not isinstance(geometry, EmptyGeometry):
                dbm_geometries.append(geometry)
        if not dbm_geometries:
            return EmptyGeometry(dimension=3)
        return FederationGeometry3D(dbm_geometries=tuple(dbm_geometries), limits=normalized_limits)
    raise ValueError("Visualization geometry currently supports only 1D, 2D, and 3D contexts.")


def _require_matplotlib() -> Tuple[Any, Any, Any]:
    try:
        pyplot = importlib.import_module("matplotlib.pyplot")
        patches = importlib.import_module("matplotlib.patches")
        path = importlib.import_module("matplotlib.path")
    except ImportError as err:
        raise ImportError("matplotlib is required for visualization support. Install pyudbm[plot].") from err
    return pyplot, patches, path


def _require_mplot3d() -> Any:
    try:
        return importlib.import_module("mpl_toolkits.mplot3d.art3d")
    except ImportError as err:
        raise ImportError("matplotlib is required for visualization support. Install pyudbm[plot].") from err


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
    elif finite_lowers or finite_uppers:
        bound = min(finite_lowers) if finite_lowers else max(finite_uppers)
        scale = max(abs(bound), 1.0)
        pad = max(scale * 0.15, 0.5)
        span = max(scale * 0.5, 3.0)
        lower = min(bound - (pad if finite_lowers else span), -pad)
        upper = bound + (span if finite_lowers else pad)
    else:
        return -5.0, 5.0

    return lower, upper


def _auto_plot_limits_for_dbm(
        dbm: DBM,
) -> Union[
    Tuple[float, float],
    Tuple[Tuple[float, float], Tuple[float, float]],
    Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
]:
    user_dimension = dbm.dimension - 1
    if user_dimension == 1:
        lower, upper, _, _ = _dbm_axis_bounds_1d(dbm)
        return _auto_plot_axis_limits([(lower, upper)])
    if user_dimension == 2:
        x_lower, x_upper, y_lower, y_upper = _dbm_axis_bounds_2d(dbm)
        return _auto_plot_axis_limits([(x_lower, x_upper)]), _auto_plot_axis_limits([(y_lower, y_upper)])
    x_lower, x_upper, y_lower, y_upper, z_lower, z_upper = _dbm_axis_bounds_3d(dbm)
    return (
        _auto_plot_axis_limits([(x_lower, x_upper)]),
        _auto_plot_axis_limits([(y_lower, y_upper)]),
        _auto_plot_axis_limits([(z_lower, z_upper)]),
    )


def _auto_plot_limits_for_federation(
        federation: Federation,
) -> Union[
    Tuple[float, float],
    Tuple[Tuple[float, float], Tuple[float, float]],
    Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
]:
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

    x_bounds = []  # type: List[Tuple[Optional[float], Optional[float]]]
    y_bounds = []  # type: List[Tuple[Optional[float], Optional[float]]]
    z_bounds = []  # type: List[Tuple[Optional[float], Optional[float]]]
    for dbm in dbms:
        x_lower, x_upper, y_lower, y_upper, z_lower, z_upper = _dbm_axis_bounds_3d(dbm)
        x_bounds.append((x_lower, x_upper))
        y_bounds.append((y_lower, y_upper))
        z_bounds.append((z_lower, z_upper))
    return _auto_plot_axis_limits(x_bounds), _auto_plot_axis_limits(y_bounds), _auto_plot_axis_limits(z_bounds)


def _set_axis_clock_labels(ax: Any, clock_names: Sequence[str], dimension: int) -> None:
    if dimension >= 1 and len(clock_names) >= 1:
        ax.set_xlabel(clock_names[0])
    if dimension >= 2 and len(clock_names) >= 2:
        ax.set_ylabel(clock_names[1])
    if dimension >= 3 and len(clock_names) >= 3:
        ax.set_zlabel(clock_names[2])
    elif dimension == 1:
        ax.set_ylabel("visual baseline")


def _resolve_limits_from_geometry(
        geometry: Union[
            EmptyGeometry, Interval1D, MultiInterval1D, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D,
            FederationGeometry2D, PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D,
            FederationGeometry3D]
) -> Union[
    Tuple[float, float],
    Tuple[Tuple[float, float], Tuple[float, float]],
    Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
]:
    if isinstance(geometry, EmptyGeometry):
        if geometry.dimension == 1:
            return -1.0, 1.0
        if geometry.dimension == 3:
            return (-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0)
        return (-1.0, 1.0), (-1.0, 1.0)

    if isinstance(geometry, Interval1D):
        return geometry.lower, geometry.upper
    if isinstance(geometry, MultiInterval1D):
        if geometry.intervals:
            return geometry.intervals[0].lower, geometry.intervals[-1].upper
        return -1.0, 1.0
    if isinstance(geometry, FederationGeometry2D):
        return geometry.limits
    if isinstance(geometry, FederationGeometry3D):
        return geometry.limits

    x_values = []  # type: List[float]
    y_values = []  # type: List[float]
    z_values = []  # type: List[float]
    if isinstance(geometry, PolygonGeometry2D):
        x_values.extend(point.x for point in geometry.vertices)
        y_values.extend(point.y for point in geometry.vertices)
    elif isinstance(geometry, SegmentGeometry2D):
        x_values.extend([geometry.segment.start.x, geometry.segment.end.x])
        y_values.extend([geometry.segment.start.y, geometry.segment.end.y])
    elif isinstance(geometry, PointGeometry2D):
        x_values.append(geometry.point.x)
        y_values.append(geometry.point.y)
    elif isinstance(geometry, PolyhedronGeometry3D):
        x_values.extend(point.x for point in geometry.vertices)
        y_values.extend(point.y for point in geometry.vertices)
        z_values.extend(point.z for point in geometry.vertices)
    elif isinstance(geometry, FaceGeometry3D):
        x_values.extend(point.x for point in geometry.face.vertices)
        y_values.extend(point.y for point in geometry.face.vertices)
        z_values.extend(point.z for point in geometry.face.vertices)
    elif isinstance(geometry, SegmentGeometry3D):
        x_values.extend([geometry.segment.start.x, geometry.segment.end.x])
        y_values.extend([geometry.segment.start.y, geometry.segment.end.y])
        z_values.extend([geometry.segment.start.z, geometry.segment.end.z])
    elif isinstance(geometry, PointGeometry3D):
        x_values.append(geometry.point.x)
        y_values.append(geometry.point.y)
        z_values.append(geometry.point.z)

    if z_values:
        xmin = min(x_values)
        xmax = max(x_values)
        ymin = min(y_values)
        ymax = max(y_values)
        zmin = min(z_values)
        zmax = max(z_values)
        if _almost_equal(xmin, xmax):
            xmin -= 1.0
            xmax += 1.0
        if _almost_equal(ymin, ymax):
            ymin -= 1.0
            ymax += 1.0
        if _almost_equal(zmin, zmax):
            zmin -= 1.0
            zmax += 1.0
        return (xmin, xmax), (ymin, ymax), (zmin, zmax)

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
        geometry: Union[
            EmptyGeometry, Interval1D, MultiInterval1D, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D,
            FederationGeometry2D, PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D,
            FederationGeometry3D],
        strict_epsilon: Optional[float],
) -> float:
    if strict_epsilon is not None:
        value = float(strict_epsilon)
        if value <= 0.0:
            raise ValueError("strict_epsilon must be positive when specified.")
        return value

    limits = _resolve_limits_from_geometry(geometry)
    if isinstance(limits[0], tuple):
        if len(limits) == 2:
            x_limits, y_limits = limits  # type: ignore[misc]
            scale = min(float(x_limits[1]) - float(x_limits[0]), float(y_limits[1]) - float(y_limits[0]))
        else:
            x_limits, y_limits, z_limits = limits  # type: ignore[misc]
            scale = min(
                float(x_limits[1]) - float(x_limits[0]),
                float(y_limits[1]) - float(y_limits[0]),
                float(z_limits[1]) - float(z_limits[0]),
            )
    else:
        scale = float(limits[1]) - float(limits[0])  # type: ignore[index]
    return max(scale * 1e-4, 1e-7)


def _fallback_default_color(ax: Any) -> Any:
    _, _, _ = _require_matplotlib()
    color_values = importlib.import_module("matplotlib").rcParams["axes.prop_cycle"].by_key().get("color") or ["C0"]
    index = int(getattr(ax, "pyudbm_plot_color_index", 0))
    color = color_values[index % len(color_values)]
    setattr(ax, "pyudbm_plot_color_index", index + 1)
    return color


def _next_default_color(ax: Any) -> Any:
    line_helper = getattr(ax, "_get_lines", None)
    getter = getattr(line_helper, "get_next_color", None)
    if callable(getter):
        return getter()
    return _fallback_default_color(ax)


def _take_default_colors(ax: Any, count: int) -> Tuple[Any, ...]:
    return tuple(_next_default_color(ax) for _ in range(count))


def _resolve_style(
        ax: Any,
        facecolor: Optional[Any],
        edgecolor: Optional[Any],
        alpha: Optional[float],
        linewidth: Optional[float],
        linestyle: Optional[Any],
) -> Tuple[Any, Any, float, float, Any]:
    if edgecolor is None and facecolor is None:
        default_color = _next_default_color(ax)
        resolved_edgecolor = default_color
        resolved_facecolor = default_color
    elif edgecolor is None:
        resolved_facecolor = facecolor
        resolved_edgecolor = facecolor
    else:
        resolved_edgecolor = edgecolor
        resolved_facecolor = facecolor if facecolor is not None else resolved_edgecolor
    resolved_alpha = 0.25 if alpha is None else float(alpha)
    resolved_linewidth = 1.5 if linewidth is None else float(linewidth)
    resolved_linestyle = "-" if linestyle is None else linestyle
    return resolved_facecolor, resolved_edgecolor, resolved_alpha, resolved_linewidth, resolved_linestyle


def _make_axes(pyplot: Any, ax: Optional[Any], dimension: int) -> Any:
    if ax is not None:
        return ax
    if dimension == 3:
        figure = pyplot.figure()
        return figure.add_subplot(111, projection="3d")
    _, new_ax = pyplot.subplots()
    return new_ax


def _set_default_view(
        ax: Any,
        geometry: Union[
            EmptyGeometry, Interval1D, MultiInterval1D, PolygonGeometry2D, SegmentGeometry2D, PointGeometry2D,
            FederationGeometry2D, PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D,
            FederationGeometry3D],
        baseline: float,
        view_limits: Optional[
            Union[
                Tuple[float, float],
                Tuple[Tuple[float, float], Tuple[float, float]],
                Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
            ]
        ] = None,
) -> None:
    limits = view_limits if view_limits is not None else _resolve_limits_from_geometry(geometry)
    if isinstance(limits[0], tuple):
        if len(limits) == 2:
            x_limits, y_limits = limits  # type: ignore[misc]
            ax.set_xlim(*x_limits)
            ax.set_ylim(*y_limits)
            ax.set_aspect("equal", adjustable="box")
        else:
            x_limits, y_limits, z_limits = limits  # type: ignore[misc]
            ax.set_xlim(*x_limits)
            ax.set_ylim(*y_limits)
            ax.set_zlim(*z_limits)
    else:
        x_limits = limits  # type: ignore[assignment]
        ax.set_xlim(*x_limits)
        ax.set_ylim(baseline - 1.0, baseline + 1.0)


def _merged_view_limits(
        ax: Any,
        dimension: int,
        baseline: float,
        view_limits: Union[
            Tuple[float, float],
            Tuple[Tuple[float, float], Tuple[float, float]],
            Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
        ],
) -> Union[
    Tuple[float, float],
    Tuple[Tuple[float, float], Tuple[float, float]],
    Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
]:
    del baseline
    if not ax.has_data():
        return view_limits

    if dimension == 1:
        current_x = ax.get_xlim()
        new_x = view_limits  # type: ignore[assignment]
        return min(current_x[0], new_x[0]), max(current_x[1], new_x[1])

    if dimension == 3:
        current_x = ax.get_xlim()
        current_y = ax.get_ylim()
        current_z = ax.get_zlim()
        new_x, new_y, new_z = view_limits  # type: ignore[misc]
        return (
            (min(current_x[0], new_x[0]), max(current_x[1], new_x[1])),
            (min(current_y[0], new_y[0]), max(current_y[1], new_y[1])),
            (min(current_z[0], new_z[0]), max(current_z[1], new_z[1])),
        )

    current_x = ax.get_xlim()
    current_y = ax.get_ylim()
    new_x, new_y = view_limits  # type: ignore[misc]
    return (
        (min(current_x[0], new_x[0]), max(current_x[1], new_x[1])),
        (min(current_y[0], new_y[0]), max(current_y[1], new_y[1])),
    )


def _line_label(label: Optional[str], index: int) -> Optional[str]:
    return label if (label is None or index == 0) else "_nolegend_"


def _resolve_annotation_text(
    annotate: bool,
    annotate_text: Optional[str],
    default_text: str,
) -> Tuple[bool, Optional[str]]:
    if annotate_text is not None:
        if not annotate:
            warnings.warn(
                "annotate_text was explicitly provided while annotate is not True, so annotate is forced to True.",
                UserWarning,
                stacklevel=3,
            )
        return True, annotate_text
    if annotate:
        return True, default_text
    return False, None


def _endpoint_marker_style(is_closed: bool, edgecolor: Any, is_clipped: bool = False) -> Dict[str, Any]:
    return {
        "marker": "s" if is_clipped else "o",
        "markersize": 6.0,
        "markeredgecolor": edgecolor,
        "markerfacecolor": edgecolor if is_closed else "none",
        "linestyle": "None",
    }


def _interval_line_range(interval: Interval1D, epsilon: float) -> Tuple[float, float]:
    start = interval.lower + (epsilon if not interval.lower_closed else 0.0)
    end = interval.upper - (epsilon if not interval.upper_closed else 0.0)
    return start, end


def _plot_interval(ax: Any, interval: Interval1D, baseline: float, epsilon: float, edgecolor: Any, linewidth: float,
                   zorder: Optional[float], label: Optional[str]) -> PlotResult:
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

    lower_marker = ax.plot([interval.lower], [baseline], color=edgecolor, zorder=zorder,
                           **_endpoint_marker_style(interval.lower_closed, edgecolor, interval.lower_clipped))[0]
    upper_marker = ax.plot([interval.upper], [baseline], color=edgecolor, zorder=zorder,
                           **_endpoint_marker_style(interval.upper_closed, edgecolor, interval.upper_clipped))[0]
    markers.extend([lower_marker, upper_marker])
    return PlotResult(ax=ax, boundaries=tuple(boundaries), markers=tuple(markers))


def _arrow_for_interval(ax: Any, x_value: float, baseline: float, direction: float, edgecolor: Any, linewidth: float,
                        zorder: Optional[float], patches: Any, extent: float) -> Any:
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
        annotation_text: Optional[str],
        facecolor: Optional[Any],
        edgecolor: Optional[Any],
        alpha: Optional[float],
        linewidth: Optional[float],
        linestyle: Optional[Any],
        label: Optional[str],
        zorder: Optional[float],
) -> PlotResult:
    del facecolor, alpha, linestyle
    _, resolved_edgecolor, _, resolved_linewidth, _ = _resolve_style(ax, None, edgecolor, None, linewidth, None)
    _, patches, _ = _require_matplotlib()

    boundaries = []  # type: List[Any]
    markers = []  # type: List[Any]
    arrows = []  # type: List[Any]
    annotations = []  # type: List[Any]
    intervals = geometry.intervals if isinstance(geometry, MultiInterval1D) else (
        (geometry,) if isinstance(geometry, Interval1D) else tuple())

    for index, interval in enumerate(intervals):
        result = _plot_interval(ax, interval, baseline, strict_epsilon, resolved_edgecolor, resolved_linewidth, zorder,
                                _line_label(label, index))
        boundaries.extend(result.boundaries)
        markers.extend(result.markers)
        extent = max(interval.upper - interval.lower, 1.0)
        if show_unbounded and interval.lower_clipped:
            arrow = _arrow_for_interval(ax, interval.lower, baseline, -1.0, resolved_edgecolor, resolved_linewidth,
                                        zorder, patches, extent)
            ax.add_patch(arrow)
            arrows.append(arrow)
        if show_unbounded and interval.upper_clipped:
            arrow = _arrow_for_interval(ax, interval.upper, baseline, 1.0, resolved_edgecolor, resolved_linewidth,
                                        zorder, patches, extent)
            ax.add_patch(arrow)
            arrows.append(arrow)
        if annotate and annotation_text is not None:
            annotation = ax.text((interval.lower + interval.upper) / 2.0, baseline + 0.08, annotation_text,
                                 color=resolved_edgecolor)
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
    candidate_points = [point for point in _pairwise_line_intersections(adjusted) if
                        _point_in_halfspaces(point, adjusted, respect_strict=False)]
    unique_points = _unique_points(candidate_points)
    if len(unique_points) < 3:
        return tuple()
    return _convex_hull(unique_points)


def _edge_linestyle(segment: BoundarySegment2D, default_linestyle: Any) -> Any:
    if segment.is_clipped:
        return ":" if not segment.is_closed else "-."
    if not segment.is_closed:
        return "--"
    return default_linestyle


def _plot_boundary_segment(ax: Any, segment: BoundarySegment2D, edgecolor: Any, linewidth: float, linestyle: Any,
                           zorder: Optional[float], label: Optional[str]) -> Any:
    return ax.plot(
        [segment.start.x, segment.end.x],
        [segment.start.y, segment.end.y],
        color=edgecolor,
        linewidth=linewidth,
        linestyle=_edge_linestyle(segment, linestyle),
        zorder=zorder,
        label=label,
    )[0]


def _arrows_for_segment(ax: Any, segment: BoundarySegment2D, edgecolor: Any, linewidth: float, zorder: Optional[float],
                        patches: Any, outward_sign: float) -> Tuple[Any, ...]:
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
        annotation_text: Optional[str],
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
        ax, facecolor, edgecolor, alpha, linewidth, linestyle
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
            line = _plot_boundary_segment(ax, segment, resolved_edgecolor, resolved_linewidth, resolved_linestyle,
                                          zorder, _line_label(label, index if not fills else index + 1))
            boundaries.append(line)
            if show_unbounded and segment.is_clipped:
                for arrow in _arrows_for_segment(ax, segment, resolved_edgecolor, resolved_linewidth, zorder, patches,
                                                 -1.0):
                    ax.add_patch(arrow)
                    arrows.append(arrow)
        if annotate and annotation_text is not None:
            center_x = sum(point.x for point in geometry.vertices) / float(len(geometry.vertices))
            center_y = sum(point.y for point in geometry.vertices) / float(len(geometry.vertices))
            annotations.append(ax.text(center_x, center_y, annotation_text, color=resolved_edgecolor))

    elif isinstance(geometry, SegmentGeometry2D):
        line = _plot_boundary_segment(ax, geometry.segment, resolved_edgecolor, resolved_linewidth, resolved_linestyle,
                                      zorder, label)
        boundaries.append(line)
        markers.append(
            ax.plot([geometry.segment.start.x], [geometry.segment.start.y], color=resolved_edgecolor, zorder=zorder,
                    **_endpoint_marker_style(geometry.segment.is_closed, resolved_edgecolor, geometry.segment.is_clipped))[0])
        markers.append(
            ax.plot([geometry.segment.end.x], [geometry.segment.end.y], color=resolved_edgecolor, zorder=zorder,
                    **_endpoint_marker_style(geometry.segment.is_closed, resolved_edgecolor, geometry.segment.is_clipped))[0])
        if annotate and annotation_text is not None:
            annotations.append(
                ax.text(geometry.segment.midpoint.x, geometry.segment.midpoint.y, annotation_text, color=resolved_edgecolor))

    elif isinstance(geometry, PointGeometry2D):
        marker = ax.plot([geometry.point.x], [geometry.point.y], color=resolved_edgecolor, zorder=zorder, label=label,
                         **_endpoint_marker_style(geometry.is_closed, resolved_edgecolor, geometry.is_clipped))[0]
        markers.append(marker)
        if annotate and annotation_text is not None:
            annotations.append(ax.text(geometry.point.x, geometry.point.y, annotation_text, color=resolved_edgecolor))

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
        annotation_text: Optional[str],
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
        ax, facecolor, edgecolor, alpha, linewidth, linestyle
    )

    fills = []  # type: List[Any]
    boundaries = []  # type: List[Any]
    markers = []  # type: List[Any]
    arrows = []  # type: List[Any]
    annotations = []  # type: List[Any]

    if isinstance(geometry, FederationGeometry2D):
        if color_mode == "per_dbm":
            color_cycle = _take_default_colors(ax, len(geometry.dbm_geometries))
            for index, dbm_geometry in enumerate(geometry.dbm_geometries):
                dbm_result = _plot_dbm_2d_geometry(
                    dbm_geometry,
                    ax=ax,
                    strict_epsilon=strict_epsilon,
                    show_unbounded=False,
                    annotate=False,
                    annotation_text=None,
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
            line = _plot_boundary_segment(ax, segment, resolved_edgecolor, resolved_linewidth, resolved_linestyle,
                                          zorder, _line_label(label, index if not fills else index + 1))
            boundaries.append(line)
            if show_unbounded and segment.is_clipped:
                sign = loop_lookup.get((_point_key(segment.start), _point_key(segment.end)), -1.0)
                for arrow in _arrows_for_segment(ax, segment, resolved_edgecolor, resolved_linewidth, zorder, patches,
                                                 sign):
                    ax.add_patch(arrow)
                    arrows.append(arrow)

        for segment in geometry.isolated_segments:
            line = _plot_boundary_segment(ax, segment, resolved_edgecolor, resolved_linewidth, resolved_linestyle,
                                          zorder, None)
            boundaries.append(line)

        for point in geometry.isolated_points:
            markers.append(ax.plot([point.x], [point.y], color=resolved_edgecolor, zorder=zorder,
                                   **_endpoint_marker_style(True, resolved_edgecolor, False))[0])

        if annotate and annotation_text is not None:
            for face in geometry.faces:
                vertices = face.outer.vertices
                center_x = sum(point.x for point in vertices) / float(len(vertices))
                center_y = sum(point.y for point in vertices) / float(len(vertices))
                annotations.append(ax.text(center_x, center_y, annotation_text, color=resolved_edgecolor))

    return PlotResult(
        ax=ax,
        fills=tuple(fills),
        boundaries=tuple(boundaries),
        markers=tuple(markers),
        arrows=tuple(arrows),
        annotations=tuple(annotations),
    )


def _plot_boundary_edge_3d(
        ax: Any,
        edge: BoundaryEdge3D,
        edgecolor: Any,
        linewidth: float,
        linestyle: Any,
        zorder: Optional[float],
        label: Optional[str],
) -> Any:
    return ax.plot(
        [edge.start.x, edge.end.x],
        [edge.start.y, edge.end.y],
        [edge.start.z, edge.end.z],
        color=edgecolor,
        linewidth=linewidth,
        linestyle=_edge_linestyle(
            BoundarySegment2D(Point2D(0.0, 0.0), Point2D(1.0, 0.0), edge.is_closed, edge.is_clipped),
            linestyle,
        ),
        zorder=zorder,
        label=label,
    )[0]


def _face_center_3d(face: Face3D) -> Point3D:
    return Point3D(
        sum(point.x for point in face.vertices) / float(len(face.vertices)),
        sum(point.y for point in face.vertices) / float(len(face.vertices)),
        sum(point.z for point in face.vertices) / float(len(face.vertices)),
    )


def _arrow_for_face_3d(ax: Any, face: Face3D, edgecolor: Any, linewidth: float, zorder: Optional[float]) -> Any:
    center = _face_center_3d(face)
    normal = _normalize3(face.normal)
    arrow_length = max(
        max(max(point.x for point in face.vertices) - min(point.x for point in face.vertices), 0.5),
        max(max(point.y for point in face.vertices) - min(point.y for point in face.vertices), 0.5),
        max(max(point.z for point in face.vertices) - min(point.z for point in face.vertices), 0.5),
    ) * 0.15
    return ax.quiver(
        [center.x],
        [center.y],
        [center.z],
        [normal.x],
        [normal.y],
        [normal.z],
        length=arrow_length,
        color=edgecolor,
        linewidth=linewidth,
        normalize=True,
    )


def _segment_arrow_direction_3d(halfspaces: Sequence[HalfSpace3D], point: Point3D) -> Point3D:
    active = [halfspace for halfspace in _active_halfspaces_3d(point, halfspaces) if halfspace.is_clip]
    if not active:
        return Point3D(0.0, 0.0, 0.0)
    direction = Point3D(
        sum(halfspace.a for halfspace in active),
        sum(halfspace.b for halfspace in active),
        sum(halfspace.c for halfspace in active),
    )
    return _normalize3(direction)


def _arrow_for_point_3d(
        ax: Any,
        point: Point3D,
        direction: Point3D,
        edgecolor: Any,
        linewidth: float,
        zorder: Optional[float],
) -> Any:
    if _norm3(direction) <= _GEOMETRY_EPSILON:
        return None
    return ax.quiver(
        [point.x],
        [point.y],
        [point.z],
        [direction.x],
        [direction.y],
        [direction.z],
        length=0.2,
        color=edgecolor,
        linewidth=linewidth,
        normalize=True,
    )


def _plot_face_geometry_3d(
        face: Face3D,
        ax: Any,
        art3d: Any,
        edgecolor: Any,
        facecolor: Any,
        alpha: float,
        linewidth: float,
        linestyle: Any,
        zorder: Optional[float],
        label: Optional[str],
) -> PlotResult:
    fills = []  # type: List[Any]
    boundaries = []  # type: List[Any]
    collection = art3d.Poly3DCollection(
        [[(point.x, point.y, point.z) for point in face.vertices]],
        facecolors=facecolor,
        edgecolors="none",
        alpha=alpha,
    )
    collection.set_label("_nolegend_")
    if zorder is not None:
        collection.set_zorder(zorder)
    ax.add_collection3d(collection)
    fills.append(collection)

    for index, edge in enumerate(face.edges):
        boundaries.append(
            _plot_boundary_edge_3d(ax, edge, edgecolor, linewidth, linestyle, zorder, _line_label(label, index))
        )
    return PlotResult(ax=ax, fills=tuple(fills), boundaries=tuple(boundaries))


def _plot_dbm_3d_geometry(
        geometry: Union[EmptyGeometry, PolyhedronGeometry3D, FaceGeometry3D, SegmentGeometry3D, PointGeometry3D],
        ax: Any,
        show_unbounded: bool,
        annotate: bool,
        annotation_text: Optional[str],
        facecolor: Optional[Any],
        edgecolor: Optional[Any],
        alpha: Optional[float],
        linewidth: Optional[float],
        linestyle: Optional[Any],
        label: Optional[str],
        zorder: Optional[float],
) -> PlotResult:
    art3d = _require_mplot3d()
    resolved_facecolor, resolved_edgecolor, resolved_alpha, resolved_linewidth, resolved_linestyle = _resolve_style(
        ax, facecolor, edgecolor, alpha, linewidth, linestyle
    )

    fills = []  # type: List[Any]
    boundaries = []  # type: List[Any]
    markers = []  # type: List[Any]
    arrows = []  # type: List[Any]
    annotations = []  # type: List[Any]

    if isinstance(geometry, PolyhedronGeometry3D):
        if geometry.faces:
            collection = art3d.Poly3DCollection(
                [[(point.x, point.y, point.z) for point in face.vertices] for face in geometry.faces],
                facecolors=resolved_facecolor,
                edgecolors="none",
                alpha=resolved_alpha,
            )
            collection.set_label("_nolegend_")
            if zorder is not None:
                collection.set_zorder(zorder)
            ax.add_collection3d(collection)
            fills.append(collection)

        for index, edge in enumerate(geometry.edges):
            boundaries.append(
                _plot_boundary_edge_3d(
                    ax,
                    edge,
                    resolved_edgecolor,
                    resolved_linewidth,
                    resolved_linestyle,
                    zorder,
                    _line_label(label, index),
                )
            )

        if show_unbounded:
            for face in geometry.faces:
                if face.is_clipped:
                    arrow = _arrow_for_face_3d(ax, face, resolved_edgecolor, resolved_linewidth, zorder)
                    arrows.append(arrow)
        if annotate and annotation_text is not None and geometry.vertices:
            center = Point3D(
                sum(point.x for point in geometry.vertices) / float(len(geometry.vertices)),
                sum(point.y for point in geometry.vertices) / float(len(geometry.vertices)),
                sum(point.z for point in geometry.vertices) / float(len(geometry.vertices)),
            )
            annotations.append(ax.text(center.x, center.y, center.z, annotation_text, color=resolved_edgecolor))

    elif isinstance(geometry, FaceGeometry3D):
        face_result = _plot_face_geometry_3d(
            geometry.face,
            ax,
            art3d,
            resolved_edgecolor,
            resolved_facecolor,
            resolved_alpha,
            resolved_linewidth,
            resolved_linestyle,
            zorder,
            label,
        )
        fills.extend(face_result.fills)
        boundaries.extend(face_result.boundaries)
        if show_unbounded and geometry.face.is_clipped:
            arrows.append(_arrow_for_face_3d(ax, geometry.face, resolved_edgecolor, resolved_linewidth, zorder))
        if annotate and annotation_text is not None:
            center = _face_center_3d(geometry.face)
            annotations.append(ax.text(center.x, center.y, center.z, annotation_text, color=resolved_edgecolor))

    elif isinstance(geometry, SegmentGeometry3D):
        boundaries.append(
            _plot_boundary_edge_3d(ax, geometry.segment, resolved_edgecolor, resolved_linewidth, resolved_linestyle, zorder, label)
        )
        markers.append(
            ax.plot(
                [geometry.segment.start.x],
                [geometry.segment.start.y],
                [geometry.segment.start.z],
                color=resolved_edgecolor,
                zorder=zorder,
                **_endpoint_marker_style(geometry.segment.is_closed, resolved_edgecolor, geometry.segment.is_clipped)
            )[0]
        )
        markers.append(
            ax.plot(
                [geometry.segment.end.x],
                [geometry.segment.end.y],
                [geometry.segment.end.z],
                color=resolved_edgecolor,
                zorder=zorder,
                **_endpoint_marker_style(geometry.segment.is_closed, resolved_edgecolor, geometry.segment.is_clipped)
            )[0]
        )
        if show_unbounded and geometry.segment.is_clipped:
            direction = _segment_arrow_direction_3d(geometry.halfspaces, geometry.segment.midpoint)
            arrow = _arrow_for_point_3d(ax, geometry.segment.midpoint, direction, resolved_edgecolor, resolved_linewidth, zorder)
            if arrow is not None:
                arrows.append(arrow)
        if annotate and annotation_text is not None:
            midpoint = geometry.segment.midpoint
            annotations.append(ax.text(midpoint.x, midpoint.y, midpoint.z, annotation_text, color=resolved_edgecolor))

    elif isinstance(geometry, PointGeometry3D):
        marker = ax.plot(
            [geometry.point.x],
            [geometry.point.y],
            [geometry.point.z],
            color=resolved_edgecolor,
            zorder=zorder,
            label=label,
            **_endpoint_marker_style(geometry.is_closed, resolved_edgecolor, geometry.is_clipped)
        )[0]
        markers.append(marker)
        if show_unbounded and geometry.is_clipped:
            direction = _segment_arrow_direction_3d(geometry.halfspaces, geometry.point)
            arrow = _arrow_for_point_3d(ax, geometry.point, direction, resolved_edgecolor, resolved_linewidth, zorder)
            if arrow is not None:
                arrows.append(arrow)
        if annotate and annotation_text is not None:
            annotations.append(ax.text(geometry.point.x, geometry.point.y, geometry.point.z, annotation_text, color=resolved_edgecolor))

    return PlotResult(
        ax=ax,
        fills=tuple(fills),
        boundaries=tuple(boundaries),
        markers=tuple(markers),
        arrows=tuple(arrows),
        annotations=tuple(annotations),
    )


def _plot_federation_3d_geometry(
        geometry: Union[EmptyGeometry, FederationGeometry3D],
        ax: Any,
        show_unbounded: bool,
        annotate: bool,
        annotation_text: Optional[str],
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

    fills = []  # type: List[Any]
    boundaries = []  # type: List[Any]
    markers = []  # type: List[Any]
    arrows = []  # type: List[Any]
    annotations = []  # type: List[Any]

    if isinstance(geometry, FederationGeometry3D):
        colors = _take_default_colors(ax, len(geometry.dbm_geometries)) if color_mode == "per_dbm" else tuple()
        for index, dbm_geometry in enumerate(geometry.dbm_geometries):
            current_facecolor = facecolor
            current_edgecolor = edgecolor
            current_alpha = alpha
            if color_mode == "per_dbm":
                current_facecolor = colors[index]
                current_edgecolor = colors[index]
                current_alpha = min(0.2, 0.25 if alpha is None else float(alpha))

            dbm_result = _plot_dbm_3d_geometry(
                dbm_geometry,
                ax=ax,
                show_unbounded=show_unbounded,
                annotate=annotate,
                annotation_text=annotation_text,
                facecolor=current_facecolor,
                edgecolor=current_edgecolor,
                alpha=current_alpha,
                linewidth=linewidth,
                linestyle=linestyle,
                label=_line_label(label, index),
                zorder=zorder,
            )
            fills.extend(dbm_result.fills)
            boundaries.extend(dbm_result.boundaries)
            markers.extend(dbm_result.markers)
            arrows.extend(dbm_result.arrows)
            annotations.extend(dbm_result.annotations)

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
        limits: Optional[
            Union[
                Tuple[float, float],
                Tuple[Tuple[float, float], Tuple[float, float]],
                Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
            ]
        ] = None,
        strict_epsilon: Optional[float] = None,
        show_unbounded: bool = True,
        annotate: bool = False,
        annotate_text: Optional[str] = None,
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

    The result is drawn on the provided axes or on a newly created axes when
    ``ax`` is omitted. The default legend label and, when enabled, the default
    annotation text are both derived from ``str(dbm)``.

    :param dbm: DBM to render.
    :type dbm: DBM
    :param ax: Optional matplotlib axes. When omitted, a new axes is created.
    :type ax: Optional[Any]
    :param limits: Optional explicit render limits. Use ``(xmin, xmax)`` for
        1D, ``((xmin, xmax), (ymin, ymax))`` for 2D, and
        ``((xmin, xmax), (ymin, ymax), (zmin, zmax))`` for 3D. When omitted,
        limits are inferred from the DBM bounds and merged with existing axes
        limits when plotting into a reused axes.
    :type limits: Optional[Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]], Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]]]
    :param strict_epsilon: Optional positive epsilon used when shrinking fill
        interiors for strict inequalities.
    :type strict_epsilon: Optional[float]
    :param show_unbounded: Whether clipped unbounded directions should be marked with arrows.
    :type show_unbounded: bool
    :param annotate: Whether to add one text annotation to the plotted geometry.
    :type annotate: bool
    :param annotate_text: Optional annotation text. When omitted and
        ``annotate=True``, ``str(dbm)`` is used. When provided while
        ``annotate`` is not ``True``, plotting emits a warning and enables
        annotations automatically.
    :type annotate_text: Optional[str]
    :param baseline: Vertical baseline used by 1D plots.
    :type baseline: float
    :param facecolor: Optional fill color for 2D and 3D regions. When both
        ``facecolor`` and ``edgecolor`` are omitted, the next matplotlib
        default cycle color is used.
    :type facecolor: Optional[Any]
    :param edgecolor: Optional boundary color. When omitted, it follows the
        fill color or the current axes color cycle.
    :type edgecolor: Optional[Any]
    :param alpha: Optional fill alpha for 2D and 3D regions.
    :type alpha: Optional[float]
    :param linewidth: Optional boundary line width.
    :type linewidth: Optional[float]
    :param linestyle: Optional default line style for closed boundaries.
    :type linestyle: Optional[Any]
    :param label: Optional legend label. When omitted, ``str(dbm)`` is used.
    :type label: Optional[str]
    :param zorder: Optional matplotlib z-order passed to created artists.
    :type zorder: Optional[float]
    :return: Container of created matplotlib artists.
    :rtype: PlotResult
    :raises ImportError: If matplotlib is not installed.
    :raises NotImplementedError: If the DBM is outside the supported ``1..3`` user-clock range.
    :raises ValueError: If ``strict_epsilon`` is non-positive or if ``limits`` are malformed.
    """

    user_dimension = dbm.dimension - 1
    if user_dimension not in {1, 2, 3}:
        raise NotImplementedError("Matplotlib plotting currently supports only 1D, 2D, and 3D DBMs.")

    resolved_label = str(dbm) if label is None else label
    resolved_annotate, resolved_annotation_text = _resolve_annotation_text(annotate, annotate_text, resolved_label)
    plot_limits = limits if limits is not None else _auto_plot_limits_for_dbm(dbm)
    pyplot, _, _ = _require_matplotlib()
    geometry = extract_dbm_geometry(dbm, limits=plot_limits)
    ax = _make_axes(pyplot, ax, user_dimension)
    epsilon = _resolve_strict_epsilon(geometry, strict_epsilon)
    if limits is None:
        plot_limits = _merged_view_limits(ax, user_dimension, baseline, plot_limits)
    _set_default_view(ax, geometry, baseline, view_limits=plot_limits)
    _set_axis_clock_labels(ax, [clock.get_full_name() for clock in dbm.context.clocks], user_dimension)
    if user_dimension == 1:
        return _plot_1d_geometry(
            geometry,  # type: ignore[arg-type]
            ax=ax,
            baseline=float(baseline),
            strict_epsilon=epsilon,
            show_unbounded=show_unbounded,
            annotate=resolved_annotate,
            annotation_text=resolved_annotation_text,
            facecolor=facecolor,
            edgecolor=edgecolor,
            alpha=alpha,
            linewidth=linewidth,
            linestyle=linestyle,
            label=resolved_label,
            zorder=zorder,
        )
    if user_dimension == 2:
        return _plot_dbm_2d_geometry(
            geometry,  # type: ignore[arg-type]
            ax=ax,
            strict_epsilon=epsilon,
            show_unbounded=show_unbounded,
            annotate=resolved_annotate,
            annotation_text=resolved_annotation_text,
            facecolor=facecolor,
            edgecolor=edgecolor,
            alpha=alpha,
            linewidth=linewidth,
            linestyle=linestyle,
            label=resolved_label,
            zorder=zorder,
        )
    return _plot_dbm_3d_geometry(
        geometry,  # type: ignore[arg-type]
        ax=ax,
        show_unbounded=show_unbounded,
        annotate=resolved_annotate,
        annotation_text=resolved_annotation_text,
        facecolor=facecolor,
        edgecolor=edgecolor,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        label=resolved_label,
        zorder=zorder,
    )


def plot_federation(
        federation: Federation,
        ax: Optional[Any] = None,
        *,
        limits: Optional[
            Union[
                Tuple[float, float],
                Tuple[Tuple[float, float], Tuple[float, float]],
                Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
            ]
        ] = None,
        strict_epsilon: Optional[float] = None,
        show_unbounded: bool = True,
        annotate: bool = False,
        annotate_text: Optional[str] = None,
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
    geometry layer. For 3D federations this renders the exact clipped geometry
    of each constituent DBM.

    The default legend label and, when enabled, the default annotation text
    are both derived from ``str(federation)``.

    :param federation: Federation to render.
    :type federation: Federation
    :param ax: Optional matplotlib axes. When omitted, a new axes is created.
    :type ax: Optional[Any]
    :param limits: Optional explicit render limits. Use ``(xmin, xmax)`` for
        1D, ``((xmin, xmax), (ymin, ymax))`` for 2D, and
        ``((xmin, xmax), (ymin, ymax), (zmin, zmax))`` for 3D. When omitted,
        limits are inferred from the federation bounds and merged with
        existing axes limits when plotting into a reused axes.
    :type limits: Optional[Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]], Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]]]
    :param strict_epsilon: Optional positive epsilon used when shrinking fill
        interiors for strict inequalities.
    :type strict_epsilon: Optional[float]
    :param show_unbounded: Whether clipped unbounded directions should be marked with arrows.
    :type show_unbounded: bool
    :param annotate: Whether to add text annotations to the plotted geometry.
    :type annotate: bool
    :param annotate_text: Optional annotation text. When omitted and
        ``annotate=True``, ``str(federation)`` is used. When provided while
        ``annotate`` is not ``True``, plotting emits a warning and enables
        annotations automatically.
    :type annotate_text: Optional[str]
    :param baseline: Vertical baseline used by 1D plots.
    :type baseline: float
    :param color_mode: ``"shared"`` to render federation pieces with one
        visual style, or ``"per_dbm"`` to show individual DBM pieces in
        distinct colors.
    :type color_mode: str
    :param facecolor: Optional fill color for 2D and 3D regions. When both
        ``facecolor`` and ``edgecolor`` are omitted, the next matplotlib
        default cycle color is used.
    :type facecolor: Optional[Any]
    :param edgecolor: Optional boundary color. When omitted, it follows the
        fill color or the current axes color cycle.
    :type edgecolor: Optional[Any]
    :param alpha: Optional fill alpha for 2D and 3D regions.
    :type alpha: Optional[float]
    :param linewidth: Optional boundary line width.
    :type linewidth: Optional[float]
    :param linestyle: Optional default line style for closed boundaries.
    :type linestyle: Optional[Any]
    :param label: Optional legend label. When omitted, ``str(federation)`` is used.
    :type label: Optional[str]
    :param zorder: Optional matplotlib z-order passed to created artists.
    :type zorder: Optional[float]
    :return: Container of created matplotlib artists.
    :rtype: PlotResult
    :raises ImportError: If matplotlib is not installed.
    :raises NotImplementedError: If the federation is outside the supported ``1..3`` user-clock range.
    :raises ValueError: If ``strict_epsilon`` is non-positive, if ``color_mode`` is invalid, or if ``limits`` are malformed.
    """

    user_dimension = len(federation.context.clocks)
    if user_dimension not in {1, 2, 3}:
        raise NotImplementedError("Matplotlib plotting currently supports only 1D, 2D, and 3D federations.")

    resolved_label = str(federation) if label is None else label
    resolved_annotate, resolved_annotation_text = _resolve_annotation_text(annotate, annotate_text, resolved_label)
    plot_limits = limits if limits is not None else _auto_plot_limits_for_federation(federation)
    pyplot, _, _ = _require_matplotlib()
    geometry = extract_federation_geometry(federation, limits=plot_limits)
    ax = _make_axes(pyplot, ax, user_dimension)
    epsilon = _resolve_strict_epsilon(geometry, strict_epsilon)
    if limits is None:
        plot_limits = _merged_view_limits(ax, user_dimension, baseline, plot_limits)
    _set_default_view(ax, geometry, baseline, view_limits=plot_limits)
    _set_axis_clock_labels(ax, [clock.get_full_name() for clock in federation.context.clocks], user_dimension)
    if user_dimension == 1:
        return _plot_1d_geometry(
            geometry,  # type: ignore[arg-type]
            ax=ax,
            baseline=float(baseline),
            strict_epsilon=epsilon,
            show_unbounded=show_unbounded,
            annotate=resolved_annotate,
            annotation_text=resolved_annotation_text,
            facecolor=facecolor,
            edgecolor=edgecolor,
            alpha=alpha,
            linewidth=linewidth,
            linestyle=linestyle,
            label=resolved_label,
            zorder=zorder,
        )
    if user_dimension == 2:
        return _plot_federation_2d_geometry(
            geometry,  # type: ignore[arg-type]
            ax=ax,
            strict_epsilon=epsilon,
            show_unbounded=show_unbounded,
            annotate=resolved_annotate,
            annotation_text=resolved_annotation_text,
            color_mode=color_mode,
            facecolor=facecolor,
            edgecolor=edgecolor,
            alpha=alpha,
            linewidth=linewidth,
            linestyle=linestyle,
            label=resolved_label,
            zorder=zorder,
        )
    return _plot_federation_3d_geometry(
        geometry,  # type: ignore[arg-type]
        ax=ax,
        show_unbounded=show_unbounded,
        annotate=resolved_annotate,
        annotation_text=resolved_annotation_text,
        color_mode=color_mode,
        facecolor=facecolor,
        edgecolor=edgecolor,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        label=resolved_label,
        zorder=zorder,
    )
