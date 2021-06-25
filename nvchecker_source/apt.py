# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

from __future__ import annotations

import re
import asyncio
from typing import Dict, Tuple
import itertools
import functools
from collections import defaultdict

from nvchecker.api import (
  session, GetVersionError,
  VersionResult, Entry, AsyncCache, KeyManager,
)

APT_RELEASE_URL = "%s/dists/%s/Release"
APT_PACKAGES_PATH = "%s/binary-%s/Packages%s"
APT_PACKAGES_URL = "%s/dists/%s/%s"
APT_PACKAGES_SUFFIX_PREFER = (".xz", ".gz", "")

DpkgVersion = Tuple[int, str, str]

def parse_version(s: str) -> DpkgVersion:
  try:
    epoch_str, rest = s.split(':', 1)
  except ValueError:
    epoch = 0
    rest = s
  else:
    epoch = int(epoch_str)

  try:
    ver, rev = rest.split('-', 1)
  except ValueError:
    ver = rest
    rev = ''

  return epoch, ver, rev

def _compare_part(a: str, b: str) -> int:
  sa = re.split(r'(\d+)', a)
  sb = re.split(r'(\d+)', b)
  for idx, (pa, pb) in enumerate(itertools.zip_longest(sa, sb)):
    if pa is None:
      return -1
    elif pb is None:
      return 1

    if idx % 2 == 1:
      ret = int(pa) - int(pb)
      if ret != 0:
        return ret
    else:
      if pa < pb:
        return -1
      elif pa > pb:
        return 1

  return 0

def compare_version_parsed(a: DpkgVersion, b: DpkgVersion) -> int:
  ret = a[0] - b[0]
  if ret != 0:
    return ret
  ret = _compare_part(a[1], b[1])
  if ret != 0:
    return ret
  return _compare_part(a[2], b[2])

def compare_version(a: str, b: str) -> int:
  va = parse_version(a)
  vb = parse_version(b)
  return compare_version_parsed(va, vb)

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

  pkg_map = defaultdict(list)
  srcpkg_map = defaultdict(list)

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
        pkg_map[pkg].append(version)
      if srcpkg is not None:
        srcpkg_map[srcpkg].append(version)
      pkg = srcpkg = None

  pkg_map_max = {pkg: max(vs, key=functools.cmp_to_key(compare_version))
                 for pkg, vs in pkg_map.items()}
  srcpkg_map_max = {pkg: max(vs, key=functools.cmp_to_key(compare_version))
                 for pkg, vs in srcpkg_map.items()}

  return pkg_map_max, srcpkg_map_max

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
