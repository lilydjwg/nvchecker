# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

NPM_URL = 'https://registry.npmjs.org/%s'

async def get_version(name, conf, *, cache, **kwargs):
  key = conf.get('npm', name)
  data = await cache.get_json(NPM_URL % key, headers={"Accept": "application/vnd.npm.install-v1+json"})
  return data['dist-tags']['latest']
