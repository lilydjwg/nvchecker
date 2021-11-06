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
  if regex.groups > 1:
    raise GetVersionError('multi-group regex')

  encoding = conf.get('encoding', 'latin1')

  data = conf.get('post_data')
  if data is None:
    res = await session.get(conf['url'])
  else:
    res = await session.post(conf['url'], body = data, headers = {
        'Content-Type': conf.get('post_data_type', 'application/x-www-form-urlencoded')
      })
  body = res.body.decode(encoding)
  versions = regex.findall(body)
  if not versions and not conf.get('missing_ok', False):
    raise GetVersionError('version string not found.')
  return versions
