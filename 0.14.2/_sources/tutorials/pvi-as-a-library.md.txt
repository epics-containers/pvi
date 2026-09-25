# Using PVI as a library

All subcommands in the CLI are also available as an API by importing pvi into a python
application. In addition, `Device` instances can be created dynamically to then use with
any of these APIs. Here is a trivial example:

```python
from pathlib import Path

from pvi.device import Device, SignalR, SignalRW, SignalX
from pvi._format.template import format_template
from pvi._format.dls import DLSFormatter

signals = [
    SignalR(name="Status", read_pv="Status_RBV"),
    SignalRW(name="Config", write_pv="Config", read_pv="Config_RBV"),
    SignalX(name="Command", write_pv="Go", value="1"),
]
device = Device(label="Simple Device", children=signals)

format_template(device, "PREFIX", Path("pvi.template"))
DLSFormatter().format(device, Path("simple.bob"))
```

which will create the `pvi.template` and `simple.bob` in the current working directory.

See the tests in the pvi repo for further example usage of this API.
