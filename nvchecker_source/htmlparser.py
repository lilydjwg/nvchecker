# MIT licensed
# Copyright (c) 2020 Ypsilik <tt2laurent.maud@gmail.com>, et al.
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from lxml import html, etree

from nvchecker.api import session, GetVersionError

async def get_version(name, conf, *, cache, **kwargs):
  key = tuple(sorted(conf.items()))
  return await cache.get(key, get_version_impl)

async def get_version_impl(info):
  conf = dict(info)

  encoding = conf.get('encoding')
  is_xml = conf.get('is_xml')
  if is_xml:
    parser = etree.XMLParser(encoding=encoding)
  else:
    parser = html.HTMLParser(encoding=encoding)
  data = conf.get('post_data')
  if data is None:
    res = await session.get(conf['url'])
  else:
    res = await session.post(conf['url'], body = data, headers = {
        'Content-Type': conf.get('post_data_type', 'application/x-www-form-urlencoded')
      })

  if is_xml:
    doc = etree.fromstring(res.body, base_url=conf['url'], parser=parser)
  else:
    doc = html.fromstring(res.body, base_url=conf['url'], parser=parser)

  try:
    els = doc.xpath(conf.get('xpath'))
  except ValueError:
    if not conf.get('missing_ok', False):
      raise GetVersionError('version string not found.')
  except etree.XPathEvalError as e:
    raise GetVersionError('bad xpath', exc_info=e)

  if is_xml:
    version = [
      str(el)
      if isinstance(el, str)
      else ''.join(el.itertext())
      for el in els
    ]
  else:
    version = [
      str(el)
      if isinstance(el, str)
      else str(el.text_content())
      for el in els
    ]
  return version
