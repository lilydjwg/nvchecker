**nvchecker** (short for *new version checker*) is for checking if a new version of some software has been released.

This is the version 2.0 branch. For the old version 1.x, please switch to the ``v1.x`` branch.

.. image:: https://travis-ci.org/lilydjwg/nvchecker.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/lilydjwg/nvchecker
.. image:: https://badge.fury.io/py/nvchecker.svg
   :alt: PyPI version
   :target: https://badge.fury.io/py/nvchecker
.. image:: https://readthedocs.org/projects/nvchecker/badge/?version=latest
   :target: https://nvchecker.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

|

.. image:: https://repology.org/badge/vertical-allrepos/nvchecker.svg
   :alt: Packaging status
   :target: https://repology.org/metapackage/nvchecker/versions

.. contents::
   :local:

Dependency
----------
- Python 3.7+
- Python library: structlog, toml, appdirs
- One of these Python library combinations (ordered by preference):

  * tornado + pycurl
  * aiohttp
  * httpx with http2 support (experimental; only latest version is supported)
  * tornado

- All commands used in your software version configuration files

Install and Run
---------------
To install::

  pip3 install nvchecker

To use the latest code, you can also clone this repository and run::

  python3 setup.py install

To see available options::

  nvchecker --help

Run with one or more software version files::

  nvchecker -c config_file

You normally will like to specify some "version record files"; see below.

Documentation
-------------

For detailed documentation, see `https://nvchecker.readthedocs.io/en/latest/ <https://nvchecker.readthedocs.io/en/latest/>`_.
