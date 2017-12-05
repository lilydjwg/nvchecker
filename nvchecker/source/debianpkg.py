# MIT licensed
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import logging
from . import session

logger = logging.getLogger(__name__)

URL = 'https://sources.debian.org/api/src/%(pkgname)s/?suite=%(suite)s'

async def get_version(name, conf):
  pkg = conf.get('debianpkg') or name
  strip_release = conf.getboolean('strip-release', False)
  suite = conf.get('suite') or "sid"
  url = URL % {"pkgname": pkg, "suite": suite}
  async with session.get(url) as res:
    data = await res.json()

  if not data.get('versions'):
    logger.error('Debian package not found: %s', name)
    return

  r = data['versions'][0]
  if strip_release:
    version = r['version'].split("-")[0]
  else:
    version = r['version']

  return version
