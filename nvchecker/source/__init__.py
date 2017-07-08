# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

try:
  import tornado, pycurl
  which = 'tornado'
except ImportError:
  import aiohttp
  which = 'aiohttp'

m = __import__('%s_httpclient' % which, globals(), locals(), level=1)
__all__ = m.__all__
for x in __all__:
  globals()[x] = getattr(m, x)
