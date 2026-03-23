pyudbm.binding.visual
========================================================

.. currentmodule:: pyudbm.binding.visual

.. automodule:: pyudbm.binding.visual


\_\_all\_\_
-----------------------------------------------------

.. autodata:: __all__


EmptyGeometry
-----------------------------------------------------

.. autoclass:: EmptyGeometry
    :members: dimension


Interval1D
-----------------------------------------------------

.. autoclass:: Interval1D
    :members: is_point,lower,upper,lower_closed,upper_closed,lower_clipped,upper_clipped


MultiInterval1D
-----------------------------------------------------

.. autoclass:: MultiInterval1D
    :members: intervals


Point2D
-----------------------------------------------------

.. autoclass:: Point2D
    :members: x,y


HalfSpace2D
-----------------------------------------------------

.. autoclass:: HalfSpace2D
    :members: evaluate,contains,contains_on_closure,is_active,a,b,c,is_strict,is_clip


BoundarySegment2D
-----------------------------------------------------

.. autoclass:: BoundarySegment2D
    :members: length,midpoint,start,end,is_closed,is_clipped


PolygonGeometry2D
-----------------------------------------------------

.. autoclass:: PolygonGeometry2D
    :members: vertices,edges,halfspaces


SegmentGeometry2D
-----------------------------------------------------

.. autoclass:: SegmentGeometry2D
    :members: segment,halfspaces


PointGeometry2D
-----------------------------------------------------

.. autoclass:: PointGeometry2D
    :members: point,is_closed,is_clipped,halfspaces


BoundaryLoop2D
-----------------------------------------------------

.. autoclass:: BoundaryLoop2D
    :members: vertices,signed_area,segments,is_hole


Face2D
-----------------------------------------------------

.. autoclass:: Face2D
    :members: outer,holes


FederationGeometry2D
-----------------------------------------------------

.. autoclass:: FederationGeometry2D
    :members: dbm_geometries,boundary_segments,loops,faces,isolated_segments,isolated_points,limits


PlotResult
-----------------------------------------------------

.. autoclass:: PlotResult
    :members: ax,fills,boundaries,markers,arrows,annotations


extract\_dbm\_geometry
-----------------------------------------------------

.. autofunction:: extract_dbm_geometry


extract\_federation\_geometry
-----------------------------------------------------

.. autofunction:: extract_federation_geometry


plot\_dbm
-----------------------------------------------------

.. autofunction:: plot_dbm


plot\_federation
-----------------------------------------------------

.. autofunction:: plot_federation


