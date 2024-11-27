# MIT licensed
# Copyright (c) 2024 Jakub Ružička <jru@debian.org>, et al.

import asyncio
import gzip
import pathlib
import urllib

import lxml.etree
from nvchecker.api import session, AsyncCache, Entry, KeyManager, VersionResult


# XML namespaces used in repodata (dead links haha)
NS = {
    'common': 'http://linux.duke.edu/metadata/common',
    'repo':   'http://linux.duke.edu/metadata/repo',
    'rpm':    'http://linux.duke.edu/metadata/rpm'
}


async def get_version(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
  **kwargs,
) -> VersionResult:
  repo = conf['repo']
  arch = conf.get('arch', 'binary')
  pkg = conf.get('pkg')
  if not pkg:
    pkg = conf.get('rpmrepo', name)

  repo_url = urllib.parse.urlparse(repo)
  repo_path = pathlib.PurePosixPath(repo_url.path)

  # get the url of repomd.xml
  repomd_path = repo_path / 'repodata' / 'repomd.xml'
  repomd_url = repo_url._replace(path=str(repomd_path)).geturl()
  # download repomd.xml (use cache)
  repomd_body = await cache.get(repomd_url, get_file)
  # parse repomd.xml
  repomd_xml = lxml.etree.fromstring(repomd_body)

  # get the url of *primary.xml.gz
  primary_element = repomd_xml.find('repo:data[@type="primary"]/repo:location', namespaces=NS)
  primary_path = repo_path / primary_element.get('href')
  primary_url = repo_url._replace(path=str(primary_path)).geturl()
  # download and decompress *primary.xml.gz (use cache)
  primary_body = await cache.get(primary_url, get_file_gz)
  # parse *primary.xml metadata
  metadata = lxml.etree.fromstring(primary_body)

  # use set to eliminate duplication
  versions_set = set()
  # iterate package metadata
  for el in metadata.findall(f'common:package[common:name="{pkg}"]', namespaces=NS):
    pkg_arch = el.findtext('common:arch', namespaces=NS)

    # filter bych arch
    if arch == 'binary':
      if pkg_arch == 'src':
        continue
    elif arch != 'any':
      if pkg_arch != arch:
        continue

    version_info = el.find('common:version', namespaces=NS)
    version = version_info.get('ver')
    versions_set.add(version)

  versions = list(versions_set)
  return versions


async def get_file(url: str) -> str:
  res = await session.get(url)
  return res.body


async def get_file_gz(url: str) -> str:
  res = await session.get(url)
  loop = asyncio.get_running_loop()
  return await loop.run_in_executor(
    None, gzip.decompress, res.body)
