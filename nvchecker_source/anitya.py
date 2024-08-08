# MIT licensed
# Copyright (c) 2017-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from nvchecker.api import RichResult

URL = 'https://release-monitoring.org/api/project/{pkg}'

async def get_version(name, conf, *, cache, **kwargs):
  pkg = conf.get('anitya_id')
  if pkg is None:
    pkg = conf.get('anitya')
  url = URL.format(pkg = pkg)
  data = await cache.get_json(url)
  return RichResult(
    version = data['version'],
    url = f'https://release-monitoring.org/project/{data["id"]}/',
  )
