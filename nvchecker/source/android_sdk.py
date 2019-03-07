# MIT licensed
# Copyright (c) 2017 Yen Chi Hsuan <yan12125 at gmail dot com>

from asyncio.locks import Lock
import os
import re
from xml.etree import ElementTree

from . import session

_ANDROID_REPO_MANIFESTS = {
  'addon': 'https://dl.google.com/android/repository/addon2-1.xml',
  'package': 'https://dl.google.com/android/repository/repository2-1.xml',
}

_repo_manifests_cache = {}
_repo_manifests_locks = {}

for repo in _ANDROID_REPO_MANIFESTS.keys():
  _repo_manifests_locks[repo] = Lock()

async def _get_repo_manifest(repo):
  async with _repo_manifests_locks[repo]:
    if repo in _repo_manifests_cache:
      return _repo_manifests_cache[repo]

    repo_xml_url = _ANDROID_REPO_MANIFESTS[repo]

    async with session.get(repo_xml_url) as res:
      data = (await res.read()).decode('utf-8')

    repo_manifest = ElementTree.fromstring(data)
    _repo_manifests_cache[repo] = repo_manifest

    return repo_manifest

async def get_version(name, conf, **kwargs):
  repo = conf['repo']
  pkg_path_prefix = conf['android_sdk']

  repo_manifest = await _get_repo_manifest(repo)

  for pkg in repo_manifest.findall('.//remotePackage'):
    if not pkg.attrib['path'].startswith(pkg_path_prefix):
      continue
    for archive in pkg.findall('./archives/archive'):
      host_os = archive.find('./host-os')
      if host_os is not None and host_os.text != 'linux':
        continue
      archive_url = archive.find('./complete/url').text
      # revision
      rev = pkg.find('./revision')
      rev_strs = []
      for part in ('major', 'minor', 'micro'):
        part_node = rev.find('./' + part)
        if part_node is not None:
          rev_strs.append(part_node.text)
      # release number
      filename, ext = os.path.splitext(archive_url)
      rel_str = filename.rsplit('-')[-1]
      mobj = re.match(r'r\d+', rel_str)
      if mobj:
        rev_strs.append(rel_str)
      return '.'.join(rev_strs)
