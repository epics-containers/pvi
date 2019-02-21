import unittest

from pvi.asynparam import Float64AsynParam
from pvi.record import AIRecord, AORecord
from pvi.modules.asyn.parameters import float64, truncate_desc


class TestFloat64(unittest.TestCase):

    def setUp(self):
        self.name = "ThresholdEnergy"
        self.desc = """
Threshold energy in keV

camserver uses this value to set the discriminators in each pixel.
It is typically set to the incident x-ray energy ($(P)$(R)Energy),
but sometimes other values may be preferable.
"""
        self.prec = 3
        self.egu = "keV"
        self.initial_value = 10
        self.autosave_fields = "VAL"
        self.widget = "TextInput"
        self.group = "AncillaryInformation"

    def test_float64_input_values_case1(self):
        demand = "Yes"
        readback = "Yes"
        intermediate_objects = float64(self.name, self.desc, self.prec,
                                       self.egu, self.autosave_fields,
                                       self.widget, self.group,
                                       self.initial_value, demand,
                                       readback)

        assert len(intermediate_objects) == 3

        returned_object_types = [type(obj) for obj in intermediate_objects]

        for expected_type in [AIRecord, AORecord, Float64AsynParam]:
            assert expected_type in returned_object_types

    def test_float64_input_values_case2(self):
        demand = "Yes"
        readback = "No"
        intermediate_objects = float64(self.name, self.desc, self.prec,
                                       self.egu, self.autosave_fields,
                                       self.widget, self.group,
                                       self.initial_value, demand,
                                       readback)

        assert len(intermediate_objects) == 2

        returned_object_types = [type(obj) for obj in intermediate_objects]

        for expected_type in [AORecord, Float64AsynParam]:
            assert expected_type in returned_object_types

        for unexpected_type in [AIRecord]:
            assert unexpected_type not in returned_object_types

    def test_float64_input_values_case3(self):
        demand = "No"
        readback = "No"
        intermediate_objects = float64(self.name, self.desc, self.prec,
                                       self.egu, self.autosave_fields,
                                       self.widget, self.group,
                                       self.initial_value, demand,
                                       readback)

        assert len(intermediate_objects) == 1

        returned_object_types = [type(obj) for obj in intermediate_objects]

        for expected_type in [Float64AsynParam]:
            assert expected_type in returned_object_types

        for unexpected_type in [AIRecord, AORecord]:
            assert unexpected_type not in returned_object_types


class TestTruncateDesc(unittest.TestCase):

    def test_empty_input(self):
        assert truncate_desc("") == ""

    def test_leading_trailing_newlines_input(self):
        input_string = """

Threshold energy in keV

camserver uses this value to set the discriminators in each pixel.
It is typically set to the incident x-ray energy ($(P)$(R)Energy),
but sometimes other values may be preferable.


"""
        expected_output = "Threshold energy in keV"

        assert truncate_desc(input_string) == expected_output

    def test_leading_trailing_whitespace_input(self):
        input_string = """
    Threshold energy in keV

camserver uses this value to set the discriminators in each pixel.
It is typically set to the incident x-ray energy ($(P)$(R)Energy),
but sometimes other values may be preferable.
    """

        expected_output = "Threshold energy in keV"

        assert truncate_desc(input_string) == expected_output
