# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from . import cmd, conf_cacheable_with_name, strip_number

get_cacheable_conf = conf_cacheable_with_name('debianpkg')

async def get_version(name, conf, **kwargs):
  referree = conf.get('pacman') or strip_number(name)
  c = "LANG=C pacman -Si %s | grep -F Version | awk '{print $3}'" % referree
  conf['cmd'] = c
  strip_release = conf.getboolean('strip-release', False)

  version = await cmd.get_version(name, conf)

  if strip_release and '-' in version:
    version = version.rsplit('-', 1)[0]
  return version
