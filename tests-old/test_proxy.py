# MIT licensed
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import sys

try:
  import aiohttp
except ImportError:
  aiohttp = None

import pytest
pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.skipif('nvchecker.source.aiohttp_httpclient' not in sys.modules,
                     reason='aiohttp no chosen'),
]

async def test_proxy(get_version, monkeypatch):
  from nvchecker.source import session

  async def fake_request(*args, proxy, **kwargs):
    class fake_response():
      status = 200

      async def read():
        return proxy.encode("ascii")

      def release():
        pass

    return fake_response

  monkeypatch.setattr(session, "nv_config", {"proxy": "255.255.255.255:65535"}, raising=False)
  monkeypatch.setattr(aiohttp.ClientSession, "_request", fake_request)

  assert await get_version("example", {"regex": "(.+)", "url": "deadbeef"}) == "255.255.255.255:65535"
  assert await get_version("example", {"regex": "(.+)", "url": "deadbeef", "proxy": "0.0.0.0:0"}) == "0.0.0.0:0"
