# MIT licensed
# Copyright (c) 2018 Felix Yan <felixonmars@archlinux.org>, et al.

import asyncio
import requests

s = requests.Session()
a = requests.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=65535)
s.mount("http://", a)
s.mount("https://", a)

__all__ = ['session', 'HTTPError']

class Session:
  def get(self, url, **kwargs):
    proxy = kwargs.get('proxy')
    if proxy:
      del kwargs['proxy']
    elif hasattr(self, 'nv_config') and self.nv_config.get('proxy'):
      proxy = self.nv_config.get('proxy')
    if proxy:
      kwargs['proxies'] = {'http': proxy, 'https': proxy}

    r = requests.Request('GET', url, **kwargs)
    return ResponseManager(r)

class ResponseManager:
  def __init__(self, req):
    self.req = req

  async def __aenter__(self):
    loop = asyncio.get_event_loop()
    prepped = s.prepare_request(self.req)
    future = loop.run_in_executor(None, s.send, prepped)
    resp = await future
    resp.raise_for_status()
    return resp

  async def __aexit__(self, exc_type, exc, tb):
    pass

real_json = requests.Response.json
async def json_response(self):
  return real_json(self)

async def read(self):
  return self.content

real_HTTPError = requests.exceptions.HTTPError
class HTTPError(real_HTTPError):
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, **kwargs)
    self.code = self.response.status_code

requests.Response.json = json_response
requests.Response.read = read
requests.models.HTTPError = requests.exceptions.HTTPError = HTTPError

session = Session()
