from functools import lru_cache
from typing import List, TypeVar

# A type variable with an upper bound of type
Cls = TypeVar("Cls", bound=type)


# Permanently cache so we don't include deserialization subclasses defined below
@lru_cache(maxsize=None)
def rec_subclasses(cls: Cls) -> List[Cls]:
    """Recursive implementation of type.__subclasses__"""

    subclasses = []
    for sub_cls in cls.__subclasses__():
        subclasses += [sub_cls] + rec_subclasses(sub_cls)

    return subclasses
