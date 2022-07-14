from xml.etree.ElementTree import Element as XmlElement

from hunt.attributes.parser import parse_match, Match


def test_parse_match(attributes_tree: XmlElement, expected_match: Match) -> None:
    """
    Test parse_match by comparing the parsed Match instance to the expected Match instance.
    :param attributes_tree: a generated element tree
    :param expected_match: the Match instance to compare against
    """
    assert parse_match(attributes_tree, steam_name=expected_match.player_name) == expected_match
