# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

import atexit
from typing import Dict, Optional

import httpx

from .base import BaseSession, TemporaryError, Response

__all__ = ['session']

class HttpxSession(BaseSession):
  def setup(
    self,
    concurreny: int = 20,
    timeout: int = 20,
  ) -> None:
    self.clients: Dict[Optional[str], httpx.AsyncClient] = {}
    self.timeout = timeout

  async def request_impl(
    self, url: str, *,
    method: str,
    proxy: Optional[str] = None,
    headers: Dict[str, str] = {},
    params = (),
    json = None,
  ) -> Response:
    client = self.clients.get(proxy)
    if not client:
      client = httpx.AsyncClient(
        timeout = httpx.Timeout(self.timeout, pool=None),
        http2 = True,
        proxies = {'all://': proxy},
      )
      self.clients[proxy] = client

    try:
      r = await client.request(
        method, url, json = json,
        headers = headers,
        params = params,
      )
      if r.status_code >= 500:
        raise TemporaryError(
          r.status_code,
          r.reason_phrase,
          r,
        )
      else:
        r.raise_for_status()

    except httpx.TransportError as e:
      raise TemporaryError(599, repr(e), e)

    body = await r.aread()
    return Response(body)

  async def aclose(self):
    for client in self.clients.values():
      await client.aclose()
    del self.clients

@atexit.register
def cleanup():
  import asyncio
  loop = asyncio.get_event_loop()
  loop.run_until_complete(session.aclose())

session = HttpxSession()
