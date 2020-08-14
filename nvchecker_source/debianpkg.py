# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

from nvchecker.api import GetVersionError

URL = 'https://sources.debian.org/api/src/%(pkgname)s/?suite=%(suite)s'

async def get_version(name, conf, *, cache, **kwargs):
  pkg = conf.get('debianpkg') or name
  strip_release = conf.get('strip_release', False)
  suite = conf.get('suite') or "sid"
  url = URL % {"pkgname": pkg, "suite": suite}
  data = await cache.get_json(url)

  if not data.get('versions'):
    raise GetVersionError('Debian package not found')

  r = data['versions'][0]
  if strip_release:
    version = r['version'].split("-")[0]
  else:
    version = r['version']

  return version
