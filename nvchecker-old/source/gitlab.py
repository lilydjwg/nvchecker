# MIT licensed
# Copyright (c) 2013-2018 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import urllib.parse

import structlog

from . import session, HTTPError

logger = structlog.get_logger(logger_name=__name__)

GITLAB_URL = 'https://%s/api/v4/projects/%s/repository/commits?ref_name=%s'
GITLAB_MAX_TAG = 'https://%s/api/v4/projects/%s/repository/tags'

async def get_version(name, conf, **kwargs):
  try:
    return await get_version_real(name, conf, **kwargs)
  except HTTPError as e:
    check_ratelimit(e, name)

async def get_version_real(name, conf, **kwargs):
  repo = urllib.parse.quote_plus(conf.get('gitlab'))
  br = conf.get('branch', 'master')
  host = conf.get('host', "gitlab.com")
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()

  if use_max_tag:
    url = GITLAB_MAX_TAG % (host, repo)
  else:
    url = GITLAB_URL % (host, repo, br)

  # Load token from config
  token = conf.get('token')
  # Load token from environ
  if token is None:
    env_name = "NVCHECKER_GITLAB_TOKEN_" + host.upper().replace(".", "_").replace("/", "_")
    token = os.environ.get(env_name)
  # Load token from keyman
  if token is None and 'keyman' in kwargs:
    key_name = 'gitlab_' + host.lower().replace('.', '_').replace("/", "_")
    token = kwargs['keyman'].get_key(key_name)

  # Set private token if token exists.
  headers = {}
  if token:
    headers["PRIVATE-TOKEN"] = token

  async with session.get(url, headers=headers) as res:
    data = await res.json()
  if use_max_tag:
    version = [tag["name"] for tag in data if tag["name"] not in ignored_tags]
  else:
    version = data[0]['created_at'].split('T', 1)[0].replace('-', '')
  return version

def check_ratelimit(exc, name):
  res = exc.response
  if not res:
    raise

  # default -1 is used to re-raise the exception
  n = int(res.headers.get('RateLimit-Remaining', -1))
  if n == 0:
    logger.error('rate limited, resetting at (unknown). '
                 'Or get an API token to increase the allowance if not yet',
                 name = name)
  else:
    raise
