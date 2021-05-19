# MIT licensed
# Copyright (c) 2020 Ypsilik <tt2laurent.maud@gmail.com>, et al.
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import sre_constants
from lxml import html, etree

from nvchecker.api import session, GetVersionError

async def get_version(name, conf, *, cache, **kwargs):
  key = tuple(sorted(conf.items()))
  return await cache.get(key, get_version_impl)

async def get_version_impl(info):
  conf = dict(info)

  encoding = conf.get('encoding')
  parser = html.HTMLParser(encoding=encoding)
  res = await session.get(conf['url'])
  doc = html.fromstring(res.body, base_url=conf['url'], parser=parser)

  try:
    version = doc.xpath(conf.get('xpath'))
  except ValueError:
    if not conf.get('missing_ok', False):
      raise GetVersionError('version string not found.')
  except etree.XPathEvalError as e:
    raise GetVersionError('bad xpath', exc_info=e)
  return version
