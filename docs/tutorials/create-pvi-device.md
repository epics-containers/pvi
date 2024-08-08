# Create a PVI Device from a database template

A PVI device yaml can be created from an existing database template with the `convert
device` subcommand. The simplest case takes a header file for the driver a template. For
example, to create a PVI device for the ADSimDetector driver:

```bash
pvi convert device ./ --header simDetector.h --template simDetector.template
```

which will create a `simDetector.pvi.device.yaml` in the current directory.

:::{note}
See `pvi convert device --help` for a full list of options.
:::

The `Device` will contain a list of components and groups of components describing the
PVs in the given templates, their types and the widgets to display for control and
readback on a UI.

This `Device` can then be edited to make any adjustments. The `pvi regroup` command can
be used to add structure to the `Device` based on a set of `.adl` UIs:

```bash
pvi regroup simDetector.pvi.device.yaml simDetector.adl simDetectorSetup.adl
```

:::{note}
See `pvi regroup --help` for a full list of options.
:::

This will modify the yaml in place to add grouping based on what PV appears on what UI
file. The `Device` can also be edited by hand. A common use case is to change the widget
type from `TextRead`/`TextWrite` to something more specific.

Once a Device has been edited, the `pvi reconvert` command can be used to make additions
without overwriting and modifications, either against a update template from the
upstream support module, or an additional template that was missed in the initial
conversion.

```bash
pvi reconvert simDetector.pvi.device.yaml simDetector.template simDetectorExtras.template
```

:::{note}
See `pvi reconvert --help` for a full list of options.
:::