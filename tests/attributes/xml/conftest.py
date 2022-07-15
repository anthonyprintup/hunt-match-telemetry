import random
import string
from typing import TypeAlias, Generator
from xml.etree.ElementTree import Element as XmlElement

from pytest import fixture

ElementDataType: TypeAlias = tuple[str, str | int | bool]
ElementDataCollectionType: TypeAlias = tuple[ElementDataType, ...]


@fixture
def expected_elements() -> Generator[ElementDataCollectionType, None, None]:
    """
    A fixture to provide information about the expected element names and values.
    :return: a generator which yields a tuple of expected elements
    """
    yield (
        ("string-element", "".join(random.choice(string.printable) for _ in range(16))),
        ("integer-element", random.randint(-1000, 1000)),
        ("bool-element-true", True),
        ("bool-element-false", False))


@fixture
def random_element_data() -> Generator[ElementDataType, None, None]:
    yield "random-element", "".join(random.choice(string.printable) for _ in range(16))


@fixture
def root_element(expected_elements: ElementDataCollectionType) -> Generator[XmlElement, None, None]:
    """
    A fixture to provide an XML element pattern which is expected by the parser.
    :return: a generator which yields an XmlElement instance
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

    # Yield the root element
    yield root_element
