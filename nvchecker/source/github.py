# MIT licensed
# Copyright (c) 2013-2018 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import re
import time
from urllib.parse import urlencode
from functools import partial

import structlog

from . import session, HTTPError

logger = structlog.get_logger(logger_name=__name__)

GITHUB_URL = 'https://api.github.com/repos/%s/commits'
GITHUB_LATEST_RELEASE = 'https://api.github.com/repos/%s/releases/latest'
# https://developer.github.com/v3/git/refs/#get-all-references
GITHUB_MAX_TAG = 'https://api.github.com/repos/%s/git/refs/tags'
GITHUB_GRAPHQL_URL = 'https://api.github.com/graphql'

async def get_version(name, conf, **kwargs):
  try:
    return await get_version_real(name, conf, **kwargs)
  except HTTPError as e:
    check_ratelimit(e, name)

QUERY_LATEST_TAG = '''
{{
  repository(name: "{name}", owner: "{owner}") {{
    refs(refPrefix: "refs/tags/", first: 1,
         query: "{query}",
         orderBy: {{field: TAG_COMMIT_DATE, direction: DESC}}) {{
      edges {{
        node {{
          name
        }}
      }}
    }}
  }}
}}
'''

async def get_latest_tag(name, conf, token):
  repo = conf.get('github')
  query = conf.get('query', '')
  owner, reponame = repo.split('/')
  headers = {
    'Authorization': 'bearer %s' % token,
    'Content-Type': 'application/json',
  }
  q = QUERY_LATEST_TAG.format(
    owner = owner,
    name = reponame,
    query = query,
  )
  async with session.post(
    GITHUB_GRAPHQL_URL,
    headers = headers,
    json = {'query': q},
  ) as res:
    j = await res.json()

  refs = j['data']['repository']['refs']['edges']
  if not refs:
    logger.error('no tag found', name=name)
    return

  return refs[0]['node']['name']

def get_token(kwargs):
  token = os.environ.get('NVCHECKER_GITHUB_TOKEN')
  if token:
    return token

  token = kwargs['keyman'].get_key('github')
  return token

async def get_version_real(name, conf, **kwargs):
  token = get_token(kwargs)

  use_latest_tag = conf.getboolean('use_latest_tag', False)
  if use_latest_tag:
    if not token:
      logger.error('token not given but it is required',
                   name = name)
      return
    return await get_latest_tag(name, conf, token)

  repo = conf.get('github')
  br = conf.get('branch')
  path = conf.get('path')
  use_latest_release = conf.getboolean('use_latest_release', False)
  use_max_tag = conf.getboolean('use_max_tag', False)
  include_tags_pattern = conf.get("include_tags_pattern", "")
  ignored_tags = conf.get("ignored_tags", "").split()
  if use_latest_release:
    url = GITHUB_LATEST_RELEASE % repo
  elif use_max_tag:
    url = GITHUB_MAX_TAG % repo
  else:
    url = GITHUB_URL % repo
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
    headers['Authorization'] = 'token %s' % token

  kwargs = {}
  if conf.get('proxy'):
    kwargs["proxy"] = conf.get("proxy")

  if use_max_tag:
    return await max_tag(partial(
      session.get, headers=headers, **kwargs),
      url, name, ignored_tags, include_tags_pattern,
      max_page = conf.getint("max_page", 1),
    )

  async with session.get(url, headers=headers, **kwargs) as res:
    logger.debug('X-RateLimit-Remaining',
                  n=res.headers.get('X-RateLimit-Remaining'))
    data = await res.json()

  if use_latest_release:
    if 'tag_name' not in data:
      logger.error('No tag found in upstream repository.',
                   name=name)
      return
    version = data['tag_name']

  else:
    # YYYYMMDD.HHMMSS
    version = data[0]['commit']['committer']['date'] \
        .rstrip('Z').replace('-', '').replace(':', '').replace('T', '.')

  return version

async def max_tag(
  getter, url, name, ignored_tags, include_tags_pattern, max_page,
):
  # paging is needed
  tags = []

  for _ in range(max_page):
    async with getter(url) as res:
      logger.debug('X-RateLimit-Remaining',
                    n=res.headers.get('X-RateLimit-Remaining'))
      links = res.headers.get('Link')
      j = await res.json()

    data = []

    for ref in j:
      tag = ref['ref'].split('/', 2)[-1]
      if tag in ignored_tags:
        continue
      data.append(tag)

    if include_tags_pattern:
      data = [x for x in data
              if re.search(include_tags_pattern, x)]
    if data:
      tags += data

    next_page_url = get_next_page_url(links)
    if not next_page_url:
      break
    else:
      url = next_page_url

  if not tags:
    logger.error('No tag found in upstream repository.',
                  name=name,
                  include_tags_pattern=include_tags_pattern)
  return tags

def get_next_page_url(links):
  if not links:
    return

  links = links.split(', ')
  next_link = [x for x in links if x.endswith('rel="next"')]
  if not next_link:
    return

  return next_link[0].split('>', 1)[0][1:]

def check_ratelimit(exc, name):
  res = exc.response
  if not res:
    raise

  # default -1 is used to re-raise the exception
  n = int(res.headers.get('X-RateLimit-Remaining', -1))
  if n == 0:
    reset = int(res.headers.get('X-RateLimit-Reset'))
    logger.error('rate limited, resetting at %s. '
                 'Or get an API token to increase the allowance if not yet'
                 % time.ctime(reset),
                 name = name,
                 reset = reset)
  else:
    raise
