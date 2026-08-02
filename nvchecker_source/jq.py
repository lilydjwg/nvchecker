# MIT licensed
# Copyright (c) 2024 Rocket Aaron <i@rocka.me>, et al.

import json
import jq

from nvchecker.api import session, GetVersionError

async def get_version(name, conf, *, cache, **kwargs):
  try:
    program = jq.compile(conf.get('filter', '.'))
  except ValueError as e:
    raise GetVersionError('bad jq filter', exc_info=e)

  key = (
    conf['url'],
    conf.get('post_data'),
    conf.get('post_data_type', 'application/json'),
  )
  obj = await cache.get(key, get_json)

  try:
    version = program.input(obj).all()
    if version == [None] and not conf.get('missing_ok', False):
      raise GetVersionError('version string not found.')
    version = [str(v) for v in version]
  except ValueError as e:
    raise GetVersionError('failed to filter json', exc_info=e)

  return version

async def get_json(info):
  url, post_data, post_data_type = info

  if post_data is None:
    res = await session.get(url)
  else:
    res = await session.post(url, body = post_data, headers = {
      'Content-Type': post_data_type,
    })

  try:
    return json.loads(res.body)
  except json.decoder.JSONDecodeError as e:
    raise GetVersionError('bad json string', exc_info=e)
