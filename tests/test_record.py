import unittest

from pvi.record import Record, AIRecord, AORecord


class TestRecord(unittest.TestCase):

    def setUp(self):
        self.record = Record("ThresholdEnergy", {"PINI": "YES"}, {"autosaveFields": "VAL"})

    def test_suffix_attribute(self):
        assert self.record.suffix == "ThresholdEnergy"

    def test_fields_attribute(self):
        assert self.record.fields == {"PINI": "YES"}

    def test_infos_attribute(self):
        assert self.record.infos == {"autosaveFields": "VAL"}

    def test_rtyp_property(self):
        with self.assertRaises(NotImplementedError):
            self.record.rtyp


class TestAIRecord(unittest.TestCase):

    def test_rtyp_property(self):
        airecord = AIRecord("ThresholdEnergy_RBV", {"EGU": "keV"}, {"autosaveFields": "VAL"})
        assert airecord.rtyp == "ai"


class TestAORecord(unittest.TestCase):

    def test_rtyp_property(self):
        aorecord = AORecord("ThresholdEnergy", {"PINI": "YES"}, {"autosaveFields": "VAL"})
        assert aorecord.rtyp == "ao"
