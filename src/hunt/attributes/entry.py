from __future__ import annotations

from dataclasses import dataclass

from .xml.serializable import MappingGenerator, Serializable, XmlElement


@dataclass(frozen=True)
class Entry(Serializable):
    amount: int
    category: str
    descriptor_name: str
    descriptor_score: int
    descriptor_type: int
    reward_type: int
    reward_size: int

    # Serialization
    @staticmethod
    def _generate_prefix(entry_id: int) -> str:
        """
        Generate a prefix for the class.
        :param entry_id: the id of the entry
        :return: a MissionBagEntry prefix
        """
        return f"MissionBagEntry_{entry_id}"

    @staticmethod
    def _data_mappings() -> MappingGenerator:
        """
        Yield each variable name and its corresponding attribute suffix.
        :return: a generator which yields the name, value
        """
        # Yield the values
        yield "amount", "amount"
        yield "category", "category"
        yield "descriptor_name", "descriptorName"
        yield "descriptor_score", "descriptorScore"
        yield "descriptor_type", "descriptorType"
        yield "reward_type", "reward"
        yield "reward_size", "rewardSize"

    # noinspection PyMethodOverriding
    def serialize(self, root: XmlElement, *, entry_id: int) -> None:  # type: ignore[override]
        """
        Serialize an Entry instance.
        :param root: the root element to serialize into
        :param entry_id: the id of the entry
        """
        # Generate the prefix
        prefix: str = Entry._generate_prefix(entry_id)

        # Serialize the data
        super().serialize(root, prefix)

    # noinspection PyMethodOverriding
    @classmethod
    def deserialize(cls, root: XmlElement, entry_id: int) -> Entry:  # type: ignore[override]
        """
        Deserialize a series of elements into an Entry instance.
        :param root: the root element to serialize into
        :param entry_id: the id of the entry
        :return: a serialized Entry instance
        """
        # Generate the prefix
        prefix: str = Entry._generate_prefix(entry_id)

        # Deserialize the data
        return super(cls, cls).deserialize(root, prefix)
