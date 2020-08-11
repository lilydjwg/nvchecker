# MIT licensed
# Copyright (c) 2013-2018 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import urllib.parse

import structlog

from . import session, HTTPError

logger = structlog.get_logger(logger_name=__name__)

GITEA_URL = 'https://%s/api/v1/repos/%s/commits?sha=%s'
GITEA_MAX_TAG = 'https://%s/api/v1/repos/%s/tags'

async def get_version(name, conf, **kwargs):
  try:
    return await get_version_real(name, conf, **kwargs)
  except HTTPError as e:
    raise

async def get_version_real(name, conf, **kwargs):
  repo = urllib.parse.quote(conf.get('gitea'))
  br = conf.get('branch', 'master')
  host = conf.get('host', "gitea.com")
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()

  if use_max_tag:
    url = GITEA_MAX_TAG % (host, repo)
  else:
    url = GITEA_URL % (host, repo, br)

  # Load token from config
  token = conf.get('token')
  # Load token from environ
  if token is None:
    env_name = "NVCHECKER_GITEA_TOKEN_" + host.upper().replace(".", "_").replace("/", "_")
    token = os.environ.get(env_name)
  # Load token from keyman
  if token is None and 'keyman' in kwargs:
    key_name = 'gitea_' + host.lower().replace('.', '_').replace("/", "_")
    token = kwargs['keyman'].get_key(key_name)

  # Set private token if token exists.
  headers = {}
  if token:
    headers["Authorization"] = "token %s" % token

  async with session.get(url, headers=headers) as res:
    data = await res.json()
  if use_max_tag:
    version = [tag["name"] for tag in data if tag["name"] not in ignored_tags]
  else:
    version = data[0]['commit']['committer']['date'].split('T', 1)[0].replace('-', '')
  return version
