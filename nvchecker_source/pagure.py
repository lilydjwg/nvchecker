# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

import urllib.parse

import structlog

from nvchecker.api import (
  VersionResult, Entry, AsyncCache, KeyManager,
)

PAGURE_URL = 'https://%s/api/0/%s/git/tags'

logger = structlog.get_logger(logger_name=__name__)

async def get_version(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
  **kwargs,
) -> VersionResult:
  repo = conf['pagure']
  host = conf.get('host', "pagure.io")

  url = PAGURE_URL % (host, repo)

  data = await cache.get_json(url)
  version = data["tags"]
  return version
