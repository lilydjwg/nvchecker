# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

async def get_version(name, conf, *, cache, **kwargs):
  url = conf['mercurial'] + '/json-tags'

  data = await cache.get_json(url)

  version = [tag['tag'] for tag in data['tags']]
  return version
