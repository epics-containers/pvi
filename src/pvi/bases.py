from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Tag, computed_field
from pydantic.fields import FieldInfo


class BaseSettings(BaseModel):
    """A Base class for consistent model settings."""

    model_config = ConfigDict(extra="forbid")


class BaseTyped(BaseSettings):
    """A Base class for tagged unions discriminated by a `type` field."""

    type: str


class TypedModel(BaseSettings):
    """A Base class for members of tagged unions discriminated by the class name.

    This class defines some hooks called by pydantic during validation and schema
    generation.

    Child classes will automatically have a type field defined, which can be used as a
    discriminator when constructing tagged unions using pydantic `Discriminator` and
    `Tag`.

    """

    # Whether child models have been rebuilt with type field inserted
    models_typed: ClassVar[bool] = False

    @computed_field  # type: ignore
    @classmethod  # type: ignore
    @property
    def type(cls) -> str:
        """Property to create type field from class name when serializing."""
        return cls.__name__

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Add computed type field to model_fields to include it in the schema.

        The `model_rebuild` must be called once all `TypedModel` child classes have been
        defined.
        """
        super().__pydantic_init_subclass__(**kwargs)

        cls.model_fields["type"] = FieldInfo(
            annotation=Literal[cls.type], default=cls.type  # type: ignore
        )

    @staticmethod
    def get_type_name(x: Any) -> str | None:
        """Get the type name from an instance or serialized `dict` of `TypeModel`.

        This is a callable for pydantic Discriminator to discriminate between types in a
        tagged union of `TypedModel` child classes.

        If given an instance of `TypeModel` then this method is being called to
        serialize an instance. The type field of the entry for this instance should be
        its class name.

        If given a dictionary, then an instance is being deserialized. The name of the
        class to be instantiated is given by the type field, and the remaining fields
        should be passed as fields to the class.

        In any other case, return `None` to cause a pydantic validation error.

        Args:
            x: `TypeModel` instance or serialized `dict` of a `TypeModel`

        """
        match x:
            case TypedModel():
                return x.__class__.__name__
            case dict() as serialized:
                return serialized.pop("type", None)
            case _:
                return None

    @classmethod
    def rebuild_child_models(cls):
        """Recursively rebuild all subclass models to insert type into core model."""
        for subclass in cls.__subclasses__():
            subclass.model_rebuild(force=True)
            subclass.rebuild_child_models()

    @classmethod
    def model_json_schema(cls, **kwargs):
        """Ensure all child models have type field added before generating schema."""
        if not cls.models_typed:
            TypedModel.rebuild_child_models()

        return super().model_json_schema(**kwargs)

    def tag(cls):
        return Annotated[cls, Tag(cls.__name__)]
