# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import json
import asyncio
from urllib.parse import urlencode

from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse
from tornado.platform.asyncio import AsyncIOMainLoop, to_asyncio_future
AsyncIOMainLoop().install()

try:
  import pycurl
  AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
except ImportError:
  pycurl = None

__all__ = ['session']

client = AsyncHTTPClient()

def try_use_http2(curl):
  if pycurl:
    curl.setopt(pycurl.HTTP_VERSION, 4)

class Session:
  def get(self, url, **kwargs):
    kwargs['prepare_curl_callback'] = try_use_http2

    proxy = kwargs.get('proxy')
    if proxy:
      del kwargs['proxy']
    elif hasattr(self, 'nv_config') and self.nv_config.get('proxy'):
      proxy = self.nv_config.get('proxy')
    if proxy:
      host, port = proxy.rsplit(':', 1)
      kwargs['proxy_host'] = host
      kwargs['proxy_port'] = int(port)

    params = kwargs.get('params')
    if params:
      del kwargs['params']
      q = urlencode(params)
      url += '?' + q

    r = HTTPRequest(url, **kwargs)
    return ResponseManager(r)

class ResponseManager:
  def __init__(self, req):
    self.req = req

  async def __aenter__(self):
    return await to_asyncio_future(client.fetch(self.req))

  async def __aexit__(self, exc_type, exc, tb):
    pass

async def json_response(self):
  return json.loads(self.body.decode('utf-8'))

async def read(self):
  return self.body

HTTPResponse.json = json_response
HTTPResponse.read = read
session = Session()
