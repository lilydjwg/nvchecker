# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import itertools
import time
from urllib.parse import urlencode
from typing import Any, Dict, Optional, Tuple

import structlog

from nvchecker.api import (
  VersionResult, Entry, AsyncCache, KeyManager,
  TemporaryError, session, GetVersionError,
)

logger = structlog.get_logger(logger_name=__name__)

def add_commit_name(version: str, commit_name: Optional[str]) -> str:
  return version if commit_name is None else version + '+' + commit_name

GITHUB_URL = 'https://api.github.com/repos/%s/commits'
GITHUB_LATEST_RELEASE = 'https://api.github.com/repos/%s/releases/latest'
# https://developer.github.com/v3/git/refs/#get-all-references
GITHUB_MAX_TAG = 'https://api.github.com/repos/%s/git/refs/tags'
GITHUB_GRAPHQL_URL = 'https://api.github.com/graphql'

async def get_version(name, conf, **kwargs):
  try:
    return await get_version_real(name, conf, **kwargs)
  except TemporaryError as e:
    check_ratelimit(e, name)

async def query_graphql(
  *,
  cache: AsyncCache,
  token: Optional[str] = None,
  headers: Optional[Dict[str, str]] = None,
  query: str,
  variables: Optional[Dict[str, object]] = None,
  json: Optional[Dict[str, object]] = None,
  url: Optional[str] = None,
  **kwargs,
) -> Any:
  if not token:
    raise GetVersionError('token not given but it is required')
  if headers is None:
    headers = {}
  headers.setdefault('Authorization', f'bearer {token}')
  headers.setdefault('Content-Type', 'application/json')

  if json is None:
    json = {}
  json['query'] = query
  if variables is not None:
    json.setdefault('variables', {}).update(variables)

  if url is None:
    url = GITHUB_GRAPHQL_URL
  return await cache.get_json(url = url, headers = headers, json = json)

async def query_rest(
  *,
  cache: AsyncCache,
  token: Optional[str] = None,
  headers: Optional[Dict[str, str]] = None,
  parameters: Optional[Dict[str, str]] = None,
  url: str,
) -> Any:
  if headers is None:
    headers = {}
  if token:
    headers.setdefault('Authorization', f'token {token}')
  headers.setdefault('Accept', 'application/vnd.github.quicksilver-preview+json')

  if parameters:
    url += '?' + urlencode(parameters)

  return await cache.get_json(url = url, headers = headers)

QUERY_LATEST_TAG = '''
query latestTag(
  $owner: String!, $name: String!,
  $query: String, $includeCommitName: Boolean = false,
) {
  repository(owner: $owner, name: $name) {
    refs(
      refPrefix: "refs/tags/", query: $query,
      first: 1, orderBy: {field: TAG_COMMIT_DATE, direction: DESC},
    ) {
      edges {
        node {
          name
          ... @include(if: $includeCommitName) { target { oid } }
        }
      }
    }
  }
}
'''

async def get_version_real(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
  **kwargs,
) -> VersionResult:
  repo = conf['github']
  use_commit_name = conf.get('use_commit_name', False)

  # Load token from config
  token = conf.get('token')
  # Load token from keyman
  if token is None:
    token = keymanager.get_key('github')

  if conf.get('use_latest_tag', False):
    owner, reponame = repo.split('/')
    j = await query_graphql(
      cache = cache,
      token = token,
      query = QUERY_LATEST_TAG,
      variables = {
        'owner': owner,
        'name': reponame,
        'query': conf.get('query'),
        'includeCommitName': use_commit_name,
      },
    )
    refs = j['data']['repository']['refs']['edges']
    if not refs:
      raise GetVersionError('no tag found')
    ref = next(
      add_commit_name(
        ref['node']['name'],
        ref['node']['target']['oid'] if use_commit_name else None,
      )
      for ref in refs
    )
    return ref
  elif conf.get('use_latest_release', False):
    data = await query_rest(
      cache = cache,
      token = token,
      url = GITHUB_LATEST_RELEASE % repo,
    )
    if 'tag_name' not in data:
      raise GetVersionError('No release found in upstream repository.')
    tag = data['tag_name']
    return tag
  elif conf.get('use_max_tag', False):
    data = await query_rest(
      cache = cache,
      token = token,
      url = GITHUB_MAX_TAG % repo,
    )
    tags = [
      add_commit_name(
        ref['ref'].split('/', 2)[-1],
        ref['object']['sha'] if use_commit_name else None,
      )
      for ref in data
    ]
    if not tags:
      raise GetVersionError('No tag found in upstream repository.')
    return tags
  else:
    br = conf.get('branch')
    path = conf.get('path')
    parameters = {}
    if br is not None:
      parameters['sha'] = br
    if path is not None:
      parameters['path'] = path
    data = await query_rest(
      cache = cache,
      token = token,
      url = GITHUB_URL % repo,
      parameters = parameters,
    )
    # YYYYMMDD.HHMMSS
    version = add_commit_name(
      data[0]['commit']['committer']['date'] \
        .rstrip('Z').replace('-', '').replace(':', '').replace('T', '.'),
      data[0]['sha'] if use_commit_name else None,
    )
    return version

def check_ratelimit(exc, name):
  res = exc.response
  if not res:
    raise

  # default -1 is used to re-raise the exception
  n = int(res.headers.get('X-RateLimit-Remaining', -1))
  if n == 0:
    reset = int(res.headers.get('X-RateLimit-Reset'))
    logger.error(f'rate limited, resetting at {time.ctime(reset)}. '
                  'Or get an API token to increase the allowance if not yet',
                 name = name,
                 reset = reset)
  else:
    raise
