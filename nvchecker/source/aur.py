# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import structlog
from datetime import datetime

from . import session, conf_cacheable_with_name

logger = structlog.get_logger(logger_name=__name__)

AUR_URL = 'https://aur.archlinux.org/rpc/?v=5&type=info&arg[]='

get_cacheable_conf = conf_cacheable_with_name('aur')

async def get_version(name, conf, **kwargs):
  aurname = conf.get('aur') or name
  use_last_modified = conf.getboolean('use_last_modified', False)
  strip_release = conf.getboolean('strip-release', False)
  async with session.get(AUR_URL, params={"v": 5, "type": "info", "arg[]": aurname}) as res:
    data = await res.json()

  if not data['results']:
    logger.error('AUR upstream not found', name=name)
    return

  version = data['results'][0]['Version']
  if use_last_modified:
    version += '-' + datetime.utcfromtimestamp(data['results'][0]['LastModified']).strftime('%Y%m%d%H%M%S')
  if strip_release and '-' in version:
    version = version.rsplit('-', 1)[0]
  return version
