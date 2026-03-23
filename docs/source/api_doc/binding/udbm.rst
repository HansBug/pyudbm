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


DBM
-----------------------------------------------------

.. autoclass:: DBM
    :members: __init__,dimension,shape,clock_names,to_string,raw,bound,is_strict,is_infinity,to_matrix,format_matrix,to_min_dbm,__str__,__repr__


Clock
-----------------------------------------------------

.. autoclass:: Clock
    :members: __init__,__repr__,__sub__,__le__,__ge__,__lt__,__gt__,__eq__,__ne__,__hash__,get_full_name


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
    :members: __init__,__str__,copy,to_dbm_list,__and__,__iand__,__or__,__ior__,__add__,__iadd__,__sub__,__isub__,up,down,reduce,free_clock,set_zero,has_zero,set_init,convex_hull,__eq__,__ne__,__le__,__ge__,__lt__,__gt__,intern,predt,contains,update_value,reset_value,get_size,extrapolate_max_bounds,is_zero,is_empty,__hash__,hash


Context
-----------------------------------------------------

.. autoclass:: Context
    :members: __init__,set_name,__getitem__,get_zero_federation


