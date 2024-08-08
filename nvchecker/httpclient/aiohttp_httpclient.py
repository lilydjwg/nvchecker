# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio
from typing import Optional, Dict

import structlog
import aiohttp

from .base import BaseSession, TemporaryError, Response, HTTPError

__all__ = ['session']

logger = structlog.get_logger(logger_name=__name__)

class AiohttpSession(BaseSession):
  session = None

  def setup(
    self,
    concurreny: int = 20,
    timeout: int = 20,
  ) -> None:
    self._concurreny = concurreny
    self._timeout = timeout

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
    if self.session is None:
      # need to create in async context
      self.session = aiohttp.ClientSession(
        connector = aiohttp.TCPConnector(limit=self._concurreny),
        timeout = aiohttp.ClientTimeout(total=self._timeout),
        trust_env = True,
      )

    kwargs = {
      'headers': headers,
      'params': params,
      'allow_redirects': follow_redirects,
    }
    if not verify_cert:
      kwargs['ssl'] = False

    if proxy is not None:
      kwargs['proxy'] = proxy
    if body is not None:
      # Make sure all backends have the same default encoding for post data.
      if 'Content-Type' not in headers:
        headers = {**headers, 'Content-Type': 'application/x-www-form-urlencoded'}
        kwargs['headers'] = headers
      kwargs['data'] = body.encode()
    elif json is not None:
      kwargs['json'] = json

    try:
      logger.debug('send request', method=method, url=url, kwargs=kwargs)
      res = await self.session.request(
        method, url, **kwargs)
    except (
      asyncio.TimeoutError, aiohttp.ClientConnectorError,
    ) as e:
      raise TemporaryError(599, repr(e), e)

    err_cls: Optional[type] = None
    if res.status >= 500:
      err_cls = TemporaryError
    elif res.status >= 400:
      err_cls = HTTPError
    if err_cls is not None:
      raise err_cls(res.status, res.reason, res)

    body = await res.content.read()
    return Response(res.headers, body)

session = AiohttpSession()
