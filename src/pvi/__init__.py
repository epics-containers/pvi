from importlib.metadata import version

from . import device

__version__ = version("pvi")
del version

__all__ = ["__version__", "device"]
