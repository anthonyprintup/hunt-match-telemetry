from typing import TypeVar
from xml.etree.ElementTree import Element as XmlElement

from ...exceptions import ParserError

_T = TypeVar("_T")


def append_element(parent_element: XmlElement, name: str, value: str) -> None:
    """
    Appends a new element to the parent element.
    :param parent_element: the element to append to
    :param name: the name of the attribute
    :param value: the value of the attribute
    """
    new_element: XmlElement = XmlElement("Attr", attrib={"name": name, "value": value})
    parent_element.append(new_element)


def get_element_value(element: XmlElement, name: str, suffix: str = "",
                      result_type: type[_T] = str) -> _T:  # type: ignore
    """
    Resolves an element's "value" attribute based from its name (and suffix).
    :param element: an XmlElement instance
    :param name: the element's name
    :param suffix: a suffix to append to the element name
    :param result_type: the type to cast the value to
    :return: the value of an element
    :raises ParserError: if the xpath isn't found
    """
    xpath: str = f"Attr[@name='{name}{'_' + suffix if suffix else ''}']"
    resolved_element: XmlElement | None = element.find(path=xpath)
    if resolved_element is not None:
        return result_type(resolved_element.attrib["value"])  # type: ignore
    raise ParserError(f"No such element {xpath!r} in the current element.")
