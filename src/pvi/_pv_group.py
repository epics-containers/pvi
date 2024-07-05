import re
from pathlib import Path

from pvi.device import (
    ComponentUnion,
    Device,
    Grid,
    Group,
    Tree,
    enforce_pascal_case,
    walk,
)


def find_pvs(pvs: list[str], file_path: Path) -> tuple[list[str], list[str]]:
    """Search for the PVs in the file and return lists of found and not found pvs"""

    with open(file_path) as f:
        file_content = f.read()

    pv_coordinates: dict[int, list[str]] = {}
    remaining_pvs = list(pvs)
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


def group_by_ui(device: Device, ui_paths: list[Path]) -> Tree:
    signals: list[ComponentUnion] = list(walk(device.children))

    # PVs without macros to search for in UI
    pv_names = [s.name for s in signals]

    group_pv_map: dict[str, list[str]] = {}
    for ui in ui_paths:
        ui_pvs, pv_names = find_pvs(pv_names, ui)
        if ui_pvs:
            group_pv_map[ui.stem] = ui_pvs

    if pv_names:
        print(f"Did not find group for {' | '.join(pv_names)}")

    # Create groups for parameters we found in the files
    ui_groups: list[Group] = [
        Group(
            name=enforce_pascal_case(group_name),
            layout=Grid(labelled=True),
            children=[  # Note: Need to preserve order in group_pvs here
                signal
                for pv_name in group_pvs
                for signal in signals
                if signal.name == pv_name
            ],
            label=group_name if enforce_pascal_case(group_name) != group_name else None,
        )
        for group_name, group_pvs in group_pv_map.items()
    ]

    # Separate any parameters we failed to find a group for
    grouped_pvs = [pv_name for group in ui_groups for pv_name in group.children]
    ungrouped_pvs = [pv_name for pv_name in signals if pv_name not in grouped_pvs]

    # Add any ungrouped parameters on the end
    if ungrouped_pvs:
        ui_groups.append(
            Group(
                name=enforce_pascal_case(device.label) + "Misc",
                layout=Grid(labelled=True),
                children=ungrouped_pvs,
                label=device.label + " Ungrouped",
            )
        )

    return ui_groups
