PVI Overview
------------

The YAML file contains information about each asyn parameter that will be
exposed by the driver, it's name, type, description, initial value, which record
type it uses, whether it is writeable or read only, which widget should be used,
etc. PVI reads these and passes them to Producer that creates intermediate Record,
Channel and AsynParam objects. These are passed to a site specific Formatter which
takes the tree of intermediate objects and writes a parameter CPP file, database
template, and site specific screens to disk.

YAML file
~~~~~~~~~

The YAML file is formed of a number of sections:

.. list-table::
    :widths: 20, 80
    :header-rows: 1

    * - Section
      - Description
    * - includes
      - The YAML files to use as base classes for superclasses
    * - local
      - A local override YAML file for site specific changes
    * - producer
      - Producer that knows how to create Records and Channels from the Components
    * - formatter
      - Site specific Formatter which can format the output files
    * - components
      - Tree of Components for each logical asyn parameter arranged in logical
        GUI groups

The Components are created from the YAML file with local overrides (also incorporating
the base classes for screens). These are passed to the Producer which produces
AsynParameters, Records and Channels. These are then passed to the Formatter which
outputs them to file:

.. digraph:: pvi_products

    bgcolor=transparent
    node [fontname=Arial fontsize=10 shape=box style=filled fillcolor="#8BC4E9"]
    edge [fontname=Arial fontsize=10 arrowhead=vee]

    Intermediate [label="[Record(),\n Channel(),\n AsynParameter()]"]
    Products [label="Template\nScreens\nDriver Params\nDocumentation"]

    {rank=same; Components -> Producer -> Intermediate -> Formatter -> Products}

Here's a cut down pilatus.yaml file that might describe a parameter in a
detector:

.. literalinclude:: ../tests/pilatus.pvi.yaml
    :language: yaml

And these settings could then be overridden in a local YAML file:

.. literalinclude:: ../tests/pilatus.local.yaml
    :language: yaml
