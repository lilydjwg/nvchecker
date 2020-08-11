# MIT licensed
# Copyright (c) 2020 Sunlei <guizaicn@gmail.com>

from xml.etree import ElementTree

from . import session


async def get_version(name, conf, **kwargs):
  sparkle = conf['sparkle']

  async with session.get(sparkle) as res:
    resp = await res.read()

  root = ElementTree.fromstring(resp)
  item = root.find('./channel/item[1]/enclosure')

  version_string = item.get('{http://www.andymatuschak.org/xml-namespaces/sparkle}shortVersionString')
  build_number = item.get('{http://www.andymatuschak.org/xml-namespaces/sparkle}version')

  if (version_string and version_string.isdigit()) and (build_number and not build_number.isdigit()):
    version_string, build_number = build_number, version_string

  version = []

  if version_string:
    version.append(version_string)
  if build_number and (build_number not in version):
    version.append(build_number)

  return '-'.join(version) if version else None
