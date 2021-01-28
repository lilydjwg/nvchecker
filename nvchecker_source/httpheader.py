# MIT licensed
# Copyright (c) 2021 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import sre_constants

from nvchecker.api import session, GetVersionError

async def get_version(name, conf, *, cache, **kwargs):
  key = tuple(sorted(conf.items()))
  return await cache.get(key, get_version_impl)

async def get_version_impl(info):
  conf = dict(info)
  url = conf['url']
  header = conf.get('header', 'Location')
  follow_redirects = conf.get('follow_redirects', False)
  method = conf.get('method', 'HEAD')

  try:
    regex = re.compile(conf['regex'])
  except sre_constants.error as e:
    raise GetVersionError('bad regex', exc_info=e)

  res = await session.request(
    url,
    method = method,
    follow_redirects = follow_redirects,
  )

  header_value = res.headers.get(header)
  if not header_value:
    raise GetVersionError('header %s not found or is empty' % header)

  try:
    version = regex.findall(header_value)
  except ValueError:
    raise GetVersionError('version string not found.')
  return version
