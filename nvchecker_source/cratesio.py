# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import re

import structlog

from nvchecker.api import RichResult

API_URL = 'https://crates.io/api/v1/crates/%s'
# https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
VERSION_PATTERN = r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'


async def get_version(name, conf, *, cache, **kwargs):
  logger = structlog.get_logger(logger_name=__name__, name=name)
  name = conf.get('cratesio') or name
  use_pre_release = conf.get('use_pre_release', False)
  data = await cache.get_json(API_URL % name)
  results = []
  for v in data['versions']:
    if v['yanked']:
      continue
    version = v['num']
    match = re.fullmatch(VERSION_PATTERN, version)
    if match is None:
      logger.warning('ignoring invalid version', version=version)
      continue
    if not use_pre_release and match.group('prerelease'):
      continue
    results.append(
      RichResult(
        version=version,
        url=f'https://crates.io/crates/{name}/{version}',
      )
    )

  return results
