from pvi.intermediate import Intermediate, ASuffix


class AsynParam(Intermediate):

    """Abstract base class for all AsynParams"""

    def __init__(self, name):
        # type: (ASuffix) -> None
        self.name = name

    @property
    def asyntyp(self):
        raise NotImplementedError(self)


class Float64AsynParam(AsynParam):

    @property
    def asyntyp(self):
        return "asynParamFloat64"
