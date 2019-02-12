import unittest

from pvi.modules.asyn.parameters import float64


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

    def test_float64_list_length_case1(self):
        demand = "Yes"
        readback = "Yes"
        intermediate_objects = float64(self.name, self.desc, self.prec,
                                       self.egu, self.autosave_fields,
                                       self.widget, self.group,
                                       self.initial_value, demand,
                                       readback)

        assert len(intermediate_objects) == 3

    def test_float64_list_length_case2(self):
        demand = "Yes"
        readback = "No"
        intermediate_objects = float64(self.name, self.desc, self.prec,
                                       self.egu, self.autosave_fields,
                                       self.widget, self.group,
                                       self.initial_value, demand,
                                       readback)

        assert len(intermediate_objects) == 2

    def test_float64_list_length_case3(self):
        demand = "No"
        readback = "No"
        intermediate_objects = float64(self.name, self.desc, self.prec,
                                       self.egu, self.autosave_fields,
                                       self.widget, self.group,
                                       self.initial_value, demand,
                                       readback)

        assert len(intermediate_objects) == 1
