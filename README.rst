PVI
===

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

PVI (PV Interface) is a framework for specifying the interface to an EPICS
driver in a single YAML file. The initial target is asyn port driver based
drivers, but it could be extended to streamDevice and other driver types at a
later date.

It allows the asyn parameter interface to be specified in a single place,
and removes boilerplate code in the driver CPP, template files, documentation,
and low level opis

============== ==============================================================
PyPI           ``pip install pvi``
Source code    https://github.com/dls-controls/pvi
Documentation  https://dls-controls.github.io/pvi
Changelog      https://github.com/dls-controls/pvi/blob/master/CHANGELOG.rst
============== ==============================================================

.. note::

    This module is currently a proposal only, so all details are subject to
    change at any point. The documentation is written in the present tense, but
    only prototype code is written.


.. |code_ci| image:: https://github.com/dls-controls/pvi/workflows/Code%20CI/badge.svg?branch=master
    :target: https://github.com/dls-controls/pvi/actions?query=workflow%3A%22Code+CI%22
    :alt: Code CI

.. |docs_ci| image:: https://github.com/dls-controls/pvi/workflows/Docs%20CI/badge.svg?branch=master
    :target: https://github.com/dls-controls/pvi/actions?query=workflow%3A%22Docs+CI%22
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/dls-controls/pvi/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/dls-controls/pvi
    :alt: Test Coverage

.. |pypi_version| image:: https://img.shields.io/pypi/v/pvi.svg
    :target: https://pypi.org/project/pvi
    :alt: Latest PyPI version

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License

..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

See https://dls-controls.github.io/pvi for more detailed documentation.
