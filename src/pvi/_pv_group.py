import re
from pathlib import Path
from typing import Dict, List, Tuple


def find_pvs(pvs: List[str], file_path: Path) -> Tuple[List[str], List[str]]:
    """Search for the PVs in the file and return lists of found and not found pvs"""

    with open(file_path, "r") as f:
        file_content = f.read()

    pv_coordinates: Dict[int, List[str]] = {}
    remaining_pvs = [pv for pv in pvs]
    for pv in pvs:
        if pv not in file_content:
            continue

        # This regex searches for the first y coordinate before the given PV
        # https://regex101.com/r/41yX56/1
        widget_regex = re.compile(
            "".join(
                (
                    # The y-coordinate in a match group named `y`
                    r"y=(?P<y>\d+)",
                    # Negative lookahead asserting no further y-coordinate before PV
                    r"(?!.*y=.*" + pv + r")",
                    # Any characters and then PV
                    r".*" + pv,
                )
            ),
            re.MULTILINE | re.DOTALL,
        )
        match = re.search(widget_regex, file_content)

        assert match, f"{pv} found in {file_path.name} but did not match a y coordinate"

        y = int(match["y"])
        if y in pv_coordinates:
            pv_coordinates[y].append(pv)
        else:
            pv_coordinates[y] = [pv]

        remaining_pvs.remove(pv)

    grouped_pvs = []
    for coord in sorted(pv_coordinates.keys()):
        grouped_pvs.extend(pv_coordinates[coord])

    return grouped_pvs, remaining_pvs
