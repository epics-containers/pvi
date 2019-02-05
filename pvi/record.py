class Record(object):

    def __init__(self, prefix, suffix, fields, infos):
        self.prefix = prefix
        self.suffix = suffix
        self.fields = fields
        self.infos = infos


class AIRecord(Record):

    def __init__(self, prefix, suffix, fields, infos):
        super(AIRecord, self).__init__(prefix, suffix, fields, infos)

    @property
    def rtyp(self):
        return "ai"
