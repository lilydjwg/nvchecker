# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import urllib.parse

import structlog

from nvchecker.api import (
  VersionResult, RichResult, Entry,
  AsyncCache, KeyManager, TemporaryError,
)

GITLAB_URL = 'https://%s/api/v4/projects/%s/repository/commits'
GITLAB_MAX_TAG = 'https://%s/api/v4/projects/%s/repository/tags'

async def get_version(name, conf, **kwargs):
  try:
    return await get_version_real(name, conf, **kwargs)
  except TemporaryError as e:
    check_ratelimit(e, name)

async def get_version_real(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
  **kwargs,
) -> VersionResult:
  repo = urllib.parse.quote_plus(conf['gitlab'])
  br = conf.get('branch')
  host = conf.get('host', "gitlab.com")
  use_max_tag = conf.get('use_max_tag', False)

  if use_max_tag:
    url = GITLAB_MAX_TAG % (host, repo)
  else:
    url = GITLAB_URL % (host, repo)
    if br:
      url += '?ref_name=%s' % br

  # Load token from config
  token = conf.get('token')
  # Load token from keyman
  if token is None:
    token = keymanager.get_key(host.lower(), 'gitlab_' + host.lower())

  # Set private token if token exists.
  headers = {}
  if token:
    headers["PRIVATE-TOKEN"] = token

  data = await cache.get_json(url, headers = headers)
  if use_max_tag:
    return [
      RichResult(
        version = tag['name'],
        revision = tag['commit']['id'],
        url = f'https://{host}/{conf["gitlab"]}/-/tags/{tag["name"]}',
      ) for tag in data
    ]
  else:
    return RichResult(
      version = data[0]['created_at'].split('T', 1)[0].replace('-', ''),
      revision = data[0]['id'],
      url = data[0]['web_url'],
    )

def check_ratelimit(exc, name):
  res = exc.response
  if not res:
    raise

  logger = structlog.get_logger(logger_name=__name__, name=name)
  # default -1 is used to re-raise the exception
  n = int(res.headers.get('RateLimit-Remaining', -1))
  if n == 0:
    logger.error('gitlab rate limited. Wait some time '
                 'or get an API token to increase the allowance if not yet')
  else:
    raise
