# MIT licensed
# Copyright (c) 2024 Rocket Aaron <i@rocka.me>, et al.

import json
import jq

from nvchecker.api import session, GetVersionError

async def get_version(name, conf, *, cache, **kwargs):
  key = tuple(sorted(conf.items()))
  return await cache.get(key, get_version_impl)

async def get_version_impl(info):
  conf = dict(info)

  try:
    program = jq.compile(conf.get('filter', '.'))
  except ValueError as e:
    raise GetVersionError('bad jq filter', exc_info=e)

  data = conf.get('post_data')
  if data is None:
    res = await session.get(conf['url'])
  else:
    res = await session.post(conf['url'], body = data, headers = {
        'Content-Type': conf.get('post_data_type', 'application/json')
      })

  try:
    obj = json.loads(res.body)
  except json.decoder.JSONDecodeError as e:
    raise GetVersionError('bad json string', exc_info=e)

  try:
    version = program.input(obj).all()
    if version == [None] and not conf.get('missing_ok', False):
      raise GetVersionError('version string not found.')
    version = [str(v) for v in version]
  except ValueError as e:
    raise GetVersionError('failed to filter json', exc_info=e)

  return version
