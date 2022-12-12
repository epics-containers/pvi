from typing import Type, TypeVar


def truncate_description(desc: str) -> str:
    """Take the first line of a multiline description, truncated to 40 chars"""
    first_line = desc.strip().split("\n")[0]
    return first_line[:40]


def join_lines(lines, indent=0):
    return ("\n" + (" " * indent)).join(lines)


def get_param_set(driver: str) -> str:
    return "asynParamSet" if driver == "asynPortDriver" else driver + "ParamSet"


T = TypeVar("T")


def narrow_type(obj, type: Type[T]) -> T:
    """Narrow the type of `obj` to the given type to pass mypy checks

    Raises `AssertionError` if `obj` is not an instance of `type`

    """
    assert isinstance(obj, type), "%s is not an instance of %s" % (
        obj,
        type.__name__,
    )
    return obj
