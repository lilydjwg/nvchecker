import re
import sre_constants
import logging
from functools import partial

from pkg_resources import parse_version
from tornado.httpclient import AsyncHTTPClient

handler_precedence = ('regex',)
logger = logging.getLogger(__name__)

def get_version_by_regex(name, conf, callback):
  try:
    r = re.compile(conf['regex'])
  except sre_constants.error:
    logger.warn('%s: bad regex, skipped.', name, exc_info=True)
    callback(name, None)
    return

  encoding = conf.get('encoding', 'latin1')
  httpclient = AsyncHTTPClient()
  httpclient.fetch(conf['url'], partial(
    _get_version_by_regex, name, r, encoding, callback
  ))

def _get_version_by_regex(name, regex, encoding, callback, res):
  body = res.body.decode(encoding)
  try:
    version = max(regex.findall(body), key=parse_version)
  except ValueError:
    logger.error('%s: version string not found.', name)
    callback(name, None)
  else:
    callback(name, version)

def get_version(name, conf, callback):
  g = globals()
  for key in handler_precedence:
    funcname = 'get_version_by_' + key
    if funcname in g:
      g[funcname](name, conf, callback)
      break
  else:
    logger.error('%s: no idea to get version info.', name)
    callback(name, None)
