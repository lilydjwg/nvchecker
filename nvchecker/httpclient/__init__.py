# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from typing import Optional

from .base import TemporaryError, HTTPError

class Proxy:
  _obj = None

  def set_obj(self, obj):
    super().__setattr__('_obj', obj)

  def __getattr__(self, name):
    return getattr(self._obj, name)

  def __setattr__(self, name, value):
    return setattr(self._obj, name, value)

session = Proxy()

def setup(
  which: Optional[str] = None,
  concurreny: int = 20,
  timeout: int = 20,
) -> None:
  if which is None:
    which = find_best_httplib()

  m = __import__(
    '%s_httpclient' % which, globals(), locals(), level=1)

  session.set_obj(m.session)
  session.setup(concurreny, timeout)

def find_best_httplib() -> str:
  try:
    import tornado, pycurl
    # connection reuse, http/2
    which = 'tornado'
  except ImportError:
    try:
      import aiohttp
      which = 'aiohttp'
      # connection reuse
    except ImportError:
      try:
        import httpx
        which = 'httpx'
      except ImportError:
        import tornado
        which = 'tornado'
        # fallback

  return which
