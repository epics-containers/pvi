from pathlib import Path

import pytest

from pvi._format.base import Formatter, IndexEntry
from pvi._format.dls import DLSFormatter
from pvi._format.template import format_template
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
    formatter = Formatter.deserialize(formatter_yaml)

    components = []
    for format in TextFormat:
        components.append(
            SignalRW(
                name=format.name.title(),
                pv=format.name.title(),
                widget=TextWrite(format=format),
                read_pv=f"{format.name.title()}_RBV",
                read_widget=TextRead(format=format),
            )
        )

    device = Device(label="Text Device", children=components)

    expected_ui = HERE / "format" / "output" / filename
    output_ui = tmp_path / filename
    formatter.format(device, "$(P)", output_ui)

    helper.assert_output_matches(expected_ui, output_ui)


def test_button(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    acquire_time = SignalRW(
        name="AcquireTime",
        pv="AcquireTime",
        widget=TextWrite(),
        read_pv="AcquireTime_RBV",
        read_widget=TextRead(),
    )
    acquire = SignalW(
        name="Acquire",
        pv="Acquire",
        widget=ButtonPanel(actions={"Start": "1", "Stop": "0"}),
    )
    acquire_w_rbv = SignalRW(
        name="AcquireWithRBV",
        pv="Acquire",
        widget=ButtonPanel(actions={"Start": "1", "Stop": "0"}),
        read_pv="Acquire_RBV",
        read_widget=LED(),
    )
    device = Device(
        label="Simple Device", children=[acquire_time, acquire, acquire_w_rbv]
    )

    expected_bob = HERE / "format" / "output" / "button.bob"
    output_bob = tmp_path / "button.bob"
    formatter.format(device, "$(P)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_pva_table(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    table = SignalRW(
        name="PVATable",
        pv="PVATable",
        widget=TableWrite(
            widgets=[TextWrite(), LED(), ComboBox(choices=["1", "A", "True"])]
        ),
    )
    device = Device(label="TableDevice", children=[table])

    expected_bob = HERE / "format" / "output" / "pva_table.bob"
    output_bob = tmp_path / "pva_table.bob"
    formatter.format(device, "$(P)$(R)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_pva_table_panda(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    table = SignalR(
        name="PandA",
        pv="PANDAQSRV:SEQ1:TABLE",
        widget=TableRead(
            widgets=[TextRead()] * 4 + [LED()] * 6 + [TextRead()] + [LED()] * 6
        ),
    )
    device = Device(label="TableDevice", children=[table])

    expected_bob = HERE / "format" / "output" / "pva_table_panda.bob"
    output_bob = tmp_path / "pva_table_panda.bob"
    formatter.format(device, "", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_combo_box(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    combo_box = SignalRW(
        name="Enum", pv="Enum", widget=ComboBox(choices=["A", "B", "C"])
    )
    device = Device(label="Device", children=[combo_box])

    expected_bob = HERE / "format" / "output" / "combo_box.bob"
    output_bob = tmp_path / "combo_box.bob"
    formatter.format(device, "$(P)$(R)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_device_ref(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    # Make a button to open an existing screen - use screen from combo box test
    device_ref = DeviceRef(
        name="ComboBox",
        pv="COMBOBOX",
        ui="combo_box",
        macros={"P": "EIGER", "R": ":CAM:"},
    )
    device = Device(label="Device", children=[device_ref])

    expected_bob = HERE / "format" / "output" / "device_ref.bob"
    output_bob = tmp_path / "device_ref.bob"
    formatter.format(device, "$(P)$(R)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_group_sub_screen(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    # This tests every valid combination of nesting Group and SubScreen
    signals = [
        SignalR(name="A", pv="A", widget=TextRead()),
        Group(
            name="Group1",
            layout=SubScreen(),
            children=[
                SignalR(name="Group1B", pv="GROUP1:B", widget=TextRead()),
                Group(
                    name="Group2",
                    layout=Grid(),
                    children=[
                        SignalR(
                            name="Group2C", pv="GROUP1:GROUP2:C", widget=TextRead()
                        ),
                        SignalR(
                            name="Group2D", pv="GROUP1:GROUP2:D", widget=TextRead()
                        ),
                    ],
                ),
            ],
        ),
        Group(
            name="Group3",
            layout=Grid(),
            children=[
                SignalR(name="Group3E", pv="GROUP3:E", widget=TextRead()),
                Group(
                    name="Group4",
                    layout=SubScreen(),
                    children=[
                        SignalR(
                            name="Group4F", pv="GROUP3:GROUP4:F", widget=TextRead()
                        ),
                        Group(
                            name="Group5",
                            layout=Grid(),
                            children=[
                                SignalR(
                                    name="Group5G",
                                    pv="GROUP3:GROUP4:GROUP5:G",
                                    widget=TextRead(),
                                ),
                                SignalR(
                                    name="Group5H",
                                    pv="GROUP3:GROUP4:GROUP5:H",
                                    widget=TextRead(),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]
    device = Device(label="Device", children=signals)

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
            IndexEntry(label="Button", ui="button.bob", macros={"P": "BUTTON"}),
            IndexEntry(label="ComboBox", ui="combo_box.bob", macros={"P": "COMBOBOX"}),
            # Check that lower case name is OK and will be capitalized to avoid
            # PascalCase validation error
            IndexEntry(label="table", ui="pva_table.bob", macros={"P": "TABLE"}),
        ],
        output_bob,
    )

    helper.assert_output_matches(expected_bob, output_bob)


def test_pvi_template(tmp_path, helper):
    read = SignalR(name="Read", pv="Read")
    write = SignalW(name="Write", pv="Write")
    read_write = SignalRW(name="ReadWrite", pv="ReadWrite")
    device = Device(label="Template Device", children=[read, write, read_write])

    expected_bob = HERE / "format" / "output" / "pvi.template"
    output_template = tmp_path / "pvi.template"
    format_template(device, "$(P)$(R)", output_template)

    helper.assert_output_matches(expected_bob, output_template)
