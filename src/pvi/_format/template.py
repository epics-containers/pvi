from dataclasses import dataclass
from pathlib import Path
from typing import List

from jinja2 import Template

from pvi.device import (
    Device,
    SignalR,
    SignalRW,
    SignalW,
    SignalX,
    walk,
)

PVI_TEMPLATE = Path(__file__).parent / "pvi.template.jinja"


@dataclass
class PviRecord:
    name: str
    pv: str
    access: str


def format_template(device: Device, pv_prefix: str, output: Path):
    records: List[PviRecord] = []
    for node in walk(device.children):
        match node:
            case SignalRW(read_pv=r, write_pv=w) as signal if r == w:
                records.append(PviRecord(signal.name, signal.write_pv, "rw"))
            case SignalRW() as signal:
                records.append(PviRecord(signal.name, signal.write_pv, "w"))
                records.append(PviRecord(signal.name, signal.read_pv, "r"))
            case SignalX() as signal:
                records.append(PviRecord(signal.name, signal.write_pv, "x"))
            case SignalW() as signal:
                records.append(PviRecord(signal.name, signal.write_pv, "w"))
            case SignalR() as signal:
                records.append(PviRecord(signal.name, signal.read_pv, "r"))

    with output.open("w") as expanded, open(PVI_TEMPLATE, "r") as template:
        template_txt = Template(template.read()).render(
            device=device.label, pv_prefix=pv_prefix, records=records
        )
        expanded.write(template_txt)
