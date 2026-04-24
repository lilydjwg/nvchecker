# MIT licensed
# Copyright (c) 2026 lilydjwg <lilydjwg@gmail.com>, et al.

from typing import Dict, Optional
import os

import niquests

from .base import BaseSession, TemporaryError, Response, HTTPError

__all__ = ['session']

class NiquestsSession(BaseSession):
  def setup(
    self,
    concurreny: int = 20,
    timeout: int = 20,
    resolver: Optional[str] = None,
  ) -> None:
    self.session = niquests.AsyncSession(
      pool_connections = concurreny,
      pool_maxsize = concurreny,
      timeout = timeout,
      resolver = resolver,
    )
    self.verify = os.environ.get('SSL_CERT_FILE', True)

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
    proxies = None
    if proxy is not None:
      proxies = {
        'http': proxy,
        'https': proxy,
      }

    try:
      if body is not None:
        # Make sure all backends have the same default encoding for post data.
        if 'Content-Type' not in headers:
          headers = {**headers, 'Content-Type': 'application/x-www-form-urlencoded'}
        body = body.encode()
      r = await self.session.request(
        method, url,
        params = params or None,
        data = body,
        json = json,
        headers = headers,
        allow_redirects = follow_redirects,
        proxies = proxies,
        verify = self.verify if verify_cert else False,
      )
      err_cls: Optional[type] = None
      assert r.status_code is not None
      if r.status_code >= 500:
        err_cls = TemporaryError
      elif r.status_code >= 400:
        err_cls = HTTPError
      if err_cls is not None:
        raise err_cls(
          r.status_code,
          r.reason,
          r,
        )
    except (niquests.ConnectionError, niquests.Timeout) as e:
      raise TemporaryError(599, repr(e), None)

    response_body = r.content
    return Response(r.headers, response_body or b'')

  async def aclose(self):
    await self.session.close()
    del self.session


session = NiquestsSession()
