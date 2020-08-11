# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from pkg_resources import parse_version

from . import conf_cacheable_with_name, session

get_cacheable_conf = conf_cacheable_with_name('pypi')

async def get_version(name, conf, **kwargs):
  package = conf.get('pypi') or name
  use_pre_release = conf.getboolean('use_pre_release', False)

  url = 'https://pypi.org/pypi/{}/json'.format(package)

  async with session.get(url) as res:
    data = await res.json()

  if use_pre_release:
    version = sorted(
      data['releases'].keys(),
      key = parse_version,
    )[-1]
  else:
    version = data['info']['version']
  return version
