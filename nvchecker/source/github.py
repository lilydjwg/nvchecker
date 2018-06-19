# MIT licensed
# Copyright (c) 2013-2018 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import re
import time
from functools import partial

import structlog

from . import session, HTTPError
from ..sortversion import sort_version_keys

logger = structlog.get_logger(logger_name=__name__)

GITHUB_URL = 'https://api.github.com/repos/%s/commits'
GITHUB_LATEST_RELEASE = 'https://api.github.com/repos/%s/releases/latest'
GITHUB_MAX_TAG = 'https://api.github.com/repos/%s/tags'

async def get_version(name, conf, **kwargs):
  try:
    return await get_version_real(name, conf, **kwargs)
  except HTTPError as e:
    check_ratelimit(e, name)

async def get_version_real(name, conf, **kwargs):
  repo = conf.get('github')
  br = conf.get('branch')
  use_latest_release = conf.getboolean('use_latest_release', False)
  use_max_tag = conf.getboolean('use_max_tag', False)
  include_tags_pattern = conf.get("include_tags_pattern", "")
  ignored_tags = conf.get("ignored_tags", "").split()
  sort_version_key = sort_version_keys[conf.get("sort_version_key", "parse_version")]
  if use_latest_release:
    url = GITHUB_LATEST_RELEASE % repo
  elif use_max_tag:
    url = GITHUB_MAX_TAG % repo
  else:
    url = GITHUB_URL % repo
    if br:
      url += '?sha=' + br
  headers = {
    'Accept': 'application/vnd.github.quicksilver-preview+json',
    'User-Agent': 'lilydjwg/nvchecker',
  }
  if 'NVCHECKER_GITHUB_TOKEN' in os.environ:
    headers['Authorization'] = 'token %s' % os.environ['NVCHECKER_GITHUB_TOKEN']
  else:
    key = kwargs['keyman'].get_key('github')
    if key:
      headers['Authorization'] = 'token %s' % key

  kwargs = {}
  if conf.get('proxy'):
    kwargs["proxy"] = conf.get("proxy")

  if use_max_tag:
    return await max_tag(partial(
      session.get, headers=headers, **kwargs),
      url, name, ignored_tags, include_tags_pattern,
      sort_version_key,
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
  getter, url, name,
  ignored_tags, include_tags_pattern, sort_version_key,
):
  # paging is needed

  while True:
    async with getter(url) as res:
      logger.debug('X-RateLimit-Remaining',
                    n=res.headers.get('X-RateLimit-Remaining'))
      links = res.headers.get('Link')
      data = await res.json()

    data = [tag["name"] for tag in data if tag["name"] not in ignored_tags]
    if include_tags_pattern:
      data = [x for x in data
              if re.search(include_tags_pattern, x)]
    if data:
      data.sort(key=sort_version_key)
      return data[-1]
    else:
      next_page_url = get_next_page_url(links)
      if not next_page_url:
        break
      else:
        url = next_page_url

  logger.error('No tag found in upstream repository.',
                name=name,
                include_tags_pattern=include_tags_pattern)
  return

def get_next_page_url(links):
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
