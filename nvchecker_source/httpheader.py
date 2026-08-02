# MIT licensed
# Copyright (c) 2021 lilydjwg <lilydjwg@gmail.com>, et al.

import re

from nvchecker.api import session, GetVersionError

async def get_version(name, conf, *, cache, **kwargs):
  try:
    regex = re.compile(conf['regex'])
  except re.error as e:
    raise GetVersionError('bad regex', exc_info=e)

  key = (
    conf['url'],
    conf.get('method', 'HEAD'),
    conf.get('follow_redirects', False),
  )
  headers = await cache.get(key, get_headers)

  header = conf.get('header', 'Location')
  header_value = headers.get(header)
  if not header_value:
    raise GetVersionError(
      'header not found or is empty',
      header = header,
      value = header_value,
    )

  try:
    version = regex.findall(header_value)
  except ValueError:
    raise GetVersionError('version string not found.')
  return version

async def get_headers(info):
  url, method, follow_redirects = info

  res = await session.request(
    url,
    method = method,
    follow_redirects = follow_redirects,
  )
  return res.headers
