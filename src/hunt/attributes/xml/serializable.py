from abc import ABC, abstractmethod
from dataclasses import is_dataclass
from typing import Generator, TypeAlias, TypeVar, get_type_hints

from .elements import ElementValueType, XmlElement, append_element, get_element_value

_T = TypeVar("_T", bound="Serializable")
MappingGenerator: TypeAlias = Generator[tuple[str, str], None, None]


class Serializable(ABC):
    @staticmethod
    @abstractmethod
    def _data_mappings() -> MappingGenerator:
        """
        Yield each variable name and its corresponding attribute suffix.
        :return: a generator which yields the name, value
        """
        raise NotImplementedError("Unimplemented _data_mappings method.")  # pragma: no cover

    @abstractmethod
    def serialize(self, root: XmlElement, name_prefix: str) -> None:
        """
        Serialize the current class into a series of XmlElement instances.
        :param root: the root element to serialize into
        :param name_prefix: the name prefix to use when appending elements
        """
        assert is_dataclass(self.__class__), "The class should be a dataclass."

        # Append each element
        for variable_name, name_suffix in self._data_mappings():
            append_element(root, name=f"{name_prefix}_{name_suffix}", value=self.__getattribute__(variable_name))

    @classmethod
    @abstractmethod
    def deserialize(cls: type[_T], root: XmlElement, name_prefix: str) -> _T:
        """
        Deserialize a series of elements into the class instance.
        :param root: the root element to deserialize from
        :param name_prefix: the name prefix to use when resolving elements
        """
        assert is_dataclass(cls), "The class should be a dataclass."

        # Generate the data by fetching each element value
        type_hints: dict[str, type[ElementValueType]] = get_type_hints(cls)
        data: dict[str, ElementValueType] = dict(
            (variable_name, get_element_value(  # type: ignore[type-var, misc]
                root, name=f"{name_prefix}_{name_suffix}", result_type=type_hints[variable_name]))
            for variable_name, name_suffix in cls._data_mappings())

        # Construct and return the class
        return cls(**data)
