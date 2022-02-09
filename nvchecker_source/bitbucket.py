# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from typing import Any, List
from urllib.parse import urlencode

from nvchecker.api import VersionResult, Entry, AsyncCache

# doc: https://developer.atlassian.com/cloud/bitbucket/rest/api-group-commits/#api-repositories-workspace-repo-slug-commits-get
BITBUCKET_URL = 'https://bitbucket.org/api/2.0/repositories/%s/commits/%s'
# doc: https://developer.atlassian.com/cloud/bitbucket/rest/api-group-refs/#api-repositories-workspace-repo-slug-refs-tags-get
BITBUCKET_MAX_TAG = 'https://bitbucket.org/api/2.0/repositories/%s/refs/tags'

async def get_version(
  name: str, conf: Entry, *,
  cache: AsyncCache,
  **kwargs: Any,
) -> VersionResult:
  repo = conf['bitbucket']
  br = conf.get('branch', '')
  use_max_tag = conf.get('use_max_tag', False)
  use_sorted_tags = conf.get('use_sorted_tags', False)

  if use_sorted_tags or use_max_tag:
    parameters = {'fields': 'values.name,next'}

    if use_sorted_tags:
      parameters['sort'] = conf.get('sort', '-target.date')
      if 'query' in conf:
        parameters['q'] = conf['query']

  if use_sorted_tags:
    url = BITBUCKET_MAX_TAG % repo
    url += '?' + urlencode(parameters)

    version = await _get_tags(url, max_page=1, cache=cache)

  elif use_max_tag:
    url = BITBUCKET_MAX_TAG % repo
    url += '?' + urlencode(parameters)

    max_page = conf.get('max_page', 3)
    version = await _get_tags(url, max_page=max_page, cache=cache)

  else:
    url = BITBUCKET_URL % (repo, br)
    data = await cache.get_json(url)

    version = data['values'][0]['date'].split('T', 1)[0].replace('-', '')

  return version

async def _get_tags(
  url: str, *,
  max_page: int,
  cache: AsyncCache,
) -> List[str]:
  ret: List[str] = []

  for _ in range(max_page):
    data = await cache.get_json(url)
    ret.extend(x['name'] for x in data['values'])
    if 'next' in data:
      url = data['next']
    else:
      break

  return ret

