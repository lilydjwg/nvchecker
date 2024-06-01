# MIT licensed
# Copyright (c) 2013-2021,2023-2024 lilydjwg <lilydjwg@gmail.com>, et al.

import structlog
from packaging.version import Version, InvalidVersion

from nvchecker.api import RichResult

logger = structlog.get_logger(logger_name=__name__)

async def get_version(name, conf, *, cache, **kwargs):
  ret = []

  package = conf.get('pypi') or name
  use_pre_release = conf.get('use_pre_release', False)

  url = 'https://pypi.org/pypi/{}/json'.format(package)

  data = await cache.get_json(url)

  for version in data['releases'].keys():
    try:
      parsed_version = Version(version)
    except InvalidVersion:
      if data['releases'][version]:
        # emit a warning if there is something under the invalid version
        # sympy has an empty "0.5.13-hg" version
        logger.warning('ignoring invalid version', version=version)
      continue

    if not use_pre_release and parsed_version.is_prerelease:
      continue

    ret.append(RichResult(
      version = version,
      url = f'https://pypi.org/project/{package}/{version}/',
    ))

  return ret
