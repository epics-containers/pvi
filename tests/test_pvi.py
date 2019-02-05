import unittest

from pvi.record import Record


class TestRecord(unittest.TestCase):

    def setUp(self):
        self.record = Record("$(P)$(R)", "ThresholdEnergy", {"PINI": "YES"}, {"autosaveFields": "VAL"})

    def test_prefix_attribute(self):
        assert self.record.prefix == "$(P)$(R)"

    def test_suffix_attribute(self):
        assert self.record.suffix == "ThresholdEnergy"

    def test_fields_attribute(self):
        assert self.record.fields == {"PINI": "YES"}

    def test_infos_attribute(self):
        assert self.record.infos == {"autosaveFields": "VAL"}
