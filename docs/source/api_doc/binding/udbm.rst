pyudbm.binding.udbm
========================================================

.. currentmodule:: pyudbm.binding.udbm

.. automodule:: pyudbm.binding.udbm


\_\_all\_\_
-----------------------------------------------------

.. autodata:: __all__


LOGGER
-----------------------------------------------------

.. autodata:: LOGGER


Clock
-----------------------------------------------------

.. autoclass:: Clock
    :members: __init__,__repr__,__sub__,__le__,__ge__,__lt__,__gt__,__eq__,__ne__,__hash__,getFullName


Valuation
-----------------------------------------------------

.. autoclass:: Valuation
    :members: __init__,__setitem__,check


IntValuation
-----------------------------------------------------

.. autoclass:: IntValuation
    :members: __setitem__


FloatValuation
-----------------------------------------------------

.. autoclass:: FloatValuation
    :members: __setitem__


VariableDifference
-----------------------------------------------------

.. autoclass:: VariableDifference
    :members: __init__,__le__,__ge__,__lt__,__gt__,__eq__,__ne__


Constraint
-----------------------------------------------------

.. autoclass:: Constraint
    :members: __init__


Federation
-----------------------------------------------------

.. autoclass:: Federation
    :members: __init__,__str__,copy,__and__,__iand__,__or__,__ior__,__add__,__iadd__,__sub__,__isub__,up,down,reduce,freeClock,setZero,hasZero,setInit,convexHull,__eq__,__ne__,__le__,__ge__,__lt__,__gt__,intern,predt,contains,updateValue,resetValue,getSize,extrapolateMaxBounds,isZero,isEmpty,__hash__,hash


Context
-----------------------------------------------------

.. autoclass:: Context
    :members: __init__,setName,__getitem__,getZeroFederation


