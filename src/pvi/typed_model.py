from __future__ import annotations

from typing import (
    Annotated,
    Any,
    ClassVar,
    Literal,
    Union,
    get_args,
)

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag, computed_field
from pydantic.fields import FieldInfo
from pydantic.json_schema import (
    DEFAULT_REF_TEMPLATE,
    GenerateJsonSchema,
    JsonSchemaMode,
)


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

    # Whether child models have been rebuilt with type field inserted
    models_typed: ClassVar[bool] = False

    @computed_field  # type: ignore
    @property
    def type(self) -> str:
        """Property to create type field from class name when serializing."""
        return self.__class__.__name__

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Add computed type field to model_fields to include it in the schema.

        The `model_rebuild` method must be called to propagate this to the core schema
        of the models, once all `TypedModel` child classes have been defined. The
        `model_json_schema` method is overridden in this class to make sure this is
        applied automatically before generating schema.

        """
        super().__pydantic_init_subclass__(**kwargs)

        cls.model_fields["type"] = FieldInfo(
            annotation=Literal[cls.__name__],  # type: ignore
            default=cls.__name__,
        )

    @classmethod
    def model_json_schema(
        cls,
        by_alias: bool = True,
        ref_template: str = DEFAULT_REF_TEMPLATE,
        schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema,
        mode: JsonSchemaMode = "validation",
        *,
        union_format: Literal["any_of", "primitive_type_array"] = "any_of",
    ):
        """Ensure all child models have type field added before generating schema."""
        if not cls.models_typed:
            TypedModel.rebuild_child_models()

        return super().model_json_schema(
            by_alias, ref_template, schema_generator, mode, union_format=union_format
        )

    @classmethod
    def rebuild_child_models(cls):
        """Recursively rebuild all subclass models to add type into core schema."""
        for subclass in cls.__subclasses__():
            subclass.model_rebuild(force=True)
            subclass.rebuild_child_models()

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
