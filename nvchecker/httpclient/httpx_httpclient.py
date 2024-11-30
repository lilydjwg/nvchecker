# MIT licensed
# Copyright (c) 2020-2022,2024 lilydjwg <lilydjwg@gmail.com>, et al.

from typing import Dict, Optional, Tuple

import httpx

from .base import BaseSession, TemporaryError, Response, HTTPError

__all__ = ['session']

class HttpxSession(BaseSession):
  def setup(
    self,
    concurreny: int = 20,
    timeout: int = 20,
  ) -> None:
    self.clients: Dict[Tuple[Optional[str], bool], httpx.AsyncClient] = {}
    self.timeout = timeout

  async def request_impl(
    self, url: str, *,
    method: str,
    proxy: Optional[str] = None,
    headers: Dict[str, str] = {},
    follow_redirects: bool = True,
    params = (),
    json = None,
    body = None,
    verify_cert: bool = True,
  ) -> Response:
    client = self.clients.get((proxy, verify_cert))
    if not client:
      client = httpx.AsyncClient(
        timeout = httpx.Timeout(self.timeout, pool=None),
        http2 = True,
        proxy = proxy,
        verify = verify_cert,
      )
      self.clients[(proxy, verify_cert)] = client

    try:
      if body is not None:
        # Make sure all backends have the same default encoding for post data.
        if 'Content-Type' not in headers:
          headers = {**headers, 'Content-Type': 'application/x-www-form-urlencoded'}
        body = body.encode()
      r = await client.request(
        method, url, json = json, content = body,
        headers = headers,
        follow_redirects = follow_redirects,
        # httpx checks for None but not ()
        params = params or None,
      )
      err_cls: Optional[type] = None
      if r.status_code >= 500:
        err_cls = TemporaryError
      elif r.status_code >= 400:
        err_cls = HTTPError
      if err_cls is not None:
        raise err_cls(
          r.status_code,
          r.reason_phrase,
          r,
        )

    except httpx.TransportError as e:
      raise TemporaryError(599, repr(e), e)

    body = await r.aread()
    return Response(r.headers, body)

  async def aclose(self):
    for client in self.clients.values():
      await client.aclose()
    del self.clients

session = HttpxSession()
