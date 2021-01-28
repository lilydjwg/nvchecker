# MIT licensed
# Copyright (c) 2019-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import structlog
from typing import Optional, Dict, Mapping
import json as _json

from ..ctxvars import tries, proxy, user_agent

logger = structlog.get_logger(logger_name=__name__)

class Response:
  '''The response of an HTTP request.

  .. py:attribute:: body
     :type: bytes

  .. py:attribute:: headers
     :type: Mapping[str, str]
  '''
  def __init__(
    self,
    headers: Mapping[str, str],
    body: bytes,
  ) -> None:
    self.headers = headers
    self.body = body

  def json(self):
    '''Convert reponse content to JSON.'''
    return _json.loads(self.body.decode('utf-8'))

class BaseSession:
  '''The base class for different HTTP backend.'''
  def setup(
    self,
    concurreny: int = 20,
    timeout: int = 20,
  ) -> None:
    pass

  async def head(self, *args, **kwargs):
    '''Shortcut for ``HEAD`` request.'''
    return await self.request(
      method='HEAD', *args, **kwargs)

  async def get(self, *args, **kwargs):
    '''Shortcut for ``GET`` request.'''
    return await self.request(
      method='GET', *args, **kwargs)

  async def post(self, *args, **kwargs):
    '''Shortcut for ``POST`` request.'''
    return await self.request(
      method='POST', *args, **kwargs)

  async def request(
    self, url: str, *,
    method: str,
    headers: Dict[str, str] = {},
    follow_redirects: bool = True,
    params = (),
    json = None,
  ) -> Response:
    t = tries.get()
    p = proxy.get()
    ua = user_agent.get()

    headers = headers.copy()
    headers.setdefault('User-Agent', ua)

    for i in range(1, t+1):
      try:
        return await self.request_impl(
          url,
          method = method,
          headers = headers,
          params = params,
          follow_redirects = follow_redirects,
          json = json,
          proxy = p or None,
        )
      except TemporaryError as e:
        if i == t:
          raise
        else:
          logger.warning('temporary error, retrying',
                         tries = i, exc_info = e)
          continue

    raise Exception('shoud not reach')

  async def request_impl(
    self, url: str, *,
    method: str,
    proxy: Optional[str] = None,
    headers: Dict[str, str] = {},
    follow_redirects: bool = True,
    params = (),
    json = None,
  ) -> Response:
    ''':meta private:'''
    raise NotImplementedError

class BaseHTTPError(Exception):
  def __init__(self, code, message, response):
    self.code = code
    self.message = message
    self.response = response

class TemporaryError(BaseHTTPError):
  '''A temporary error (e.g. network error) happens.'''

class HTTPError(BaseHTTPError):
  ''' An HTTP 4xx error happens '''
