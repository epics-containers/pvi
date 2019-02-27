import unittest
from mock import Mock, patch
from annotypes import Array, NO_DEFAULT

from pvi.yaml_loader import lookup_component, get_component_yaml_info, \
    get_intermediate_objects, ComponentData, validate

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

        all_components_data = get_component_yaml_info(filepath)
        returned_component_type = all_components_data[0].component_type
        returned_component_type_lineno = all_components_data[0].lineno
        returned_params = all_components_data[0].component_params

        assert returned_component_type == expected_component_type
        assert returned_component_type_lineno == expected_component_type_lineno
        assert returned_params == expected_params


class TestGetIntermediateObjects(unittest.TestCase):

    @patch("pvi.yaml_loader.lookup_component")
    def test_args_passed_to_component(self, mock_lookup):
        filepath = "/tmp/yamltest.yaml"
        component_type = "mymodule.components.MyComponent"
        component_type_lineno = 18
        component_params = dict(
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

        # mock_lookup should return a component, and that component should
        # return an array of intermediate objects
        mock_lookup.return_value.return_value = Array[Mock]([Mock()])

        component_data = ComponentData(component_type, filepath,
                                       component_type_lineno, component_params)

        get_intermediate_objects([component_data])

        mock_component = mock_lookup.return_value
        mock_component.assert_called_once_with(name="SomeName",
                                               description="Some description",
                                               prec=3,
                                               egu="keV",
                                               autosave_fields="VAL",
                                               widget="TextInput",
                                               group="AncillaryInformation",
                                               initial_value=10,
                                               demand="Yes",
                                               readback="Yes")


class TestValidate(unittest.TestCase):

    def test_string_validation(self):
        component_params = dict(my_param=1)

        mock_anno = Mock()
        mock_anno.typ = str

        mock_component = Mock()
        mock_component.call_types = dict(my_param=mock_anno)

        expected_params = dict(my_param="1")
        validated_params = validate(mock_component, component_params)

        assert validated_params == expected_params

    def test_int_validation(self):
        component_params = dict(my_param="2")

        mock_anno = Mock()
        mock_anno.typ = int

        mock_component = Mock()
        mock_component.call_types = dict(my_param=mock_anno)

        expected_params = dict(my_param=2)
        validated_params = validate(mock_component, component_params)

        assert validated_params == expected_params

    def test_missing_required_param(self):
        component_params = dict()

        mock_anno = Mock()
        mock_anno.typ = int
        mock_anno.default = NO_DEFAULT

        mock_component = Mock()
        mock_component.call_types = dict(my_param=mock_anno)

        with self.assertRaises(AssertionError):
            validate(mock_component, component_params)
