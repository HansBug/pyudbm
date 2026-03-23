# Matplotlib Visualization Plan For DBM And Federation

## Purpose

This document turns the current design discussion around DBM / federation visualization into a concrete implementation plan for `pyudbm`.

The immediate goal is not to implement the feature in this document, but to define:

1. the user-facing API shape,
2. the internal geometry pipeline,
3. the exact boundary and unbounded-region semantics,
4. the dependency and packaging strategy,
5. the staged delivery plan and test strategy.

The plan is written against the current repository state:

- high-level Python API in `pyudbm/binding/udbm.py`
- immutable `DBM` snapshots via `Federation.to_dbm_list()`
- DBM cell access through `raw()`, `bound()`, `is_strict()`, `is_infinity()`, and `to_matrix()`

This is important because the visualization work should layer on top of the current wrapper instead of inventing a second semantic representation.

## Current Technical Baseline

The current Python layer already exposes enough information to reconstruct exact zone geometry without touching the native submodules:

- `Federation.to_dbm_list()` exports detached DBM snapshots.
- `DBM.clock_names` gives the matrix headers.
- `DBM.bound(i, j)` decodes DBM bounds.
- `DBM.is_strict(i, j)` tells whether a bound is open.
- `DBM.is_infinity(i, j)` tells whether a bound is unbounded.
- `DBM.to_string(full=True)` already demonstrates that the Python layer sees the closed DBM, not just the syntactic source constraint set.

That means the visualization feature can be implemented entirely in safe wrapper-owned files under `pyudbm/` and `test/`, without modifying `UDBM/` or `UUtils/`.

## Scope

### In scope

- Matplotlib-based plotting support for `DBM` and `Federation`
- 1D, 2D, and 3D visualization only
- explicit handling of:
  - closed boundaries
  - open boundaries
  - bounded regions
  - unbounded regions
  - degenerate results such as points, segments, rays, faces, and empty sets
- optional dependency design so matplotlib is not required for normal package use
- artist-oriented integration compatible with the normal matplotlib workflow

### Out of scope

- visualization for dimensions above 3
- automatic projection from high-dimensional zones into lower dimensions
- interactive GUI tooling
- animation API
- non-matplotlib backends
- changing UDBM semantics or adding new symbolic operations

For any DBM or federation whose user-clock dimension is outside `1..3`, the plotting API should raise a clear exception rather than guessing.

## Design Principles

### 1. Use exact geometry, not raster approximations

The visualization pipeline should reconstruct half-spaces from DBM constraints and compute exact clipped geometric objects.

The implementation should not depend on:

- dense sampling over a grid
- image masks
- contour reconstruction from boolean membership

Those approaches would blur open versus closed boundaries, behave poorly for thin or degenerate regions, and make unbounded zones hard to explain.

### 2. Separate geometry extraction from rendering

The implementation should be split into two layers:

- geometry layer:
  - convert `DBM` or `Federation` into internal geometric primitives
  - no matplotlib dependency in the core data transformation code
- rendering layer:
  - convert those primitives into matplotlib artists
  - handle styling, axes integration, legends, and draw order

This split keeps the code testable and avoids locking geometry logic to matplotlib internals.

### 3. Preserve existing UDBM semantics

The plotting layer must reflect the current symbolic meaning of the DBM or federation.

It must not silently:

- convexify a federation
- reduce away DBMs unless the caller did so
- reinterpret open boundaries as closed
- truncate infinity without marking that truncation visually

### 4. Fit normal matplotlib usage

The plotting API should behave like normal matplotlib helpers:

- accept an existing `ax`
- create one only when needed
- return useful artists or an artist container
- allow styling through familiar keyword arguments
- not call `plt.show()`

## Proposed Public API

### Module layout

Add a dedicated plotting namespace instead of mixing matplotlib imports into the base package import path:

- `pyudbm/plotting/__init__.py`
- `pyudbm/plotting/_geometry.py`
- `pyudbm/plotting/_matplotlib.py`

Optional thin convenience hooks can later be added to `DBM` and `Federation`, but the first public contract should live in the plotting module.

### Main entry points

Recommended first-pass public functions:

```python
def plot_dbm(dbm, ax=None, **kwargs):
    ...


def plot_federation(federation, ax=None, **kwargs):
    ...
```

Second-stage convenience methods may forward into these functions:

```python
DBM.plot(...)
Federation.plot(...)
```

Those methods should lazy-import matplotlib and raise an informative import error when the optional dependency is missing.

### Suggested keyword parameters

The first public API should stay small but cover the important control points.

Common parameters:

- `ax=None`
- `facecolor=None`
- `edgecolor=None`
- `alpha=None`
- `linewidth=None`
- `linestyle=None`
- `label=None`
- `zorder=None`

Visualization-specific parameters:

- `limits=None`
  - render box or axis limits used for clipping unbounded regions
- `strict_epsilon=None`
  - rendering-only inward offset used to distinguish open boundaries from filled interiors
- `show_unbounded=True`
  - whether to add unbounded-region indicators such as arrows or boundary markers
- `color_mode="shared"`
  - one style for the whole federation or per-DBM color cycling
- `annotate=False`
  - optional lightweight annotation of DBM index or textual summary

Dimension-specific parameters:

- 1D:
  - `baseline=0.0`
- 2D:
  - `xclock=None`, `yclock=None`
- 3D:
  - `xclock=None`, `yclock=None`, `zclock=None`

The axis-selection parameters are optional for the initial implementation if we keep the simpler rule:

- dimension 1 means the only user clock is plotted on the x-axis
- dimension 2 means the two user clocks define `(x, y)`
- dimension 3 means the three user clocks define `(x, y, z)`

That is the simplest first version and best matches the current scope restriction.

### Return value

Do not return only `ax`. Return a small artist container object instead.

Recommended shape:

```python
class PlotResult:
    ax: Any
    fills: tuple
    boundaries: tuple
    markers: tuple
    indicators: tuple
```

This allows callers to post-process artists in the normal matplotlib way.

## Packaging And Dependency Plan

Matplotlib should remain optional.

### Dependency files

Add a new optional requirements file:

- `requirements-plot.txt`

Initial content should likely be:

```text
matplotlib
```

The current `setup.py` already turns `requirements-*.txt` into `extras_require`, so this file will automatically produce an install extra similar to:

```bash
pip install .[plot]
```

### Import policy

The base import path:

```python
import pyudbm
```

must not import matplotlib.

Only plotting-specific code paths should import matplotlib, preferably inside plotting functions or inside the plotting module itself.

### Error message policy

When matplotlib is missing and the user calls plotting code, raise `ImportError` with a direct message such as:

```text
Matplotlib plotting support is optional. Install pyudbm with the 'plot' extra or install matplotlib manually.
```

## Internal Architecture

### Geometry data model

The geometry layer should define small explicit internal objects rather than passing raw tuples around everywhere.

Suggested internal shapes:

- `Interval1D`
- `Ray1D`
- `Point1D`
- `Polygon2D`
- `Segment2D`
- `Point2D`
- `Polyhedron3D`
- `Face3D`
- `Segment3D`
- `Point3D`
- `EmptyGeometry`

Each geometry object should carry enough metadata to preserve rendering semantics:

- coordinates
- per-boundary openness / closedness
- whether a face or edge comes from clip-box truncation
- whether a boundary is genuinely part of the zone

This matters because the same plotted segment may mean very different things:

- a real closed zone boundary,
- a real open zone boundary,
- a synthetic clipping boundary introduced only for display.

### Geometry pipeline overview

The pipeline should look like this:

1. Normalize input:
   - `DBM` stays as one convex zone
   - `Federation` becomes a list of DBMs via `to_dbm_list()`
2. Determine plotting dimension from context clock count
3. Determine render box
4. Convert DBM matrix cells into half-space inequalities
5. Clip an initial bounding shape against all finite half-spaces
6. Record strictness and truncation metadata
7. Convert geometry into matplotlib artists

## Mapping DBM Constraints To Plot Half-Spaces

For a DBM over user clocks `x1, ..., xn` with reference clock `x0 = 0`, the cell `(i, j)` means:

`xi - xj < c` or `xi - xj <= c`

with infinity meaning no finite upper bound.

This directly yields affine half-spaces in `R^n`.

Examples:

- `(x, 0) <= 5` becomes `x <= 5`
- `(0, x) <= -2` becomes `x >= 2`
- `(x, y) < 3` becomes `x - y < 3`
- `(y, x) <= 7` becomes `y - x <= 7`

Only finite non-diagonal constraints need to contribute half-spaces.

The geometry layer should therefore iterate over all `(i, j)` with:

- `i != j`
- finite bound

and translate them into affine constraints over the visible coordinates.

No dependence on `to_min_dbm()` is required for the first version.

That is a deliberate design choice:

- the closed DBM matrix is already exposed and easy to consume
- the packed min-DBM export is harder to decode and not needed for correctness
- redundant constraints are acceptable in a clipping pipeline

## Dimension-Specific Plan

### 1D

#### Semantics

A 1D DBM denotes one convex subset of the non-negative real line over a single clock.

Typical cases:

- closed interval: `0 <= x <= 5`
- open interval: `1 < x < 4`
- half-line: `x >= 0`, `x > 2`, `x <= 7`
- point: `x == 3`
- empty set

#### Geometry extraction

Recover:

- lower bound from `(0, x)`
- upper bound from `(x, 0)`

Use strictness from the corresponding DBM cells.

If either side is infinite, interpret as a ray.

#### Rendering

Recommended style:

- interval interior:
  - horizontal line segment or narrow filled strip
- closed endpoint:
  - filled marker
- open endpoint:
  - hollow marker
- unbounded side:
  - arrow pointing outward

This is clearer than a pure filled rectangle and keeps open versus closed semantics visible.

### 2D

#### Semantics

A 2D DBM is a convex zone in the plane over two clocks.

The zone is the intersection of finitely many half-planes:

- axis-aligned bounds from `x` and `y`
- diagonal bounds from `x - y` and `y - x`

#### Geometry extraction

Start with a finite render box:

- either explicitly provided by `limits`
- or inferred from finite DBM bounds plus padding
- or fallback to a default box if the zone is heavily unbounded

Represent the current candidate region as a convex polygon.

Apply polygon clipping sequentially for each finite DBM half-plane:

- weak inequality keeps the boundary as closed
- strict inequality marks the supporting line as open

The clipping algorithm can be a half-plane version of Sutherland-Hodgman because the current polygon remains convex throughout.

#### Degenerate outputs

The result may collapse to:

- polygon
- segment
- point
- empty set

The renderer must handle those explicitly instead of assuming positive area.

#### Rendering

Use separate artists for:

- interior fill
- true boundaries
- synthetic clip-box edges
- unbounded indicators

Recommended semantics:

- true closed boundary:
  - solid line
- true open boundary:
  - dashed line
- synthetic clip-box boundary:
  - very faint line or none
- unbounded direction:
  - arrow or hatched edge indicator attached to the clipped side

### 3D

#### Semantics

A 3D DBM is a convex polyhedral zone over three clocks.

#### Geometry extraction

Start from a finite axis-aligned render box in `R^3`.

Clip that box by each finite affine half-space derived from the DBM.

Represent the current shape as:

- vertices
- faces
- face metadata

The initial implementation does not need a general-purpose computational-geometry package.

But it does need a robust internal convex-polyhedron clipping routine.

That can be written specifically for convex half-space clipping:

1. keep explicit faces,
2. clip each face polygon against the plane,
3. accumulate intersection edges,
4. reconstruct the new clipping face when a plane cuts the polyhedron.

#### Rendering

Use `mpl_toolkits.mplot3d.art3d.Poly3DCollection` for filled faces and plain line artists for emphasized edges.

Recommended initial rendering strategy:

- low alpha faces
- stronger visible boundary edges
- dashed style for open faces
- optional arrows or textual indicators for truncated unbounded directions

3D open-boundary semantics are inherently less visually obvious than 1D and 2D, so explicit legends and documentation will matter.

## Open And Closed Boundary Semantics

This is the most important semantic requirement and must be designed explicitly.

### Problem

A filled patch in matplotlib visually suggests a closed region, even when a DBM boundary is strict.

For example:

- `x < 5`
- `x - y < 3`

should not look identical to:

- `x <= 5`
- `x - y <= 3`

### Proposed rule

Use two separate mechanisms:

1. boundary styling
2. rendering-only interior shrink for strict constraints

### Boundary styling

- closed boundary:
  - solid edge
- open boundary:
  - dashed edge

This is the primary visible distinction.

### Interior shrink

When a region is filled, the fill should be computed using a tiny inward offset for strict constraints:

- `a^T x < b` becomes `a^T x <= b - epsilon_render`

This epsilon is only for the rendered fill, not for semantic geometry reporting.

Benefits:

- the fill no longer visually includes the open boundary
- the true boundary line can still be drawn at the real mathematical location

The default `strict_epsilon` should be scale-aware, derived from axis span rather than fixed globally.

## Unbounded Region Semantics

This is the second major semantic requirement.

### Problem

Matplotlib axes are finite, but zones may be unbounded.

Examples:

- `x >= 0`
- `x - y < 3`
- `x >= 1 and y >= 1`

If such a zone is simply clipped to current axis limits with no annotation, the user cannot tell whether:

- the region is truly bounded, or
- the picture is just cut off.

### Proposed rule

All rendering should happen inside a finite render box, but truncation must be visually marked.

### Render box

`limits` should support:

- 1D:
  - `(xmin, xmax)`
- 2D:
  - `((xmin, xmax), (ymin, ymax))`
- 3D:
  - `((xmin, xmax), (ymin, ymax), (zmin, zmax))`

If `limits` is omitted:

- infer finite limits from visible finite DBM bounds when possible
- add padding
- if a direction is fully unbounded, use a conservative default span centered on known finite structure or the origin

### Truncation metadata

During clipping, record whether a visible boundary segment or face lies on the render box only because the true zone extends farther.

### Visual indicators

Recommended first version:

- 1D:
  - arrowheads on unbounded side
- 2D:
  - arrows attached near the clipped edge midpoint and pointing outward
- 3D:
  - a lighter first version may use boundary-edge markers or a note in the legend, because arrow placement in 3D is harder to read

Synthetic clip-box edges should not use the same visual weight as true zone boundaries.

## Federation Rendering Plan

`Federation` should be rendered as the exact union of its DBM components, not as a convex hull.

### Default behavior

For `plot_federation(fed, ...)`:

1. obtain `dbms = fed.to_dbm_list()`
2. render each DBM separately
3. combine the artists into one `PlotResult`

### Style policy

Initial supported modes:

- `color_mode="shared"`
  - one face/edge style for all DBMs
- `color_mode="per_dbm"`
  - cycle colors across DBMs

The default should be `"shared"` because it better communicates “one federation, many convex pieces”.

### Overlap policy

Do not attempt geometric boolean union between DBMs in the first version.

Reasons:

- federations are already the correct semantic union object
- exact polygon / polyhedron union is a separate geometry problem
- simply layering convex components with controlled alpha is enough for an initial exact and useful rendering

## Error Model

The plotting layer should fail explicitly on unsupported or nonsensical inputs.

Recommended errors:

- `ImportError`
  - matplotlib not installed
- `TypeError`
  - object is not `DBM` or `Federation`
- `ValueError`
  - user-clock dimension not in `1..3`
- `ValueError`
  - malformed `limits`
- `RuntimeError`
  - internal geometry clipping produced an inconsistent convex object

Error messages should say whether the dimension count includes the implicit zero clock.

The user-facing rule should be documented as:

- supported visible dimensions are the number of user clocks, not DBM matrix size

## Proposed File Layout

Recommended new files:

- `pyudbm/plotting/__init__.py`
- `pyudbm/plotting/_geometry.py`
- `pyudbm/plotting/_matplotlib.py`
- `test/plotting/__init__.py`
- `test/plotting/test_geometry.py`
- `test/plotting/test_matplotlib.py`
- `requirements-plot.txt`

Potential later edits:

- `pyudbm/__init__.py`
- `pyudbm/binding/__init__.py`
- `pyudbm/binding/udbm.py`
- `setup.py`

The first version does not need to expose plotting from the root package if we want to keep the public surface narrower.

## Implementation Phases

### Phase 1: geometry foundation

Goal:

- implement internal geometry extraction for 1D and 2D without matplotlib dependency

Tasks:

- define internal geometry classes
- implement DBM-to-half-space extraction
- implement render-box handling
- implement 1D interval / ray extraction
- implement 2D convex polygon clipping
- preserve strictness and clip-origin metadata

Success criteria:

- pure-Python tests can validate geometry objects from representative DBMs

### Phase 2: matplotlib rendering for 1D and 2D

Goal:

- expose stable user-facing plotting helpers for the most practical cases first

Tasks:

- add lazy matplotlib import path
- render 1D intervals, rays, and points
- render 2D polygons, segments, and points
- add open / closed boundary styles
- add unbounded indicators
- return `PlotResult`

Success criteria:

- user can plot common zones and federations on provided axes
- open / closed and bounded / unbounded distinctions are visible

### Phase 3: 3D geometry and rendering

Goal:

- extend the same semantics to 3D

Tasks:

- implement convex polyhedron clipping
- render with `Poly3DCollection`
- support degenerate 3D outputs
- add unbounded truncation indication

Success criteria:

- basic 3-clock zones render correctly
- unsupported dimensions above 3 still fail explicitly

### Phase 4: convenience API and polish

Goal:

- make the feature feel native inside `pyudbm`

Tasks:

- optional `DBM.plot()` and `Federation.plot()`
- better defaults for color and legend behavior
- docstring examples
- package-level export decisions

## Test Strategy

### Unit tests for geometry

The geometry layer should be tested independently from matplotlib.

Representative cases:

- 1D:
  - `x == 0`
  - `x < 5`
  - `x <= 5`
  - `x > 2`
  - `x >= 0`
  - empty zone
- 2D:
  - bounded rectangle-like zone
  - bounded diagonal zone
  - unbounded wedge
  - line segment from equality constraints
  - point from `x == c and y == d`
  - empty zone
- 3D:
  - bounded box-like zone
  - diagonal-face bounded zone
  - unbounded polyhedron clipped by render box

Assertions should cover:

- coordinates
- openness flags
- truncation flags
- degenerate-object classification

### Rendering tests

Rendering tests should avoid brittle pixel-perfect image comparison in the first version.

Prefer asserting:

- returned artist container types
- number of artists created
- linestyle choice for open vs closed boundaries
- presence of indicators for unbounded regions
- compatibility with caller-provided `ax`

Image-based regression tests can be considered later if the repo wants them.

## Documentation Plan

When implementation begins, documentation should include:

- plotting API docstrings
- one or two examples in a future public tutorial or README section
- explicit explanation that:
  - higher-than-3D plotting is unsupported
  - matplotlib is optional
  - unbounded regions are shown through clipping plus indicators

The docs should not oversell 3D semantics. If the first 3D version has visual tradeoffs, that should be stated plainly.

## Risks And Tradeoffs

### 1. Strict-boundary rendering is visually subtle

Dashed edges alone are not enough, especially with filled polygons.

Mitigation:

- keep separate fill and boundary artists
- use inward render epsilon for strict fills

### 2. Unbounded-region inference depends on finite render limits

Any finite figure necessarily clips infinity.

Mitigation:

- make clipping explicit in API and visuals
- record synthetic clip boundaries separately

### 3. 3D implementation complexity is much higher than 2D

Mitigation:

- do not block 1D / 2D delivery on 3D
- stage 3D after the 2D pipeline is stable

### 4. Federation union rendering can look visually dense

Mitigation:

- default to shared color with moderate alpha
- do not attempt exact boolean union initially

## Recommended Immediate Next Step

When implementation starts, begin with Phase 1 and Phase 2 only:

- geometry extraction
- 1D plotting
- 2D plotting
- optional dependency plumbing
- targeted tests

That yields the highest value with the lowest geometry complexity, and it validates the core semantic decisions about:

- open vs closed boundaries
- exact vs truncated infinity
- DBM vs federation layering

3D should be treated as a separate follow-up milestone even if the API is designed from day one to reserve that capability.
