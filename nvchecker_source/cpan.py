# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from nvchecker.api import RichResult

# Using metacpan
CPAN_URL = 'https://fastapi.metacpan.org/release/%s'

async def get_version(name, conf, *, cache, **kwargs):
  key = conf.get('cpan', name)
  data = await cache.get_json(CPAN_URL % key)
  return RichResult(
    version = str(data['version']),
    url = f'https://metacpan.org/release/{data["author"]}/{data["name"]}',
  )
