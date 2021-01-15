# MIT licensed
# Copyright (c) 2013-2021 lilydjwg <lilydjwg@gmail.com>, et al.

from packaging.version import Version

async def get_version(name, conf, *, cache, **kwargs):
  package = conf.get('pypi') or name
  use_pre_release = conf.get('use_pre_release', False)

  url = 'https://pypi.org/pypi/{}/json'.format(package)

  data = await cache.get_json(url)

  if use_pre_release:
    version = sorted(
      data['releases'].keys(),
      key = Version,
    )[-1]
  else:
    version = data['info']['version']
  return version
