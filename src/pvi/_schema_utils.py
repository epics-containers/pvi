from functools import cache
from typing import TypeVar

# A type variable with an upper bound of type
Cls = TypeVar("Cls", bound=type)


# Permanently cache so we don't include deserialization subclasses defined below
@cache
def rec_subclasses(cls: Cls) -> list[Cls]:
    """Recursive implementation of type.__subclasses__"""

    subclasses: list[Cls] = []
    for sub_cls in cls.__subclasses__():
        subclasses += [sub_cls] + rec_subclasses(sub_cls)

    return subclasses
