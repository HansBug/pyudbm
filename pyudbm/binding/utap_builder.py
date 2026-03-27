"""
Lightweight Python-first UTAP model builder.

This module provides the first-phase authoring layer for constructing small
UTAP models from Python without manually writing XML. The current
implementation keeps the Python-side authoring API lightweight while
delegating the final document construction to a native helper built on top of
official UTAP document-building and parsing components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple, Union

from ._utap import _build_model as _native_build_model
from .utap import Expectation, ModelDocument, Option, Query

__all__ = ["ModelBuilder", "TemplateBuilder"]


@dataclass
class _LocationState:
    name: str
    invariant: str
    urgent: bool
    committed: bool


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


def _normalize_optional_text(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("text values must be strings")
    return value.strip()


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

        state = _TemplateState(name=normalized_name, parameters=_normalize_optional_text(parameters))
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
                arguments=tuple(str(item) for item in arguments),
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
                comment=_normalize_optional_text(comment),
                options=_normalize_options(options),
                expectation=_normalize_expectation(expectation),
                location=_normalize_optional_text(location),
            )
        )
        return self

    def build(self) -> ModelDocument:
        """
        Build the current model into one public :class:`ModelDocument`.

        :return: Parsed public model document.
        :rtype: ModelDocument
        :raises ValueError: If the builder contains inconsistent structure.

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

        self._validate()
        return ModelDocument(_native_build_model(self._build_payload()))

    def _validate(self) -> None:
        template_names = {item.name for item in self._templates}
        process_names = {item.name for item in self._processes}

        if self._system_process_names is None:
            raise ValueError("system() must be called before build()")

        for template in self._templates:
            if template.initial_location is None:
                raise ValueError("template {0!r} must define one initial location".format(template.name))

            location_names = {item.name for item in template.locations}
            for edge in template.edges:
                if edge.source not in location_names:
                    raise ValueError(
                        "template {0!r} edge source {1!r} does not exist".format(template.name, edge.source)
                    )
                if edge.target not in location_names:
                    raise ValueError(
                        "template {0!r} edge target {1!r} does not exist".format(template.name, edge.target)
                    )

        for process in self._processes:
            if process.template_name not in template_names:
                raise ValueError(
                    "process {0!r} references unknown template {1!r}".format(process.name, process.template_name)
                )

        for process_name in self._system_process_names:
            if process_name not in process_names:
                raise ValueError("system references unknown process {0!r}".format(process_name))

    def _build_payload(self) -> dict:
        return {
            "declarations": tuple(self._declaration_lines),
            "templates": tuple(
                {
                    "name": template.name,
                    "parameters": template.parameters,
                    "declarations": tuple(template.declaration_lines),
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
                    "initial_location": template.initial_location,
                }
                for template in self._templates
            ),
            "processes": tuple(
                {
                    "name": process.name,
                    "template_name": process.template_name,
                    "arguments": tuple(process.arguments),
                }
                for process in self._processes
            ),
            "system_process_names": tuple(self._system_process_names),
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
                for query in self._queries
            ),
        }


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
                invariant=_normalize_optional_text(invariant),
                urgent=urgent,
                committed=committed,
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
        update: str = ""
    ) -> "TemplateBuilder":
        """
        Append one edge between two named locations.

        ``when`` is a convenient alias for ``guard``. If both are provided,
        their normalized text must match.

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
        :param update: Optional assignment text.
        :type update: str
        :return: The current template builder.
        :rtype: TemplateBuilder
        :raises ValueError: If ``when`` and ``guard`` disagree.

        Example::

            >>> from pyudbm.binding.utap_builder import ModelBuilder
            >>> template = (
            ...     ModelBuilder()
            ...     .template("P")
            ...     .location("Init", initial=True)
            ...     .location("Done")
            ...     .edge("Init", "Done", when="x >= 1")
            ... )
            >>> type(template).__name__
            'TemplateBuilder'
        """

        self._ensure_open()
        normalized_guard = _normalize_optional_text(guard)
        normalized_when = _normalize_optional_text(when)
        if normalized_guard and normalized_when and normalized_guard != normalized_when:
            raise ValueError("edge guard is ambiguous: use either 'guard' or 'when'")

        self._state.edges.append(
            _EdgeState(
                source=_require_text("source", source),
                target=_require_text("target", target),
                guard=normalized_guard or normalized_when,
                sync=_normalize_optional_text(sync),
                update=_normalize_optional_text(update),
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
