pyudbm.binding.ucdd
========================================================

.. currentmodule:: pyudbm.binding.ucdd

.. automodule:: pyudbm.binding.ucdd


\_\_all\_\_
-----------------------------------------------------

.. autodata:: __all__


OP\_AND
-----------------------------------------------------

.. autodata:: OP_AND


OP\_XOR
-----------------------------------------------------

.. autodata:: OP_XOR


TYPE\_BDD
-----------------------------------------------------

.. autodata:: TYPE_BDD


TYPE\_CDD
-----------------------------------------------------

.. autodata:: TYPE_CDD


CDDLevelInfo
-----------------------------------------------------

.. autoclass:: CDDLevelInfo
    :members: level,type,clock1,clock2,diff


CDDClock
-----------------------------------------------------

.. autoclass:: CDDClock
    :members: __init__,__repr__,get_full_name,__hash__,__sub__,__le__,__ge__,__lt__,__gt__,__eq__,__ne__


CDDVariableDifference
-----------------------------------------------------

.. autoclass:: CDDVariableDifference
    :members: __init__,__le__,__ge__,__lt__,__gt__,__eq__,__ne__


CDDBool
-----------------------------------------------------

.. autoclass:: CDDBool
    :members: __init__,__repr__,__hash__,get_full_name,as_cdd,__invert__,__and__,__rand__,__or__,__ror__,__xor__,__rxor__,__sub__,__rsub__,__eq__,__ne__


CDDContext
-----------------------------------------------------

.. autoclass:: CDDContext
    :members: __init__,from_context,base_context,__getitem__,__hash__,clock,bool,level_info,all_level_info,bool_name_for_level,true,false


BDDTraceSet
-----------------------------------------------------

.. autoclass:: BDDTraceSet
    :members: __init__,__len__,__iter__,to_rows,to_dicts


CDDExtraction
-----------------------------------------------------

.. autoclass:: CDDExtraction
    :members: __init__,to_federation,has_bdd_part


CDD
-----------------------------------------------------

.. autoclass:: CDD
    :members: __init__,true,false,upper,lower,interval,bddvar,bddnvar,from_dbm,from_federation,copy,__repr__,__and__,__rand__,__or__,__ror__,__sub__,__rsub__,__xor__,__rxor__,__invert__,__eq__,__ne__,ite,apply,apply_reduce,reduce,reduce2,equiv,nodecount,edgecount,is_bdd,is_true,is_false,remove_negative,delay,past,delay_invariant,predt,contains_dbm,extract_dbm,extract_bdd,extract_bdd_and_dbm,bdd_traces,apply_reset,transition,transition_back,transition_back_past,to_federation


