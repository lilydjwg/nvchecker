from functools import partial
import json

from tornado.httpclient import AsyncHTTPClient

URL = 'https://www.archlinux.org/packages/search/json/?name='

def get_version(name, conf, callback):
  pkg = conf['archpkg']
  url = URL + pkg
  AsyncHTTPClient().fetch(url, partial(_pkg_done, name, callback))

def _pkg_done(name, callback, res):
  if res.error:
    raise res.error

  data = json.loads(res.body.decode('utf-8'))

  if not data['results']:
    logger.error('Arch package not found: %s', name)
    callback(name, None)
    return

  version = data['results'][0]['pkgver']
  callback(name, version)
