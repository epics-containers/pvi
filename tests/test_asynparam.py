import unittest

from pvi.asynparam import AsynParam


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
