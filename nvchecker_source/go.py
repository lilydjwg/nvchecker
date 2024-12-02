# MIT licensed
# Copyright (c) 2024 bgme <i@bgme.me>.

from lxml import html

from nvchecker.api import (
  RichResult, Entry, AsyncCache, KeyManager,
  session, GetVersionError,
)

GO_PKG_URL = 'https://pkg.go.dev/{pkg}?tab=versions'
GO_PKG_VERSION_URL = 'https://pkg.go.dev/{pkg}@{version}'


async def get_version(
    name: str, conf: Entry, *,
    cache: AsyncCache, keymanager: KeyManager,
    **kwargs,
) -> RichResult:
  key = tuple(sorted(conf.items()))
  return await cache.get(key, get_version_impl)


async def get_version_impl(info) -> RichResult:
  conf = dict(info)
  pkg_name = conf.get('go')

  url = GO_PKG_URL.format(pkg=pkg_name)
  res = await session.get(url)
  doc = html.fromstring(res.body.decode())

  elements = doc.xpath("//div[@class='Version-tag']/a/text()")
  try:
    version = elements[0] # type: ignore
    return RichResult(
      version = version, # type: ignore
      url = GO_PKG_VERSION_URL.format(pkg=pkg_name, version=version),
    )
  except IndexError:
    raise GetVersionError("parse error", pkg_name=pkg_name)
