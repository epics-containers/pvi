import unittest

from pvi.modules.asyn.parameters import float64


class TestFloat64(unittest.TestCase):

    def test_float64_list_length(self):
        name = "ThresholdEnergy"
        desc = """
Threshold energy in keV

camserver uses this value to set the discriminators in each pixel.
It is typically set to the incident x-ray energy ($(P)$(R)Energy),
but sometimes other values may be preferable.
"""
        prec = 3
        egu = "keV"
        initial_value = 10
        autosave_fields = "VAL"
        demand = "Yes"
        readback = "Yes"
        widget = "TextInput"
        group = "AncillaryInformation"
        intermediate_objects = float64(name, desc, prec, egu, autosave_fields,
                                       widget, group, initial_value, demand,
                                       readback)

        assert len(intermediate_objects) == 3
