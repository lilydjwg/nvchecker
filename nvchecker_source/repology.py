# MIT licensed
# Copyright (c) 2019 lilydjwg <lilydjwg@gmail.com>, et al.

from nvchecker.util import GetVersionError

API_URL = 'https://repology.org/api/v1/project/{}'

async def get_version(name, conf, *, cache, **kwargs):
  project = conf.get('repology') or name
  repo = conf.get('repo')
  if not repo:
    raise GetVersionError('repo field is required for repology source')

  url = API_URL.format(project)
  data = await cache.get_json(url)

  versions = [pkg['version'] for pkg in data if pkg['repo'] == repo]
  if not versions:
    raise GetVersionError('package is not found', repo=repo)

  return versions[0]
