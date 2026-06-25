# Generate a PVI template from a Device

A database template can be generated from a PVI `Device` that adds an info tag to every
record:

```bash
pvi generate-template simDetector.pvi.device.yaml SIM pvi.template
```

:::{note}
See `pvi generate-template --help` for a full list of options.
:::

The info tags can be constructed into an NTTable and served over PVAccess by
loading the template into an IOC using pvxs. For more details see the
[docs](../explanations/pvi-pv).
