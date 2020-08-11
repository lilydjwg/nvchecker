# MIT licensed
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import structlog

from . import session, conf_cacheable_with_name

logger = structlog.get_logger(logger_name=__name__)

URL = 'https://sources.debian.org/api/src/%(pkgname)s/?suite=%(suite)s'

get_cacheable_conf = conf_cacheable_with_name('debianpkg')

async def get_version(name, conf, **kwargs):
  pkg = conf.get('debianpkg') or name
  strip_release = conf.getboolean('strip-release', False)
  suite = conf.get('suite') or "sid"
  url = URL % {"pkgname": pkg, "suite": suite}
  async with session.get(url) as res:
    data = await res.json()

  if not data.get('versions'):
    logger.error('Debian package not found', name=name)
    return

  r = data['versions'][0]
  if strip_release:
    version = r['version'].split("-")[0]
  else:
    version = r['version']

  return version
