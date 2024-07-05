[![CI](https://github.com/epics-containers/pvi/actions/workflows/ci.yml/badge.svg)](https://github.com/epics-containers/pvi/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/epics-containers/pvi/branch/main/graph/badge.svg)](https://codecov.io/gh/epics-containers/pvi)
[![PyPI](https://img.shields.io/pypi/v/pvi.svg)](https://pypi.org/project/pvi)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# PVI

PVI (PV Interface) is a framework for specifying the interface to an EPICS
driver in a single YAML file. The initial target is asyn port driver based
drivers, but it could be extended to streamDevice and other driver types at a
later date.

It allows the asyn parameter interface to be specified in a single place,
and removes boilerplate code in the driver CPP, template files, documentation,
and low level opis.

Source          | <https://github.com/epics-containers/pvi>
:---:           | :---:
PyPI            | `pip install pvi`
Documentation   | <https://epics-containers.github.io/pvi>
Releases        | <https://github.com/epics-containers/pvi/releases>

---

Note: This module is currently a proposal only, so all details are subject to
change at any point. The documentation is written in the present tense, but only
prototype code is written.

---

<!-- README only content. Anything below this line won't be included in index.md -->

See https://epics-containers.github.io/pvi for more detailed documentation.
