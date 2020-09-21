# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

from __future__ import annotations

import asyncio
from io import StringIO
from typing import Dict, Tuple

from nvchecker.api import (
  session, GetVersionError,
  VersionResult, Entry, AsyncCache, KeyManager,
)

APT_RELEASE_URL = "%s/dists/%s/Release"
APT_PACKAGES_PATH = "%s/binary-%s/Packages%s"
APT_PACKAGES_URL = "%s/dists/%s/%s"
APT_PACKAGES_SUFFIX_PREFER = (".xz", ".gz", "")

def _decompress_data(url: str, data: bytes) -> str:
  if url.endswith(".xz"):
    import lzma
    data = lzma.decompress(data)
  elif url.endswith(".gz"):
    import gzip
    data = gzip.decompress(data)

  return data.decode('utf-8')

async def get_url(url: str) -> str:
  res = await session.get(url)
  data = res.body
  loop = asyncio.get_running_loop()
  return await loop.run_in_executor(
    None, _decompress_data,
    url, data)

async def parse_packages(key: Tuple[AsyncCache, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
  cache, url = key
  apt_packages = await cache.get(url, get_url) # type: ignore

  pkg_map = {}
  srcpkg_map = {}

  pkg = None
  srcpkg = None
  for line in apt_packages.split('\n'):
    if line.startswith("Package: "):
      pkg = line[9:]
    elif line.startswith("Source: "):
      srcpkg = line[8:]
    elif line.startswith("Version: "):
      version = line[9:]
      if pkg is not None:
        pkg_map[pkg] = version
      if srcpkg is not None:
        srcpkg_map[srcpkg] = version
      pkg = srcpkg = None

  return pkg_map, srcpkg_map

async def get_version(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
  **kwargs,
) -> VersionResult:
  srcpkg = conf.get('srcpkg')
  pkg = conf.get('pkg')
  mirror = conf['mirror']
  suite = conf['suite']
  repo = conf.get('repo', 'main')
  arch = conf.get('arch', 'amd64')
  strip_release = conf.get('strip_release', False)

  if srcpkg and pkg:
    raise GetVersionError('Setting both srcpkg and pkg is ambigious')
  elif not srcpkg and not pkg:
    pkg = name

  apt_release = await cache.get(
    APT_RELEASE_URL % (mirror, suite), get_url) # type: ignore
  for suffix in APT_PACKAGES_SUFFIX_PREFER:
    packages_path = APT_PACKAGES_PATH % (repo, arch, suffix)
    if " " + packages_path in apt_release:
      break
  else:
    raise GetVersionError('Packages file not found in APT repository')

  pkg_map, srcpkg_map = await cache.get(
    (cache, APT_PACKAGES_URL % (mirror, suite, packages_path)), parse_packages) # type: ignore

  if pkg and pkg in pkg_map:
    version = pkg_map[pkg]
  elif srcpkg and srcpkg in srcpkg_map:
    version = srcpkg_map[srcpkg]
  else:
    raise GetVersionError('package not found in APT repository')

  if strip_release:
    version = version.split("-")[0]
  return version
