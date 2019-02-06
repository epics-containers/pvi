class AsynParam(object):

    """Abstract base class for all AsynParams"""

    def __init__(self, name, initial_value):
        self.name = name
        self.initial_value = initial_value

    @property
    def asyntyp(self):
        raise NotImplementedError(self)
