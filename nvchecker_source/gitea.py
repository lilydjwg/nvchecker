# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import urllib.parse

GITEA_URL = 'https://%s/api/v1/repos/%s/commits'
GITEA_MAX_TAG = 'https://%s/api/v1/repos/%s/tags'
GITEA_LATEST_RELEASE = 'https://%s/api/v1/repos/%s/releases'

from nvchecker.api import (
  VersionResult, RichResult, Entry,
  AsyncCache, KeyManager, GetVersionError
)

async def get_version(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
) -> VersionResult:
  repo = urllib.parse.quote(conf['gitea'])
  br = conf.get('branch')
  host = conf.get('host', 'gitea.com')
  use_max_tag = conf.get('use_max_tag', False)
  use_latest_release = conf.get('use_latest_release', False)
  if use_max_tag and use_latest_release:
      raise GetVersionError('You cannot specify both use_max_tag and use_latest_release')

  if use_max_tag:
    url = GITEA_MAX_TAG % (host, repo)
  elif use_latest_release:
    url = GITEA_LATEST_RELEASE % (host, repo)
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
        revision = tag['id'],
        url = f'https://{host}/{conf["gitea"]}/releases/tag/{tag["name"]}',
      ) for tag in data
    ]
  elif use_latest_release:
    return RichResult(
      version = data[0]['name'],
      gitref = f"refs/tags/{data[0]['tag_name']}",
      url = data[0]['html_url'],
    )
  else:
    return RichResult(
      version = data[0]['commit']['committer']['date'],
      revision = data[0]['sha'],
      url = data[0]['html_url'],
    )
