# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import atexit
import asyncio
from typing import Optional, Dict

import structlog
import aiohttp

from .base import BaseSession, TemporaryError, Response

__all__ = ['session']

logger = structlog.get_logger(logger_name=__name__)
connector = aiohttp.TCPConnector(limit=20)

class AiohttpSession(BaseSession):
  def __init__(self):
    self.session = aiohttp.ClientSession(
      connector = aiohttp.TCPConnector(limit=20),
      timeout = aiohttp.ClientTimeout(total=20),
      trust_env = True,
    )

  async def request_impl(
    self, url: str, *,
    method: str,
    proxy: Optional[str] = None,
    headers: Dict[str, str] = {},
    params = (),
    json = None,
  ) -> Response:
    kwargs = {
      'headers': headers,
      'params': params,
    }

    if proxy is not None:
      kwargs['proxy'] = proxy

    try:
      logger.debug('send request', method=method, url=url, kwargs=kwargs)
      res = await self.session.request(
        method, url, **kwargs)
    except (
      asyncio.TimeoutError, aiohttp.ClientConnectorError,
    ) as e:
      raise TemporaryError(599, repr(e), e)

    if res.status >= 500:
      raise TemporaryError(res.status, res.reason, res)
    else:
      res.raise_for_status()

    body = await res.content.read()
    return Response(body)

@atexit.register
def cleanup():
  loop = asyncio.get_event_loop()
  loop.run_until_complete(session.session.close())

session = AiohttpSession()
