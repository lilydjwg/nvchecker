Usage of nvchecker commands
===========================

**nvchecker** (short for *new version checker*) is for checking if a new version of some software has been released.

This is the version 2.0 branch. For the old version 1.x, please switch to the ``v1.x`` branch.

.. image:: https://travis-ci.org/lilydjwg/nvchecker.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/lilydjwg/nvchecker
.. image:: https://badge.fury.io/py/nvchecker.svg
   :alt: PyPI version
   :target: https://badge.fury.io/py/nvchecker

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

JSON logging
~~~~~~~~~~~~
With ``--logger=json`` or ``--logger=both``, you can get a structured logging
for programmatically consuming. You can use ``--json-log-fd=FD`` to specify the
file descriptor to send logs to (take care to do line buffering). The logging
level option (``-l`` or ``--logging``) doesn't take effect with this.

The JSON log is one JSON string per line. The following documented events and
fields are stable, undocumented ones may change without notice.

event=updated
  An update is detected. Fields ``name``, ``old_version`` and ``version`` are
  available. ``old_version`` maybe ``null``.

event=up-to-date
  There is no update. Fields ``name`` and ``version`` are available.

event=no-result
  No version is detected. There may be an error. Fields ``name`` is available.

level=error
  There is an error. Fields ``name`` and ``exc_info`` may be available to give
  further information.

Upgrade from 1.x version
~~~~~~~~~~~~~~~~~~~~~~~~

There are several backward-incompatible changes from the previous 1.x version.

1. Version 2.x requires Python 3.7+ to run.
2. The command syntax changes a bit. You need to use a ``-c`` switch to specify your software version configuration file (or use the default).
3. The configuration file format has been changed from ini to `toml`_. You can use the ``nvchecker-ini2toml`` script to convert your old configuration files. However, comments and formatting will be lost, and some options may not be converted correctly.
4. Several options have been renamed. ``max_concurrent`` to ``max_concurrency``, and all option names have their ``-`` be replaced with ``_``.
5. All software configuration tables need a ``source`` option to specify which source is to be used rather than being figured out from option names in use. This enables additional source plugins to be discovered.
6. The version record files have been changed to use JSON format (the old format will be converted on writing).
7. The ``vcs`` source is removed. (It's available inside `lilac <https://github.com/archlinuxcn/lilac>`_ at the moment.) A ``git`` source is provided.
8. ``include_tags_pattern`` and ``ignored_tags`` are removed. Use :ref:`list options` instead.

Version Record Files
--------------------
Version record files record which version of the software you know or is available. They are a simple JSON object mapping software names to known versions.

The ``nvtake`` Command
~~~~~~~~~~~~~~~~~~~~~~
This command helps to manage version record files. It reads both old and new version record files, and a list of names given on the commandline. It then update the versions of those names in the old version record file.

This helps when you have known (and processed) some of the updated software, but not all. You can tell nvchecker that via this command instead of editing the file by hand.

This command will help most if you specify where you version record files are in your config file. See below for how to use a config file.

The ``nvcmp`` Command
~~~~~~~~~~~~~~~~~~~~~
This command compares the ``newver`` file with the ``oldver`` one and prints out any differences as updates, e.g.::

    $ nvcmp -c sample_source.toml
    Sparkle Test App None -> 2.0
    test 0.0 -> 0.1

Configuration Files
-------------------
The software version source files are in `toml`_ format. The *key name* is the name of the software. Following fields are used to tell nvchecker how to determine the current version of that software.

See ``sample_source.toml`` for an example.

Configuration Table
~~~~~~~~~~~~~~~~~~~
A special table named ``__config__`` provides some configuration options.

Relative path are relative to the source files, and ``~`` and environmental variables are expanded.

Currently supported options are:

oldver
  Specify a version record file containing the old version info.

newver
  Specify a version record file to store the new version info.

proxy
  The HTTP proxy to use. The format is ``proto://host:port``, e.g. ``http://localhost:8087``. Different backends have different level support for this, e.g. with ``pycurl`` you can use ``socks5h://host:port`` proxies.

max_concurrency
  Max number of concurrent jobs. Default: 20.

http_timeout
  Time in seconds to wait for HTTP requests. Default: 20.

keyfile
  Specify an ini config file containing key (token) information. This file
  should contain a ``keys`` table, mapping key names to key values. See
  specific source for the key name(s) to use.

Global Options
~~~~~~~~~~~~~~
The following options apply to every check sources. You can use them in any
item in your configuration file.

prefix
  Strip the prefix string if the version string starts with it. Otherwise the
  version string is returned as-is.

from_pattern, to_pattern
  Both are Python-compatible regular expressions. If ``from_pattern`` is found
  in the version string, it will be replaced with ``to_pattern``.

missing_ok
  Suppress warnings and errors if a version checking module finds nothing.
  Currently only ``regex`` supports it.

proxy
  The HTTP proxy to use. The format is ``proto://host:port``, e.g.
  ``http://localhost:8087``. Different backends have different level support
  for this, e.g. with ``pycurl`` you can use ``socks5h://host:port`` proxies.

  Set it to ``""`` (empty string) to override the global setting.

  This only works when the source implementation uses the builtin HTTP client,
  and doesn't work with the ``aur`` source because it's batched (however the
  global proxy config still applies).

user_agent
  The user agent string to use for HTTP requests.

tries
  Try specified times when a network error occurs. Default is ``1``.

  This only works when the source implementation uses the builtin HTTP client.

If both ``prefix`` and ``from_pattern``/``to_pattern`` are used,
``from_pattern``/``to_pattern`` are ignored. If you want to strip the prefix
and then do something special, just use ``from_pattern```/``to_pattern``. For
example, the transformation of ``v1_1_0`` => ``1.1.0`` can be achieved with
``from_pattern = v(\d+)_(\d+)_(\d+)`` and ``to_pattern = \1.\2.\3``.

.. _list options:

List Options
~~~~~~~~~~~~

The following options apply to sources that return a list. See
individual source tables to determine whether they are
supported.

include_regex
  Only consider version strings that match the given regex. The whole string
  should match the regex. Be sure to use ``.*`` when you mean it!

exclude_regex
  Don't consider version strings that match the given regex. The whole string
  should match the regex. Be sure to use ``.*`` when you mean it! This option
  has higher precedence that ``include_regex``; that is, if matched by this
  one, it's excluded even it's also matched by ``include_regex``.

sort_version_key
  Sort the version string using this key function. Choose between
  ``parse_version`` and ``vercmp``. Default value is ``parse_version``.
  ``parse_version`` use ``pkg_resources.parse_version``. ``vercmp`` use
  ``pyalpm.vercmp``.

ignored
  Version strings that are explicitly ignored, separated by whitespace. This
  can be useful to avoid some known mis-named versions, so newer ones won't be
  "overridden" by the old broken ones.

Search in a Webpage
~~~~~~~~~~~~~~~~~~~
::

  source = "regex"

Search through a specific webpage for the version string. This type of version finding has these fields:

url
  The URL of the webpage to fetch.

encoding
  (*Optional*) The character encoding of the webpage, if ``latin1`` is not appropriate.

regex
  A regular expression used to find the version string.

  It can have zero or one capture group. The capture group or the whole match is the version string.

  When multiple version strings are found, the maximum of those is chosen.

This source supports :ref:`list options`.

Search in an HTTP header
~~~~~~~~~~~~~~~~~~~~~~~~
::

  source = "httpheader"

Send an HTTP request and search through a specific header.

url
  The URL of the HTTP request.

header
  (*Optional*) The header to look at. Default is ``Location``. Another useful header is ``Content-Disposition``.

regex
  A regular expression used to find the version string.

  It can have zero or one capture group. The capture group or the whole match is the version string.

  When multiple version strings are found, the maximum of those is chosen.

method
  (*Optional*) The HTTP method to use. Default is ``HEAD``.

follow_redirects
  (*Optional*) Whether to follow 3xx HTTP redirects. Default is ``false``. If you are looking at a ``Location`` header, you shouldn't change this.


Find with a Command
~~~~~~~~~~~~~~~~~~~
::

  source = "cmd"

Use a shell command line to get the version. The output is striped first, so trailing newlines do not bother.

cmd
  The command line to use. This will run with the system's standard shell (i.e. ``/bin/sh``).

Check AUR
~~~~~~~~~
::

  source = "aur"

Check `Arch User Repository <https://aur.archlinux.org/>`_ for updates.
Per-item proxy setting doesn't work for this because several items will be
batched into one request.

aur
  The package name in AUR. If empty, use the name of software (the *table name*).

strip_release
  Strip the release part.

use_last_modified
  Append last modified time to the version.

Check GitHub
~~~~~~~~~~~~
::

  source = "github"

Check `GitHub <https://github.com/>`_ for updates. The version returned is in
date format ``%Y%m%d.%H%M%S``, e.g. ``20130701.012212``, unless ``use_latest_release``
or ``use_max_tag`` is used. See below.

github
  The github repository, with author, e.g. ``lilydjwg/nvchecker``.

branch
  Which branch to track? Default: ``master``.

path
  Only commits containing this file path will be returned.

use_latest_release
  Set this to ``true`` to check for the latest release on GitHub.

  GitHub releases are not the same with git tags. You'll see big version names
  and descriptions in the release page for such releases, e.g.
  `zfsonlinux/zfs's <https://github.com/zfsonlinux/zfs/releases>`_, and those
  small ones like `nvchecker's <https://github.com/lilydjwg/nvchecker/releases>`_
  are only git tags that should use ``use_max_tag`` below.

  Will return the release name instead of date.

use_latest_tag
  Set this to ``true`` to check for the latest tag on GitHub.

  This requires a token because it's using the v4 GraphQL API.

query
  When ``use_latest_tag`` is ``true``, this sets a query for the tag. The exact
  matching method is not documented by GitHub.

use_max_tag
  Set this to ``true`` to check for the max tag on GitHub. Unlike
  ``use_latest_release``, this option includes both annotated tags and
  lightweight ones, and return the largest one sorted by the
  ``sort_version_key`` option. Will return the tag name instead of date.

token
  A personal authorization token used to call the API.

An authorization token may be needed in order to use ``use_latest_tag`` or to
request more frequently than anonymously.

To set an authorization token, you can set:

- a key named ``github`` in the keyfile
- the token option

This source supports :ref:`list options` when ``use_max_tag`` is set.

Check Gitea
~~~~~~~~~~~
::

  source = "gitea"

Check `Gitea <https://gitea.com/>`_ for updates. The version returned is in date format ``%Y%m%d``, e.g. ``20130701``,
unless ``use_max_tag`` is used. See below.

gitea
  The gitea repository, with author, e.g. ``gitea/tea``.

branch
  Which branch to track? Default: ``master``.

use_max_tag
  Set this to ``true`` to check for the max tag on Gitea. Will return the biggest one
  sorted by ``pkg_resources.parse_version``. Will return the tag name instead of date.

host
  Hostname for self-hosted Gitea instance.

token
  Gitea authorization token used to call the API.

To set an authorization token, you can set:

- a key named ``gitea_{host}`` in the keyfile, where ``host`` is all-lowercased host name
- the token option

This source supports :ref:`list options` when ``use_max_tag`` is set.

Check BitBucket
~~~~~~~~~~~~~~~
::

  source = "bitbucket"

Check `BitBucket <https://bitbucket.org/>`_ for updates. The version returned
is in date format ``%Y%m%d``, e.g. ``20130701``, unless ``use_max_tag`` is used. See below.

bitbucket
  The bitbucket repository, with author, e.g. ``lilydjwg/dotvim``.

branch
  Which branch to track? Default is the repository's default.

use_max_tag
  Set this to ``true`` to check for the max tag on BitBucket. Will return the biggest one
  sorted by ``pkg_resources.parse_version``. Will return the tag name instead of date.

max_page
  How many pages do we search for the max tag? Default is 3. This works when
  ``use_max_tag`` is set.

This source supports :ref:`list options` when ``use_max_tag`` is set.

Check GitLab
~~~~~~~~~~~~
::

  source = "gitlab"

Check `GitLab <https://gitlab.com/>`_ for updates. The version returned is in date format ``%Y%m%d``, e.g. ``20130701``,
unless ``use_max_tag`` is used. See below.

gitlab
  The gitlab repository, with author, e.g. ``Deepin/deepin-music``.

branch
  Which branch to track? Default: ``master``.

use_max_tag
  Set this to ``true`` to check for the max tag on GitLab. Will return the biggest one
  sorted by ``pkg_resources.parse_version``. Will return the tag name instead of date.

host
  Hostname for self-hosted GitLab instance.

token
  GitLab authorization token used to call the API.

To set an authorization token, you can set:

- a key named ``gitlab_{host}`` in the keyfile, where ``host`` is all-lowercased host name
- the token option

This source supports :ref:`list options` when ``use_max_tag`` is set.

Check PyPI
~~~~~~~~~~
::

  source = "pypi"

Check `PyPI <https://pypi.python.org/>`_ for updates.

pypi
  The name used on PyPI, e.g. ``PySide``.

use_pre_release
  Whether to accept pre release. Default is false.

Check RubyGems
~~~~~~~~~~~~~~
::

  source = "gems"

Check `RubyGems <https://rubygems.org/>`_ for updates.

gems
  The name used on RubyGems, e.g. ``sass``.

This source supports :ref:`list options`.

Check NPM Registry
~~~~~~~~~~~~~~~~~~
::

  source = "npm"

Check `NPM Registry <https://registry.npmjs.org/>`_ for updates.

npm
  The name used on NPM Registry, e.g. ``coffee-script``.

To configure which registry to query, a source plugin option is available.
You can specify like this::

  [__config__.source.npm]
  registry = "https://registry.npm.taobao.org"

Check Hackage
~~~~~~~~~~~~~
::

  source = "hackage"

Check `Hackage <https://hackage.haskell.org/>`_ for updates.

hackage
  The name used on Hackage, e.g. ``pandoc``.

Check CPAN
~~~~~~~~~~
::

  source = "cpan"

Check `MetaCPAN <https://metacpan.org/>`_ for updates.

cpan
  The name used on CPAN, e.g. ``YAML``.

Check Packagist
~~~~~~~~~~~~~~~
::

  source = "packagist"

Check `Packagist <https://packagist.org/>`_ for updates.

packagist
  The name used on Packagist, e.g. ``monolog/monolog``.

Check Local Pacman Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

  source = "pacman"

This is used when you run ``nvchecker`` on an Arch Linux system and the program always keeps up with a package in your configured repositories for `Pacman`_.

pacman
  The package name to reference to.

strip_release
  Strip the release part.

Check Arch Linux official packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

  source = "archpkg"

This enables you to track the update of `Arch Linux official packages <https://www.archlinux.org/packages/>`_, without needing of pacman and an updated local Pacman databases.

archpkg
  Name of the Arch Linux package.

strip_release
  Strip the release part, only return part before ``-``.

provided
  Instead of the package version, return the version this package provides. Its value is what the package provides, and ``strip_release`` takes effect too. This is best used with libraries.

Check Debian Linux official packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

  source = "debianpkg"

This enables you to track the update of `Debian Linux official packages <https://packages.debian.org>`_, without needing of apt and an updated local APT database.

debianpkg
  Name of the Debian Linux source package.

suite
  Name of the Debian release (jessie, wheezy, etc, defaults to sid)

strip_release
  Strip the release part.

Check Ubuntu Linux official packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

  source = "ubuntupkg"

This enables you to track the update of `Ubuntu Linux official packages <https://packages.ubuntu.com/>`_, without needing of apt and an updated local APT database.

ubuntupkg
  Name of the Ubuntu Linux source package.

suite
  Name of the Ubuntu release (xenial, zesty, etc, defaults to None, which means no limit on suite)

strip_release
  Strip the release part.

Check Repology
~~~~~~~~~~~~~~
::

  source = "repology"

This enables you to track updates from `Repology <https://repology.org/>`_ (repology.org).

repology
  Name of the ``project`` to check.

repo
  Check the version in this repo. This field is required.

subrepo
  Check the version in this subrepo. This field is optional.
  When ommited all subrepos are queried.

This source supports :ref:`list options`.

Check Anitya
~~~~~~~~~~~~
::

  source = "anitya"

This enables you to track updates from `Anitya <https://release-monitoring.org/>`_ (release-monitoring.org).

anitya
  ``distro/package``, where ``distro`` can be a lot of things like "fedora", "arch linux", "gentoo", etc. ``package`` is the package name of the chosen distribution.

Check Android SDK
~~~~~~~~~~~~~~~~~
::

  source = "android_sdk"

This enables you to track updates of Android SDK packages listed in ``sdkmanager --list``.

android_sdk
  The package path prefix. This value is matched against the ``path`` attribute in all <remotePackage> nodes in an SDK manifest XML. The first match is used for version comparisons.

repo
  Should be one of ``addon`` or ``package``. Packages in ``addon2-1.xml`` use ``addon`` and packages in ``repository2-1.xml`` use ``package``.

channel
  Choose the target channel from one of ``stable``, ``beta``, ``dev`` or ``canary``. This option also accepts a comma-seperated list to pick from multiple channels. For example, the latest unstable version is picked with ``beta,dev,canary``.

Check Sparkle framework
~~~~~~~~~~~~~~~~~~~~~~~
::

  source = "sparkle"

This enables you to track updates of macOS applications which using `Sparkle framework <https://sparkle-project.org/>`_.

sparkle
  The url of the sparkle appcast.

Check Pagure
~~~~~~~~~~~~
::

  source = "pagure"

This enables you to check updates from `Pagure <https://pagure.io>`_.

pagure
  The project name, optionally with a namespace.

host
  Hostname of alternative instance like src.fedoraproject.org.

This source returns tags and supports :ref:`list options`.

Check APT repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

  source = "apt"

This enables you to track the update of an arbitrary APT repository, without needing of apt and an updated local APT database.

pkg
  Name of the APT binary package.

srcpkg
  Name of the APT source package.

mirror
  URL of the repository.

suite
  Name of the APT repository release (jessie, wheezy, etc)

repo
  Name of the APT repository (main, contrib, etc, defaults to main)

arch
  Architecture of the repository (i386, amd64, etc, defaults to amd64)

strip_release
  Strip the release part.

Note that either pkg or srcpkg needs to be specified (but not both) or the item name will be used as pkg.

Check Git repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

  source = "git"

This enables you to check tags or branch commits of an arbitrary git repository, also useful for scenarios like a github project having too many tags.

git
  URL of the Git repository.

use_commit
  Return a commit hash instead of tags.

branch
  When ``use_commit`` is true, return the commit on the specified branch instead of the default one.

When this source returns tags (``use_commit`` is not true) it supports :ref:`list options`.

Check container registry
~~~~~~~~~~~~~~~~~~~~~~~~
::

  source = "container"

This enables you to check tags of images on a container registry like Docker.

container
  The path for the container image. For official Docker images, use namespace ``library/`` (e.g. ``library/python``).

registry
  The container registry host. Default: ``docker.io``

This source returns tags and supports :ref:`list options`.

Check ALPM database
~~~~~~~~~~~~~~~~~~~
::

  source = "alpm"

Check package updates in a local ALPM database.

alpm
  Name of the package.

repo
  Name of the package repository in which the package resides.

dbpath
  Path to the ALPM database directory. Default: ``/var/lib/pacman``.

strip_release
  Strip the release part, only return the part before ``-``.

provided
  Instead of the package version, return the version this package provides. Its value is what the package provides, and ``strip_release`` takes effect too. This is best used with libraries.

Manually updating
~~~~~~~~~~~~~~~~~
::

  source = "manual"

This enables you to manually specify the version (maybe because you want to approve each release before it gets to the script).

manual
  The version string.

Extending
~~~~~~~~~
It's possible to extend the supported sources by writing
plugins. See :doc:`plugin` for documentation.

.. _Pacman: https://wiki.archlinux.org/index.php/Pacman
.. _toml: https://toml.io/
