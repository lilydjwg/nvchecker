# MIT licensed
# Copyright (c) 2013-2020, 2024 lilydjwg <lilydjwg@gmail.com>, et al.

import time
from urllib.parse import urlencode
from typing import List, Tuple, Union, Optional
import asyncio

import structlog

from nvchecker.api import (
  VersionResult, Entry, AsyncCache, KeyManager,
  HTTPError, session, RichResult, GetVersionError,
)

ALLOW_REQUEST = None
RATE_LIMITED_ERROR = False

GITHUB_URL = 'https://api.%s/repos/%s/commits'
GITHUB_LATEST_RELEASE = 'https://api.%s/repos/%s/releases/latest'
# https://developer.github.com/v3/git/refs/#get-all-references
GITHUB_MAX_TAG = 'https://api.%s/repos/%s/git/refs/tags'
GITHUB_MAX_RELEASE = 'https://api.%s/repos/%s/releases'
GITHUB_GRAPHQL_URL = 'https://api.%s/graphql'

async def get_version(name, conf, **kwargs):
  global RATE_LIMITED_ERROR, ALLOW_REQUEST

  if RATE_LIMITED_ERROR:
    raise RuntimeError('rate limited')

  if ALLOW_REQUEST is None:
    ALLOW_REQUEST = asyncio.Event()
    ALLOW_REQUEST.set()

  for _ in range(2): # retry once
    try:
      await ALLOW_REQUEST.wait()
      return await get_version_real(name, conf, **kwargs)
    except HTTPError as e:
      if e.code in [403, 429]:
        if n := check_ratelimit(e, name):
          ALLOW_REQUEST.clear()
          await asyncio.sleep(n+1)
          ALLOW_REQUEST.set()
          continue
        RATE_LIMITED_ERROR = True
      raise

QUERY_LATEST_TAG = '''
{{
  repository(name: "{name}", owner: "{owner}") {{
    refs(refPrefix: "refs/tags/", first: 1,
         query: "{query}",
         orderBy: {{field: TAG_COMMIT_DATE, direction: DESC}}) {{
      edges {{
        node {{
          name
          target {{
            oid
          }}
        }}
      }}
    }}
  }}
}}
'''

QUERY_LATEST_RELEASE_WITH_PRERELEASES = '''
{{
  repository(name: "{name}", owner: "{owner}") {{
    releases(first: 1, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
      edges {{
        node {{
          name
          url
          tag {{
            name
          }}
          tagCommit {{
            oid
          }}
        }}
      }}
    }}
  }}
}}
'''

async def get_latest_tag(key: Tuple[str, str, str, str]) -> RichResult:
  host, repo, query, token = key
  owner, reponame = repo.split('/')
  headers = {
    'Authorization': f'bearer {token}',
    'Content-Type': 'application/json',
  }
  q = QUERY_LATEST_TAG.format(
    owner = owner,
    name = reponame,
    query = query,
  )

  res = await session.post(
    GITHUB_GRAPHQL_URL % host,
    headers = headers,
    json = {'query': q},
  )
  j = res.json()

  refs = j['data']['repository']['refs']['edges']
  if not refs:
    raise GetVersionError('no tag found')

  version = refs[0]['node']['name']
  revision = refs[0]['node']['target']['oid']
  return RichResult(
    version = version,
    gitref = f"refs/tags/{version}",
    revision = revision,
    url = f'https://github.com/{repo}/releases/tag/{version}',
  )

async def get_latest_release_with_prereleases(key: Tuple[str, str, str, str]) -> RichResult:
  host, repo, token, use_release_name = key
  owner, reponame = repo.split('/')
  headers = {
    'Authorization': f'bearer {token}',
    'Content-Type': 'application/json',
  }
  q = QUERY_LATEST_RELEASE_WITH_PRERELEASES.format(
    owner = owner,
    name = reponame,
  )

  res = await session.post(
    GITHUB_GRAPHQL_URL % host,
    headers = headers,
    json = {'query': q},
  )
  j = res.json()

  refs = j['data']['repository']['releases']['edges']
  if not refs:
    raise GetVersionError('no release found')

  tag_name = refs[0]['node']['tag']['name']
  if use_release_name:
    version = refs[0]['node']['name']
  else:
    version = tag_name

  return RichResult(
    version = version,
    gitref = f"refs/tags/{tag_name}",
    revision = refs[0]['node']['tagCommit']['oid'],
    url = refs[0]['node']['url'],
  )

async def get_version_real(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
  **kwargs,
) -> VersionResult:
  repo = conf['github']
  host = conf.get('host', "github.com")

  # Load token from config
  token = conf.get('token')
  # Load token from keyman
  if token is None:
    token = keymanager.get_key(host.lower(), 'github')

  use_latest_tag = conf.get('use_latest_tag', False)
  if use_latest_tag:
    if not token:
      raise GetVersionError('token not given but it is required')

    query = conf.get('query', '')
    return await cache.get((host, repo, query, token), get_latest_tag) # type: ignore

  use_latest_release = conf.get('use_latest_release', False)
  include_prereleases = conf.get('include_prereleases', False)
  use_release_name = conf.get('use_release_name', False)
  if use_latest_release and include_prereleases:
    if not token:
      raise GetVersionError('token not given but it is required')

    return await cache.get(
      (host, repo, token, use_release_name),
      get_latest_release_with_prereleases) # type: ignore

  br = conf.get('branch')
  path = conf.get('path')
  use_max_tag = conf.get('use_max_tag', False)
  use_max_release = conf.get('use_max_release', False)
  if use_latest_release:
    url = GITHUB_LATEST_RELEASE % (host, repo)
  elif use_max_tag:
    url = GITHUB_MAX_TAG % (host, repo)
  elif use_max_release:
    url = GITHUB_MAX_RELEASE % (host, repo)
  else:
    url = GITHUB_URL % (host, repo)
    parameters = {}
    if br:
      parameters['sha'] = br
    if path:
      parameters['path'] = path
    url += '?' + urlencode(parameters)
  headers = {
    'Accept': 'application/vnd.github.quicksilver-preview+json',
  }
  if token:
    headers['Authorization'] = f'token {token}'

  data = await cache.get_json(url, headers = headers)

  if use_max_tag:
    tags: List[Union[str, RichResult]] = [
      RichResult(
        version = ref['ref'].split('/', 2)[-1],
        gitref = ref['ref'],
        revision = ref['object']['sha'],
        url = f'https://github.com/{repo}/releases/tag/{ref["ref"].split("/", 2)[-1]}',
      ) for ref in data
    ]
    if not tags:
      raise GetVersionError('No tag found in upstream repository.')
    return tags

  if use_max_release:
    releases: List[Union[str, RichResult]] = [
      RichResult(
        version = ref['name'] if use_release_name else ref['tag_name'],
        gitref = f"refs/tags/{ref['tag_name']}",
        url = ref['html_url'],
      ) for ref in data if include_prereleases or not ref['prerelease']
    ]
    if not releases:
      raise GetVersionError('No release found in upstream repository.')
    return releases

  if use_latest_release:
    if 'tag_name' not in data:
      raise GetVersionError('No release found in upstream repository.')

    if use_release_name:
      version = data['name']
    else:
      version = data['tag_name']

    return RichResult(
      version = version,
      gitref = f"refs/tags/{data['tag_name']}",
      url = data['html_url'],
    )

  else:
    return RichResult(
      # YYYYMMDD.HHMMSS
      version = data[0]['commit']['committer']['date'].rstrip('Z').replace('-', '').replace(':', '').replace('T', '.'),
      revision = data[0]['sha'],
      url = data[0]['html_url'],
    )

def check_ratelimit(exc: HTTPError, name: str) -> Optional[int]:
  res = exc.response
  if not res:
    raise exc

  logger = structlog.get_logger(logger_name=__name__, name=name)
  if v := res.headers.get('retry-after'):
    n = int(v)
    logger.warning('retry-after', n=n)
    return n

  # default -1 is used to re-raise the exception
  n = int(res.headers.get('X-RateLimit-Remaining', -1))
  if n == 0:
    reset = int(res.headers.get('X-RateLimit-Reset'))
    logger.error(f'rate limited, resetting at {time.ctime(reset)}. '
                  'Or get an API token to increase the allowance if not yet',
                 reset = reset)
    return None

  raise exc
