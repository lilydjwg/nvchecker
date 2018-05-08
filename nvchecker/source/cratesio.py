# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
from . import session

API_URL = 'https://crates.io/api/v1/crates/%s'

async def get_version(name, conf, **kwargs):
  name = conf.get('cratesio') or name
  async with session.get(API_URL % name) as res:
    data = await res.json()
  version = [v['num'] for v in data['versions'] if not v['yanked']][0]
  return version
