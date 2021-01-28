# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import atexit
import asyncio
from typing import Optional, Dict

import structlog
import aiohttp

from .base import BaseSession, TemporaryError, Response, HTTPError

__all__ = ['session']

logger = structlog.get_logger(logger_name=__name__)
connector = aiohttp.TCPConnector(limit=20)

class AiohttpSession(BaseSession):
  def setup(
    self,
    concurreny: int = 20,
    timeout: int = 20,
  ) -> None:
    self.session = aiohttp.ClientSession(
      connector = aiohttp.TCPConnector(limit=concurreny),
      timeout = aiohttp.ClientTimeout(total=timeout),
      trust_env = True,
    )

  async def request_impl(
    self, url: str, *,
    method: str,
    proxy: Optional[str] = None,
    headers: Dict[str, str] = {},
    follow_redirects: bool = True,
    params = (),
    json = None,
  ) -> Response:
    kwargs = {
      'headers': headers,
      'params': params,
      'allow_redirects': follow_redirects,
    }

    if proxy is not None:
      kwargs['proxy'] = proxy
    if json is not None:
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

@atexit.register
def cleanup():
  loop = asyncio.get_event_loop()
  loop.run_until_complete(session.session.close())

session = AiohttpSession()
