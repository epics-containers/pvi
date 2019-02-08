class AsynParam(object):

    """Abstract base class for all AsynParams"""

    def __init__(self, name, initial_value):
        self.name = name
        self.initial_value = initial_value

    @property
    def asyntyp(self):
        raise NotImplementedError(self)


class Float64AsynParam(AsynParam):

    def __init__(self, name, initial_value):
        super(Float64AsynParam, self).__init__(name, initial_value)

    @property
    def asyntyp(self):
        return "asynParamFloat64"
