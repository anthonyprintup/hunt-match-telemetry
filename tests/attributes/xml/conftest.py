import random
import string
from typing import TypeAlias
from xml.etree.ElementTree import Element as XmlElement

from pytest import fixture

from hunt.attributes.xml.elements import ElementValueType

ElementDataType: TypeAlias = tuple[str, ElementValueType]
ElementDataCollectionType: TypeAlias = tuple[ElementDataType, ...]


@fixture
def expected_elements() -> ElementDataCollectionType:
    """
    A fixture to provide information about the expected element names and values.
    :return: a tuple of element data tuples
    """
    return (
        ("string-element", "".join(random.choice(string.printable) for _ in range(16))),
        ("integer-element", random.randint(-1000, 1000)),
        ("bool-element-true", True),
        ("bool-element-false", False))


@fixture
def existing_element_name(expected_elements: ElementDataCollectionType) -> str:
    """
    A fixture to provide a name of an element that's guaranteed to exist.
    :return: an existing element name
    """
    return expected_elements[0][0]


@fixture
def random_element_data() -> ElementDataType:
    return "random-element", "".join(random.choice(string.printable) for _ in range(16))


@fixture
def root_element(expected_elements: ElementDataCollectionType) -> XmlElement:
    """
    A fixture to provide an XML element pattern which is expected by the parser.
    :return: an XmlElement instance populated in the expected parser format
    """
    # Create the root element
    root_element: XmlElement = XmlElement("Attributes", attrib={"Version": "37"})

    # Append a few elements to perform tests on later
    element_name: str
    element_value: str | int | bool
    for element_name, element_value in expected_elements:
        value: str
        match element_value:
            case bool():
                value = str(element_value).lower()
            case _:
                value = str(element_value)
        root_element.append(XmlElement("Attr", attrib={"name": element_name, "value": value}))

    # Return the root element
    return root_element
