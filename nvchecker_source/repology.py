# MIT licensed
# Copyright (c) 2019 lilydjwg <lilydjwg@gmail.com>, et al.

from nvchecker.api import GetVersionError

API_URL = 'https://repology.org/api/v1/project/{}'

async def get_version(name, conf, *, cache, **kwargs):
  project = conf.get('repology') or name
  repo = conf.get('repo')
  subrepo = conf.get('subrepo')
  if not repo:
    raise GetVersionError('repo field is required for repology source')

  url = API_URL.format(project)
  data = await cache.get_json(url)

  pkgs = [pkg for pkg in data if pkg['repo'] == repo]
  if not pkgs:
    raise GetVersionError('package is not found', repo=repo)

  if subrepo:
    pkgs = [pkg for pkg in pkgs if pkg.get('subrepo') == subrepo]
    if not pkgs:
        raise GetVersionError('package is not found in subrepo',
                              repo=repo, subrepo=subrepo)

  versions = [pkg['version'] for pkg in pkgs]
  return versions
