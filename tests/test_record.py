import unittest

from pvi.record import Record, AIRecord, AORecord


class TestRecord(unittest.TestCase):

    def setUp(self):
        self.record = Record("ThresholdEnergy",
                             "@asyn($(PORT),$(ADDR),$(TIMEOUT))",
                             {"PINI": "YES"}, {"autosaveFields": "VAL"})

    def test_suffix_attribute(self):
        assert self.record.suffix == "ThresholdEnergy"

    def test_inout_parameter_attribute(self):
        assert self.record.inout_parameter == \
               "@asyn($(PORT),$(ADDR),$(TIMEOUT))"

    def test_fields_attribute(self):
        assert self.record.fields == {"PINI": "YES"}

    def test_infos_attribute(self):
        assert self.record.infos == {"autosaveFields": "VAL"}

    def test_rtyp_property(self):
        with self.assertRaises(NotImplementedError):
            self.record.rtyp

    def test_inout_field_property(self):
        with self.assertRaises(NotImplementedError):
            self.record.inout_field


class TestAIRecord(unittest.TestCase):

    def setUp(self):
        self.airecord = AIRecord("ThresholdEnergy_RBV",
                                 "@asyn($(PORT),$(ADDR),$(TIMEOUT))",
                                 {"EGU": "keV"}, {"autosaveFields": "VAL"})

    def test_rtyp_property(self):
        assert self.airecord.rtyp == "ai"

    def test_inout_field_property(self):
        assert self.airecord.inout_field == "INP"


class TestAORecord(unittest.TestCase):

    def setUp(self):
        self.aorecord = AORecord("ThresholdEnergy",
                                 "@asyn($(PORT),$(ADDR),$(TIMEOUT))",
                                 {"PINI": "YES"}, {"autosaveFields": "VAL"})

    def test_rtyp_property(self):
        assert self.aorecord.rtyp == "ao"

    def test_inout_field_property(self):
        assert self.aorecord.inout_field == "OUT"
