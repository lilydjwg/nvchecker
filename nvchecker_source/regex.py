# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import sre_constants

import structlog

from nvchecker.httpclient import session
from nvchecker.util import GetVersionError

logger = structlog.get_logger(logger_name=__name__)

async def get_version(name, conf, *, cache, **kwargs):
  key = sorted(conf.items())
  return await cache.get(key, get_version_impl)

async def get_version_impl(info):
  conf = dict(info)

  try:
    regex = re.compile(conf['regex'])
  except sre_constants.error as e:
    raise GetVersionError('bad regex', exc_info=e)

  encoding = conf.get('encoding', 'latin1')

  kwargs = {}
  headers = {}
  if conf.get('proxy'):
    kwargs["proxy"] = conf.get("proxy")
  if conf.get('user_agent'):
    headers['User-Agent'] = conf['user_agent']

  async with session.get(conf['url'], headers=headers, **kwargs) as res:
    body = (await res.read()).decode(encoding)
    try:
      version = regex.findall(body)
    except ValueError:
      version = None
      if not conf.get('missing_ok', False):
        raise GetVersionError('version string not found.')
    return version
