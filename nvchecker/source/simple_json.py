# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from . import session

def simple_json(urlpat, confkey, version_from_json):

  async def get_version(name, conf):
    repo = conf.get(confkey) or name
    url = urlpat % repo
    kwargs = {}
    if conf.get('proxy'):
      kwargs["proxy"] = conf.get('proxy')

    async with session.get(url, **kwargs) as res:
      data = await res.json()
    version = version_from_json(data)
    return name, version

  return get_version
