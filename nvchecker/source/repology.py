# MIT licensed
# Copyright (c) 2019 lilydjwg <lilydjwg@gmail.com>, et al.

import structlog
import functools

from . import session

logger = structlog.get_logger(logger_name=__name__)

API_URL = 'https://repology.org/api/v1/project/{}'

async def get_version(name, conf, **kwargs):
  project = conf.get('repology') or name
  repo = conf.get('repo')
  if not repo:
    logger.error('repo field is required for repology source', name = name)


  url = API_URL.format(project)
  data = await _request(url)

  versions = [pkg['version'] for pkg in data if pkg['repo'] == repo]
  if not versions:
    logger.error('package is not found', name=name, repo=repo)
    return

  return versions[0]

@functools.lru_cache()
async def _request(url):
  async with session.get(url) as res:
    return await res.json()
