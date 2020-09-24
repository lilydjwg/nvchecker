# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import json
import re
from nvchecker.api import session

NPM_URL = 'https://registry.npmjs.org/%s'

def configure(config):
  global NPM_URL
  url = config.get('registry')
  if url:
    NPM_URL = f'{url.rstrip("/")}/%s'

async def get_first_1k(url):
  headers = {
    "Accept": "application/vnd.npm.install-v1+json",
    "Range": "bytes=0-1023",
  }
  res = await session.get(url, headers=headers)
  return res.body

async def get_version(name, conf, *, cache, **kwargs):
  key = conf.get('npm', name)
  data = await cache.get(NPM_URL % key, get_first_1k)

  dist_tags = json.loads(re.search(b'"dist-tags":({.*?})', data).group(1))
  return dist_tags['latest']
