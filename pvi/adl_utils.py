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
        box_y,
        box_h,
        box_x,
        box_w,
        box_title,
        margin,
        label_counter,
        label_height,
        widget_height,
        widget_x,
        widget_dist,
    ):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.box_y = box_y
        self.box_h = box_h
        self.box_x = box_x
        self.box_w = box_w
        self.box_title = box_title
        self.margin = margin
        self.label_counter = label_counter
        self.label_height = label_height
        self.widget_height = widget_height
        self.widget_x = widget_x
        self.widget_dist = widget_dist

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
        self.box_y = self.y
        self.box_x = self.x

        # Adjust the box height depending on the number of channels in each group,
        # label height and two border spaces for top and bottom.
        self.box_h = (nodes + 1) * self.label_height + (2 * self.margin)

        # Make a new column when the position of bottom of current box is greater than
        # the main window height
        if (self.box_y + self.box_h) > self.h:
            self.y = 50  # Start back at the top
            self.box_y = self.y
            self.x = self.box_x + self.box_w + self.margin  # New column
            self.box_x = self.x

        box_title_y = self.box_y + self.margin  # Make group label at top of box

        # Use this if planning on having groups with loads of channels
        # if self.box_h > self.h:
        #     self.box_h = self.h - 60
        #     self.w += 245

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
            width=235
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
            width=235
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

        if widget_type == Widget.BUTTON:
            widget = self.make_button(widget_label, write_pv)
        elif widget_type == Widget.LED:
            widget = self.make_led(read_pv)
        elif widget_type == Widget.COMBO:
            widget = self.make_combo(write_pv, read_pv)
        elif (widget_type == Widget.TEXTINPUT) and read_pv:
            pv_demand = self.make_demand(write_pv, widget_width=60)
            # Split variable is for two side-by-side widgets i.e. text input & readback
            pv_rbv = self.make_rbv(read_pv, widget_width=60, split=65)
            widget = pv_demand + pv_rbv
        elif widget_type == Widget.TEXTINPUT:
            pv_demand = self.make_demand(write_pv, widget_width=125)
            widget = pv_demand
        elif widget_type == Widget.TEXTUPDATE:
            pv_rbv = self.make_rbv(read_pv, split=0, widget_width=125)
            widget = pv_rbv
        else:
            raise NotImplementedError

        # After the last label, set y to start next box below
        box_space = 20
        if self.label_counter == (nodes - 1):
            self.y = self.box_y + self.box_h + box_space
        else:
            self.label_counter += 1

        return pv_label + widget

    def make_label(self, widget_label):
        """ Make a label per channel. """
        label_x = self.x + self.margin
        label_y = (
            self.box_y
            + self.margin
            + (self.label_height * self.label_counter)
            + self.box_title
        )
        label_text = f"""
# (Static Text)
    text {{
        object {{
            x={label_x}
            y={label_y}
            width=110
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

    def make_demand(self, write_pv, widget_width):
        """ Make text input widgets. """
        self.widget_x = self.x + self.widget_dist
        # Keep the widget aligned with the label
        demand_y = (
            self.box_y
            + self.margin
            + (self.label_height * self.label_counter)
            + self.box_title
        )
        return f"""
# (Textentry)
    "text entry" {{
        object {{
            x={self.widget_x}
            y={demand_y}
            width={widget_width}
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

    def make_rbv(self, read_pv, split, widget_width):
        """ Make text update widgets. """
        self.widget_x = self.x + self.widget_dist + split
        rbv_y = (
            self.box_y
            + self.margin
            + (self.label_height * self.label_counter)
            + self.box_title
        )
        return f"""
# (Textupdate)
    "text update" {{
        object {{
            x={self.widget_x}
            y={rbv_y}
            width={widget_width}
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
        self.widget_x = self.x + self.widget_dist
        btn_y = (
            self.box_y
            + self.margin
            + (self.label_height * self.label_counter)
            + self.box_title
        )
        return f"""# (Message Button)
object activeMessageButtonClass
beginObjectProperties
major 4
minor 0
release 0
x {self.widget_x}
y {btn_y}
w 125
h {self.widget_height}
fgColor index {self.def_fg_colour_ctrl}
onColor index 3
offColor index 3
topShadowColor index 1
botShadowColor index 11
controlPv "{write_pv}"
pressValue "1"
onLabel "{widget_label}"
offLabel "{widget_label}"
3d
font "{self.def_font_class}-bold-r-12.0"
endObjectProperties

"""

    def make_led(self, read_pv):
        """ Make centered LED widget. """
        center = 50
        self.widget_x = self.x + self.widget_dist + center
        led_y = (
            self.box_y
            + self.margin
            + (self.label_height * self.label_counter)
            + self.box_title
        )
        return f"""# (Byte)
object ByteClass
beginObjectProperties
major 4
minor 0
release 0
x {self.widget_x}
y {led_y}
w 17
h {self.widget_height}
controlPv "{read_pv}"
lineColor index 14
onColor index 15
offColor index 19
lineWidth 2
numBits 1
endObjectProperties
"""

    def make_combo(self, write_pv, read_pv):
        self.widget_x = self.x + self.widget_dist
        com_y = (
            self.box_y
            + self.margin
            + (self.label_height * self.label_counter)
            + self.box_title
        )
        return f"""
# (Menu Button)
    menu {{
        object {{
            x={self.widget_x}
            y={com_y}
            width=120
            height={self.widget_height}
        }}
        control {{
            chan="{write_pv}"
            clr=14
            bclr=51
        }}
    }}
"""
