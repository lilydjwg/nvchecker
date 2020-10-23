# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from nvchecker.api import session, GetVersionError

URL = 'https://www.archlinux.org/packages/search/json/'

async def request(pkg):
  res = await session.get(URL, params={"name": pkg})
  return res.json()

async def get_version(name, conf, *, cache, **kwargs):
  pkg = conf.get('archpkg') or name
  strip_release = conf.get('strip_release', False)
  provided = conf.get('provided')

  data = await cache.get(pkg, request)

  if not data['results']:
    raise GetVersionError('Arch package not found')

  r = [r for r in data['results'] if r['repo'] != 'testing'][0]

  if provided:
    provides = dict(x.split('=', 1) for x in r['provides'] if '=' in x)
    version = provides.get(provided, None)
    if strip_release:
      version = version.split('-', 1)[0]
  elif strip_release:
    version = r['pkgver']
  else:
    version = r['pkgver'] + '-' + r['pkgrel']

  return version
