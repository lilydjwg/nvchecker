# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017,2020 Chih-Hsuan Yen <yan12125 at gmail dot com>

import os
import re
from xml.etree import ElementTree

from nvchecker.api import session

_ANDROID_REPO_MANIFESTS = {
  'addon': 'https://dl.google.com/android/repository/addon2-1.xml',
  'package': 'https://dl.google.com/android/repository/repository2-1.xml',
}

# See <channel> tags in Android SDK XML manifests
_CHANNEL_MAP = {
  'stable': 'channel-0',
  'beta': 'channel-1',
  'dev': 'channel-2',
  'canary': 'channel-3',
}

async def _get_repo_manifest(repo):
  repo_xml_url = _ANDROID_REPO_MANIFESTS[repo]

  res = await session.get(repo_xml_url)
  data = res.body.decode('utf-8')

  repo_manifest = ElementTree.fromstring(data)
  return repo_manifest

async def get_version(name, conf, *, cache, **kwargs):
  repo = conf['repo']
  pkg_path_prefix = conf['android_sdk']
  channels = [_CHANNEL_MAP[channel]
              for channel in conf.get('channel', 'stable').split(',')]

  repo_manifest = await cache.get(repo, _get_repo_manifest)

  versions = []

  for pkg in repo_manifest.findall('.//remotePackage'):
    if not pkg.attrib['path'].startswith(pkg_path_prefix):
      continue
    channelRef = pkg.find('./channelRef')
    if channelRef.attrib['ref'] not in channels:
      continue
    for archive in pkg.findall('./archives/archive'):
      host_os = archive.find('./host-os')
      if host_os is not None and host_os.text != conf.get('host_os', 'linux'):
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
      versions.append('.'.join(rev_strs))
      # A package suitable for the target host OS is found - skip remaining
      break

  return versions
