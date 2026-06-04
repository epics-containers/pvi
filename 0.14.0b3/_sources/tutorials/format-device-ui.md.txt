# Format a UI from a Device

A UI can be formatted from a PVI `Device`. Formatters currently exist for adl, edl and
bob files. This is selected based on the file extension of the given output path and
formatter. Formatters are in the `formatters` directory in the root of the pvi repo. For
example, to create a bob UI from the simDetector.pvi.device.yaml created in
[](create-pvi-device):

```bash
pvi format simDetector.bob simDetector.pvi.device.yaml dls.bob.pvi.formatter.yaml
```

The format command will search for parents of the given `Device` (from the `parent`
field) and include those PVs on the UI. If the `Device` yaml files for the parents exist
in another directory, the directory can be provided with the `--yaml-path` option.

:::{note}
    See `pvi format --help` for a full list of options.
:::
