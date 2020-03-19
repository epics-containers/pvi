from enum import Enum
from pathlib import Path
from typing import List, Union

from pydantic import BaseModel, Field
from ruamel.yaml import YAML
from typing_extensions import Literal

# from ._version_git import __version__













here = Path(__file__).parent
open(here / "schema.yaml", "w").write(Schema.schema_json(indent=2))
data = YAML().load(here / "thing.yaml")
schema = Schema(**data)
print(schema)

# __all__ = ["__version__"]
