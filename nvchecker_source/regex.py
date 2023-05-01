# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import re

from nvchecker.api import session, GetVersionError

async def get_version(name, conf, *, cache, **kwargs):
  try:
    regex = re.compile(conf['regex'])
  except re.error as e:
    raise GetVersionError('bad regex', exc_info=e)
  if regex.groups > 1:
    raise GetVersionError('multi-group regex')

  key = (
    conf['url'],
    conf.get('encoding', 'latin1'),
    conf.get('post_data'),
    conf.get('post_data_type', 'application/x-www-form-urlencoded'),
  )
  body = await cache.get(key, get_url)

  versions = regex.findall(body)
  if not versions and not conf.get('missing_ok', False):
    raise GetVersionError('version string not found.')
  return versions

async def get_url(info):
  url, encoding, post_data, post_data_type = info

  if post_data is None:
    res = await session.get(url)
  else:
    res = await session.post(url, body = post_data, headers = {
      'Content-Type': post_data_type,
    })
  body = res.body.decode(encoding)
  return body
