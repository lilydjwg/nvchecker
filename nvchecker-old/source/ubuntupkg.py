# MIT licensed
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import structlog

from . import session, conf_cacheable_with_name

logger = structlog.get_logger(logger_name=__name__)

URL = 'https://api.launchpad.net/1.0/ubuntu/+archive/primary?ws.op=getPublishedSources&source_name=%s&exact_match=true'

get_cacheable_conf = conf_cacheable_with_name('ubuntupkg')

async def get_version(name, conf, **kwargs):
  pkg = conf.get('ubuntupkg') or name
  strip_release = conf.getboolean('strip-release', False)
  suite = conf.get('suite')
  url = URL % pkg

  if suite:
    suite = "https://api.launchpad.net/1.0/ubuntu/" + suite

  releases = []

  while not releases:
    async with session.get(url) as res:
      data = await res.json()

    if not data.get('entries'):
      logger.error('Ubuntu package not found', name=name)
      return

    releases = [r for r in data["entries"] if r["status"] == "Published"]

    if suite:
      releases = [r for r in releases if r["distro_series_link"] == suite]

    if "next_collection_link" not in data:
      break

    url = data["next_collection_link"]

  if not releases:
    logger.error('Ubuntu package not found', name=name)
    return

  if strip_release:
    version = releases[0]['source_package_version'].split("-")[0]
  else:
    version = releases[0]['source_package_version']

  return version
