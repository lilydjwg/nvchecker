# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import logging
from . import session

logger = logging.getLogger(__name__)

URL = 'https://www.archlinux.org/packages/search/json/'

async def get_version(name, conf):
  pkg = conf.get('archpkg') or name
  strip_release = conf.getboolean('strip-release', False)
  async with session.get(URL, params={"name": pkg}) as res:
    data = await res.json()

  if not data['results']:
    logger.error('Arch package not found: %s', name)
    return

  r = [r for r in data['results'] if r['repo'] != 'testing'][0]
  if strip_release:
    version = r['pkgver']
  else:
    version = r['pkgver'] + '-' + r['pkgrel']

  return version
