from __future__ import annotations

from typing import (
    Annotated,
    Any,
    Union,
    cast,
    get_args,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    GetJsonSchemaHandler,
    Tag,
    computed_field,
    model_validator,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema


class TypedModel(BaseModel):
    """A Base class for members of tagged unions discriminated by the class name.

    This class defines some hooks called by pydantic during validation and schema
    generation.

    Child classes will automatically have a type field defined, which can be used as a
    discriminator when constructing tagged unions using pydantic `Discriminator` and
    `Tag`.

    """

    # Do not allow extra fields during validation
    model_config = ConfigDict(extra="forbid")

    @computed_field  # type: ignore
    @property
    def type(self) -> str:
        """Property to create type field from class name when serializing."""
        return self.__class__.__name__

    @model_validator(mode="before")
    @classmethod
    def _strip_own_type(cls, data: Any) -> Any:
        """Accept a serialized `type` field naming this class when validating.

        Inside tagged unions the discriminator removes `type`, but when a model is
        validated directly (e.g. `Device.model_validate_json(device.model_dump_json())`)
        it would otherwise be rejected as an extra field. A `type` naming a different
        class is left in place so validation still fails.

        """
        # Before-validators see raw input; pass non-dicts on for pydantic to reject
        if not isinstance(data, dict):
            return data
        fields = cast(dict[str, Any], data)
        if fields.get("type") == cls.__name__:
            return {k: v for k, v in fields.items() if k != "type"}
        return fields

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Add the type discriminator to the JSON schema of every child class.

        `type` is serialized by the computed field above and consumed by the
        discriminator during validation, so it only needs adding to the schema. Doing
        it here, rather than inserting it into `model_fields` and rebuilding models,
        means instances created before schema generation (such as default widgets)
        always match their model's serializer.

        """
        json_schema = handler(core_schema)
        target = handler.resolve_ref_schema(json_schema)
        target.setdefault("properties", {})["type"] = {
            "const": cls.__name__,
            "default": cls.__name__,
            "title": "Type",
            "type": "string",
        }
        return json_schema

    @classmethod
    def _tag(cls):
        """Create a pydantic `Tag` for this class to include it in tagged unions."""
        return Annotated[cls, Tag(cls.__name__)]

    @staticmethod
    def discriminator():
        """Create a pydantic `Discriminator` for a tagged union of `TypedModel`."""
        return Field(discriminator=Discriminator(TypedModel._get_type_name))

    @staticmethod
    def _get_type_name(x: TypedModel | dict[str, Any]) -> str | None:
        """Get the type name from an instance or serialized `dict` of `TypeModel`.

        This is a callable for pydantic Discriminator to discriminate between types in a
        tagged union of `TypedModel` child classes.

        If given an instance of `TypedModel` then this method is being called to
        serialize an instance. The type field of the entry for this instance should be
        its class name.

        If given a dictionary, then an instance is being deserialized. The name of the
        class to be instantiated is given by the type field, and the remaining fields
        should be passed as fields to the class.

        In any other case, return `None` to cause a pydantic validation error.

        Args:
            x: `TypedModel` instance or serialized `dict` of a `TypedModel`

        """
        match x:
            case TypedModel():
                return x.__class__.__name__
            case dict() as serialized:
                return serialized.pop("type", None)


def as_tagged_union(union: type[TypedModel]):
    """Create a tagged union from a `Union` of `TypedModel`.

    Members will be tagged with their class name to be discriminated by pydantic.

    Args:
        union: `Union` of `TypedModel` to convert to a tagged union

    """
    union_members = get_args(union)

    return Annotated[
        Union[tuple(cls._tag() for cls in union_members)],  # type: ignore # noqa: UP007
        TypedModel.discriminator(),
    ]
