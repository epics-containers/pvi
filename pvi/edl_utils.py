class GenerateEDL:
    """ Returns the strings required to create an entire edl screen,
    containing widgets for each channel."""
    def __init__(self, w, h, x, y, box_y, box_h, box_x, box_w, space,
                 label_counter, def_font_class, def_fg_colour_ctrl, def_bg_colour_ctrl,
                 def_fg_colour_mon, def_bg_colour_mon):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.box_y = box_y
        self.box_h = box_h
        self.box_x = box_x
        self.box_w = box_w
        self.space = space
        self.label_counter = label_counter
        self.def_font_class = def_font_class
        self.def_fg_colour_ctrl = def_fg_colour_ctrl
        self.def_bg_colour_ctrl = def_bg_colour_ctrl
        self.def_fg_colour_mon = def_fg_colour_mon
        self.def_bg_colour_mon = def_bg_colour_mon

    def make_main_window(self, window_title):
        self.w = self.box_x + self.box_w + 5
        if self.box_x <= 5:
            self.h = self.box_y + self.box_h + 50
        return f"""4 0 1
beginScreenProperties
major 4
minor 0
release 1
x 300
y 50
w {self.w}
h {self.h}
font "{self.def_font_class}-bold-r-12.0"
ctlFont "{self.def_font_class}-bold-r-12.0"
btnFont "{self.def_font_class}-bold-r-12.0"
fgColor index 14
bgColor index 3
textColor index 14
ctlFgColor1 index {self.def_fg_colour_mon}
ctlFgColor2 index {self.def_fg_colour_ctrl}
ctlBgColor1 index {self.def_bg_colour_mon}
ctlBgColor2 index {self.def_bg_colour_ctrl}
topShadowColor index 1
botShadowColor index 11
title "{window_title} features - $(P)$(R)"
showGrid
snapToGrid
gridSize 5
endScreenProperties

# (Group)
object activeGroupClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w {self.w}
h 30

beginGroup

# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w {self.w}
h 30
lineColor index 3
fill
fillColor index 3
endObjectProperties

# (Lines)
object activeLineClass
beginObjectProperties
major 4
minor 0
release 1
x 0
y 2
w {self.w}
h 24
lineColor index 11
fillColor index 0
numPoints 3
xPoints {{
  0 0
  1 {self.w}
  2 {self.w}
}}
yPoints {{
  0 26
  1 26
  2 2
}}
endObjectProperties

# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 0
x 0
y 2
w {self.w}
h 24
font "{self.def_font_class}-bold-r-16.0"
fontAlign "center"
fgColor index 14
bgColor index 48
value "{window_title} features - $(P)$(R)"
endObjectProperties

# (Lines)
object activeLineClass
beginObjectProperties
major 4
minor 0
release 1
x 0
y 2
w {self.w}
h 24
lineColor index 1
fillColor index 0
numPoints 3
xPoints {{
  0 0
  1 0
  2 {self.w}
}}
yPoints {{
  0 26
  1 2
  2 2
}}
endObjectProperties

endGroup

endObjectProperties

"""

    def make_box(self, box_label, nodes):
        self.label_counter = 0
        self.box_y = self.y
        self.box_x = self.x
        self.w = 245
        self.box_h = nodes * 20 + (2 * self.space)
        if (self.box_y + self.box_h + 30) > self.h:
            self.y = 50
            self.box_y = self.y
            self.x = self.box_x + self.w + 5
            self.box_x = self.x
        box_title_y = self.box_y - 10

        # if self.box_h > self.h:
        #     self.box_h = self.h - 60
        #     self.w += 245

        return f"""# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x {self.x}
y {self.y}
w {self.w}
h {self.box_h}
lineColor index 14
fill
fillColor index 5
endObjectProperties

# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 0
x {self.x}
y {box_title_y}
w 150
h 14
font "{self.def_font_class}-medium-r-12.0"
fontAlign "center"
fgColor index 14
bgColor index 8
value "  {box_label}  "
autoSize
border
endObjectProperties

"""

    def make_widget(self, widget_label, nodes, widget_type, read_pv, write_pv):
        pv_label = self.make_label(widget_label)
        if str(widget_type) == "Widget.BUTTON":
            widget = self.make_button(widget_label, write_pv)
        elif str(widget_type) == "Widget.LED":
            widget = self.make_led(read_pv)
        elif str(widget_type) == "Widget.COMBO":
            widget = self.make_combo(write_pv, read_pv)
        elif (str(widget_type) == "Widget.TEXTINPUT") and read_pv:
            pv_demand = self.make_demand(write_pv, widget_width=60)
            pv_rbv = self.make_rbv(read_pv, widget_width=60, split=65)
            widget = pv_demand + pv_rbv
        elif str(widget_type) == "Widget.TEXTINPUT":
            pv_demand = self.make_demand(write_pv, widget_width=125)
            widget = pv_demand
        elif str(widget_type) == "Widget.TEXTUPDATE":
            pv_rbv = self.make_rbv(read_pv, split=0, widget_width=125)
            widget = pv_rbv
        else:
            print("Error somewhere, no widget to return")
            return str(None)

        if self.label_counter == (nodes-1):
            self.y = self.box_y + self.box_h + self.space
        else:
            self.label_counter += 1

        return pv_label + widget

    def make_label(self, widget_label):
        nx = self.x + 5
        label_h = 20
        label_y = self.box_y + self.space + (label_h*self.label_counter)
        label_text = f"""# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 0
x {nx}
y {label_y}
w 110
h {label_h}
font "{self.def_font_class}-bold-r-10.0"
fgColor index 14
bgColor index 3
useDisplayBg
value "{widget_label}"

endObjectProperties

"""
        return label_text

    def make_demand(self, write_pv, widget_width):
        nx = self.x + 115
        demand_h = 17
        demand_y = self.box_y + self.space + ((demand_h+3)*self.label_counter)
        return f"""# (Textentry)
object TextentryClass
beginObjectProperties
major 10
minor 0
release 0
x {nx}
y {demand_y}
w {widget_width}
h {demand_h}
controlPv "{write_pv}"
fgColor index {self.def_fg_colour_ctrl}
fgAlarm
bgColor index {self.def_bg_colour_ctrl}
fill
font "{self.def_font_class}-bold-r-12.0"
endObjectProperties

"""

    def make_rbv(self, read_pv, split, widget_width):
        nx = self.x + 115 + split
        rbv_h = 17
        rbv_y = self.box_y + self.space + ((rbv_h+3)*self.label_counter)
        return f"""# (Textupdate)
object TextupdateClass
beginObjectProperties
major 10
minor 0
release 0
x {nx}
y {rbv_y}
w {widget_width}
h {rbv_h}
controlPv "{read_pv}"
fgColor index {self.def_fg_colour_mon}
fgAlarm
bgColor index {self.def_bg_colour_mon}
fill
font "{self.def_font_class}-bold-r-12.0"
fontAlign "center"
endObjectProperties

"""

    def make_button(self, widget_label, write_pv):
        nx = self.x + 115
        btn_h = 17
        btn_y = self.box_y + self.space + ((btn_h+3)*self.label_counter)
        return f"""# (Message Button)
object activeMessageButtonClass
beginObjectProperties
major 4
minor 0
release 0
x {nx}
y {btn_y}
w 125
h {btn_h}
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
        nx = self.x + 165
        led_h = 17
        led_y = self.box_y + self.space + ((led_h+3)*self.label_counter)
        return f"""# (Byte)
object ByteClass
beginObjectProperties
major 4
minor 0
release 0
x {nx}
y {led_y}
w 17
h {led_h}
controlPv "{read_pv}"
lineColor index 14
onColor index 15
offColor index 19
lineWidth 2
numBits 1
endObjectProperties
"""

    def make_combo(self, write_pv, read_pv):
        nx = self.x + 115
        com_h = 17
        com_y = self.box_y + self.space + ((com_h+3)*self.label_counter)
        return f"""# (Menu Button)
object activeMenuButtonClass
beginObjectProperties
major 4
minor 0
release 0
x {nx}
y {com_y}
w 125
h {com_h}
fgColor index {self.def_fg_colour_ctrl}
bgColor index {self.def_bg_colour_ctrl}
inconsistentColor index 0
topShadowColor index 1
botShadowColor index 11
controlPv "{write_pv}"
indicatorPv "{read_pv}"
font "{self.def_font_class}-bold-r-12.0"
endObjectProperties

"""

    def make_checkbox(self):
        pass

    def make_bar(self, read_pv):
        return f"""# (Bar)
object activeBarClass
beginObjectProperties
major 4
minor 1
release 0
x 566
y 388
w 238
h 188
indicatorColor index 17
fgColor index 14
bgColor index 6
indicatorPv "{read_pv}"
font "helvetica-medium-r-18.0"
min "0"
max "100"
scaleFormat "FFloat"
orientation "vertical"
endObjectProperties
"""

    def make_exit_button(self):
        exit_x = self.w - 100
        exit_y = self.h - min(30, self.h - self.y)
        return f"""# (Exit Button)
object activeExitButtonClass
beginObjectProperties
major 4
minor 1
release 0
x {exit_x}
y {exit_y}
w 95
h 25
fgColor index 46
bgColor index 3
topShadowColor index 1
botShadowColor index 11
label "EXIT"
font "{self.def_font_class}-bold-r-14.0"
3d
endObjectProperties

"""
