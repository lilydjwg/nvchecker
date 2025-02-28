# MIT licensed
# Copyright (c) 2025 Maxim Slipenko <maxim@slipenko.com>, et al.

from nvchecker.api import (
  GetVersionError
)
from nvchecker.httpclient.base import HTTPError

URL="https://api.snapcraft.io/v2/snaps/info/%(snap)s"

async def get_version(
  name: str, conf, *,
  cache, keymanager,
  **kwargs,
):
  try:
    snap = conf.get("snap")
    channel = conf.get("channel")

    result = await cache.get_json(
      URL % { "snap": snap },
      headers={
        "Snap-Device-Series": "16",
      },
    )
  except HTTPError:
    raise GetVersionError(f"Failed to request snap info for {snap}")
  
  for c in result['channel-map']:
    if c['channel']['name'] == channel:
      return c['version']
  
  raise GetVersionError(f"Failed to find version for {snap}")
