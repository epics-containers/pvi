import re
from pathlib import Path
from typing import Dict, List, Tuple

from pvi._produce.asyn import AsynParameter, AsynProducer
from pvi.device import Grid, Group, walk


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


def sanitize_name(name: str) -> str:
    name = name.replace(" ", "")
    name = name.replace("-", "")
    name = name.replace("_", "")
    return name


def group_parameters(
    producer: AsynProducer, ui_paths: List[Path]
) -> List[Group[AsynParameter]]:
    initial_parameters: List[AsynParameter] = [
        param for param in walk(producer.parameters) if isinstance(param, AsynParameter)
    ]

    # Group PVs that appear in the given ui files
    pvs = [
        node.name
        for node in walk(producer.parameters)
        if isinstance(node, AsynParameter)
    ]

    group_pv_map: Dict[str, List[str]] = {}
    for ui in ui_paths:
        ui_pvs, pvs = find_pvs(pvs, ui)
        if ui_pvs:
            group_pv_map[ui.stem] = ui_pvs

    if pvs:
        print(f'Did not find group for {"|".join(pvs)}')

    # Create groups for parameters we found in the files
    ui_groups: List[Group[AsynParameter]] = [
        Group(
            sanitize_name(group_name),
            Grid(labelled=True),
            [  # Note: Need to preserve order in group_pvs here
                param
                for pv in group_pvs
                for param in initial_parameters
                if param.name == pv
            ],
        )
        for group_name, group_pvs in group_pv_map.items()
    ]

    # Separate any parameters we failed to find a group for
    grouped_parameters = [param for group in ui_groups for param in group.children]
    ungrouped_parameters = [
        param for param in initial_parameters if param not in grouped_parameters
    ]

    # Replace with grouped parameters and any ungrouped parameters on the end
    if ungrouped_parameters:
        ui_groups.append(
            Group(
                sanitize_name(producer.label + "Misc"),
                Grid(labelled=True),
                ungrouped_parameters,
            )
        )

    return ui_groups
