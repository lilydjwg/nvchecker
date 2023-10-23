# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from nvchecker.api import RichResult

GEMS_URL = 'https://rubygems.org/api/v1/versions/%s.json'

async def get_version(name, conf, *, cache, **kwargs):
  key = conf.get('gems', name)
  data = await cache.get_json(GEMS_URL % key)
  return [
    RichResult(
      version = item['number'],
      url = f'https://rubygems.org/gems/{key}/versions/{item["number"]}',
    ) for item in data
  ]
