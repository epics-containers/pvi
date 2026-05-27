from pathlib import Path

import pytest
from pydantic import ValidationError

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
    SignalX,
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
                write_pv=f"$(P){format.name.title()}",
                write_widget=TextWrite(format=format),
                read_pv=f"$(P){format.name.title()}_RBV",
                read_widget=TextRead(format=format),
            )
        )

    device = Device(label="Text Device - $(P)", children=components)

    expected_ui = HERE / "format" / "output" / filename
    output_ui = tmp_path / filename
    formatter.format(device, output_ui)

    helper.assert_output_matches(expected_ui, output_ui)


def test_button(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    acquire_time = SignalRW(
        name="AcquireTime",
        write_pv="$(P)AcquireTime",
        write_widget=TextWrite(),
        read_pv="$(P)AcquireTime_RBV",
        read_widget=TextRead(),
    )
    acquire = SignalW(
        name="Acquire",
        write_pv="$(P)Acquire",
        write_widget=ButtonPanel(actions={"Start": "1", "Stop": "0"}),
    )
    acquire_w_rbv = SignalRW(
        name="AcquireWithRBV",
        write_pv="$(P)Acquire",
        write_widget=ButtonPanel(actions={"Start": "1", "Stop": "0"}),
        read_pv="$(P)Acquire_RBV",
        read_widget=LED(),
    )
    device = Device(
        label="Simple Device - $(P)", children=[acquire_time, acquire, acquire_w_rbv]
    )

    expected_bob = HERE / "format" / "output" / "button.bob"
    output_bob = tmp_path / "button.bob"
    formatter.format(device, output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_button_raises(tmp_path, helper):
    with pytest.raises(ValidationError, match="String should match pattern"):
        ButtonPanel(actions={"start": "1", "Stop": "0"})


def test_pva_table(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    table = SignalRW(
        name="PVATable",
        write_pv="$(P)PVATable",
        write_widget=TableWrite(
            widgets=[TextWrite(), ComboBox(choices=["1", "A", "True"])]
        ),
    )
    device = Device(label="TableDevice - $(P)", children=[table])

    expected_bob = HERE / "format" / "output" / "pva_table.bob"
    output_bob = tmp_path / "pva_table.bob"
    formatter.format(device, output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_pva_table_panda(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    table = SignalR(
        name="PandA",
        read_pv="PANDAQSRV:SEQ1:TABLE",
        read_widget=TableRead(
            widgets=[TextRead()] * 4 + [LED()] * 6 + [TextRead()] + [LED()] * 6
        ),
    )
    device = Device(label="TableDevice", children=[table])

    expected_bob = HERE / "format" / "output" / "pva_table_panda.bob"
    output_bob = tmp_path / "pva_table_panda.bob"
    formatter.format(device, output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_combo_box(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    combo_box = SignalRW(
        name="Enum",
        write_pv="$(P)Enum",
        write_widget=ComboBox(choices=["A", "B", "C"]),
        read_pv="$(P)Enum_RBV",
    )
    device = Device(label="Device - $(P)", children=[combo_box])

    expected_bob = HERE / "format" / "output" / "combo_box.bob"
    output_bob = tmp_path / "combo_box.bob"
    formatter.format(device, output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_device_ref(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    # Make a button to open an existing screen - use screen from combo box test
    device_ref = DeviceRef(
        name="ComboBox",
        pv="COMBOBOX",
        ui="combo_box",
        macros={"P": "TEST:"},
    )
    device = Device(label="Device - $(P)", children=[device_ref])

    expected_bob = HERE / "format" / "output" / "device_ref.bob"
    output_bob = tmp_path / "device_ref.bob"
    formatter.format(device, output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_group_sub_screen(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    # This tests every valid combination of nesting Group and SubScreen
    signals = [
        SignalR(name="A", read_pv="$(P)A", read_widget=TextRead()),
        Group(
            name="Group1",
            layout=SubScreen(),
            children=[
                SignalR(name="Group1B", read_pv="$(P)GROUP1:B", read_widget=TextRead()),
                Group(
                    name="Group2",
                    layout=Grid(),
                    children=[
                        SignalR(
                            name="Group2C",
                            read_pv="$(P)GROUP1:GROUP2:C",
                            read_widget=TextRead(),
                        ),
                        SignalR(
                            name="Group2D",
                            read_pv="$(P)GROUP1:GROUP2:D",
                            read_widget=TextRead(),
                        ),
                    ],
                ),
            ],
        ),
        Group(
            name="Group3",
            layout=Grid(),
            children=[
                SignalR(name="Group3E", read_pv="$(P)GROUP3:E", read_widget=TextRead()),
                Group(
                    name="Group4",
                    layout=SubScreen(),
                    children=[
                        SignalR(
                            name="Group4F",
                            read_pv="$(P)GROUP3:GROUP4:F",
                            read_widget=TextRead(),
                        ),
                        Group(
                            name="Group5",
                            layout=Grid(),
                            children=[
                                SignalR(
                                    name="Group5G",
                                    read_pv="$(P)GROUP3:GROUP4:GROUP5:G",
                                    read_widget=TextRead(),
                                ),
                                SignalR(
                                    name="Group5H",
                                    read_pv="$(P)GROUP3:GROUP4:GROUP5:H",
                                    read_widget=TextRead(),
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
    formatter.format(device, output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_index(tmp_path, helper):
    expected_bob = HERE / "format" / "output" / "index.bob"
    output_bob = tmp_path / "index.bob"

    DLSFormatter().format_index(
        "Index",
        [
            IndexEntry(label="Button - $(P)", ui="button.bob", macros={"P": "TEST:"}),
            IndexEntry(label="ComboBox", ui="combo_box.bob", macros={"P": "TEST:"}),
            # Check that lower case name is OK and will be capitalized to avoid
            # PascalCase validation error
            IndexEntry(label="table", ui="pva_table.bob", macros={"P": "TEST:"}),
        ],
        output_bob,
    )

    helper.assert_output_matches(expected_bob, output_bob)


def test_pvi_template(tmp_path, helper):
    read = SignalR(name="Read", read_pv="$(P)Read")
    write = SignalW(name="Write", write_pv="$(P)Write")
    read_write = SignalRW(
        name="ReadWrite", write_pv="$(P)ReadWrite", read_pv="$(P)ReadWrite_RBV"
    )
    read_write_single = SignalRW(name="ReadWriteSingle", write_pv="$(P)ReadWriteSingle")
    execute = SignalX(name="Execute", write_pv="$(P)Execute")
    device = Device(
        label="Template Device",
        children=[read, write, read_write, read_write_single, execute],
    )

    expected_bob = HERE / "format" / "output" / "pvi.template"
    output_template = tmp_path / "pvi.template"
    format_template(device, "$(P)", output_template)

    helper.assert_output_matches(expected_bob, output_template)


def test_group_label_preserved_through_subscreen(tmp_path, helper):
    """Group.label must survive SubScreen reconstruction.

    When create_group_formatters reconstructs a Group for SubScreen layout, and
    when move_to_subscreen wraps a Group in a SubScreen, both must forward the
    original label rather than letting it default to None.  Without the fix,
    get_label() falls back to to_title_case(name) and a name like
    "Bl04iEaErio01" would produce "Bl 04i Ea Erio 01" instead of the intended
    "BL04I-EA-E1RIO-01".
    """
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    # A sibling signal forces the SubScreen group through create_group_formatters
    # rather than the single-group special-case expansion of create_screen_formatter,
    # so the SubScreen button is rendered and its label can be verified.
    labeled_sub = Group(
        name="Bl04iEaErio01",
        label="BL04I-EA-E1RIO-01",
        layout=SubScreen(),
        children=[
            SignalR(
                name="Status",
                read_pv="$(P)BL04I:EA:E1RIO01:Status",
                read_widget=TextRead(),
            ),
        ],
    )
    sibling = SignalR(name="OtherSig", read_pv="$(P)Other", read_widget=TextRead())
    device = Device(label="Label Test - $(P)", children=[sibling, labeled_sub])

    expected_bob = HERE / "format" / "output" / "group_label_preserved.bob"
    output_bob = tmp_path / "group_label_preserved.bob"
    formatter.format(device, output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_nested_grid_groups_flattened(tmp_path, helper):
    """A Grid group nested inside another Grid group must be flattened, not raise.

    fastcs emits attribute sub-groups as Group(Grid()).  When a controller with
    INLINE (Grid) group_layout also has such attribute groups, PVI would
    previously raise NotImplementedError.  The fix flattens the inner Grid's
    children directly into the parent Group as individual rows.
    """
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = Formatter.deserialize(formatter_yaml)

    # Outer Grid group containing an inner Grid group — the formerly forbidden nesting.
    outer = Group(
        name="OuterGroup",
        label="Outer Group",
        layout=Grid(),
        children=[
            SignalR(name="DirectSignal", read_pv="$(P)Direct", read_widget=TextRead()),
            Group(
                name="InnerGroup",
                label="Inner Group",
                layout=Grid(),
                children=[
                    SignalR(
                        name="NestedA", read_pv="$(P)Nested:A", read_widget=TextRead()
                    ),
                    SignalR(
                        name="NestedB", read_pv="$(P)Nested:B", read_widget=TextRead()
                    ),
                ],
            ),
        ],
    )
    device = Device(label="Grid Flatten Test - $(P)", children=[outer])

    expected_bob = HERE / "format" / "output" / "nested_grid_flattened.bob"
    output_bob = tmp_path / "nested_grid_flattened.bob"
    formatter.format(device, output_bob)

    helper.assert_output_matches(expected_bob, output_bob)
