Run in a container
==================

Pre-built containers with pvi and its dependencies already
installed are available on `Github Container Registry
<https://ghcr.io/epics-containers/pvi>`_.

Starting the container
----------------------

To pull the container from github container registry and run::

    $ docker run ghcr.io/epics-containers/pvi:main --version

To get a released version, use a numbered release instead of ``main``.
