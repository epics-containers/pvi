# How to Write a Site Specific Formatter

This guide explains how you can create a pvi formatter to generate screens for
your own use cases.

## Overview

The formatters role is to take a `Device` - defined either in code or in a
`pvi.device.yaml` file - and turn this into a screen file that can be used by the
display software. The `Device` has a list of components that specify its name, a widget
type and any additional properties that can be assigned to that widget (such as a pv
name). During formatting, `Component` objects of the `Device` are translated into
widgets to be written to a UI file.

```{literalinclude} ../../src/pvi/device.py
:pyobject: Component
```

There are various types of `Component`. The simplest is a read-only signal.

```{literalinclude} ../../src/pvi/device.py
:pyobject: SignalR
```

To add structure, there is a `Group` component, which itself has a list of `Components`.

```{literalinclude} ../../src/pvi/device.py
:pyobject: Group
```

To make a screen from this, we need a template UI file. This contains a blank
representation of each supported widget for each of the supported file formats (bob, edl
etc...). Below is an example of a `textentry` widget for a .bob file.

```{literalinclude} ../../src/pvi/_format/dls.bob
:language: xml
:lines: 46-54
```

By extracting and altering the template widgets with the information provided by the
components, we can create a screen file.

## Create a Formatter subclass

To start, we will need to create our own formatter class. These inherit from an abstract
`Formatter` class that is defined in base.py. Inside, we need to define one mandatory
`format` function, which will be used to create our screen file:

```{literalinclude} ../../src/pvi/_format/base.py
:pyobject: Formatter.format
```

With a formatter defined, we now can start to populate this by defining the screen
dependencies.

## Define the ScreenLayout properties

Each screen requires a number of layout properties that allow you to customise the size
and placement of widgets. These are stored within `ScreenLayout` dataclass with the
following configurable parameters:

```{literalinclude} ../../src/pvi/_format/screen.py
:pyobject: ScreenLayout
```

When defining these in our formatter, we have the option of deciding which properties
should be configurable inside of the formatter.yaml. Properties defined as member
variables of the formatter class (and then referenced by the layout properties in the
screen format function) will be available to adjust inside of the formatter.yaml.
Anything else, should be considered as defaults for the formatter:

```{literalinclude} ../../src/pvi/_format/dls.py
:language: python
:start-after: LP DOCS REF
:end-before: SW DOCS REF
```

In the example above, everything has been made adjustable from the formatter.yaml except
the properties relating to groups. This is because they are more dependant on the file
format used rather than the users personal preference.

For clarity, the example below shows how the formatter.yaml can be used to set the
layout properties. Note that these are optional as each property is defined with a
default value.

```{literalinclude} ../../formatters/dls.bob.pvi.formatter.yaml
```

## Assign a template file

As previously stated, a template file provides the formatter with a base model of all
of the supported widgets that it can then overwrite with component data. Currently,
pvi supports templates for edl, adl and bob files, which can be referenced from the
\_format directory with the filename 'dls' + the file formats suffix (eg. dls.bob).

Inside of the format function, we need to provide a reference to the template file that
can then be used to identify what each widget should look like.

```python3
template = BobTemplate(str(Path(__file__).parent / "dls.bob"))
```

## Divide the template into widgets

With a template defined, we now need to assign each part of it to a supported widget
formatter. This is achieved by instantiating a WidgetFormatterFactory composed of
WidgetFormatters created from the UI template. WidgetFormatters are created by searching
the UI template for the given search term and a set of properties in the template to
replace with widget fields.

:::{note}
The `WidgetFormatter`s are generic types that must be parameterised depending on the
specific UI. Commonly this would use `str` for formatting text to a file directly. In
this case we use `_Element`, which will serialised to text with the `lxml` library.
:::

```{literalinclude} ../../src/pvi/_format/dls.py
:language: python
:start-after: SW DOCS REF
:end-before: MAKE_WIDGETS DOCS REF
```

```{warning}
This function uses a unique search term to locate and extract a widget from the template.
As such, the search term MUST be unique to avoid extracting multiple or irrelevant
widgets from the template.
```

## Define screen and group widget functions

Additionally, formatters for the title and a group on a screen must be defined along
with functions to create multiple components, for example a rectangle with a label on
top. In this example, we provide two arguments: The `bounds`, to set the widgets size
and position, and the `title` to populate the label with.

```{literalinclude} ../../src/pvi/_format/dls.py
:language: python
:start-after: MAKE_WIDGETS DOCS REF
:end-before: SCREEN_INI DOCS REF
```

## Construct a ScreenFormatter

These formatters can be used to define a `ScreenFormatterFactory`

```{literalinclude} ../../src/pvi/_format/dls.py
:language: python
:start-after: SCREEN_INI DOCS REF
:end-before: SCREEN_FORMAT DOCS REF
```

which can be used to instantiate a `ScreenFormatter` by passing a set of `Components`
and a title. This can then create `WidgetFormatters` for each `Component` for the
specific UI type the factory was parameterised with.

```{literalinclude} ../../src/pvi/_format/dls.py
:language: python
:start-after: SCREEN_FORMAT DOCS REF
:end-before: SCREEN_WRITE DOCS REF
```

In this case the `write_bob` function calls into the `lxml` library to format the
`_Element` instances to text. For `str` formatters this would call
`pathlib.Path.write_file`.
