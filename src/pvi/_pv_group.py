from pathlib import Path
from typing import List, NewType

from pvi._produce.asyn import AsynParameter, AsynProducer
from pvi.device import walk


def find_producer_pvs(producer: AsynProducer, file_path: Path) -> List[str]:
    """Return a subset of the producer PVs in the given file"""

    pvs = [
        node.name
        for node in walk(producer.parameters)
        if isinstance(node, AsynParameter)
    ]

    with open(file_path, "r") as f:
        file_content = f.read()

    return [pv for pv in pvs if pv in file_content]
