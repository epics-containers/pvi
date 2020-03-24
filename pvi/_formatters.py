from ._types import WithType


class Formatter(WithType):
    template_path: str
    device_path: str
    opi_path: str
    bob_path: str
    adl_path: str
    edl_path: str
