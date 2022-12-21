from pathlib import Path

from pvi._format.base import Formatter
from pvi._yaml_utils import deserialize_yaml
from pvi.device import (
    LED,
    ComboBox,
    Device,
    SignalR,
    TableRead,
    TableWrite,
    TextRead,
    TextWrite,
)

HERE = Path(__file__).parent


def test_pva_table(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = deserialize_yaml(Formatter, formatter_yaml)

    table = SignalR(
        "PVATable",
        "PVATable",
        TableWrite([TextWrite(), LED(), ComboBox(["1", "A", "True"])]),
    )
    device = Device("TableDevice", "asynPortDriver", children=[table])

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
    device = Device("TableDevice", "asynPortDriver", children=[table])

    expected_bob = HERE / "format" / "output" / "pva_table_panda.bob"
    output_bob = tmp_path / "pva_table_panda.bob"
    formatter.format(device, "", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)


def test_combo_box(tmp_path, helper):
    formatter_yaml = HERE / "format" / "input" / "dls.bob.pvi.formatter.yaml"
    formatter = deserialize_yaml(Formatter, formatter_yaml)

    combo_box = SignalR("Enum", "Enum", ComboBox(["A", "B", "C"]))
    device = Device("Device", "asynPortDriver", children=[combo_box])

    expected_bob = HERE / "format" / "output" / "combo_box.bob"
    output_bob = tmp_path / "combo_box.bob"
    formatter.format(device, "$(P)$(R)", output_bob)

    helper.assert_output_matches(expected_bob, output_bob)
