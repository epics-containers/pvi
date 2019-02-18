import unittest
from mock import Mock, patch

from pvi.yaml_loader import lookup_component


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
