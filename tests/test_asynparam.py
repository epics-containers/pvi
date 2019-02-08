import unittest

from pvi.asynparam import AsynParam, Float64AsynParam


class TestAsynParam(unittest.TestCase):

    def setUp(self):
        self.asynparam = AsynParam("THRESHOLDENERGY", 10)

    def test_name_attribute(self):
        assert self.asynparam.name == "THRESHOLDENERGY"

    def test_initial_value_attribute(self):
        assert self.asynparam.initial_value == 10

    def test_asyntyp_property(self):
        with self.assertRaises(NotImplementedError):
            self.asynparam.asyntyp


class TestFloat64AsynParam(unittest.TestCase):

    def test_asyntyp_property(self):
        float64_asynparam = Float64AsynParam("THRESHOLDENERGY", 10)
        assert float64_asynparam.asyntyp == "asynParamFloat64"
