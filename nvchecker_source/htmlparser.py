# MIT licensed
# Copyright (c) 2020 Ypsilik <tt2laurent.maud@gmail.com>, et al.
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from lxml import html, etree

from nvchecker.api import session, GetVersionError

async def get_version(name, conf, *, cache, **kwargs):
  key = (
    conf['url'],
    conf.get('post_data'),
    conf.get('post_data_type', 'application/x-www-form-urlencoded'),
  )
  body = await cache.get(key, get_body)

  encoding = conf.get('encoding')
  is_xml = conf.get('is_xml')
  if is_xml:
    parser = etree.XMLParser(encoding=encoding)
    doc = etree.fromstring(body, base_url=conf['url'], parser=parser)
  else:
    parser = html.HTMLParser(encoding=encoding)
    doc = html.fromstring(body, base_url=conf['url'], parser=parser)

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

async def get_body(info):
  url, post_data, post_data_type = info

  if post_data is None:
    res = await session.get(url)
  else:
    res = await session.post(url, body = post_data, headers = {
      'Content-Type': post_data_type,
    })
  return res.body
