from xml.etree.ElementTree import Element as XmlElement

from hunt.attributes.parser import parse_match, Match


def test_parse_match(attributes_tree: XmlElement, expected_match: Match) -> None:
    assert parse_match(attributes_tree, steam_name=expected_match.player_name) == expected_match
