# MIT licensed
# Copyright (c) 2013-2018 lilydjwg <lilydjwg@gmail.com>, et al.

from . import session, conf_cacheable_with_name

API_URL = 'https://crates.io/api/v1/crates/%s'

get_cacheable_conf = conf_cacheable_with_name('cratesio')

async def get_version(name, conf, **kwargs):
  name = conf.get('cratesio') or name
  async with session.get(API_URL % name) as res:
    data = await res.json()
  version = [v['num'] for v in data['versions'] if not v['yanked']][0]
  return version
