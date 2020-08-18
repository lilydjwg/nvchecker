# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

PACKAGIST_URL = 'https://packagist.org/packages/%s.json'

async def get_version(name, conf, *, cache, **kwargs):
  key = conf.get('packagist', name)
  data = await cache.get_json(PACKAGIST_URL % key)

  versions = {
    version: details
    for version, details in data["package"]['versions'].items()
    if version != "dev-master"
  }

  if len(versions):
    return max(versions, key=lambda version: versions[version]["time"])
