"""
Lightweight Python-first UTAP model builder and spec layer.

This module provides two related public entry points:

* chainable builders for interactive authoring;
* frozen spec dataclasses for programmatic generation and snapshots.

Both flows normalize into one shared payload and then delegate the final
native document construction to the official UTAP-backed helper exposed by
``pyudbm.binding._utap``.
"""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple, Union

from ._utap import _build_model as _native_build_model
from .utap import Expectation, ModelDocument, Option, Query

__all__ = [
    "EdgeSpec",
    "LocationSpec",
    "ModelBuilder",
    "ModelSpec",
    "QuerySpec",
    "TemplateBuilder",
    "TemplateSpec",
    "build_model",
]


@dataclass(frozen=True)
class LocationSpec:
    """
    Immutable specification of one template location.

    :param name: Location name.
    :type name: str
    :param initial: Whether this is the initial location.
    :type initial: bool
    :param invariant: Optional invariant text.
    :type invariant: str
    :param urgent: Whether the location is urgent.
    :type urgent: bool
    :param committed: Whether the location is committed.
    :type committed: bool

    Example::

        >>> from pyudbm.binding.utap_builder import LocationSpec
        >>> LocationSpec("Init", initial=True).initial
        True
    """

    name: str
    initial: bool = False
    invariant: str = ""
    urgent: bool = False
    committed: bool = False


@dataclass(frozen=True)
class EdgeSpec:
    """
    Immutable specification of one template edge.

    ``guard``, ``sync``, and ``update`` are the normalized textual fields
    ultimately consumed by the native builder.

    :param source: Source location name.
    :type source: str
    :param target: Target location name.
    :type target: str
    :param guard: Optional normalized guard text.
    :type guard: str
    :param sync: Optional normalized synchronisation text.
    :type sync: str
    :param update: Optional normalized assignment text.
    :type update: str

    Example::

        >>> from pyudbm.binding.utap_builder import EdgeSpec
        >>> EdgeSpec("Idle", "Busy", sync="tick!").sync
        'tick!'
    """

    source: str
    target: str
    guard: str = ""
    sync: str = ""
    update: str = ""


@dataclass(frozen=True)
class QuerySpec:
    """
    Immutable specification of one model query.

    :param formula: Query formula text.
    :type formula: str
    :param comment: Optional query comment text.
    :type comment: str
    :param options: Query-local option entries.
    :type options: Tuple[Option, ...]
    :param expectation: Optional expectation metadata.
    :type expectation: Expectation or None
    :param location: Optional query location text.
    :type location: str

    Example::

        >>> from pyudbm.binding.utap_builder import QuerySpec
        >>> QuerySpec("A[] not deadlock").formula
        'A[] not deadlock'
    """

    formula: str
    comment: str = ""
    options: Tuple[Option, ...] = ()
    expectation: Optional[Expectation] = None
    location: str = ""


@dataclass(frozen=True)
class TemplateSpec:
    """
    Immutable specification of one template.

    :param name: Template name.
    :type name: str
    :param parameters: Optional raw parameter text.
    :type parameters: str
    :param declarations: Raw local declaration blocks.
    :type declarations: Tuple[str, ...]
    :param locations: Template locations.
    :type locations: Tuple[LocationSpec, ...]
    :param edges: Template edges.
    :type edges: Tuple[EdgeSpec, ...]

    Example::

        >>> from pyudbm.binding.utap_builder import LocationSpec, TemplateSpec
        >>> spec = TemplateSpec("P", locations=(LocationSpec("Init", initial=True),))
        >>> spec.name
        'P'
    """

    name: str
    parameters: str = ""
    declarations: Tuple[str, ...] = ()
    locations: Tuple[LocationSpec, ...] = ()
    edges: Tuple[EdgeSpec, ...] = ()


@dataclass(frozen=True)
class ModelSpec:
    """
    Immutable specification of one UTAP model.

    ``processes`` uses tuples of the shape
    ``(process_name, template_name, arguments)`` where ``arguments`` is a
    tuple of raw textual argument expressions.

    :param declarations: Raw global declaration blocks.
    :type declarations: Tuple[str, ...]
    :param templates: Template specifications.
    :type templates: Tuple[TemplateSpec, ...]
    :param processes: Process-instantiation tuples.
    :type processes: Tuple[Tuple[str, str, Tuple[str, ...]], ...]
    :param system_process_names: Process names listed in the system line.
    :type system_process_names: Tuple[str, ...]
    :param queries: Query specifications.
    :type queries: Tuple[QuerySpec, ...]

    Example::

        >>> from pyudbm.binding.utap_builder import LocationSpec, ModelSpec, TemplateSpec
        >>> spec = ModelSpec(
        ...     declarations=("clock x;",),
        ...     templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True),)),),
        ...     processes=(("P1", "P", ()),),
        ...     system_process_names=("P1",),
        ... )
        >>> spec.system_process_names
        ('P1',)
    """

    declarations: Tuple[str, ...] = ()
    templates: Tuple[TemplateSpec, ...] = ()
    processes: Tuple[Tuple[str, str, Tuple[str, ...]], ...] = ()
    system_process_names: Tuple[str, ...] = ()
    queries: Tuple[QuerySpec, ...] = ()


@dataclass
class _LocationState:
    name: str
    invariant: str
    urgent: bool
    committed: bool
    initial: bool


@dataclass
class _EdgeState:
    source: str
    target: str
    guard: str
    sync: str
    update: str


@dataclass
class _TemplateState:
    name: str
    parameters: str
    declaration_lines: List[str] = field(default_factory=list)
    locations: List[_LocationState] = field(default_factory=list)
    edges: List[_EdgeState] = field(default_factory=list)
    initial_location: Optional[str] = None


@dataclass
class _ProcessState:
    name: str
    template_name: str
    arguments: Tuple[str, ...]


def _require_text(field_name: str, value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("{0} must be a string".format(field_name))

    text = value.strip()
    if not text:
        raise ValueError("{0} must not be empty".format(field_name))
    return text


def _normalize_optional_text(field_name: str, value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("{0} must be a string".format(field_name))
    return value.strip()


def _stringify_expression(field_name: str, value: object) -> str:
    if isinstance(value, str):
        text = value.strip()
    else:
        text = str(value).strip()
    if not text:
        raise ValueError("{0} must not be empty".format(field_name))
    return text


def _normalize_names(kind: str, names: Sequence[str]) -> Tuple[str, ...]:
    if not names:
        raise ValueError("{0} requires at least one name".format(kind))

    normalized = tuple(_require_text("{0} name".format(kind), item) for item in names)
    if len(set(normalized)) != len(normalized):
        raise ValueError("{0} names must be unique within one call".format(kind))
    return normalized


def _normalize_options(options: Iterable[Union[Option, Tuple[str, str]]]) -> Tuple[Option, ...]:
    result = []
    for item in options:
        if isinstance(item, Option):
            result.append(item)
        else:
            try:
                name, value = item
            except (TypeError, ValueError):
                raise TypeError("query options must be Option instances or (name, value) pairs")
            result.append(Option(_require_text("option name", name), _require_text("option value", value)))
    return tuple(result)


def _normalize_expectation(expectation: Optional[Expectation]) -> Expectation:
    if expectation is None:
        return Expectation("Symbolic", "True", "", ())
    if not isinstance(expectation, Expectation):
        raise TypeError("expectation must be an Expectation instance or None")
    return expectation


def _normalize_reset(reset: object) -> Tuple[Tuple[str, str], ...]:
    if reset in (None, ()):
        return ()

    if isinstance(reset, MappingABC):
        items = reset.items()
    elif isinstance(reset, str):
        raise TypeError("reset must be a mapping or an iterable of (name, value) pairs")
    else:
        items = reset

    result = []
    for item in items:
        try:
            name, value = item
        except (TypeError, ValueError):
            raise TypeError("reset must contain (name, value) pairs")
        result.append((_require_text("reset name", name), _stringify_expression("reset value", value)))
    return tuple(result)


def _render_reset(reset: object) -> str:
    entries = _normalize_reset(reset)
    if not entries:
        return ""
    return ", ".join("{0} = {1}".format(name, value) for name, value in entries)


def _normalize_guard_text(guard: str, when: str) -> str:
    normalized_guard = _normalize_optional_text("guard", guard)
    normalized_when = _normalize_optional_text("when", when)
    if normalized_guard and normalized_when and normalized_guard != normalized_when:
        raise ValueError("edge guard is ambiguous: use either 'guard' or 'when'")
    return normalized_guard or normalized_when


def _normalize_sync_text(sync: str, send: str, recv: str) -> str:
    normalized_sync = _normalize_optional_text("sync", sync)
    normalized_send = _normalize_optional_text("send", send)
    normalized_recv = _normalize_optional_text("recv", recv)

    if normalized_send and normalized_recv:
        raise ValueError("edge sync is ambiguous: use only one of 'send' or 'recv'")

    derived_sync = ""
    if normalized_send:
        derived_sync = "{0}!".format(normalized_send)
    elif normalized_recv:
        derived_sync = "{0}?".format(normalized_recv)

    if normalized_sync and derived_sync and normalized_sync != derived_sync:
        raise ValueError("edge sync is ambiguous: use either 'sync' or 'send'/'recv'")
    return normalized_sync or derived_sync


def _normalize_update_text(update: str, reset: object) -> str:
    normalized_update = _normalize_optional_text("update", update)
    rendered_reset = _render_reset(reset)
    if normalized_update and rendered_reset and normalized_update != rendered_reset:
        raise ValueError("edge update is ambiguous: use either 'update' or 'reset'")
    return normalized_update or rendered_reset


def _normalize_process_arguments(arguments: Iterable[object]) -> Tuple[str, ...]:
    if isinstance(arguments, (str, bytes)):
        raise TypeError("process arguments must be an iterable of argument expressions, not a string")

    try:
        iterator = iter(arguments)
    except TypeError:
        raise TypeError("process arguments must be an iterable of argument expressions")

    return tuple(_stringify_expression("process argument", item) for item in iterator)


def _normalize_process_entry(process: Tuple[str, ...]) -> Tuple[str, str, Tuple[str, ...]]:
    if not isinstance(process, tuple):
        raise TypeError("process specs must be tuples")
    if len(process) == 2:
        name, template_name = process
        arguments = ()
    elif len(process) == 3:
        name, template_name, arguments = process
    else:
        raise ValueError("process specs must have the shape (name, template_name) or (name, template_name, arguments)")

    return (
        _require_text("process name", name),
        _require_text("template name", template_name),
        _normalize_process_arguments(arguments),
    )


def _normalize_location_spec(location: LocationSpec) -> LocationSpec:
    if not isinstance(location, LocationSpec):
        raise TypeError("template locations must be LocationSpec instances")

    return LocationSpec(
        name=_require_text("location name", location.name),
        initial=bool(location.initial),
        invariant=_normalize_optional_text("invariant", location.invariant),
        urgent=bool(location.urgent),
        committed=bool(location.committed),
    )


def _normalize_edge_spec(edge: EdgeSpec) -> EdgeSpec:
    if not isinstance(edge, EdgeSpec):
        raise TypeError("template edges must be EdgeSpec instances")

    return EdgeSpec(
        source=_require_text("source", edge.source),
        target=_require_text("target", edge.target),
        guard=_normalize_optional_text("guard", edge.guard),
        sync=_normalize_optional_text("sync", edge.sync),
        update=_normalize_optional_text("update", edge.update),
    )


def _normalize_query_spec(query: QuerySpec) -> QuerySpec:
    if not isinstance(query, QuerySpec):
        raise TypeError("model queries must be QuerySpec instances")

    return QuerySpec(
        formula=_require_text("formula", query.formula),
        comment=_normalize_optional_text("comment", query.comment),
        options=_normalize_options(query.options),
        expectation=_normalize_expectation(query.expectation),
        location=_normalize_optional_text("location", query.location),
    )


def _normalize_template_spec(template: TemplateSpec) -> TemplateSpec:
    if not isinstance(template, TemplateSpec):
        raise TypeError("model templates must be TemplateSpec instances")

    return TemplateSpec(
        name=_require_text("template name", template.name),
        parameters=_normalize_optional_text("parameters", template.parameters),
        declarations=tuple(_require_text("declaration", item) for item in template.declarations),
        locations=tuple(_normalize_location_spec(item) for item in template.locations),
        edges=tuple(_normalize_edge_spec(item) for item in template.edges),
    )


def _normalize_model_spec(spec: ModelSpec) -> ModelSpec:
    if not isinstance(spec, ModelSpec):
        raise TypeError("spec must be a ModelSpec instance")

    if spec.system_process_names:
        system_process_names = _normalize_names("system process", spec.system_process_names)
    else:
        system_process_names = ()

    return ModelSpec(
        declarations=tuple(_require_text("declaration", item) for item in spec.declarations),
        templates=tuple(_normalize_template_spec(item) for item in spec.templates),
        processes=tuple(_normalize_process_entry(item) for item in spec.processes),
        system_process_names=system_process_names,
        queries=tuple(_normalize_query_spec(item) for item in spec.queries),
    )


def _validate_model_spec(spec: ModelSpec) -> None:
    if not spec.system_process_names:
        raise ValueError("system_process_names must not be empty")

    template_names = set()
    for template in spec.templates:
        if template.name in template_names:
            raise ValueError("duplicate template {0!r}".format(template.name))
        template_names.add(template.name)

        location_names = set()
        initial_locations = []
        for location in template.locations:
            if location.name in location_names:
                raise ValueError("template {0!r} has duplicate location {1!r}".format(template.name, location.name))
            location_names.add(location.name)
            if location.initial:
                initial_locations.append(location.name)

        if not initial_locations:
            raise ValueError("template {0!r} must define one initial location".format(template.name))
        if len(initial_locations) > 1:
            raise ValueError("template {0!r} has multiple initial locations".format(template.name))

        for edge in template.edges:
            if edge.source not in location_names:
                raise ValueError("template {0!r} edge source {1!r} does not exist".format(template.name, edge.source))
            if edge.target not in location_names:
                raise ValueError("template {0!r} edge target {1!r} does not exist".format(template.name, edge.target))

    process_names = set()
    for process_name, template_name, _ in spec.processes:
        if process_name in process_names:
            raise ValueError("duplicate process {0!r}".format(process_name))
        process_names.add(process_name)
        if template_name not in template_names:
            raise ValueError("process {0!r} references unknown template {1!r}".format(process_name, template_name))

    for process_name in spec.system_process_names:
        if process_name not in process_names:
            raise ValueError("system references unknown process {0!r}".format(process_name))


def _payload_from_model_spec(spec: ModelSpec) -> dict:
    return {
        "declarations": tuple(spec.declarations),
        "templates": tuple(
            {
                "name": template.name,
                "parameters": template.parameters,
                "declarations": tuple(template.declarations),
                "locations": tuple(
                    {
                        "name": location.name,
                        "invariant": location.invariant,
                        "urgent": location.urgent,
                        "committed": location.committed,
                    }
                    for location in template.locations
                ),
                "edges": tuple(
                    {
                        "source": edge.source,
                        "target": edge.target,
                        "guard": edge.guard,
                        "sync": edge.sync,
                        "update": edge.update,
                    }
                    for edge in template.edges
                ),
                "initial_location": next(location.name for location in template.locations if location.initial),
            }
            for template in spec.templates
        ),
        "processes": tuple(
            {
                "name": process_name,
                "template_name": template_name,
                "arguments": tuple(arguments),
            }
            for process_name, template_name, arguments in spec.processes
        ),
        "system_process_names": tuple(spec.system_process_names),
        "queries": tuple(
            {
                "formula": query.formula,
                "comment": query.comment,
                "options": tuple({"name": option.name, "value": option.value} for option in query.options),
                "expectation": {
                    "value_type": query.expectation.value_type,
                    "status": query.expectation.status,
                    "value": query.expectation.value,
                    "resources": tuple(
                        {
                            "name": resource.name,
                            "value": resource.value,
                            "unit": resource.unit,
                        }
                        for resource in query.expectation.resources
                    ),
                },
                "location": query.location,
            }
            for query in spec.queries
        ),
    }


def _build_document_from_spec(spec: ModelSpec) -> ModelDocument:
    normalized_spec = _normalize_model_spec(spec)
    _validate_model_spec(normalized_spec)
    return ModelDocument(_native_build_model(_payload_from_model_spec(normalized_spec)))


def build_model(spec: ModelSpec) -> ModelDocument:
    """
    Build one public :class:`ModelDocument` from a :class:`ModelSpec`.

    :param spec: Immutable model specification.
    :type spec: ModelSpec
    :return: Parsed public model document.
    :rtype: ModelDocument

    Example::

        >>> from pyudbm.binding.utap_builder import LocationSpec, ModelSpec, TemplateSpec, build_model
        >>> document = build_model(
        ...     ModelSpec(
        ...         declarations=("clock x;",),
        ...         templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True),)),),
        ...         processes=(("P1", "P", ()),),
        ...         system_process_names=("P1",),
        ...     )
        ... )
        >>> document.templates[0].name
        'P'
    """

    return _build_document_from_spec(spec)


class ModelBuilder:
    """
    Build one UTAP model from lightweight Python authoring calls.

    The builder focuses on the common small-model path: global declarations,
    templates, processes, system composition, and queries. Calling
    :meth:`build` returns a public :class:`ModelDocument`.

    Example::

        >>> from pyudbm.binding.utap_builder import ModelBuilder
        >>> document = (
        ...     ModelBuilder()
        ...     .clock("x")
        ...     .template("P")
        ...         .location("Init", initial=True)
        ...         .end()
        ...     .process("P1", "P")
        ...     .system("P1")
        ...     .build()
        ... )
        >>> document.templates[0].name
        'P'
    """

    def __init__(self):
        """
        Initialize one empty model builder.

        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> isinstance(ModelBuilder(), ModelBuilder)
            True
        """

        self._declaration_lines = []
        self._templates = []
        self._processes = []
        self._system_process_names = None
        self._queries = []

    def declaration(self, text: str) -> "ModelBuilder":
        """
        Append one raw global declaration block.

        :param text: Declaration text appended to the global declaration
            section.
        :type text: str
        :return: The current builder.
        :rtype: ModelBuilder

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> builder = ModelBuilder().declaration("const int N = 1;")
            >>> isinstance(builder, ModelBuilder)
            True
        """

        self._declaration_lines.append(_require_text("text", text))
        return self

    def clock(self, *names: str) -> "ModelBuilder":
        """
        Append one ``clock`` declaration for one or more names.

        :param names: Clock names declared in one statement.
        :type names: str
        :return: The current builder.
        :rtype: ModelBuilder

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> builder = ModelBuilder().clock("x", "y")
            >>> isinstance(builder, ModelBuilder)
            True
        """

        normalized = _normalize_names("clock", names)
        self._declaration_lines.append("clock {0};".format(", ".join(normalized)))
        return self

    def chan(self, *names: str, broadcast: bool = False, urgent: bool = False) -> "ModelBuilder":
        """
        Append one channel declaration for one or more names.

        :param names: Channel names declared in one statement.
        :type names: str
        :param broadcast: Whether the declaration is for broadcast channels.
        :type broadcast: bool
        :param urgent: Whether the declaration is for urgent channels.
        :type urgent: bool
        :return: The current builder.
        :rtype: ModelBuilder

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> builder = ModelBuilder().chan("tick", urgent=True)
            >>> isinstance(builder, ModelBuilder)
            True
        """

        normalized = _normalize_names("channel", names)
        prefix_parts = []
        if urgent:
            prefix_parts.append("urgent")
        if broadcast:
            prefix_parts.append("broadcast")
        prefix_parts.append("chan")
        self._declaration_lines.append("{0} {1};".format(" ".join(prefix_parts), ", ".join(normalized)))
        return self

    def integer(
        self,
        name: str,
        *,
        lower: Optional[object] = None,
        upper: Optional[object] = None,
        init: Optional[object] = None,
        const: bool = False
    ) -> "ModelBuilder":
        """
        Append one integer declaration.

        When both ``lower`` and ``upper`` are provided, the declaration uses
        the bounded form ``int[min,max] name``. When ``const=True``, an
        initializer is required.

        :param name: Integer variable name.
        :type name: str
        :param lower: Optional lower bound.
        :type lower: object or None
        :param upper: Optional upper bound.
        :type upper: object or None
        :param init: Optional initializer expression.
        :type init: object or None
        :param const: Whether to declare a constant integer.
        :type const: bool
        :return: The current builder.
        :rtype: ModelBuilder

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> builder = ModelBuilder().integer("count", lower=0, upper=3, init=1)
            >>> isinstance(builder, ModelBuilder)
            True
        """

        normalized_name = _require_text("integer name", name)
        if (lower is None) != (upper is None):
            raise ValueError("integer bounds require both 'lower' and 'upper'")
        if const and init is None:
            raise ValueError("const integer {0!r} requires an initializer".format(normalized_name))

        prefix = "const " if const else ""
        if lower is None:
            type_text = "int"
        else:
            type_text = "int[{0},{1}]".format(
                _stringify_expression("lower", lower),
                _stringify_expression("upper", upper),
            )

        declaration = "{0}{1} {2}".format(prefix, type_text, normalized_name)
        if init is not None:
            declaration = "{0} = {1}".format(declaration, _stringify_expression("init", init))
        self._declaration_lines.append(declaration + ";")
        return self

    def template(self, name: str, *, parameters: str = "", declaration: str = "") -> "TemplateBuilder":
        """
        Start one template builder owned by this model.

        :param name: Template name.
        :type name: str
        :param parameters: Optional raw template parameter text.
        :type parameters: str
        :param declaration: Optional raw local declaration text.
        :type declaration: str
        :return: The template builder.
        :rtype: TemplateBuilder
        :raises ValueError: If the template name already exists.

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder, TemplateBuilder
            >>> template = ModelBuilder().template("P")
            >>> isinstance(template, TemplateBuilder)
            True
        """

        normalized_name = _require_text("template name", name)
        if any(item.name == normalized_name for item in self._templates):
            raise ValueError("duplicate template {0!r}".format(normalized_name))

        state = _TemplateState(name=normalized_name, parameters=_normalize_optional_text("parameters", parameters))
        if declaration.strip():
            state.declaration_lines.append(_require_text("declaration", declaration))

        self._templates.append(state)
        return TemplateBuilder(self, state)

    def process(self, name: str, template: str, *arguments: object) -> "ModelBuilder":
        """
        Append one process instantiation line.

        :param name: Process instance name.
        :type name: str
        :param template: Template name referenced by the process.
        :type template: str
        :param arguments: Optional raw argument texts rendered with
            :func:`str`.
        :type arguments: object
        :return: The current builder.
        :rtype: ModelBuilder
        :raises ValueError: If the process name already exists.

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> builder = (
            ...     ModelBuilder()
            ...     .template("P")
            ...         .location("Init", initial=True)
            ...         .end()
            ...     .process("P1", "P")
            ... )
            >>> isinstance(builder, ModelBuilder)
            True
        """

        normalized_name = _require_text("process name", name)
        normalized_template = _require_text("template name", template)
        if any(item.name == normalized_name for item in self._processes):
            raise ValueError("duplicate process {0!r}".format(normalized_name))

        self._processes.append(
            _ProcessState(
                name=normalized_name,
                template_name=normalized_template,
                arguments=_normalize_process_arguments(arguments),
            )
        )
        return self

    def system(self, *process_names: str) -> "ModelBuilder":
        """
        Set the process order used by the system declaration.

        :param process_names: Process instance names listed in the system
            declaration.
        :type process_names: str
        :return: The current builder.
        :rtype: ModelBuilder

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> builder = ModelBuilder().system("P1")
            >>> isinstance(builder, ModelBuilder)
            True
        """

        self._system_process_names = _normalize_names("system process", process_names)
        return self

    def query(
        self,
        formula: str,
        *,
        comment: str = "",
        options: Iterable[Union[Option, Tuple[str, str]]] = (),
        expectation: Optional[Expectation] = None,
        location: str = "",
    ) -> "ModelBuilder":
        """
        Append one model query.

        :param formula: Query formula text.
        :type formula: str
        :param comment: Optional query comment text.
        :type comment: str
        :param options: Optional query-local options.
        :type options: Iterable[Option or Tuple[str, str]]
        :param expectation: Optional structured expectation metadata.
        :type expectation: Expectation or None
        :param location: Optional query location text.
        :type location: str
        :return: The current builder.
        :rtype: ModelBuilder

        Example::

            >>> from pyudbm.binding import Expectation
            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> builder = ModelBuilder().query("A[] not deadlock", expectation=Expectation("", "", "", ()))
            >>> isinstance(builder, ModelBuilder)
            True
        """

        self._queries.append(
            Query(
                formula=_require_text("formula", formula),
                comment=_normalize_optional_text("comment", comment),
                options=_normalize_options(options),
                expectation=_normalize_expectation(expectation),
                location=_normalize_optional_text("location", location),
            )
        )
        return self

    def to_spec(self) -> ModelSpec:
        """
        Export the current builder state as one public :class:`ModelSpec`.

        :return: Immutable model specification snapshot.
        :rtype: ModelSpec

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder, ModelSpec
            >>> spec = ModelBuilder().clock("x").template("P").location("Init", initial=True).end().to_spec()
            >>> isinstance(spec, ModelSpec)
            True
        """

        return ModelSpec(
            declarations=tuple(self._declaration_lines),
            templates=tuple(
                TemplateSpec(
                    name=template.name,
                    parameters=template.parameters,
                    declarations=tuple(template.declaration_lines),
                    locations=tuple(
                        LocationSpec(
                            name=location.name,
                            initial=location.initial,
                            invariant=location.invariant,
                            urgent=location.urgent,
                            committed=location.committed,
                        )
                        for location in template.locations
                    ),
                    edges=tuple(
                        EdgeSpec(
                            source=edge.source,
                            target=edge.target,
                            guard=edge.guard,
                            sync=edge.sync,
                            update=edge.update,
                        )
                        for edge in template.edges
                    ),
                )
                for template in self._templates
            ),
            processes=tuple((process.name, process.template_name, tuple(process.arguments)) for process in self._processes),
            system_process_names=tuple(self._system_process_names or ()),
            queries=tuple(
                QuerySpec(
                    formula=query.formula,
                    comment=query.comment,
                    options=tuple(query.options),
                    expectation=query.expectation,
                    location=query.location,
                )
                for query in self._queries
            ),
        )

    def build(self) -> ModelDocument:
        """
        Build the current model into one public :class:`ModelDocument`.

        :return: Parsed public model document.
        :rtype: ModelDocument

        Example::

            >>> from pyudbm.binding import ModelBuilder, ModelDocument
            >>> document = (
            ...     ModelBuilder()
            ...     .clock("x")
            ...     .template("P")
            ...         .location("Init", initial=True)
            ...         .end()
            ...     .process("P1", "P")
            ...     .system("P1")
            ...     .build()
            ... )
            >>> isinstance(document, ModelDocument)
            True
        """

        return _build_document_from_spec(self.to_spec())


class TemplateBuilder:
    """
    Build one template inside a :class:`ModelBuilder`.

    The template builder is name-first and string-friendly. Locations and
    edges are accumulated on the owning model until :meth:`end` returns the
    parent builder again.

    Example::

        >>> from pyudbm.binding.utap_builder import ModelBuilder, TemplateBuilder
        >>> template = ModelBuilder().template("P")
        >>> isinstance(template, TemplateBuilder)
        True
    """

    def __init__(self, model_builder: ModelBuilder, state: _TemplateState):
        """
        Initialize one template builder owned by ``model_builder``.

        :param model_builder: Owning model builder.
        :type model_builder: ModelBuilder
        :param state: Mutable internal template state.
        :type state: _TemplateState
        :return: ``None``.
        :rtype: None
        """

        self._model_builder = model_builder
        self._state = state
        self._closed = False

    def __enter__(self) -> "TemplateBuilder":
        """
        Enter the template-builder context manager.

        :return: The current template builder.
        :rtype: TemplateBuilder

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> with ModelBuilder().template("P") as template:
            ...     template.location("Init", initial=True)
            >>> type(template).__name__
            'TemplateBuilder'
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Leave the template-builder context manager.

        :param exc_type: Exception type, if any.
        :type exc_type: type or None
        :param exc_val: Exception value, if any.
        :type exc_val: BaseException or None
        :param exc_tb: Exception traceback, if any.
        :type exc_tb: object
        :return: ``None``.
        :rtype: None
        """

        self._closed = True

    def declaration(self, text: str) -> "TemplateBuilder":
        """
        Append one raw local declaration block.

        :param text: Local declaration text.
        :type text: str
        :return: The current template builder.
        :rtype: TemplateBuilder

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> template = ModelBuilder().template("P").declaration("int i;")
            >>> type(template).__name__
            'TemplateBuilder'
        """

        self._ensure_open()
        self._state.declaration_lines.append(_require_text("text", text))
        return self

    def location(
        self,
        name: str,
        *,
        initial: bool = False,
        invariant: str = "",
        urgent: bool = False,
        committed: bool = False
    ) -> "TemplateBuilder":
        """
        Append one location to the current template.

        :param name: Location name.
        :type name: str
        :param initial: Whether this location is the initial location.
        :type initial: bool
        :param invariant: Optional invariant text.
        :type invariant: str
        :param urgent: Whether the location is urgent.
        :type urgent: bool
        :param committed: Whether the location is committed.
        :type committed: bool
        :return: The current template builder.
        :rtype: TemplateBuilder
        :raises ValueError: If the location name already exists or multiple
            initial locations are requested.

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> template = ModelBuilder().template("P").location("Init", initial=True)
            >>> type(template).__name__
            'TemplateBuilder'
        """

        self._ensure_open()
        normalized_name = _require_text("location name", name)
        if any(item.name == normalized_name for item in self._state.locations):
            raise ValueError(
                "template {0!r} has duplicate location {1!r}".format(self._state.name, normalized_name)
            )
        if initial and self._state.initial_location is not None:
            raise ValueError("template {0!r} already has an initial location".format(self._state.name))

        self._state.locations.append(
            _LocationState(
                name=normalized_name,
                invariant=_normalize_optional_text("invariant", invariant),
                urgent=urgent,
                committed=committed,
                initial=initial,
            )
        )
        if initial:
            self._state.initial_location = normalized_name
        return self

    def edge(
        self,
        source: str,
        target: str,
        *,
        when: str = "",
        guard: str = "",
        sync: str = "",
        send: str = "",
        recv: str = "",
        update: str = "",
        reset: object = ()
    ) -> "TemplateBuilder":
        """
        Append one edge between two named locations.

        ``when`` is an alias for ``guard``. ``send`` and ``recv`` are sugar
        for ``sync="name!"`` and ``sync="name?"``. ``reset`` is sugar for a
        comma-joined assignment list such as ``{"x": 0}``.

        :param source: Source location name.
        :type source: str
        :param target: Target location name.
        :type target: str
        :param when: Optional guard alias.
        :type when: str
        :param guard: Optional guard text.
        :type guard: str
        :param sync: Optional synchronisation text such as ``"tick?"``.
        :type sync: str
        :param send: Optional send-side synchronisation sugar.
        :type send: str
        :param recv: Optional receive-side synchronisation sugar.
        :type recv: str
        :param update: Optional assignment text.
        :type update: str
        :param reset: Optional mapping or pair-sequence rendered into an
            assignment list.
        :type reset: object
        :return: The current template builder.
        :rtype: TemplateBuilder

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> template = (
            ...     ModelBuilder()
            ...     .template("P")
            ...     .location("Init", initial=True)
            ...     .location("Done")
            ...     .edge("Init", "Done", send="tick", reset={"x": 0})
            ... )
            >>> type(template).__name__
            'TemplateBuilder'
        """

        self._ensure_open()
        self._state.edges.append(
            _EdgeState(
                source=_require_text("source", source),
                target=_require_text("target", target),
                guard=_normalize_guard_text(guard, when),
                sync=_normalize_sync_text(sync, send, recv),
                update=_normalize_update_text(update, reset),
            )
        )
        return self

    def end(self) -> ModelBuilder:
        """
        Finish the current template and return the parent builder.

        :return: The owning model builder.
        :rtype: ModelBuilder

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> builder = ModelBuilder().template("P").location("Init", initial=True).end()
            >>> isinstance(builder, ModelBuilder)
            True
        """

        self._closed = True
        return self._model_builder

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("template builder is already closed")
