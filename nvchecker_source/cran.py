# MIT licensed
# Copyright (c) 2022 Pekka Ristola <pekkarr [at] protonmail [dot] com>, et al.

from nvchecker.api import session, RichResult, GetVersionError

CRAN_URL = 'https://cran.r-project.org/package=%s/DESCRIPTION'
VERSION_FIELD = 'Version: '

async def request(pkg):
  url = CRAN_URL % pkg
  res = await session.get(url)
  return res.body.decode('utf-8', errors='ignore')

async def get_version(name, conf, *, cache, **kwargs):
  package = conf.get('cran', name)

  desc = await cache.get(package, request)

  for line in desc.splitlines():
    if line.startswith(VERSION_FIELD):
      version = line[len(VERSION_FIELD):]
      break
  else:
    raise GetVersionError('Invalid DESCRIPTION file')

  return RichResult(
    version = version,
    url = f'https://cran.r-project.org/web/packages/{package}/',
  )
