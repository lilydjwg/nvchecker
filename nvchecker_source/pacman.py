# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from nvchecker.api import Entry
from nvchecker_source import cmd

async def get_version(name: str, conf: Entry, **kwargs) -> str:
  referree = conf.get('pacman') or name
  c = "LANG=C pacman -Si %s | grep -F Version | awk '{print $3}' | head -n 1" % referree
  conf['cmd'] = c
  strip_release = conf.get('strip_release', False)

  versions = await cmd.get_version(name, conf, **kwargs)
  version = versions[0]

  if strip_release and '-' in version:
    version = version.rsplit('-', 1)[0]
  return version
