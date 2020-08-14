# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

from nvchecker.api import GetVersionError

URL = 'https://api.launchpad.net/1.0/ubuntu/+archive/primary?ws.op=getPublishedSources&source_name=%s&exact_match=true'

async def get_version(name, conf, *, cache, **kwargs):
  pkg = conf.get('ubuntupkg') or name
  strip_release = conf.get('strip_release', False)
  suite = conf.get('suite')
  url = URL % pkg

  if suite:
    suite = "https://api.launchpad.net/1.0/ubuntu/" + suite

  releases = []

  while not releases:
    data = await cache.get_json(url)

    if not data.get('entries'):
      raise GetVersionError('Ubuntu package not found')

    releases = [r for r in data["entries"] if r["status"] == "Published"]

    if suite:
      releases = [r for r in releases if r["distro_series_link"] == suite]

    if "next_collection_link" not in data:
      break

    url = data["next_collection_link"]

  if not releases:
    raise GetVersionError('Ubuntu package not found')
    return

  if strip_release:
    version = releases[0]['source_package_version'].split("-")[0]
  else:
    version = releases[0]['source_package_version']

  return version
