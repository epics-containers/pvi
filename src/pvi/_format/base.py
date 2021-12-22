from dataclasses import dataclass
from pathlib import Path

from pvi._schema_utils import as_discriminated_union
from pvi.device import Device


@as_discriminated_union
@dataclass
class Formatter:
    def format(self, device: Device, prefix: str, path: Path):
        raise NotImplementedError(self)
