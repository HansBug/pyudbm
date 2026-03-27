pyudbm.binding.utap\_builder
========================================================

.. currentmodule:: pyudbm.binding.utap_builder

.. automodule:: pyudbm.binding.utap_builder


\_\_all\_\_
-----------------------------------------------------

.. autodata:: __all__


ModelBuilder
-----------------------------------------------------

.. autoclass:: ModelBuilder
    :members: __init__,from_document,declaration,set_declarations,clock,chan,integer,template,update_template,edit_template,remove_template,process,update_process,remove_process,system,query,update_query,remove_query,to_spec,build


TemplateBuilder
-----------------------------------------------------

.. autoclass:: TemplateBuilder
    :members: __init__,__enter__,__exit__,declaration,set_declarations,location,update_location,remove_location,edge,update_edge,remove_edge,end


build\_model
-----------------------------------------------------

.. autofunction:: build_model


ModelSpec
-----------------------------------------------------

.. autoclass:: ModelSpec


TemplateSpec
-----------------------------------------------------

.. autoclass:: TemplateSpec


LocationSpec
-----------------------------------------------------

.. autoclass:: LocationSpec


EdgeSpec
-----------------------------------------------------

.. autoclass:: EdgeSpec


QuerySpec
-----------------------------------------------------

.. autoclass:: QuerySpec
