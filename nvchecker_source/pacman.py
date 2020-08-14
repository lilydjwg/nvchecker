# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from nvchecker_source import cmd # type: ignore

async def get_version(name, conf, **kwargs):
  referree = conf.get('pacman') or name
  c = "LANG=C pacman -Si %s | grep -F Version | awk '{print $3}' | head -n 1" % referree
  conf['cmd'] = c
  strip_release = conf.get('strip_release', False)

  version = await cmd.get_version(name, conf, **kwargs)

  if strip_release and '-' in version:
    version = version.rsplit('-', 1)[0]
  return version
