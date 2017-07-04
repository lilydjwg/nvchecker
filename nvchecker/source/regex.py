# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import sre_constants
import logging

from . import session
from ..sortversion import sort_version_keys

logger = logging.getLogger(__name__)

async def get_version(name, conf):
  try:
    regex = re.compile(conf['regex'])
  except sre_constants.error:
    logger.warn('%s: bad regex, skipped.', name, exc_info=True)
    return name, None

  encoding = conf.get('encoding', 'latin1')

  kwargs = {}
  headers = {}
  if conf.get('proxy'):
    kwargs["proxy"] = conf.get("proxy")
  if conf.get('user_agent'):
    headers['User-Agent'] = conf['user_agent']
  sort_version_key = sort_version_keys[conf.get("sort_version_key", "parse_version")]

  async with session.get(conf['url'], headers=headers, **kwargs) as res:
    version = None
    try:
      body = (await res.read()).decode(encoding)
      try:
        version = max(regex.findall(body), key=sort_version_key)
      except ValueError:
        logger.error('%s: version string not found.', name)
    finally:
      return name, version
