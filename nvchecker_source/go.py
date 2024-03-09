# MIT licensed
# Copyright (c) 2024 bgme <i@bgme.me>.

from lxml import html

from nvchecker.api import (
  VersionResult, Entry, AsyncCache, KeyManager,
  session, GetVersionError,
)

GO_PKG_URL = 'https://pkg.go.dev/{pkg}?tab=versions'


async def get_version(
    name: str, conf: Entry, *,
    cache: AsyncCache, keymanager: KeyManager,
    **kwargs,
) -> VersionResult:
  key = tuple(sorted(conf.items()))
  return await cache.get(key, get_version_impl)


async def get_version_impl(info) -> VersionResult:
  conf = dict(info)
  pkg_name = conf.get('go')

  url = GO_PKG_URL.format(pkg=pkg_name)
  res = await session.get(url)
  doc = html.fromstring(res.body.decode())

  elements = doc.xpath("//div[@class='Version-tag']/a/text()")
  try:
    version = elements[0]
    return version
  except IndexError:
    raise GetVersionError("parse error", pkg_name=pkg_name)
