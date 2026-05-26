# PVI IOC Introspection

PVI can be used to add info tags to existing EPICS database to create a V4 PV with an
NTTable of the PVs within the IOC. This can be done with the `format_template` function
by passing a `Device` instance, a PV prefix and an output path to write the template to.
Or, using the CLI command `pvi generate-template` with a `pvi.device.yaml`.  The PV
prefix is the prefix of the PVI PV itself. Usually this would match the prefix of the
actual PVs, as defined in the `Device` signals, but it doesn't have to.

## Template Format

This will generate a new template containing records for all of the signals in the
`Device` that inserts an info tag to the existing record.

```
record("*", "$(P)$(R)Gain") {
    info(Q:group, {
        "$(P)$(R)PVI": {
            "pvi.Gain.w": {
                "+channel": "NAME",
                "+type": "plain",
            }
        }
    })
}

record("*", "$(P)$(R)Gain_RBV") {
    info(Q:group, {
        "$(P)$(R)PVI": {
            "pvi.Gain.r": {
                "+channel": "NAME",
                "+type": "plain",
            }
        }
    })
}
...
record("*", "$(P)$(R)UniqueId_RBV") {
    info(Q:group, {
        "$(P)$(R)PVI": {
            "pvi.UniqueId.r": {
                "+channel": "NAME",
                "+type": "plain",
            }
        }
    })
}
...
record("*", "$(P)$(R)WaitForPlugins") {
    info(Q:group, {
        "$(P)$(R)PVI": {
            "pvi.WaitForPlugins.w": {
                "+channel": "NAME",
                "+type": "plain",
            }
        }
    })
}
```

These info tags are then collected and served as a V4 PV by QSRV. This info tag adds an
entry into the V4 PV `$(P)$(R)PVI` with the name `pvi.GainX.w` where `w` is the access
mode (`r`, `w`, `rw`, `x`). Each `Device` in the IOC will produce its own PVI PV,
differentiated by the `R` macro in this case.

For more information on the syntax of the info tags, see the [QSRV documentation][QSRV].

## PVI NTTable

With an IOC running the PVI PV can be accessed using PVAccess, for example the `pvget`
CLI tool in [PVAccessCPP], or the [p4p] python library.

```shell
❯ pvget SIM:DET:PVI
SIM:DET:PVI structure
    structure record
        structure _options
            boolean atomic true
    structure pvi
        structure Gain
            string r SIM:DET:Gain_RBV
            string w SIM:DET:Gain
...
        structure UniqueId
            string r SIM:DET:UniqueId_RBV
...
        structure WaitForPlugins
            string w SIM:DET:WaitForPlugins
```

[QSRV]: https://epics-base.github.io/pva2pva/qsrv_page.html
[PVAccessCPP]: https://github.com/epics-base/pvAccessCPP
[p4p]: https://github.com/mdavidsaver/p4p
