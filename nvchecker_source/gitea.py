# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import urllib.parse

GITEA_URL = 'https://%s/api/v1/repos/%s/commits?sha=%s'
GITEA_MAX_TAG = 'https://%s/api/v1/repos/%s/tags'

from nvchecker.api import (
  VersionResult, Entry, AsyncCache, KeyManager,
)

async def get_version(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
) -> VersionResult:
  repo = urllib.parse.quote(conf['gitea'])
  br = conf.get('branch', 'master')
  host = conf.get('host', 'gitea.com')
  use_max_tag = conf.get('use_max_tag', False)

  if use_max_tag:
    url = GITEA_MAX_TAG % (host, repo)
  else:
    url = GITEA_URL % (host, repo, br)

  # Load token from config
  token = conf.get('token')
  # Load token from keyman
  if token is None:
    key_name = 'gitea_' + host.lower()
    token = keymanager.get_key(key_name)

  # Set private token if token exists.
  headers = {}
  if token:
    headers["Authorization"] = f'token {token}'

  data = await cache.get_json(url, headers = headers)
  if use_max_tag:
    version = [tag["name"] for tag in data]
  else:
    version = data[0]['commit']['committer']['date'].split('T', 1)[0].replace('-', '')
  return version
