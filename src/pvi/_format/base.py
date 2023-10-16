from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Dict, List

from pvi._schema_utils import as_discriminated_union, desc
from pvi.device import Device, DeviceRef


@dataclass
class IndexEntry:
    label: Annotated[str, desc("Button label")]
    file_name: Annotated[str, desc("File name of UI file")]
    macros: Annotated[Dict[str, str], desc("Macros to launch UI with")]


@as_discriminated_union
@dataclass
class Formatter:
    def format(self, device: Device, prefix: str, path: Path):
        raise NotImplementedError(self)

    def format_index(self, label: str, index_entries: List[IndexEntry], path: Path):
        """Format an index of buttons to open the given UIs.

        Args:
            label: Title of generated index UI
            index_entries: Buttons to format on the index UI
            path: Output path of generated UI

        """
        self.format(
            Device(
                label,
                children=[
                    DeviceRef(index.label, index.file_name, index.macros)
                    for index in index_entries
                ],
            ),
            prefix="Index",
            path=path,
        )
