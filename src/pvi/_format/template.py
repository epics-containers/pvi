from dataclasses import dataclass
from pathlib import Path
from typing import List

from jinja2 import Template

from pvi.device import Device, SignalR, SignalRW, SignalW, signal_access_mode, walk

PVI_TEMPLATE = Path(__file__).parent / "pvi.template.jinja"


@dataclass
class PviRecord:
    name: str
    access: str


def format_template(device: Device, prefix: str, output: Path):
    records: List[PviRecord] = []
    for node in walk(device.children):
        match node:
            case SignalR() | SignalW() | SignalRW() as signal:
                records.append(PviRecord(signal.pv, signal_access_mode(signal)))

    with output.open("w") as expanded, open(PVI_TEMPLATE, "r") as template:
        template_txt = Template(template.read()).render(
            records=records, prefix=prefix, device=device.label
        )
        expanded.write(template_txt)
