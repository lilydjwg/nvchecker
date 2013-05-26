**nvchecker** (short for *new version checker*) is for checking if a new version of some software has been released.

nvchecker is now **in development**.

Configuration Files
===================

The configuration files are in ini format. *Section names* is the name of the software. Following fields are used to tell nvchecker how to determine the current version of that software.

See ``sample_config.ini`` for an example.

Search in a Webpage
-------------------
Search through a specific webpage for the version string. This type of version finding has these fields:

url
  The URL of the webpage to fetch.

encoding
  (*Optional*) The character encoding of the webpage, if ``latin1`` is not appropriate.

regex
  A regular expression used to find the version string.

  It can have zero or one capture group. The capture group or the whole match is the version string.

  When multiple version strings are found, the maximum of those is chosen.

Find with a Command
-------------------
Use a shell command line to get the version. The output is striped first, so trailing newlines do not bother.

cmd
  The command line to use. This will run with the system's standard shell (e.g. ``/bin/sh``).

Other
-----
More to come. Send me a patch or pull request if you can't wait and have written one yourself :-)

Dependency
==========
- Python 3
- Tornado
- All commands used in your configuration files

Running
=======
To see available options:

  ./nvchecker --help

Run with one or more configuration files:

  ./nvchecker config_file_1 config_file_2 ...
