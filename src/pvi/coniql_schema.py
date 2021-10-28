# This will eventually go in a different module so pvi and coniql (and gda) can use it
from enum import Enum


# These must match the types defined in schema.gql
class DisplayForm(Enum):
    DEFAULT = "DEFAULT"
    STRING = "STRING"
    BINARY = "BINARY"
    DECIMAL = "DECIMAL"
    HEX = "HEX"
    EXPONENTIAL = "EXPONENTIAL"
    ENGINEERING = "ENGINEERING"


class Widget(Enum):
    TEXTINPUT = "TEXTINPUT"
    TEXTUPDATE = "TEXTUPDATE"
    MULTILINETEXTUPDATE = "MULTILINETEXTUPDATE"
    LED = "LED"
    COMBO = "COMBO"
    CHECKBOX = "CHECKBOX"
    BAR = "BAR"
    BUTTON = "BUTTON"
    PLOTX = "PLOTX"
    PLOTY = "PLOTY"


class Layout(Enum):
    SCREEN = "SCREEN"
    BOX = "BOX"
    PLOT = "PLOT"
    ROW = "ROW"
    TABLE = "TABLE"
