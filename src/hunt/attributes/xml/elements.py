import builtins
from typing import TypeVar, TypeAlias
from xml.etree.ElementTree import Element as XmlElement

from ...exceptions import ParserError

_T = TypeVar("_T")
ValueType: TypeAlias = str | int | bool


def append_element(parent_element: XmlElement, name: str, value: ValueType) -> None:
    """
    Appends a new element to the parent element.
    :param parent_element: the element to append to
    :param name: the name of the attribute
    :param value: the value of the attribute
    """
    # Transform the value to a string
    match value:
        case bool():
            value = str(value).lower()
        case _:
            value = str(value)

    # Create and append the element
    new_element: XmlElement = XmlElement("Attr", attrib={"name": name, "value": value})
    parent_element.append(new_element)


# https://github.com/python/mypy/issues/3737
def get_element_value(element: XmlElement, name: str, suffix: str = "",
                      result_type: type[_T] = str) -> _T:  # type: ignore
    """
    Resolves an element's "value" attribute based from its name (and suffix).
    :param element: an XmlElement instance
    :param name: the element's name
    :param suffix: a suffix to append to the element name
    :param result_type: the type to cast the value to
    :return: the value of an element
    :raises ParserError: if the xpath isn't found,
                         if the element is missing a "value" attribute, or
                         if the result type isn't a supported type
    """
    xpath: str = f"Attr[@name={name + ('_' + suffix if suffix else '')!r}]"
    resolved_element: XmlElement | None = element.find(path=xpath)
    if resolved_element is not None:
        value: str | None = resolved_element.attrib.get("value", None)
        if value is None:
            raise ParserError(f"Missing \"value\" attribute in element {xpath!r}.")

        match result_type:
            case builtins.str | builtins.int:
                return result_type(value)  # type: ignore
            case builtins.bool:
                return value == "true"  # type: ignore
            case _:
                raise ParserError("Type not implemented.")
    raise ParserError(f"No such element {xpath!r} in the current element.")
