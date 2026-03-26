pyudbm.binding.utap
========================================================

.. currentmodule:: pyudbm.binding.utap

.. automodule:: pyudbm.binding.utap


\_\_all\_\_
-----------------------------------------------------

.. autodata:: __all__


MAPPED\_FIELDS
-----------------------------------------------------

.. autodata:: MAPPED_FIELDS


MAPPED\_FIELD\_NOTES
-----------------------------------------------------

.. autodata:: MAPPED_FIELD_NOTES


UNMAPPED\_FIELDS
-----------------------------------------------------

.. autodata:: UNMAPPED_FIELDS


UNMAPPED\_FIELD\_REASONS
-----------------------------------------------------

.. autodata:: UNMAPPED_FIELD_REASONS


Position
-----------------------------------------------------

.. autoclass:: Position
    :members: start,end,line,column,end_line,end_column,path


Option
-----------------------------------------------------

.. autoclass:: Option
    :members: name,value


Resource
-----------------------------------------------------

.. autoclass:: Resource
    :members: name,value,unit


Expectation
-----------------------------------------------------

.. autoclass:: Expectation
    :members: value_type,status,value,resources


TypeInfo
-----------------------------------------------------

.. autoclass:: TypeInfo
    :members: kind,position,size,text,declaration,is_unknown,is_range,is_integer,is_boolean,is_function,is_function_external,is_clock,is_process,is_process_set,is_location,is_location_expr,is_instance_line,is_branchpoint,is_channel,is_record,is_array,is_scalar,is_diff,is_void,is_cost,is_integral,is_invariant,is_probability,is_guard,is_constraint,is_formula,is_double,is_string


Symbol
-----------------------------------------------------

.. autoclass:: Symbol
    :members: name,type,position


Expression
-----------------------------------------------------

.. autoclass:: Expression
    :members: text,kind,position,type,size,children,is_empty


Diagnostic
-----------------------------------------------------

.. autoclass:: Diagnostic
    :members: message,context,position,line,column,end_line,end_column,path


FeatureFlags
-----------------------------------------------------

.. autoclass:: FeatureFlags
    :members: has_priority_declaration,has_strict_invariants,has_stop_watch,has_strict_lower_bound_on_controllable_edges,has_clock_guard_recv_broadcast,has_urgent_transition,has_dynamic_templates,all_broadcast,sync_used,supports_symbolic,supports_stochastic,supports_concrete


Branchpoint
-----------------------------------------------------

.. autoclass:: Branchpoint
    :members: name,index,position,symbol


Location
-----------------------------------------------------

.. autoclass:: Location
    :members: name,index,position,symbol,name_expression,invariant,exp_rate,cost_rate,is_urgent,is_committed


Edge
-----------------------------------------------------

.. autoclass:: Edge
    :members: index,control,action_name,source_name,source_kind,target_name,target_kind,guard,assign,sync,prob,select_text,select_symbols,select_values


Query
-----------------------------------------------------

.. autoclass:: Query
    :members: formula,comment,options,expectation,location


ParsedQueryExpectation
-----------------------------------------------------

.. autoclass:: ParsedQueryExpectation
    :members: result_kind,status,value,time_ms,mem_kib


ParsedQuery
-----------------------------------------------------

.. autoclass:: ParsedQuery
    :members: line,no,builder,text,quantifier,options,expression,is_smc,declaration,result_type,expectation


Process
-----------------------------------------------------

.. autoclass:: Process
    :members: name,index,position,template_name,parameters,arguments,mapping,argument_count,unbound_count,restricted_symbols


Template
-----------------------------------------------------

.. autoclass:: Template
    :members: name,index,position,parameter,declaration,init_name,type,mode,is_ta,is_instantiated,dynamic,is_defined,locations,branchpoints,edges


ModelDocument
-----------------------------------------------------

.. autoclass:: ModelDocument
    :members: __init__,__repr__,write_xml,dumps,to_xml,dump,global_declarations,before_update_text,after_update_text,channel_priority_texts,global_clock_names,template_clock_names,feature_summary,capability_summary,pretty,load_query,loads_query,parse_query


builtin\_declarations
-----------------------------------------------------

.. autofunction:: builtin_declarations


load\_query
-----------------------------------------------------

.. autofunction:: load_query


loads\_query
-----------------------------------------------------

.. autofunction:: loads_query


parse\_query
-----------------------------------------------------

.. autofunction:: parse_query


load\_xml
-----------------------------------------------------

.. autofunction:: load_xml


loads\_xml
-----------------------------------------------------

.. autofunction:: loads_xml


load\_xta
-----------------------------------------------------

.. autofunction:: load_xta


loads\_xta
-----------------------------------------------------

.. autofunction:: loads_xta


