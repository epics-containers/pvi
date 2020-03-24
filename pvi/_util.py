from typing import Iterator

from ._types import Component, ComponentTree, Group


def truncate_description(desc: str) -> str:
    """Take the first line of a multiline description, truncated to 40 chars"""
    first_line = desc.strip().split("\n")[0]
    return first_line[:40]


def walk(components: ComponentTree) -> Iterator[Component]:
    """Depth first traversal of component tree"""
    for component in components:
        yield component
        if isinstance(component, Group):
            yield from walk(component.children)
