# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from nvchecker.api import RichResult

HACKAGE_URL = 'https://hackage.haskell.org/package/%s/preferred.json'

async def get_version(name, conf, *, cache, **kwargs):
  key = conf.get('hackage', name)
  data = await cache.get_json(HACKAGE_URL % key)
  version = data['normal-version'][0]
  return RichResult(
    version = version,
    url = f'https://hackage.haskell.org/package/{key}-{version}',
  )
