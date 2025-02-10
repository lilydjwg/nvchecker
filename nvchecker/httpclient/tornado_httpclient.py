# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import json as _json
from urllib.parse import urlencode
from typing import Optional, Dict, Any
import os

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

try:
  import pycurl
except ImportError:
  pycurl = None # type: ignore

from .base import BaseSession, TemporaryError, Response, HTTPError

__all__ = ['session']

HTTP2_AVAILABLE = None if pycurl else False
SSL_CERT_FILE = os.environ.get('SSL_CERT_FILE')

def setup_curl(curl):
  global HTTP2_AVAILABLE
  if HTTP2_AVAILABLE is None:
    try:
      curl.setopt(pycurl.HTTP_VERSION, 4)
      HTTP2_AVAILABLE = True
    except pycurl.error:
      HTTP2_AVAILABLE = False
  elif HTTP2_AVAILABLE:
    curl.setopt(pycurl.HTTP_VERSION, 4)

  if SSL_CERT_FILE:
    curl.setopt_string(pycurl.CAINFO, SSL_CERT_FILE)
  curl.setopt_string(pycurl.ACCEPT_ENCODING, "")

class TornadoSession(BaseSession):
  def setup(
    self,
    concurreny: int = 20,
    timeout: int = 20,
  ) -> None:
    impl: Optional[str]
    if pycurl:
      impl = "tornado.curl_httpclient.CurlAsyncHTTPClient"
    else:
      impl = None
    AsyncHTTPClient.configure(
      impl, max_clients = concurreny)
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
    kwargs: Dict[str, Any] = {
      'method': method,
      'headers': headers,
      'request_timeout': self.timeout,
      'follow_redirects': follow_redirects,
      'validate_cert': verify_cert,
    }

    if body:
      # By default the content type is already 'application/x-www-form-urlencoded'
      kwargs['body'] = body
    elif json:
      kwargs['body'] = _json.dumps(json)
    kwargs['prepare_curl_callback'] = setup_curl

    if proxy:
      host, port = proxy.rsplit(':', 1)
      kwargs['proxy_host'] = host
      kwargs['proxy_port'] = int(port)

    if params:
      q = urlencode(params)
      url += '?' + q

    r = HTTPRequest(url, **kwargs)
    res = await AsyncHTTPClient().fetch(
      r, raise_error=False)
    err_cls: Optional[type] = None
    if res.code >= 500:
      err_cls = TemporaryError
    elif res.code >= 400:
      err_cls = HTTPError
    if err_cls is not None:
      raise err_cls(
        res.code, res.reason, res
      )

    return Response(res.headers, res.body)

session = TornadoSession()
