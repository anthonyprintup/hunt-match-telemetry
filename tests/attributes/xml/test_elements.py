import pytest

from hunt.attributes.xml.elements import XmlElement, ElementValueType, ParserError, append_element, get_element_value

from .conftest import ElementDataType, ElementDataCollectionType


def test_append_element(root_element: XmlElement, random_element_data: ElementDataType) -> None:
    """
    Test append_element by appending elements to the root element and checking if they were appended properly.
    :param root_element: the root element of the tree
    """
    # Element data
    element_name: str
    expected_value: ElementValueType
    [element_name, expected_value] = random_element_data

    # Append an element
    append_element(root_element, name=element_name, value=expected_value)

    # Check if the element was appended properly
    expected_element: XmlElement | None = root_element.find(path=f"Attr[@name='{element_name}']")
    assert expected_element is not None
    assert "value" in expected_element.attrib.keys()
    assert type(expected_value)(expected_element.attrib["value"]) == expected_value


def test_get_element_value(root_element: XmlElement, expected_elements: ElementDataCollectionType) -> None:
    """
    Test get_element_value by resolving expected elements with different types.
    :param root_element: the root element of the tree
    """
    # Invoke get_element_value
    for element_name, expected_value in expected_elements:
        result = get_element_value(root_element, name=element_name, result_type=type(expected_value))  # type: ignore
        assert result == expected_value


def test_get_element_value_missing_value_attribute(root_element: XmlElement) -> None:
    """
    Test get_element_value by passing it an element name that is missing the "value" attribute.
    :param root_element: the root element of the tree
    """
    # Insert a faulty element
    faulty_element_name: str = "faulty-element-name"
    root_element.append(XmlElement("Attr", attrib={"name": faulty_element_name, "wrong_value": "faulty"}))

    # Invoke get_element_value
    with pytest.raises(ParserError, match=r"""Missing "value" attribute in element .*\."""):
        get_element_value(root_element, name=faulty_element_name)


def test_get_element_value_invalid_type_cast(root_element: XmlElement, existing_element_name: str) -> None:
    """
    Test get_element_value by passing it an invalid result type.
    :param root_element: the root element of the tree
    """
    # Invoke get_element_value
    with pytest.raises(ParserError, match=r"Couldn't cast the value .* to an .* type."):
        get_element_value(root_element, name=existing_element_name, result_type=int)


def test_get_element_value_type_not_implemented(root_element: XmlElement, existing_element_name: str) -> None:
    """
    Test get_element_value by passing it an invalid result type.
    :param root_element: the root element of the tree
    """
    # Invoke get_element_value
    with pytest.raises(ParserError, match=r"Type conversion not supported."):
        # noinspection PyTypeChecker
        get_element_value(root_element, name=existing_element_name, result_type=float)  # type: ignore


def test_get_element_value_missing_element(root_element: XmlElement) -> None:
    """
    Test get_element_value by passing it an element name that shouldn't exist.
    :param root_element: the root element of the tree
    """
    # Invoke get_element_value
    with pytest.raises(ParserError, match=r"No such element .* in the current element tree."):
        get_element_value(root_element, name="nonexistent-element-name")
