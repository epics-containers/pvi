from .aps import APSFormatter
from .base import Formatter
from .dls import DLSFormatter

__all__ = ["Formatter", "APSFormatter", "DLSFormatter"]

# Rebuild all Formatter models at module load time to ensure the type field
# is properly included in the schema and serializer. This must happen after
# all subclasses are defined. We rebuild unconditionally because Device models
# may have already set models_typed=True on the shared class variable.
Formatter.rebuild_child_models()
