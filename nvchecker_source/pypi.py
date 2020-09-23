# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import xmlrpc.client
from typing import List, Tuple, Union
from pkg_resources import parse_version

from nvchecker.api import session

async def pypi_xmlrpc_request(key: Tuple[str, str, bool]) -> Union[str, List[str]]:
  url, package, use_pre_release = key
  payload = xmlrpc.client.dumps((package, use_pre_release), "package_releases")

  res = await session.post(url, headers={"Content-Type": "text/xml"}, body=payload)
  params, methodname = xmlrpc.client.loads(res.body)
  return params[0] # type: ignore

async def get_version(name, conf, *, cache, **kwargs):
  package = conf.get('pypi') or name
  use_pre_release = bool(conf.get('use_pre_release', False))

  url = 'https://pypi.org/pypi'
  data = await cache.get((url, package, use_pre_release), pypi_xmlrpc_request)

  if use_pre_release:
    version = sorted(
      data,
      key = parse_version,
    )[-1]
  else:
    version = data
  return version
