from pathlib import Path

import pytest

from pvi._format.base import Formatter, IndexEntry
from pvi._format.dls import DLSFormatter
from pvi._format.template import format_template
from pvi._yaml_utils import deserialize_yaml
from pvi.device import (
    LED,
    ButtonPanel,
    ComboBox,
    Device,
    DeviceRef,
    Grid,
    Group,
    SignalR,
    SignalRW,
    SignalW,
    SubScreen,
    TableRead,
    TableWrite,
    TextFormat,
    TextRead,
    TextWrite,
)

HERE = Path(__file__).parent


@pytest.mark.parametrize(
    "filename,formatter",
    [
        ("text_format.adl", "aps.adl.pvi.formatter.yaml"),
        ("text_format.edl", "dls.edl.pvi.formatter.yaml"),
        ("text_format.bob", "dls.bob.pvi.formatter.yaml"),
    ],
)
def test_text_format(tmp_path, helper, filename, formatter):
    formatter_yaml = HERE / "format" / "input" / formatter
    formatter = deserialize_yaml(Formatter, formatter_yaml)

    components = []
    for format in TextFormat:
        components.append(
            SignalRW(
                format.name.title(),
                pv=format.name.title(),
                widget=TextWrite(format=format),
                read_pv=f"{format.name.title()}_RBV",
                read_widget=TextRead(format=format),
            )
        )

    device = Device("Text Device", children=components)

    expected_ui = HERE / "format" / "output" / filename
    output_ui = tmp_path / filename
    formatter.format(device, "$(P)", output_ui)

    helper.assert_output_matches(expected_ui, output_ui)


def test_button(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = deserialize_yaml(Formatter, formatter_yaml)

    acquire_time = SignalRW(
        "AcquireTime",
        pv="AcquireTime",
        widget=TextWrite(),
        read_pv="AcquireTime_RBV",
        read_widget=TextRead(),
    )
    acquire = SignalW(
        "Acquire",
        pv="Acquire",
        widget=ButtonPanel(actions={"Start": 1, "Stop": 0}),
    )
    acquire_w_rbv = SignalRW(
        "AcquireWithRBV",
        pv="Acquire",
        widget=ButtonPanel(actions={"Start": 1, "Stop": 0}),
        read_pv="Acquire_RBV",
        read_widget=LED(),
    )
    device = Device("Simple Device", children=[acquire_time, acquire, acquire_w_rbv])

    expected_bob = HERE / "format" / "output" / "button.bob"
    output_bob = tmp_path / "button.bob"
    formatter.format(device, "$(P)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_pva_table(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = deserialize_yaml(Formatter, formatter_yaml)

    table = SignalR(
        "PVATable",
        "PVATable",
        TableWrite([TextWrite(), LED(), ComboBox(["1", "A", "True"])]),
    )
    device = Device("TableDevice", children=[table])

    expected_bob = HERE / "format" / "output" / "pva_table.bob"
    output_bob = tmp_path / "pva_table.bob"
    formatter.format(device, "$(P)$(R)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_pva_table_panda(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = deserialize_yaml(Formatter, formatter_yaml)

    table = SignalR(
        "PandA ",
        "PANDAQSRV:SEQ1:TABLE",
        TableRead([TextRead()] * 4 + [LED()] * 6 + [TextRead()] + [LED()] * 6),
    )
    device = Device("TableDevice", children=[table])

    expected_bob = HERE / "format" / "output" / "pva_table_panda.bob"
    output_bob = tmp_path / "pva_table_panda.bob"
    formatter.format(device, "", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_combo_box(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = deserialize_yaml(Formatter, formatter_yaml)

    combo_box = SignalR("Enum", "Enum", ComboBox(["A", "B", "C"]))
    device = Device("Device", children=[combo_box])

    expected_bob = HERE / "format" / "output" / "combo_box.bob"
    output_bob = tmp_path / "combo_box.bob"
    formatter.format(device, "$(P)$(R)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_device_ref(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = deserialize_yaml(Formatter, formatter_yaml)

    # Make a button to open an existing screen - use screen from combo box test
    device_ref = DeviceRef(
        "ComboBox", pv="COMBOBOX", ui="combo_box", macros={"P": "EIGER", "R": ":CAM:"}
    )
    device = Device("Device", children=[device_ref])

    expected_bob = HERE / "format" / "output" / "device_ref.bob"
    output_bob = tmp_path / "device_ref.bob"
    formatter.format(device, "$(P)$(R)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_group_sub_screen(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = deserialize_yaml(Formatter, formatter_yaml)

    # This tests every valid combination of nesting Group and SubScreen
    signals = [
        SignalR("A", "A", widget=TextRead()),
        Group(
            "Group 1",
            layout=SubScreen(),
            children=[
                SignalR("Group 1 B", "GROUP1:B", widget=TextRead()),
                Group(
                    "Group 2",
                    layout=Grid(),
                    children=[
                        SignalR("Group 2 C", "GROUP1:GROUP2:C", widget=TextRead()),
                        SignalR("Group 2 D", "GROUP1:GROUP2:D", widget=TextRead()),
                    ],
                ),
            ],
        ),
        Group(
            "Group 3",
            layout=Grid(),
            children=[
                SignalR("Group 3 E", "GROUP3:E", widget=TextRead()),
                Group(
                    "Group 4",
                    layout=SubScreen(),
                    children=[
                        SignalR("Group 4 F", "GROUP3:GROUP4:F", widget=TextRead()),
                        Group(
                            "Group 5",
                            layout=Grid(),
                            children=[
                                SignalR(
                                    "Group 5 G",
                                    "GROUP3:GROUP4:GROUP5:G",
                                    widget=TextRead(),
                                ),
                                SignalR(
                                    "Group 5 H",
                                    "GROUP3:GROUP4:GROUP5:H",
                                    widget=TextRead(),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]
    device = Device("Device", children=signals)

    expected_bob = HERE / "format" / "output" / "sub_screen.bob"
    output_bob = tmp_path / "sub_screen.bob"
    formatter.format(device, "$(P)$(R)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_index(tmp_path, helper):
    expected_bob = HERE / "format" / "output" / "index.bob"
    output_bob = tmp_path / "index.bob"

    DLSFormatter().format_index(
        "Index",
        [
            IndexEntry("Button", "button.bob", {"P": "BUTTON"}),
            IndexEntry("ComboBox", "combo_box.bob", {"P": "COMBOBOX"}),
            IndexEntry("Table", "pva_table.bob", {"P": "TABLE"}),
        ],
        output_bob,
    )

    helper.assert_output_matches(expected_bob, output_bob)


def test_pvi_template(tmp_path, helper):
    read = SignalR("Read", "Read")
    write = SignalW("Write", "Write")
    read_write = SignalRW("ReadWrite", "ReadWrite")
    device = Device("Template Device", children=[read, write, read_write])

    expected_bob = HERE / "format" / "output" / "pvi.template"
    output_template = tmp_path / "pvi.template"
    format_template(device, "$(P)$(R)", output_template)

    helper.assert_output_matches(expected_bob, output_template)
