# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

# doc: https://developer.atlassian.com/cloud/bitbucket/rest/api-group-commits/#api-repositories-workspace-repo-slug-commits-get
BITBUCKET_URL = 'https://bitbucket.org/api/2.0/repositories/%s/commits/%s'
# doc: https://developer.atlassian.com/cloud/bitbucket/rest/api-group-refs/#api-repositories-workspace-repo-slug-refs-tags-get
BITBUCKET_MAX_TAG = 'https://bitbucket.org/api/2.0/repositories/%s/refs/tags?sort=-target.date'

async def get_version(name, conf, *, cache, **kwargs):
  repo = conf['bitbucket']
  br = conf.get('branch', '')
  use_max_tag = conf.get('use_max_tag', False)

  if use_max_tag:
    url = BITBUCKET_MAX_TAG % repo
    max_page = conf.get('max_page', 3)
    data = await _get_tags(url, max_page=max_page, cache=cache)

  else:
    url = BITBUCKET_URL % (repo, br)
    data = await cache.get_json(url)

  if use_max_tag:
    version = data
  else:
    version = data['values'][0]['date'].split('T', 1)[0].replace('-', '')
  return version

async def _get_tags(url, *, max_page, cache):
  ret = []

  for _ in range(max_page):
    data = await cache.get_json(url)
    ret.extend(x['name'] for x in data['values'])
    if 'next' in data:
      url = data['next']
    else:
      break

  return ret

