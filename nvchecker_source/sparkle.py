# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2020 Sunlei <guizaicn@gmail.com>

from xml.etree import ElementTree

from nvchecker.api import session

async def get_version(name, conf, *, cache, **kwargs):
  sparkle = conf['sparkle']
  return await cache.get(sparkle, get_version_impl)

async def get_version_impl(sparkle):
  res = await session.get(sparkle)
  root = ElementTree.fromstring(res.body)
  version = root.find('./channel/item[1]/{http://www.andymatuschak.org/xml-namespaces/sparkle}version')

  return version.text
