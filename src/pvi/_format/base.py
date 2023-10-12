from pathlib import Path

from pvi._schema_utils import BaseSettings, as_discriminated_union
from pvi.device import Device


@as_discriminated_union
class Formatter(BaseSettings):
    def format(self, device: Device, prefix: str, path: Path):
        raise NotImplementedError(self)
