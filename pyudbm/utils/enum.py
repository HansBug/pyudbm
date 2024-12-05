from typing import Protocol, Dict, TypeVar

T = TypeVar('T', bound='EnumProtocol')


class EnumProtocol(Protocol[T]):
    __members__: Dict[str, T]

    # noinspection PyPropertyDefinition
    @property
    def name(self) -> str:
        ...  # pragma: no cover

    # noinspection PyPropertyDefinition
    @property
    def value(self) -> int:
        ...  # pragma: no cover

    def __hash__(self) -> int:
        ...  # pragma: no cover

    def __eq__(self, other: object) -> bool:
        ...  # pragma: no cover

    def __repr__(self) -> str:
        ...  # pragma: no cover
