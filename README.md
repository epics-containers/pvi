<img alt="FastCS Logo" align="right" width="100" height="100" src="https://raw.githubusercontent.com/epics-containers/pvi/main/docs/images/pvi-logo.svg" target=https://github.com/epics-containers/pvi>

[![CI](https://github.com/epics-containers/pvi/actions/workflows/ci.yml/badge.svg)](https://github.com/epics-containers/pvi/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/epics-containers/pvi/branch/main/graph/badge.svg)](https://codecov.io/gh/epics-containers/pvi)
[![PyPI](https://img.shields.io/pypi/v/pvi.svg)](https://pypi.org/project/pvi)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# PVI

PVI (PV Interface) is a framework for specifying the interface to an EPICS
driver. PVI can be used either as a library or an application. PVI Devices can be
defined either in code or a YAML file. It can be used to generate UIs (adl, edl, bob) or
a template appending info tags to existing records to define an NTTable of the PVs in an
IOC.

Source          | <https://github.com/epics-containers/pvi>
:---:           | :---:
PyPI            | `pip install pvi`
Documentation   | <https://epics-containers.github.io/pvi>
Releases        | <https://github.com/epics-containers/pvi/releases>

## Projects Using PVI

- [ibek](https://github.com/epics-containers/ibek) - IOC Builder for EPICS and
  Kubernetes
- [FastCS](https://github.com/DiamondLightSource/FastCS) - Control system agnostic
  framework for building device support in Python for both EPICS and Tango

<!-- README only content. Anything below this line won't be included in index.md -->

See https://epics-containers.github.io/pvi for more detailed documentation.
