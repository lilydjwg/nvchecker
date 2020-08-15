# MIT licensed
# Copyright (c) 2019-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import structlog
from typing import Optional, Dict
import json as _json

from ..ctxvars import tries, proxy, user_agent

logger = structlog.get_logger(logger_name=__name__)

class Response:
  def __init__(self, body):
    self.body = body

  def json(self):
    return _json.loads(self.body.decode('utf-8'))

class BaseSession:
  async def get(self, *args, **kwargs):
    return await self.request(
      method='GET', *args, **kwargs)

  async def post(self, *args, **kwargs):
    return await self.request(
      method='POST', *args, **kwargs)

  async def request(self, *args, **kwargs):
    t = tries.get()
    p = proxy.get()
    ua = user_agent.get()

    headers = kwargs.setdefault('headers', {})
    headers['User-Agent'] = ua

    for i in range(1, t+1):
      try:
        return await self.request_impl(
          proxy = p,
          *args, **kwargs,
        )
      except TemporaryError as e:
        if i == t:
          raise
        else:
          logger.warning('temporary error, retrying',
                         tries = i, exc_info = e)
          continue

  async def request_impl(
    self, url: str, *,
    method: str,
    proxy: Optional[str] = None,
    headers: Dict[str, str] = {},
    params = (),
    json = None,
  ) -> Response:
    raise NotImplementedError

class TemporaryError(Exception):
  def __init__(self, code, message, response):
    self.code = code
    self.message = message
    self.response = response

