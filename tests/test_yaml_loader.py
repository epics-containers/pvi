import unittest
from mock import Mock, patch

from pvi.yaml_loader import lookup_component, get_component_yaml_info

yaml_text = """
type: pvi.producers.MyProducer
overridden_by: $(yamlname).local.yaml

takes:
  - type: builtin.takes.string
    name: P
    description: Record prefix part 1

  - type: builtin.takes.string
    name: R
    description: Record prefix part 2

  - type: builtin.takes.string
    name: PORT
    description: Port name

components:
  - type: mymodule.components.MyComponent
    name: SomeName
    description: Some description
    prec: 3
    egu: keV
    initial_value: 10
    autosave_fields: VAL
    demand: Yes
    readback: Yes
    widget: TextInput
    group: AncillaryInformation
"""


class TestLookupComponent(unittest.TestCase):

    @patch("importlib.import_module")
    def test_load_component(self, mock_import):

        def component():
            pass

        component_type = "mymodule.components.MyComponent"
        filename = "yamltest.yaml"
        lineno = 1

        mock_import.return_value = Mock(MyComponent=component)
        returned_component = lookup_component(component_type, filename, lineno)

        mock_import.assert_called_once_with("pvi.modules.mymodule.components")
        assert returned_component == component


class TestGetComponentYamlInfo(unittest.TestCase):

    def test_get_info_for_one_component(self):
        filepath = "/tmp/yamltest.yaml"

        with open(filepath, "w") as f:
            f.write(yaml_text)

        expected_component_type = "mymodule.components.MyComponent"
        expected_component_type_lineno = 18
        expected_params = dict(
            name="SomeName",
            description="Some description",
            prec=3,
            egu="keV",
            autosave_fields="VAL",
            widget="TextInput",
            group="AncillaryInformation",
            initial_value=10,
            demand="Yes",
            readback="Yes"
        )

        components_and_info = get_component_yaml_info(filepath)
        returned_component_type = components_and_info[0][0]
        returned_component_type_lineno = components_and_info[0][2]
        returned_params = components_and_info[0][3]

        assert returned_component_type == expected_component_type
        assert returned_component_type_lineno == expected_component_type_lineno
        assert returned_params == expected_params
