How to Write a Site Specific Formatter
======================================
This guide explains how you can create a pvi formatter to generate screens for
your own use cases.

Overview
--------
The formatters role is to take a device.yaml file and turn this into a screen file that
can be used by the display software. Inside of the device.yaml file is a list of
components that specify its name, a widget type and any additional properties that can be
assigned to that widget (such as a pv name). During formatting, the device.yaml file is
deserialised into component objects, which are later translated into widgets:

.. literalinclude:: ../../../src/pvi/device.py
    :pyobject: Component

.. literalinclude:: ../../../src/pvi/device.py
    :pyobject: SignalR

To make a screen from this, we need a template file. This contains a blank representation
of each supported widget for each of the supported file formats (bob, edl etc...). Below
is an example of a 'text entry' widget for a .bob file:

.. literalinclude:: ../../../src/pvi/_format/dls.bob
    :lines: 57-73

By extracting and altering the template widgets with the information provided by the
components, we can create a screen file.

Create a formatter subclass
---------------------------
To start, we will need to create our own formatter class. These inherit from an abstract
'Formatter' class that is defined in base.py. Inside, we need to define one mandatory
'format' function, which will be used to create our screen file:

.. literalinclude:: ../../../src/pvi/_format/base.py
    :pyobject: Formatter

The format function takes in a device: a list of components obtained from our
deserialised device.yaml file, A prefix: the pv prefix of the device, and a path: the
output destination for the generated screen file.

With a formatter defined, we now can start to populate this by defining the screen
dependencies.

Define the Screen Layout Properties
-----------------------------------
Each screen requires a number of layout properties that allow you to customise the size
and placement of widgets. These are stored within a 'ScrenLayout' dataclass that can
be imported from utils.py. Within the dataclass are the following configurable parameters:

.. literalinclude:: ../../../src/pvi/_format/screen.py
    :pyobject: ScreenLayout

When defining these in our formatter, we have the option of deciding which properties
should be configurable inside of the formatter.yaml. Properties defined as member
variables of the formatter class (and then referenced by the layout properties in the
screen format function) will be available to adjust inside of the formatter.yaml.
Anything else, should be considered as defaults for the formatter:

.. literalinclude:: ../../../src/pvi/_format/dls.py
    :start-after: LP DOCS REF
    :end-before: SW DOCS REF

In the example above, everything has been made adjustable from the formatter.yaml except
the properties relating to groups. This is becuase they are more dependant on the file
format used rather than the users personal preference.

For clarity, the example below shows how the formatter.yaml can be used to set the
layout properties. Note that these are optional as each property is defined with a
default value:

.. literalinclude:: ../../../formatters/dls.bob.pvi.formatter.yaml

Assign a Template File
----------------------
As previously stated, a template file provides the formatter with a base model of all
of the supported widgets that it can then overwrite with component data. Currently,
pvi supports templates for edl, adl and bob files, which can be referenced from the
_format directory with the filename 'dls' + the file formats suffix (eg. dls.bob).

Inside of the format function, we need to provide a reference to the template file that
can then be used to identify what each widget should look like:

.. code-block:: python3

        template = BobTemplate(str(Path(__file__).parent / "dls.bob"))

..
    Documentation does not explain what the WidgetTemplate function does,
    nor its subclasses BobTemplate, EdlTemplate & AdlTemplate.

Divide the Template into Widgets
--------------------------------
With a template defined, we now need to assign each part of it to a supported widget.
This is achieved using the ScreenWidgets dataclass (from utils.py). With this, we can
assign each of the widget classes to a snippet of the template using the
WidgetFactory.from_template method:

.. literalinclude:: ../../../src/pvi/_format/dls.py
    :start-after: SW DOCS REF
    :end-before: MAKE_WIDGETS DOCS REF

This function uses a unique search term to locate and extract a widget from the template.
As such, the search term MUST be unique to avoid extracing multiple or irrelevant
widgets from the template.

Define screen and group widget functions
----------------------------------------
Two widgets that are not handled by ScreenWidgets are the screen title and group object.
This is because the style of these widgets differ greatly for each file type. For
instance, with edl and adl files, groups are represented by a rectangle and title placed
behind a collection of widgets. Conversely, bob files handle groups using its dedicated
group object, which places widgets as children under the group object. Becuase of this,
we need to define two functions: one for the additional screen widgets (such as the title),
and one to represent the group widgets.

We then need to define two functions that can be used to create multiple instances of
these widgets. In this example, we provide two arguments: The 'bounds', to set the
widgets size and position, and the 'title' to populate the label with.

.. literalinclude:: ../../../src/pvi/_format/dls.py
    :start-after: MAKE_WIDGETS DOCS REF
    :end-before: SCREEN_INI DOCS REF

Construct a Screen Object
-------------------------
Provided that you have defined the LayoutProperties, template, ScreenWidgets and the
screen title and group object functions, we are now ready to define a screen object.

.. literalinclude:: ../../../src/pvi/_format/dls.py
    :start-after: SCREEN_INI DOCS REF
    :end-before: SCREEN_FORMAT DOCS REF

Note that screen_cls and group_cls are defined separately here as GroupFactories. This is
because they take in the make_widgets function, which has the possibility of returning
multiple widgets. (In edl files for example, we return a rectangle and label widget to
represent a group.)

The screen object itself contains two key functions: The 'screen' function takes a
deserialised device.yaml file and converts each of its components into widgets. It then
calculates the size and position of these widgets to generate a uniform screen layout.
On the output of this, we can call a (screen.)format function that populates these widgets
with the extracted properties from the device.yaml, and converts them into the chosen file
format:

.. literalinclude:: ../../../src/pvi/_format/dls.py
    :start-after: SCREEN_FORMAT DOCS REF
    :end-before: SCREEN_WRITE DOCS REF

Generate the Screen file
------------------------
After calling format on the screen object, you will be left with a list of strings that
represent each widget in your chosen file format. The final step is to create a
screen file by unpacking the list and writing each widget to the file:

.. literalinclude:: ../../../src/pvi/_format/dls.py
    :start-after: SCREEN_WRITE DOCS REF

And thats it. With this you can now create your own custom formatters. Below you can
find a complete example formatter, supporting both edl and bob file formats for DLS:

.. literalinclude:: ../../../src/pvi/_format/dls.py
    :pyobject: DLSFormatter
