from __future__ import annotations

from dataclasses import dataclass

from .xml.serializable import MappingGenerator, Serializable, XmlElement


@dataclass(frozen=True)
class Accolade(Serializable):
    bloodline_xp: int
    bounty: int
    category: str
    event_points: int
    bloodbonds: int
    generated_bloodbonds: int
    hunt_dollars: int
    hits: int
    hunter_points: int
    hunter_xp: int
    weighting: int
    xp: int

    # Serialization
    @staticmethod
    def _generate_prefix(accolade_id: int) -> str:
        """
        Generate a prefix for the class.
        :param accolade_id: the id of the accolade
        :return: a MissionAccoladeEntry prefix
        """
        return f"MissionAccoladeEntry_{accolade_id}"

    @staticmethod
    def _data_mappings() -> MappingGenerator:
        """
        Yield each variable name and its corresponding attribute suffix.
        :return: a generator which yields the name, value
        """
        # Yield the values
        yield "bloodline_xp", "bloodlineXp"
        yield "bounty", "bounty"
        yield "category", "category"
        yield "event_points", "eventPoints"
        yield "bloodbonds", "gems"
        yield "generated_bloodbonds", "generatedGems"
        yield "hunt_dollars", "gold"
        yield "hits", "hits"
        yield "hunter_points", "hunterPoints"
        yield "hunter_xp", "hunterXp"
        yield "weighting", "weighting"
        yield "xp", "xp"

    # noinspection PyMethodOverriding
    def serialize(self, root: XmlElement, *, accolade_id: int) -> None:  # type: ignore[override]
        """
        Serialize an Accolade instance.
        :param root: the root element to serialize into
        :param accolade_id: the id of the accolade
        """
        # Generate the prefix
        prefix: str = Accolade._generate_prefix(accolade_id)

        # Serialize the data
        super().serialize(root, prefix)

    # noinspection PyMethodOverriding
    @classmethod
    def deserialize(cls, root: XmlElement, accolade_id: int) -> Accolade:  # type: ignore[override]
        """
        Deserialize a series of elements into an Accolade instance.
        :param root: the root element to serialize into
        :param accolade_id: the id of the accolade
        :return: a serialized Accolade instance
        """
        # Generate the prefix
        prefix: str = Accolade._generate_prefix(accolade_id)

        # Deserialize the data
        return super(cls, cls).deserialize(root, prefix)
