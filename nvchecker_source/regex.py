# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import sre_constants

from nvchecker.api import session, GetVersionError

async def get_version(name, conf, *, cache, **kwargs):
  key = tuple(sorted(conf.items()))
  return await cache.get(key, get_version_impl)

async def get_version_impl(info):
  conf = dict(info)

  try:
    regex = re.compile(conf['regex'])
  except sre_constants.error as e:
    raise GetVersionError('bad regex', exc_info=e)

  encoding = conf.get('encoding', 'latin1')

  res = await session.get(conf['url'])
  body = res.body.decode(encoding)
  try:
    version = regex.findall(body)
  except ValueError:
    if not conf.get('missing_ok', False):
      raise GetVersionError('version string not found.')
  return version
