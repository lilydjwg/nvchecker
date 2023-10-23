# MIT licensed
# Copyright (c) 2013-2021 Th3Whit3Wolf <the.white.wolf.is.1337@gmail.com>, et al.

from nvchecker.api import RichResult

API_URL = 'https://open-vsx.org/api/%s/%s'

async def get_version(name, conf, *, cache, **kwargs):
  name = conf.get('openvsx') or name
  splitName = name.split('.')
  publisher = splitName[0]
  extension = splitName[1]
  data = await cache.get_json(API_URL % (publisher, extension))
  version = data['version']
  return RichResult(
    version = version,
    url = f'https://open-vsx.org/extension/{publisher}/{extension}/{version}',
  )
