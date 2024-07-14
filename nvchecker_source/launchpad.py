# MIT Licensed
# Copyright (c) 2024 Bert Peters <bertptrs@archlinux.org>, et al.
from __future__ import annotations
from nvchecker.api import AsyncCache, Entry, RichResult

PROJECT_INFO_URL = "https://api.launchpad.net/1.0/{launchpad}"

async def get_version(name: str, conf: Entry, *, cache: AsyncCache, **kwargs):
  launchpad = conf["launchpad"]

  project_data = await cache.get_json(PROJECT_INFO_URL.format(launchpad=launchpad))
  data = await cache.get_json(project_data['releases_collection_link'])

  return [
    RichResult(version=entry["version"], url=entry["web_link"])
    for entry in data["entries"]
  ]



