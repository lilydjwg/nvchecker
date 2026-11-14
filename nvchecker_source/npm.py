# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import json
import re
from nvchecker.api import session, RichResult

NPM_URL = 'https://registry.npmjs.org/%s'

def configure(config):
  global NPM_URL
  url = config.get('registry')
  if url:
    NPM_URL = f'{url.rstrip("/")}/%s'

_PARTIAL_RANGE = "bytes=0-1023"

async def get_first_1k(url):
  headers = {
    "Accept": "application/vnd.npm.install-v1+json",
    "Range": _PARTIAL_RANGE,
  }
  res = await session.get(url, headers=headers)
  return res.body

async def get_full(url):
  headers = {
    "Accept": "application/vnd.npm.install-v1+json",
  }
  res = await session.get(url, headers=headers)
  return res.body

def parse_dist_tags(data):
  match = re.search(b'"dist-tags":({.*?})', data)
  if match is None:
    return None
  try:
    return json.loads(match.group(1))
  except ValueError:
    return None

async def get_metadata(url):
  data = await get_first_1k(url)
  if parse_dist_tags(data) is None:
    # The ranged fetch can truncate a large "dist-tags" block mid-JSON.
    data = await get_full(url)
  return data

async def get_version(name, conf, *, cache, **kwargs):
  key = conf.get('npm', name)
  data = await cache.get(NPM_URL % key, get_metadata)

  dist_tags = parse_dist_tags(data)
  if dist_tags is None:
    raise ValueError(f'npm: no parsable "dist-tags" for {key}')
  version = dist_tags['latest']

  # There is no standardised URL scheme, so we only return an URL for the default registry
  if NPM_URL.startswith('https://registry.npmjs.org/'):
    return RichResult(
      version = version,
      url = f'https://www.npmjs.com/package/{key}/v/{version}',
    )
  else:
    return version
