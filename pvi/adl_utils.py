import math

from ._types import Widget


class GenerateADL:
    """ Returns the strings required to create an entire edl screen,
    containing widgets for each channel."""

    def __init__(
        self,
        w,
        h,
        x,
        y,
        max_box_h,
        box_y,
        box_h,
        box_x,
        box_w,
        box_column,
        box_title,
        max_nodes,
        margin,
        column_counter,
        label_counter,
        label_reset,
        label_height,
        label_width,
        widget_height,
        widget_width,
    ):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.max_box_h = max_box_h
        self.box_y = box_y
        self.box_h = box_h
        self.box_x = box_x
        self.box_w = box_w
        self.box_column = box_column
        self.box_title = box_title
        self.max_nodes = max_nodes
        self.margin = margin
        self.column_counter = column_counter
        self.label_reset = label_reset
        self.label_counter = label_counter
        self.label_height = label_height
        self.label_width = label_width
        self.widget_height = widget_height
        self.widget_width = widget_width

    def make_main_window(self, window_title):
        """ Make the main window depending on the number of box columns, and
        add a title panel at the top. """

        # Main window width varies depending on box_x value, which is indicative
        # of the current column
        self.w = self.box_x + self.box_w + self.margin

        # If there's only one box column, the window height adjusts to minimum
        # size required to display boxes, otherwise, use fixed window height.
        if self.box_x == self.margin:
            self.h = self.box_y + self.box_h + self.margin

        return f"""
file {{
    name="{window_title}_parameters.adl"
    version=030109
}}
display {{
    object {{
        x=391
        y=58
        width={self.w}
        height={self.h}
    }}
    clr=14
    bclr=4
    cmap=""
    gridSpacing=5
    gridOn=0
    snapToGrid=0
}}
"color map" {{
    ncolors=65
    colors {{
        ffffff,
        ececec,
        dadada,
        c8c8c8,
        bbbbbb,
        aeaeae,
        9e9e9e,
        919191,
        858585,
        787878,
        696969,
        5a5a5a,
        464646,
        2d2d2d,
        000000,
        00d800,
        1ebb00,
        339900,
        2d7f00,
        216c00,
        fd0000,
        de1309,
        be190b,
        a01207,
        820400,
        5893ff,
        597ee1,
        4b6ec7,
        3a5eab,
        27548d,
        fbf34a,
        f9da3c,
        eeb62b,
        e19015,
        cd6100,
        ffb0ff,
        d67fe2,
        ae4ebc,
        8b1a96,
        610a75,
        a4aaff,
        8793e2,
        6a73c1,
        4d52a4,
        343386,
        c7bb6d,
        b79d5c,
        a47e3c,
        7d5627,
        58340f,
        99ffff,
        73dfff,
        4ea5f9,
        2a63e4,
        0a00b8,
        ebf1b5,
        d4db9d,
        bbc187,
        a6a462,
        8b8239,
        73ff6b,
        52da3b,
        3cb420,
        289315,
        1a7309,
    }}
}}
rectangle {{
    object {{
        x=0
        y=4
        width={self.w}
        height=25
    }}
    "basic attribute" {{
        clr=2
    }}
}}
text {{
    object {{
        x=0
        y=5
        width={self.w}
        height=25
    }}
    "basic attribute" {{
        clr=54
    }}
    textix="{window_title} features - $(P)$(R)"
    align="horiz. centered"
}}"""

    def make_box(self, box_label, nodes):
        # Reset label counter for each new box
        self.label_counter = 0
        self.label_reset = 0
        self.column_counter = 0

        # Position new box
        self.box_y = self.y
        self.box_x = self.x
        self.box_w = self.box_column

        # Initial box height
        self.box_h = (nodes + 1) * self.label_height + (2 * self.margin)

        # Add columns to a single box when there are too many channels to fit
        # vertically in the window
        if self.box_h > self.h:
            self.box_h = self.max_box_h
            self.max_nodes = math.floor(
                (self.box_h - (2 * self.margin)) / self.label_height
            )
            remainder = nodes - self.max_nodes
            num_cols = math.ceil(remainder / self.max_nodes)
            self.box_w += num_cols * self.box_column

        if (self.box_y + self.box_h) > self.h:
            self.y = 40  # Start back at the top
            self.box_y = self.y
            self.x += self.widget_width + self.margin  # New column
            self.box_x = self.x

        box_title_y = self.box_y + self.margin  # Make group label at top of box
        box_title_w = self.box_w - (2 * self.margin)

        return f"""
# (Rectangle)
    rectangle {{
        object {{
            x={self.x}
            y={self.y}
            width={self.box_w}
            height={self.box_h}
        }}
        "basic attribute" {{
            clr=14
            fill="outline"
        }}
    }}

    rectangle {{
        object {{
            x=10
            y={box_title_y}
            width={box_title_w}
            height={self.box_title}
        }}
        "basic attribute" {{
            clr=2
        }}
    }}
    text {{
        object {{
            x={self.x}
            y={box_title_y}
            width={box_title_w}
            height={self.box_title}
        }}
        "basic attribute" {{
            clr=54
        }}
        textix="{box_label}"
        align="horiz. centered"
    }}
"""

    def make_widget(self, widget_label, nodes, widget_type, read_pv, write_pv):
        pv_label = self.make_label(widget_label)
        self.widget_width = (self.box_column / 2) - (2 * self.margin)

        if widget_type == Widget.BUTTON:
            widget = self.make_button(widget_label, write_pv)

        elif widget_type == Widget.CHECKBOX:
            widget = self.make_choice(write_pv)

        elif widget_type == Widget.LED:
            led_width = 20
            self.x = (
                self.get_widget_x()
                + (((self.box_column / 2) - led_width) / 2)
                - self.margin
            )
            widget = self.make_led(read_pv)

        elif widget_type == Widget.COMBO:
            self.widget_width = (self.box_column / 4) - (3 / 2 * self.margin)
            pv_menu = self.make_combo(write_pv)
            self.x += +self.widget_width + self.margin
            pv_rbv = self.make_rbv(read_pv)
            widget = pv_menu + pv_rbv

        elif (widget_type == Widget.TEXTINPUT) and read_pv:
            self.widget_width = (self.box_column / 4) - (3 / 2 * self.margin)
            pv_demand = self.make_demand(write_pv)
            self.x += self.widget_width + self.margin
            pv_rbv = self.make_rbv(read_pv)
            widget = pv_demand + pv_rbv

        elif widget_type == Widget.TEXTINPUT:
            pv_demand = self.make_demand(write_pv)
            widget = pv_demand

        elif widget_type == Widget.TEXTUPDATE:
            self.x = self.get_widget_x()
            pv_rbv = self.make_rbv(read_pv)
            widget = pv_rbv

        else:
            raise NotImplementedError

        # After the last label, set y to start next box below
        box_space = 15
        if self.label_counter == (nodes - 1):
            self.y = self.box_y + self.box_h + box_space
            self.x = self.box_x
        else:
            self.label_counter += 1
            self.label_reset += 1

        return pv_label + widget

    def make_label(self, widget_label):
        """ Make a label per channel. """
        # Start labelling again at top of next column
        if (self.y + (2 * self.label_height)) > (self.box_y + self.box_h):
            self.column_counter += 1
            self.label_reset = 0
            self.x = self.box_x + self.margin + (self.box_column * self.column_counter)
            self.y = (
                self.box_y + self.margin + (self.label_height * (self.label_reset + 1))
            )
        else:
            self.x = self.box_x + self.margin + (self.box_column * self.column_counter)
            self.y = (
                self.box_y + self.margin + (self.label_height * (self.label_reset + 1))
            )
        label_text = f"""
# (Static Text)
    text {{
        object {{
            x={self.x}
            y={self.y}
            width={self.label_width}
            height={self.label_height}
        }}
        "basic attribute" {{
            clr=14
        }}
        textix="{widget_label}"
        align="horiz. right"
    }}
"""
        return label_text

    def make_demand(self, write_pv):
        """ Make text input widgets. """
        return f"""
# (Textentry)
    "text entry" {{
        object {{
            x={self.get_widget_x()}
            y={self.y}
            width={self.widget_width}
            height={self.widget_height}
        }}
        control {{
            chan="{write_pv}"
            clr=14
            bclr=51
        }}
        limits {{
        }}
    }}
"""

    def make_rbv(self, read_pv):
        """ Make text update widgets. """
        return f"""
# (Textupdate)
    "text update" {{
        object {{
            x={self.x}
            y={self.y}
            width={self.widget_width}
            height={self.widget_height}
        }}
        monitor {{
            chan="{read_pv}"
            clr=54
            bclr=4
        }}
        align="horiz. left"
        limits {{
        }}
    }}
"""

    def make_button(self, widget_label, write_pv):
        return f"""
"message button" {{
    object {{
            x={self.get_widget_x()}
            y={self.y}
            width={self.widget_width}
            height={self.widget_height}
    }}
    control {{
            chan="{write_pv}"
            clr=14
            bclr=51
    }}
    label="{widget_label}"
    press_msg="0"
}}
"""

    def make_led(self, read_pv):
        """ Make centered LED widget. """
        return f"""
byte {{
    object {{
        x={self.x}
        y={self.y}
        width=20
        height={self.widget_height}
    }}
    monitor {{
        chan="{read_pv}"
        clr=60
        bclr=64
    }}
    sbit=0
}}

"""

    def make_combo(self, write_pv):
        return f"""
# (Menu Button)
    menu {{
        object {{
            x={self.get_widget_x()}
            y={self.y}
            width={self.widget_width}
            height={self.widget_height}
        }}
        control {{
            chan="{write_pv}"
            clr=14
            bclr=51
        }}
    }}
"""

    def make_choice(self, write_pv):
        return f"""
"choice button" {{
    object {{
        x={self.get_widget_x()}
        y={self.y}
        width={self.widget_width}
        height={self.widget_height}
    }}
    control {{
        chan="{write_pv}"
        clr=14
        bclr=51
    }}
        stacking="column"
}}"""

    def get_widget_x(self):
        # Adjust for demand and readback widgets
        self.x += self.label_width + self.margin
        return self.x
