# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import structlog

from . import session, conf_cacheable_with_name, strip_number

logger = structlog.get_logger(logger_name=__name__)

URL = 'https://www.archlinux.org/packages/search/json/'

get_cacheable_conf = conf_cacheable_with_name('archpkg')

async def get_version(name, conf, **kwargs):
  pkg = conf.get('archpkg') or strip_number(name)
  strip_release = conf.getboolean('strip-release', False)
  async with session.get(URL, params={"name": pkg}) as res:
    data = await res.json()

  if not data['results']:
    logger.error('Arch package not found', name=name)
    return

  r = [r for r in data['results'] if r['repo'] != 'testing'][0]
  if strip_release:
    version = r['pkgver']
  else:
    version = r['pkgver'] + '-' + r['pkgrel']

  return version
