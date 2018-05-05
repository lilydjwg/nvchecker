# MIT licensed
# Copyright (c) 2017 lilydjwg <lilydjwg@gmail.com>, et al.

import structlog

from . import session

logger = structlog.get_logger(logger_name=__name__)

URL = 'https://release-monitoring.org/api/project/{pkg}'

async def get_version(name, conf, **kwargs):
  pkg = conf.get('anitya')
  url = URL.format(pkg = pkg)

  async with session.get(url) as res:
    data = await res.json()

  return data['version']
