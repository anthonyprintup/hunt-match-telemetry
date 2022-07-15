from hunt.attributes.xml.elements import XmlElement, append_element, get_element_value

from .conftest import ElementValueType, ElementDataType, ElementDataCollectionType


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
    element_name: str
    expected_value: ElementValueType
    for element_name, expected_value in expected_elements:
        assert get_element_value(root_element, name=element_name, result_type=type(expected_value)) == expected_value
