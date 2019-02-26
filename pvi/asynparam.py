from annotypes import Anno

from pvi.intermediate import Intermediate, ASuffix

with Anno("The initial value (if any) of an asyn parameter"):
    AInitialValue = int


class AsynParam(Intermediate):

    """Abstract base class for all AsynParams"""

    def __init__(self, name, initial_value):
        # type: (ASuffix, AInitialValue) -> None
        self.name = name
        self.initial_value = initial_value

    @property
    def asyntyp(self):
        raise NotImplementedError(self)


class Float64AsynParam(AsynParam):

    @property
    def asyntyp(self):
        return "asynParamFloat64"
