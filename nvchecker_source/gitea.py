# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import urllib.parse

GITEA_URL = 'https://%s/api/v1/repos/%s/commits'
GITEA_MAX_TAG = 'https://%s/api/v1/repos/%s/tags'

from nvchecker.api import (
  VersionResult, RichResult, Entry,
  AsyncCache, KeyManager,
)

async def get_version(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
) -> VersionResult:
  repo = urllib.parse.quote(conf['gitea'])
  br = conf.get('branch')
  host = conf.get('host', 'gitea.com')
  use_max_tag = conf.get('use_max_tag', False)

  if use_max_tag:
    url = GITEA_MAX_TAG % (host, repo)
  else:
    url = GITEA_URL % (host, repo)
    if br:
      url += '?sha=' + br

  # Load token from config
  token = conf.get('token')
  # Load token from keyman
  if token is None:
    token = keymanager.get_key(host.lower(), 'gitea_' + host.lower())

  # Set private token if token exists.
  headers = {}
  if token:
    headers["Authorization"] = f'token {token}'

  data = await cache.get_json(url, headers = headers)
  if use_max_tag:
    return [
      RichResult(
        version = tag['name'],
        url = f'https://{host}/{conf["gitea"]}/releases/tag/{tag["name"]}',
      ) for tag in data
    ]
  else:
    return RichResult(
      version = data[0]['commit']['committer']['date'].split('T', 1)[0].replace('-', ''),
      url = data[0]['html_url'],
    )
