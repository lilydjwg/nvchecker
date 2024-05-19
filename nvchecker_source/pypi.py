# MIT licensed
# Copyright (c) 2013-2021 lilydjwg <lilydjwg@gmail.com>, et al.

from packaging.version import Version

from nvchecker.api import RichResult

async def get_version(name, conf, *, cache, **kwargs):
  ret = []

  package = conf.get('pypi') or name
  use_pre_release = conf.get('use_pre_release', False)

  url = 'https://pypi.org/pypi/{}/json'.format(package)

  data = await cache.get_json(url)

  for version in data['releases'].keys():
    parsed_version = Version(version)

    if not use_pre_release and parsed_version.is_prerelease:
      continue

    ret.append(RichResult(
      version = version,
      url = f'https://pypi.org/project/{package}/{version}/',
    ))

  return ret
