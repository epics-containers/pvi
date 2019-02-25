from annotypes import Anno, Mapping

from pvi.intermediate import Intermediate, ASuffix

with Anno("The field names and values of an asyn parameter"):
    AFields = Mapping[str, str]

with Anno("The info names and values of an asyn parameter"):
    AInfos = Mapping[str, str]


class Record(Intermediate):

    """Abstract base class for all Records, so it's not advised to
    create instances of this Record class, only of its subclasses
    """

    def __init__(self, suffix, fields, infos):
        # type: (ASuffix, AFields, AInfos) -> None
        self.suffix = suffix
        self.fields = fields
        self.infos = infos

    @property
    def rtyp(self):
        raise NotImplementedError(self)

    @property
    def inout_field(self):
        raise NotImplementedError(self)


class AIRecord(Record):

    def __init__(self, suffix, fields, infos):
        # type: (ASuffix, AFields, AInfos) -> None
        super(AIRecord, self).__init__(suffix, fields, infos)

    @property
    def rtyp(self):
        return "ai"

    @property
    def inout_field(self):
        return "INP"


class AORecord(Record):

    def __init__(self, suffix, fields, infos):
        # type: (ASuffix, AFields, AInfos) -> None
        super(AORecord, self).__init__(suffix, fields, infos)

    @property
    def rtyp(self):
        return "ao"

    @property
    def inout_field(self):
        return "OUT"
