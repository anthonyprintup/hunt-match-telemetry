from __future__ import annotations

from abc import ABC, abstractmethod
from xml.etree.ElementTree import Element as XmlElement


class Serializable(ABC):
    @abstractmethod
    def serialize(self, root: XmlElement) -> None:
        """
        Serialize the current class into a series of XmlElement instances.
        :param root: the root element to serialize into
        """
        raise NotImplementedError("Unimplemented serialize method.")

    @staticmethod
    @abstractmethod
    def deserialize(root: XmlElement) -> Serializable:
        """
        Deserialize a series of elements into the class instance.
        :param root: the root element to deserialize from
        """
        raise NotImplementedError("Unimplemented deserialize method.")
