# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

from nvchecker.api import (
  VersionResult, RichResult, Entry, AsyncCache, KeyManager,
)

PAGURE_URL = 'https://%s/api/0/%s/git/tags?with_commits=true'

async def get_version(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
  **kwargs,
) -> VersionResult:
  repo = conf['pagure']
  host = conf.get('host', "pagure.io")

  url = PAGURE_URL % (host, repo)

  data = await cache.get_json(url)
  return [
    RichResult(
      version = version,
      url = f'https://{host}/{repo}/tree/{version_hash}',
    ) for version, version_hash in data["tags"].items()
  ]
