# MIT licensed
# Copyright (c) 2017 lilydjwg <lilydjwg@gmail.com>, et al.

import logging
from . import session

logger = logging.getLogger(__name__)

URL = 'https://release-monitoring.org/api/project/{pkg}'

async def get_version(name, conf):
  pkg = conf.get('anitya')
  url = URL.format(pkg = pkg)

  async with session.get(url) as res:
    data = await res.json()

  return data['version']
