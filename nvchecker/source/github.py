# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os

from . import session
from ..sortversion import sort_version_keys

GITHUB_URL = 'https://api.github.com/repos/%s/commits?sha=%s'
GITHUB_LATEST_RELEASE = 'https://api.github.com/repos/%s/releases/latest'
GITHUB_MAX_TAG = 'https://api.github.com/repos/%s/tags'

async def get_version(name, conf):
  repo = conf.get('github')
  br = conf.get('branch', 'master')
  use_latest_release = conf.getboolean('use_latest_release', False)
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()
  sort_version_key = sort_version_keys[conf.get("sort_version_key", "parse_version")]
  if use_latest_release:
    url = GITHUB_LATEST_RELEASE % repo
  elif use_max_tag:
    url = GITHUB_MAX_TAG % repo
  else:
    url = GITHUB_URL % (repo, br)
  headers = {'Accept': "application/vnd.github.quicksilver-preview+json"}
  if 'NVCHECKER_GITHUB_TOKEN' in os.environ:
    headers['Authorization'] = 'token %s' % os.environ['NVCHECKER_GITHUB_TOKEN']

  kwargs = {}
  if conf.get('proxy'):
    kwargs["proxy"] = conf.get("proxy")
  async with session.get(url, headers=headers, **kwargs) as res:
    data = await res.json()
  if use_latest_release:
    version = data['tag_name']
  elif use_max_tag:
    data = [tag["name"] for tag in data if tag["name"] not in ignored_tags]
    data.sort(key=sort_version_key)
    version = data[-1]
  else:
    # YYYYMMDD.HHMMSS
    version = data[0]['commit']['committer']['date'] \
        .rstrip('Z').replace('-', '').replace(':', '').replace('T', '.')
  return version
