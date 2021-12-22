pvi
===========================

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

This skeleton module is a generic Python project structure which provides a
means to keep tools and techniques in sync between multiple Python projects.

============== ==============================================================
PyPI           ``pip install pvi``
Source code    https://github.com/epics-containers/pvi
Documentation  https://dls-controls.github.io/pvi
Changelog      https://github.com/epics-containers/pvi/blob/master/CHANGELOG.rst
============== ==============================================================

It integrates the following tools:

- Pipenv for version management
- Pre-commit with black, flake8, isort and mypy for static analysis
- Pytest for code and coverage
- Sphinx for tutorials, how-to guides, explanations and reference documentation
- Github Actions for code and docs CI and deployment to PyPI and Github Pages
- VSCode settings using black, flake8, isort and mypy on save

The ``skeleton`` branch of this module contains the source code that can be
merged into new or existing projects, and pulled from to keep them up to date.

The ``master`` branch contains the
docs and a command line tool to ease the adoption of this skeleton into new
and existing projects::

    $ python -m pvi new /path/to/be/created
    $ python -m pvi existing /path/to/existing/repo

.. |code_ci| image:: https://github.com/epics-containers/pvi/workflows/Code%20CI/badge.svg?branch=master
    :target: https://github.com/epics-containers/pvi/actions?query=workflow%3A%22Code+CI%22
    :alt: Code CI

.. |docs_ci| image:: https://github.com/epics-containers/pvi/workflows/Docs%20CI/badge.svg?branch=master
    :target: https://github.com/epics-containers/pvi/actions?query=workflow%3A%22Docs+CI%22
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/epics-containers/pvi/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/epics-containers/pvi
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
