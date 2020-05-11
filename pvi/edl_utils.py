class GenerateEDL:
    """ Returns the strings required to create an entire edl screen,
    containing widgets for each channel."""
    def __init__(self, w, h, x, y, boxy, boxh, boxx, boxw, space,
                 labelcounter, defFontClass, defFgColorCtrl, defBgColorCtrl,
                 defFgColorMon, defBgColorMon):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.boxy = boxy
        self.boxh = boxh
        self.boxx = boxx
        self.boxw = boxw
        self.space = space
        self.labelcounter = labelcounter
        self.defFontClass = defFontClass
        self.defFgColorCtrl = defFgColorCtrl
        self.defBgColorCtrl = defBgColorCtrl
        self.defFgColorMon = defFgColorMon
        self.defBgColorMon = defBgColorMon

    def make_main_window(self, window_title):
        self.w = self.boxx + self.boxw + 5
        if self.boxx <= 5:
            self.h = self.boxy + self.boxh + 50
        return f"""4 0 1
beginScreenProperties
major 4
minor 0
release 1
x 300
y 50
w {self.w}
h {self.h}
font "{self.defFontClass}-bold-r-12.0"
ctlFont "{self.defFontClass}-bold-r-12.0"
btnFont "{self.defFontClass}-bold-r-12.0"
fgColor index 14
bgColor index 3
textColor index 14
ctlFgColor1 index {self.defFgColorMon}
ctlFgColor2 index {self.defFgColorCtrl}
ctlBgColor1 index {self.defBgColorMon}
ctlBgColor2 index {self.defBgColorCtrl}
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
font "{self.defFontClass}-bold-r-16.0"
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
        self.labelcounter = 0
        self.boxy = self.y
        self.boxx = self.x
        self.w = 245
        self.boxh = nodes * 20 + (2 * self.space)
        if (self.boxy + self.boxh + 30) > self.h:
            self.y = 50
            self.boxy = self.y
            self.x = self.boxx + self.w + 5
            self.boxx = self.x
        box_titley = self.boxy - 10

        # if self.boxh > self.h:
        #     self.boxh = self.h - 60
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
h {self.boxh}
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
y {box_titley}
w 150
h 14
font "{self.defFontClass}-medium-r-12.0"
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

        if self.labelcounter == (nodes-1):
            self.y = self.boxy + self.boxh + self.space
        else:
            self.labelcounter += 1

        return pv_label + widget

    def make_label(self, widget_label):
        nx = self.x + 5
        labelh = 20
        labely = self.boxy + self.space + (labelh*self.labelcounter)
        label_text = f"""# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 0
x {nx}
y {labely}
w 110
h {labelh}
font "{self.defFontClass}-bold-r-10.0"
fgColor index 14
bgColor index 3
useDisplayBg
value "{widget_label}"

endObjectProperties

"""
        return label_text

    def make_demand(self, write_pv, widget_width):
        nx = self.x + 115
        demandh = 17
        demandy = self.boxy + self.space + ((demandh+3)*self.labelcounter)
        return f"""# (Textentry)
object TextentryClass
beginObjectProperties
major 10
minor 0
release 0
x {nx}
y {demandy}
w {widget_width}
h {demandh}
controlPv "{write_pv}"
fgColor index {self.defFgColorCtrl}
fgAlarm
bgColor index {self.defBgColorCtrl}
fill
font "{self.defFontClass}-bold-r-12.0"
endObjectProperties

"""

    def make_rbv(self, read_pv, split, widget_width):
        nx = self.x + 115 + split
        rbvh = 17
        rbvy = self.boxy + self.space + ((rbvh+3)*self.labelcounter)
        return f"""# (Textupdate)
object TextupdateClass
beginObjectProperties
major 10
minor 0
release 0
x {nx}
y {rbvy}
w {widget_width}
h {rbvh}
controlPv "{read_pv}"
fgColor index {self.defFgColorMon}
fgAlarm
bgColor index {self.defBgColorMon}
fill
font "{self.defFontClass}-bold-r-12.0"
fontAlign "center"
endObjectProperties

"""

    def make_button(self, widget_label, write_pv):
        nx = self.x + 115
        btnh = 17
        btny = self.boxy + self.space + ((btnh+3)*self.labelcounter)
        return f"""# (Message Button)
object activeMessageButtonClass
beginObjectProperties
major 4
minor 0
release 0
x {nx}
y {btny}
w 125
h {btnh}
fgColor index {self.defFgColorCtrl}
onColor index 3
offColor index 3
topShadowColor index 1
botShadowColor index 11
controlPv "{write_pv}"
pressValue "1"
onLabel "{widget_label}"
offLabel "{widget_label}"
3d
font "{self.defFontClass}-bold-r-12.0"
endObjectProperties

"""

    def make_led(self, read_pv):
        nx = self.x + 165
        ledh = 17
        ledy = self.boxy + self.space + ((ledh+3)*self.labelcounter)
        return f"""# (Byte)
object ByteClass
beginObjectProperties
major 4
minor 0
release 0
x {nx}
y {ledy}
w 17
h {ledh}
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
        comh = 17
        comy = self.boxy + self.space + ((comh+3)*self.labelcounter)
        return f"""# (Menu Button)
object activeMenuButtonClass
beginObjectProperties
major 4
minor 0
release 0
x {nx}
y {comy}
w 125
h {comh}
fgColor index {self.defFgColorCtrl}
bgColor index {self.defBgColorCtrl}
inconsistentColor index 0
topShadowColor index 1
botShadowColor index 11
controlPv "{write_pv}"
indicatorPv "{read_pv}"
font "{self.defFontClass}-bold-r-12.0"
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
        exitX = self.w - 100
        exitY = self.h - min(30, self.h - self.y)
        return f"""# (Exit Button)
object activeExitButtonClass
beginObjectProperties
major 4
minor 1
release 0
x {exitX}
y {exitY}
w 95
h 25
fgColor index 46
bgColor index 3
topShadowColor index 1
botShadowColor index 11
label "EXIT"
font "{self.defFontClass}-bold-r-14.0"
3d
endObjectProperties

"""
