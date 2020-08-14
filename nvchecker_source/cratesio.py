# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

API_URL = 'https://crates.io/api/v1/crates/%s'

async def get_version(name, conf, *, cache, **kwargs):
  name = conf.get('cratesio') or name
  data = await cache.get_json(API_URL % name)
  version = [v['num'] for v in data['versions'] if not v['yanked']][0]
  return version
