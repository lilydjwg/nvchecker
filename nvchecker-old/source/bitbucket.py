# MIT licensed
# Copyright (c) 2013-2019 lilydjwg <lilydjwg@gmail.com>, et al.

from . import session
from ..sortversion import sort_version_keys

# doc: https://confluence.atlassian.com/display/BITBUCKET/commits+or+commit+Resource
BITBUCKET_URL = 'https://bitbucket.org/api/2.0/repositories/%s/commits/%s'
BITBUCKET_MAX_TAG = 'https://bitbucket.org/api/2.0/repositories/%s/refs/tags'

async def get_version(name, conf, **kwargs):
  repo = conf.get('bitbucket')
  br = conf.get('branch', '')
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()
  sort_version_key = sort_version_keys[conf.get("sort_version_key", "parse_version")]

  if use_max_tag:
    url = BITBUCKET_MAX_TAG % repo
    max_page = conf.getint('max_page', 3)
    data = await _get_tags(url, max_page=max_page)

  else:
    url = BITBUCKET_URL % (repo, br)
    async with session.get(url) as res:
      data = await res.json()

  if use_max_tag:
    data = [tag for tag in data if tag not in ignored_tags]
    data.sort(key=sort_version_key)
    version = data
  else:
    version = data['values'][0]['date'].split('T', 1)[0].replace('-', '')
  return version

async def _get_tags(url, *, max_page):
  ret = []

  for _ in range(max_page):
    async with session.get(url) as res:
      data = await res.json()
    ret.extend(x['name'] for x in data['values'])
    if 'next' in data:
      url = data['next']
    else:
      break

  return ret

